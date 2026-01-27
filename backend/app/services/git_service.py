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
    def pull_and_deploy(project_path: str, branch: str, post_command: str = None, run_as_user: str = "root") -> Tuple[bool, str, Optional[str]]:
        """
        Pull latest code and run post-deploy commands.
        Returns: (success, logs, commit_hash)
        """
        logs = []
        commit_hash = None
        run_as_user = run_as_user or "root" # Ensure not None

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
        logs.append(f"╔══════════════════════════════════════════════════════════╗")
        logs.append(f"║  Deploying: {project_path}")
        logs.append(f"║  Branch: {branch}")
        logs.append(f"║  User: {run_as_user}")
        logs.append(f"╚══════════════════════════════════════════════════════════╝")
        logs.append("")
        logs.append("▶ Step 1: Fetching and pulling latest changes...")
        logs.append(f"  $ git pull origin {branch}")
        logs.append("")

        # Git pull often needs to be run as the owner of the repo?
        # Or root can do it if permissions allow.
        # Ideally, we should run git pull as the user too?
        # Assuming permissions are correct (775), root can pull.
        # Or we should run git pull as the user too.
        # Let's run GIT commands as the user too for safety/permissions consistency.

        # Original code ran simple subprocess, which runs as root (backend user).
        # Let's wrap git pull in sudo too if user != root?
        # But `GitService._run_command` doesn't support sudo yet.
        # For now, let's keep git pull as is (root), assuming root has access.
        # If permissions fail, user might need to fix repo ownership.

        success, output = GitService._run_command(["git", "pull", "origin", branch], cwd=project_path)
        logs.append(output)

        if not success:
            logs.append("")
            logs.append("✗ Git pull failed. Deployment aborted.")
            return False, "\n".join(logs), None

        # Get commit hash after pull
        commit_hash = GitService.get_current_commit(project_path)
        if commit_hash:
            logs.append("")
            logs.append(f"✓ Git pull successful. Current commit: {commit_hash}")

        # 3. Post Deploy Command
        if post_command:
            logs.append("")
            logs.append("▶ Step 2: Running post-deploy command...")
            logs.append(f"  $ {post_command}")
            logs.append("")

            try:
                # Use specified user
                user_name = run_as_user

                logs.append(f"  (Running as user: {user_name})")
                logs.append("")

                safe_command = ["sudo", "-u", user_name, "sh", "-c", post_command]

                result = subprocess.run(
                    safe_command,
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=600,  # 10 minute timeout for build commands
                )
                logs.append(result.stdout)

                if result.returncode != 0:
                    logs.append("")
                    logs.append(f"✗ Post-deploy command failed with exit code {result.returncode}")
                    return False, "\n".join(logs), commit_hash

            except subprocess.TimeoutExpired:
                logs.append("")
                logs.append("✗ Post-deploy command timed out after 10 minutes")
                return False, "\n".join(logs), commit_hash
            except Exception as e:
                logs.append("")
                logs.append(f"✗ Error executing post-deploy command: {str(e)}")
                return False, "\n".join(logs), commit_hash

            logs.append("")
            logs.append("✓ Post-deploy command completed successfully")

        logs.append("")
        logs.append("═══════════════════════════════════════════════════════════")
        logs.append("✓ Deployment completed successfully!")
        logs.append("═══════════════════════════════════════════════════════════")

        return True, "\n".join(logs), commit_hash
