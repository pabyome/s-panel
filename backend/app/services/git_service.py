import subprocess
import os
import logging
import shlex
import uuid
import yaml
from typing import Tuple, Optional, List, Dict


try:
    import pwd
except ImportError:
    pwd = None

logger = logging.getLogger(__name__)


class CommandGroup:
    def __init__(self, isolated: bool = False):
        self.isolated = isolated
        self.commands: List[List[str]] = []

class GitService:
    @staticmethod
    def parse_command_string(command_str: str) -> List[str]:
        """
        Splits command string by '&&', respecting parentheses nesting.
        Returns a list of raw command strings (groups).
        """
        groups = []
        current = []
        paren_level = 0
        i = 0
        length = len(command_str)

        while i < length:
            char = command_str[i]

            if char == '(':
                paren_level += 1
                current.append(char)
            elif char == ')':
                paren_level -= 1
                current.append(char)
            elif char == '&':
                # Check for &&
                if i + 1 < length and command_str[i+1] == '&':
                    if paren_level == 0:
                        # Split point
                        groups.append("".join(current).strip())
                        current = []
                        i += 2 # Skip &&
                        continue
                    else:
                        current.append(char)
                else:
                    current.append(char)
            else:
                current.append(char)

            i += 1

        if current:
            groups.append("".join(current).strip())

        return [g for g in groups if g]

    @staticmethod
    def validate_command(command: str) -> Tuple[bool, str, List[CommandGroup]]:
        """
        Validates and parses command into groups.
        Returns: (is_valid, error_message, list_of_command_groups)
        """
        if not command:
            return True, "", []

        cmd_str = command.strip()

        # 1. Split into top-level groups respecting ()
        # e.g. "(cd A && B) && (cd C)" -> ["(cd A && B)", "(cd C)"]
        raw_groups = GitService.parse_command_string(cmd_str)

        parsed_groups = []
        allowed_executables = {
            "npm", "yarn", "pnpm", "bun",
            "pip", "uv", "poetry", "python", "python3",
            "php", "composer",
            "make", "cargo", "go",
            "echo", "ls", "mkdir", "cp", "mv", "rm", "touch", "cd"
        }

        for raw_group in raw_groups:
            if not raw_group:
                continue

            iso = False
            inner_cmd = raw_group

            # Check isolation
            if raw_group.startswith("(") and raw_group.endswith(")"):
                iso = True
                inner_cmd = raw_group[1:-1].strip()

            group = CommandGroup(isolated=iso)

            # Split inner commands by && (simple split now valid inside the group)
            # Recursion is theoretically better but we assume only 1 level of grouping needed for (cd x && y)
            # If user does (A && (B && C)), our parse_command_string handles top level,
            # but here simple split might break nested parens if they exist.
            # For this feature request, we assume flat chaining inside subshell.

            sub_commands = inner_cmd.split("&&")

            for sub_cmd in sub_commands:
                sub_cmd = sub_cmd.strip()
                if not sub_cmd:
                    continue

                try:
                    parts = shlex.split(sub_cmd)
                except ValueError as e:
                    return False, f"Syntax error: {str(e)}", []

                if not parts:
                    continue

                executable = parts[0]
                is_local_script = executable.startswith("./") or executable.startswith("/")

                if not is_local_script and executable not in allowed_executables:
                    return False, f"Command '{executable}' is not in the allowed list.", []

                group.commands.append(parts)

            if group.commands:
                parsed_groups.append(group)

        return True, "Command is valid", parsed_groups

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
        parsed_deployment_groups = []



        def append_log(msg):
            logs.append(msg)
            if log_callback:
                log_callback("\n".join(logs))

        # 0. Validate post_command security
        if post_command:
            is_valid, msg, parsed_groups_v2 = GitService.validate_command(post_command)
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
        if parsed_deployment_groups:
            append_log("")
            append_log("▶ Step 2: Running post-deploy command...")
            append_log(f"  $ {post_command}")
            append_log("")
            append_log(f"  (Running as user: {run_as_user})")
            append_log("")

            current_cwd = project_path

            for group in parsed_deployment_groups:
                # Save CWD if isolated
                start_cwd = current_cwd


                for cmd_parts in group.commands:
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

                # Restore CWD if isolated
                if group.isolated:
                    current_cwd = start_cwd

            append_log("")
            append_log("✓ Post-deploy command completed successfully")

        append_log("")
        append_log("═══════════════════════════════════════════════════════════")
        append_log("✓ Deployment completed successfully!")
        append_log("═══════════════════════════════════════════════════════════")

        return True, "\n".join(logs), commit_hash
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
        parsed_groups = []

        def append_log(msg):
            logs.append(msg)
            if log_callback:
                log_callback("\n".join(logs))

        # 0. Validate post_command security
        if post_command:
            is_valid, msg, parsed_groups = GitService.validate_command(post_command)
            if not is_valid:
                return False, f"Security Validation Failed: {msg}", None

        # 1. Check path
        if not os.path.isdir(project_path):
            return False, f"Project path does not exist: {project_path}", None

        # 1b. Fix Dubious Ownership (Safe Directory)
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
        if parsed_groups:
            append_log("")
            append_log("▶ Step 2: Running post-deploy command...")


            append_log(f"  $ {post_command}")
            append_log("")
            append_log(f"  (Running as user: {run_as_user})")
            append_log("")

            current_cwd = project_path

            for group in parsed_groups:
                # Save CWD if isolated
                start_cwd = current_cwd

                for cmd_parts in group.commands:
                    try:
                        executable = cmd_parts[0]

                        # Handle built-in cd
                        if executable == "cd":
                            if len(cmd_parts) > 1:
                                target_dir = cmd_parts[1]
                                # Resolve path relative to current_cwd
                                new_path = os.path.abspath(os.path.join(current_cwd, target_dir))
                                if os.path.isdir(new_path):
                                    current_cwd = new_path
                                    append_log(f"  $ cd {target_dir}")
                                else:
                                    append_log(f"✗ cd failed: Directory not found: {target_dir}")
                                    return False, "\n".join(logs), commit_hash
                            continue

                        # Construct command with sudo
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

                # Restore CWD if isolated
                if group.isolated:
                    current_cwd = start_cwd

            append_log("")
            append_log("✓ Post-deploy command completed successfully")

        append_log("")
        append_log("═══════════════════════════════════════════════════════════")
        append_log("✓ Deployment completed successfully!")
        append_log("═══════════════════════════════════════════════════════════")

        return True, "\n".join(logs), commit_hash

    @staticmethod
    def deploy_swarm(
        project_path: str,
        branch: str,
        app_name: str,
        swarm_replicas: int = 2,
        current_port: int = 3000,
        dockerfile_path: str = "Dockerfile",
        run_as_user: str = "root",
        log_callback=None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Deploy application to Docker Swarm.
        Returns: (success, logs, commit_hash)
        """
        logs = []
        commit_hash = None
        registry = "127.0.0.1:5001"

        def append_log(msg):
            logs.append(msg)
            if log_callback:
                log_callback("\n".join(logs))

        if not os.path.isdir(project_path):
            return False, f"Project path does not exist: {project_path}", None

        # Resolve dockerfile path (relative to project_path or absolute)
        if not os.path.isabs(dockerfile_path):
            full_dockerfile_path = os.path.join(project_path, dockerfile_path)
        else:
            full_dockerfile_path = dockerfile_path

        if not os.path.isfile(full_dockerfile_path):
            return False, f"Dockerfile not found at {full_dockerfile_path}", None

        try:
            subprocess.run(
                ["git", "config", "--global", "--add", "safe.directory", project_path],
                cwd=project_path, check=False, capture_output=True
            )
        except Exception:
            pass

        append_log(f"╔══════════════════════════════════════════════════════════╗")
        append_log(f"║  Docker Swarm Deployment: {app_name}")
        append_log(f"║  Path: {project_path}")
        append_log(f"║  Branch: {branch}")
        append_log(f"║  Replicas: {swarm_replicas} | Port: {current_port}")
        append_log(f"╚══════════════════════════════════════════════════════════╝")
        append_log("")

        append_log("▶ Step 1: Pulling latest changes...")
        append_log(f"  $ git pull origin {branch}")
        append_log("")

        success, output = GitService._run_command(["git", "pull", "origin", branch], cwd=project_path)
        append_log(output)

        if not success:
            append_log("✗ Git pull failed. Deployment aborted.")
            return False, "\n".join(logs), None

        commit_hash = GitService.get_current_commit(project_path)
        if commit_hash:
            append_log(f"✓ Git pull successful. Commit: {commit_hash}")
        append_log("")

        safe_name = app_name.lower().replace(" ", "-").replace("_", "-")
        image_tag = f"{registry}/{safe_name}:{commit_hash or 'latest'}"
        image_latest = f"{registry}/{safe_name}:latest"

        append_log("▶ Step 2: Building Docker image...")
        append_log(f"  $ docker build -f {full_dockerfile_path} -t {image_tag} .")
        append_log("")

        try:
            result = subprocess.run(
                ["docker", "build", "-f", full_dockerfile_path, "-t", image_tag, "-t", image_latest, "."],
                cwd=project_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600
            )
            append_log(result.stdout)
            if result.returncode != 0:
                append_log(f"✗ Docker build failed with exit code {result.returncode}")
                return False, "\n".join(logs), commit_hash
        except subprocess.TimeoutExpired:
            append_log("✗ Docker build timed out after 10 minutes")
            return False, "\n".join(logs), commit_hash
        except Exception as e:
            append_log(f"✗ Docker build error: {str(e)}")
            return False, "\n".join(logs), commit_hash

        append_log("✓ Docker image built successfully")
        append_log("")

        append_log("▶ Step 3: Pushing image to local registry...")
        append_log(f"  $ docker push {image_tag}")
        append_log("")

        try:
            result = subprocess.run(
                ["docker", "push", image_tag],
                cwd=project_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300
            )
            append_log(result.stdout)
            if result.returncode != 0:
                append_log(f"✗ Docker push failed with exit code {result.returncode}")
                return False, "\n".join(logs), commit_hash
            subprocess.run(["docker", "push", image_latest], cwd=project_path, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired:
            append_log("✗ Docker push timed out")
            return False, "\n".join(logs), commit_hash
        except Exception as e:
            append_log(f"✗ Docker push error: {str(e)}")
            return False, "\n".join(logs), commit_hash

        append_log("✓ Image pushed to registry")
        append_log("")

        env_vars = {"NODE_ENV": "production"}
        env_file_path = os.path.join(project_path, ".env")
        if os.path.isfile(env_file_path):
            try:
                with open(env_file_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, _, value = line.partition("=")
                            env_vars[key.strip()] = value.strip().strip('"').strip("'")
            except Exception as e:
                append_log(f"  Warning: Could not read .env file: {e}")

        # Enforce APP_PORT and PORT from deployment config (overrides .env)
        env_vars["PORT"] = str(current_port)
        env_vars["APP_PORT"] = str(current_port)


        append_log("▶ Step 4: Deploying to Docker Swarm...")

        stack_config = {
            "version": "3.8",
            "services": {
                "backend": {
                    "image": image_tag,
                    "deploy": {
                        "replicas": swarm_replicas,
                        "update_config": {"parallelism": 1, "delay": "10s", "order": "start-first", "failure_action": "rollback"},
                        "rollback_config": {"parallelism": 1, "delay": "10s"},
                        "restart_policy": {"condition": "on-failure", "delay": "5s", "max_attempts": 3}
                    },
                    "ports": [f"{current_port}:{current_port}"],
                    "environment": env_vars,
                    "extra_hosts": {"host.docker.internal": "host-gateway"},
                    "networks": ["app-net"]
                }
            },
            "networks": {"app-net": {"driver": "overlay"}}
        }

        stack_file = f"/tmp/{safe_name}-stack.yml"
        try:
            with open(stack_file, "w") as f:
                yaml.dump(stack_config, f, default_flow_style=False)
            append_log(f"  Generated stack config: {stack_file}")
        except Exception as e:
            append_log(f"✗ Failed to write stack config: {e}")
            return False, "\n".join(logs), commit_hash

        append_log(f"  $ docker stack deploy -c {stack_file} {safe_name}")
        append_log("")

        try:
            result = subprocess.run(
                ["docker", "stack", "deploy", "-c", stack_file, safe_name],
                cwd=project_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120
            )
            append_log(result.stdout)
            if result.returncode != 0:
                append_log(f"✗ Stack deploy failed with exit code {result.returncode}")
                return False, "\n".join(logs), commit_hash
        except subprocess.TimeoutExpired:
            append_log("✗ Stack deploy timed out")
            return False, "\n".join(logs), commit_hash
        except Exception as e:
            append_log(f"✗ Stack deploy error: {str(e)}")
            return False, "\n".join(logs), commit_hash

        append_log("")
        append_log("═══════════════════════════════════════════════════════════")
        append_log("✓ Docker Swarm deployment completed successfully!")
        append_log(f"  Stack: {safe_name} | Image: {image_tag} | Replicas: {swarm_replicas}")
        append_log("═══════════════════════════════════════════════════════════")

        return True, "\n".join(logs), commit_hash
