import subprocess
import os
import logging
import shlex
from typing import Tuple, Optional, List

try:
    import pwd
except ImportError:
    pwd = None

logger = logging.getLogger(__name__)


class GitService:
    @staticmethod
    def validate_command(command: str) -> Tuple[bool, str, List[List[str]]]:
        """
        Validates a shell command for safety and parses it.
        Returns: (is_valid, error_message, list_of_command_lists)
        """
        if not command:
            return True, "", []

        # Normalize
        cmd_str = command.strip()

        # Split by && to support simple chaining
        # using split("&&") is simplistic but valid for "cmd1 && cmd2" structure.
        # It does NOT handle "cmd1 && cmd2" inside quotes, but that's acceptable limitation for this tool.
        # Ideally we parse the whole string, but shlex doesn't handle operators like && easily outside shell.
        # We assume users separate commands by &&.
        sub_commands_raw = cmd_str.split("&&")

        parsed_commands = []

        allowed_executables = {
            "npm", "yarn", "pnpm", "bun",
            "pip", "uv", "poetry", "python", "python3",
            "php", "composer",
            "make", "cargo", "go",
            "echo", "ls", "mkdir", "cp", "mv", "rm", "touch", "cd"
        }

        for sub_cmd_raw in sub_commands_raw:
            sub_cmd_raw = sub_cmd_raw.strip()
            if not sub_cmd_raw:
                continue

            # Strip subshell grouping parentheses to support (cd foo && bar) syntax
            # We execute linearly, so we unwrap them.
            sub_cmd_raw = sub_cmd_raw.lstrip("(").rstrip(")")

            try:
                # Use shlex to parse arguments correctly (handling quotes)
                parts = shlex.split(sub_cmd_raw)
            except ValueError as e:
                return False, f"Syntax error in command: {str(e)}", []

            if not parts:
                continue

            executable = parts[0]

            # Allow local scripts (./script.sh)
            is_local_script = executable.startswith("./") or executable.startswith("/")

            # Check allowlist
            if not is_local_script and executable not in allowed_executables:
                return False, f"Command '{executable}' is not in the allowed list.", []

            # Additional checks for dangerous arguments could go here
            # e.g. blocking ";", "|", ">" is handled implicitly because shlex treats them as args
            # and we run with shell=False, so they won't be interpreted by shell.
            # However, we should ensure no argument tries to use shell features that might be passed to a sub-shell?
            # Since strict execution avoids shell, passing ">" as an arg just passes strictly ">".

            parsed_commands.append(parts)

        return True, "Command is valid", parsed_commands

    @staticmethod
    def _run_command(command: list[str], cwd: str) -> Tuple[bool, str]:
        """Runs a shell command and returns (success, output)."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stdout or str(e)
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 5 minutes"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_current_commit(project_path: str) -> Optional[str]:
        """Get the current commit hash (short version)."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    @staticmethod
    def pull_and_deploy(project_path: str, branch: str, post_command: str = None, run_as_user: str = "root", log_callback=None) -> Tuple[bool, str, Optional[str]]:
        """
        Pull latest code and run post-deploy commands.
        Returns: (success, logs, commit_hash)
        """
        logs = []
        commit_hash = None
        run_as_user = run_as_user or "root" # Ensure not None
        parsed_deployment_commands = []

        def append_log(msg):
            logs.append(msg)
            if log_callback:
                log_callback("\n".join(logs))

        # 0. Validate post_command security
        if post_command:
            is_valid, msg, parsed_deployment_commands = GitService.validate_command(post_command)
            if not is_valid:
                return False, f"Security Validation Failed: {msg}", None

        # 1. Check path
        if not os.path.isdir(project_path):
            return False, f"Project path does not exist: {project_path}", None

        # 1b. Fix Dubious Ownership (Safe Directory)
        # When running as root, we need to explicitly trust directories owned by other users
        # This prevents "fatal: detected dubious ownership"
        try:
             subprocess.run(
                 ["git", "config", "--global", "--add", "safe.directory", project_path],
                 cwd=project_path,
                 check=False,
                 capture_output=True
             )
        except Exception:
             pass

        # 2. Git Pull
        append_log(f"╔══════════════════════════════════════════════════════════╗")
        append_log(f"║  Deploying: {project_path}")
        append_log(f"║  Branch: {branch}")
        append_log(f"║  User: {run_as_user}")
        append_log(f"╚══════════════════════════════════════════════════════════╝")
        append_log("")
        append_log("▶ Step 1: Fetching and pulling latest changes...")
        append_log(f"  $ git pull origin {branch}")
        append_log("")

        success, output = GitService._run_command(["git", "pull", "origin", branch], cwd=project_path)
        append_log(output)

        if not success:
            append_log("")
            append_log("✗ Git pull failed. Deployment aborted.")
            return False, "\n".join(logs), None

        # Get commit hash after pull
        commit_hash = GitService.get_current_commit(project_path)
        if commit_hash:
            append_log("")
            append_log(f"✓ Git pull successful. Current commit: {commit_hash}")

        # 3. Post Deploy Command
        if parsed_deployment_commands:
            append_log("")
            append_log("▶ Step 2: Running post-deploy command...")
            append_log(f"  $ {post_command}")
            append_log("")
            append_log(f"  (Running as user: {run_as_user})")
            append_log("")

            current_cwd = project_path

            for cmd_parts in parsed_deployment_commands:
                try:
                    executable = cmd_parts[0]

                    # Handle built-in cd
                    if executable == "cd":
                        if len(cmd_parts) > 1:
                            target_dir = cmd_parts[1]
                            # Resolve path relative to current_cwd
                            new_path = os.path.abspath(os.path.join(current_cwd, target_dir))
                            # Security check: prevent cd out of known areas?
                            # For simplicity we allow it, as user is essentially admin/deployer
                            if os.path.isdir(new_path):
                                current_cwd = new_path
                                append_log(f"  $ cd {target_dir}")
                            else:
                                append_log(f"✗ cd failed: Directory not found: {target_dir}")
                                return False, "\n".join(logs), commit_hash
                        continue

                    # Construct command with sudo
                    # "sudo -u user executable args..."
                    safe_command = ["sudo", "-u", run_as_user] + cmd_parts

                    # Log the command being run
                    pretty_cmd = " ".join(cmd_parts)
                    append_log(f"  $ {pretty_cmd}")

                    result = subprocess.run(
                        safe_command,
                        cwd=current_cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        timeout=600,
                    )
                    append_log(result.stdout)

                    if result.returncode != 0:
                        append_log("")
                        append_log(f"✗ Command failed with exit code {result.returncode}")
                        return False, "\n".join(logs), commit_hash

                except subprocess.TimeoutExpired:
                    append_log("")
                    append_log("✗ Command timed out after 10 minutes")
                    return False, "\n".join(logs), commit_hash
                except Exception as e:
                    append_log("")
                    append_log(f"✗ Error executing command: {str(e)}")
                    return False, "\n".join(logs), commit_hash

            append_log("")
            append_log("✓ Post-deploy command completed successfully")

        append_log("")
        append_log("═══════════════════════════════════════════════════════════")
        append_log("✓ Deployment completed successfully!")
        append_log("═══════════════════════════════════════════════════════════")

        return True, "\n".join(logs), commit_hash
