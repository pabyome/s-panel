import subprocess
import os
import logging
from typing import Tuple, Optional

try:
    import pwd
except ImportError:
    pwd = None

logger = logging.getLogger(__name__)


class GitService:
    @staticmethod
    def validate_command(command: str) -> Tuple[bool, str]:
        """
        Validates a shell command for safety.
        Allowed: npm, yarn, pnpm, bun, pip, uv, poetry, python, php, composer, make, cargo, go, ./
        Blocked: sudo, su, dangerous file ops, chaining with dangerous intent
        """
        if not command:
            return True, ""

        # Normalize
        cmd = command.strip()

        # Check against blacklist
        blacklist = [
            "sudo", "su ", "rm -rf", "mv /", "cp /", "chown", "chmod",
            "|", ">", ">>", "<",  # Block pipes and redirections for simplicity/safety
            ";", # Block command chaining with semicolon (use && instead)
            "`", "$(", # Block command substitution
            "/bin/", "/usr/", "/etc/", "/var/", # strict path blocking
        ]

        for term in blacklist:
            if term in cmd:
                return False, f"Command contains forbidden term: '{term}'"

        # Allow-list for command prefixes (and && chaining)
        # We split by && to check each sub-command
        sub_commands = cmd.split("&&")

        allowed_prefixes = [
            "npm", "yarn", "pnpm", "bun",
            "pip", "uv", "poetry", "python", "python3",
            "php", "composer",
            "make", "cargo", "go",
            "./", # Allow local scripts
            "cd", "echo", "ls", "mkdir", "cp", "mv", "rm", "touch", "(", # Common shell ops
        ]

        for sub_cmd in sub_commands:
            sub_cmd = sub_cmd.strip()
            if not sub_cmd:
                continue

            is_valid = False
            for prefix in allowed_prefixes:
                if sub_cmd.startswith(prefix + " ") or sub_cmd == prefix or sub_cmd.startswith(prefix):
                     is_valid = True
                     break

            if not is_valid:
                return False, f"Command starting with '{sub_cmd.split(' ')[0]}' is not in the allow-list."

        return True, "Command is valid"

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

        def append_log(msg):
            logs.append(msg)
            if log_callback:
                log_callback("\n".join(logs))

        # 0. Validate post_command security
        if post_command:
            is_valid, msg = GitService.validate_command(post_command)
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
        if post_command:
            append_log("")
            append_log("▶ Step 2: Running post-deploy command...")
            append_log(f"  $ {post_command}")
            append_log("")

            try:
                # Use specified user
                user_name = run_as_user
                append_log(f"  (Running as user: {user_name})")
                append_log("")

                safe_command = ["sudo", "-u", user_name, "sh", "-c", post_command]

                # We could stream here, but for stability let's keep it blocking
                # but maybe with a slightly shorter timeout logic or just wait
                result = subprocess.run(
                    safe_command,
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=600,
                )
                append_log(result.stdout)

                if result.returncode != 0:
                    append_log("")
                    append_log(f"✗ Post-deploy command failed with exit code {result.returncode}")
                    return False, "\n".join(logs), commit_hash

            except subprocess.TimeoutExpired:
                append_log("")
                append_log("✗ Post-deploy command timed out after 10 minutes")
                return False, "\n".join(logs), commit_hash
            except Exception as e:
                append_log("")
                append_log(f"✗ Error executing post-deploy command: {str(e)}")
                return False, "\n".join(logs), commit_hash

            append_log("")
            append_log("✓ Post-deploy command completed successfully")

        append_log("")
        append_log("═══════════════════════════════════════════════════════════")
        append_log("✓ Deployment completed successfully!")
        append_log("═══════════════════════════════════════════════════════════")

        return True, "\n".join(logs), commit_hash
