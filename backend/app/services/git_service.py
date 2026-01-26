import subprocess
import os
import shlex
from typing import Tuple
try:
    import pwd
except ImportError:
    pwd = None

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
                text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stdout
        except Exception as e:
            return False, str(e)

    @staticmethod
    def pull_and_deploy(project_path: str, branch: str, post_command: str = None) -> Tuple[bool, str]:
        logs = []

        # 1. Check path
        if not os.path.isdir(project_path):
            return False, f"Project path does not exist: {project_path}"

        # 2. Git Pull
        logs.append(f"--- Deploying to {project_path} (Branch: {branch}) ---")
        logs.append("Executing: git pull")

        # Ensure we fetch origin first? Or just pull. Assumes remote is configured.
        success, output = GitService._run_command(["git", "pull", "origin", branch], cwd=project_path)
        logs.append(output)

        if not success:
            logs.append("!!! Git Pull Failed. Aborting.")
            return False, "\n".join(logs)

        # 3. Post Deploy Command
        if post_command:
            logs.append(f"Executing Post-Deploy Command: {post_command}")
            # Security Note: Running shell commands is risky. Ideally we'd use non-shell run,
            # but user likely wants '&&' chaining provided in the UI example.
            # Security Improvement: Execute as the owner of the project directory.
            # This prevents the command from running as root (if panel is root).
            try:
                stat_info = os.stat(project_path)
                uid = stat_info.st_uid

                if pwd:
                    user_name = pwd.getpwuid(uid).pw_name
                else:
                    # Fallback for non-Unix
                    user_name = os.getlogin() # or just return error

                logs.append(f"Detected project owner: {user_name}. Demoting privileges...")

                # Construct command to run as user
                # We use sh -c to preserve the shell behavior (&& chaining etc)
                # sudo -u <user> sh -c "<command>"
                safe_command = ["sudo", "-u", user_name, "sh", "-c", post_command]

                result = subprocess.run(
                    safe_command,
                    cwd=project_path,
                    # shell=False because we are invoking sudo directly
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                logs.append(result.stdout)

                if result.returncode != 0:
                     logs.append(f"!!! Post-deploy command failed with code {result.returncode}")
                     return False, "\n".join(logs)

            except ImportError:
                 # pwd might not exist on Windows, but this is Linux/Mac target
                 logs.append("!!! Could not determine user. Running as current user (Risk!).")
                 # Fallback to original unsafe behavior or fail? Fail safe is better.
                 return False, "Could not determine project owner for safe execution."
            except Exception as e:
                logs.append(f"!!! Error executing post-deploy command: {str(e)}")
                return False, "\n".join(logs)

        logs.append("--- Deployment Successful ---")
        return True, "\n".join(logs)
