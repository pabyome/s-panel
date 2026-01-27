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
    def pull_and_deploy(project_path: str, branch: str, post_command: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Pull latest code and run post-deploy commands.
        Returns: (success, logs, commit_hash)
        """
        logs = []
        commit_hash = None

        # 1. Check path
        if not os.path.isdir(project_path):
            return False, f"Project path does not exist: {project_path}", None

        # 2. Git Pull
        logs.append(f"╔══════════════════════════════════════════════════════════╗")
        logs.append(f"║  Deploying: {project_path}")
        logs.append(f"║  Branch: {branch}")
        logs.append(f"╚══════════════════════════════════════════════════════════╝")
        logs.append("")
        logs.append("▶ Step 1: Fetching and pulling latest changes...")
        logs.append(f"  $ git pull origin {branch}")
        logs.append("")

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
                stat_info = os.stat(project_path)
                uid = stat_info.st_uid

                if pwd:
                    user_name = pwd.getpwuid(uid).pw_name
                else:
                    user_name = os.getlogin()

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
