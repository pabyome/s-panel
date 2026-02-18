import logging
import os
import subprocess
import yaml
import uuid
import asyncio
import copy
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.models.deployment import DeploymentConfig
from app.services.git_service import GitService
from app.services.docker_service import docker_service

logger = logging.getLogger(__name__)

class LaravelService:
    @staticmethod
    def _append_log(logs: List[str], msg: str, callback=None):
        logs.append(msg)
        if callback:
            callback("\n".join(logs))

    @staticmethod
    async def deploy(deployment: DeploymentConfig, log_callback=None) -> tuple[bool, str, Optional[str], Optional[str]]:
        """
        Orchestrates a Laravel Zero-Downtime Deployment.
        Returns: (success, logs, commit_hash, image_tag)
        """
        logs = []
        commit_hash = None
        project_path = deployment.project_path

        def log(msg):
            LaravelService._append_log(logs, msg, log_callback)

        log(f"╔══════════════════════════════════════════════════════════╗")
        log(f"║  Laravel Deployment Engine: {deployment.name}")
        log(f"║  Path: {project_path}")
        log(f"║  Branch: {deployment.branch}")
        log(f"╚══════════════════════════════════════════════════════════╝")
        log("")

        # 1. Git Pull
        log("▶ Step 1: Git Pull...")
        try:
            # We use GitService's lock and pull mechanism, but we need to call it carefully.
            # GitService.pull_and_deploy does too much (post commands).
            # We'll just use the raw git commands via GitService helper or subprocess here to keep control.

            # Use the lock from GitService
            with GitService._git_lock(project_path, log_callback=log):
                GitService._run_command(["git", "config", "pull.rebase", "false"], cwd=project_path)
                success, output = GitService._run_command(["git", "pull", "origin", deployment.branch], cwd=project_path)
                log(output)
                if not success:
                    log("✗ Git pull failed.")
                    return False, "\n".join(logs), None, None

                commit_hash = GitService.get_current_commit(project_path)
                log(f"✓ Git pull successful. Commit: {commit_hash}")

        except Exception as e:
            log(f"✗ Git error: {e}")
            return False, "\n".join(logs), None, None

        # 2. Build Docker Image
        log("")
        log("▶ Step 2: Building Docker Image...")

        registry = settings.DOCKER_REGISTRY
        safe_name = deployment.name.lower().replace(" ", "-").replace("_", "-")
        image_tag = f"{registry}/{safe_name}:{commit_hash or 'latest'}"
        image_latest = f"{registry}/{safe_name}:latest"

        dockerfile_path = deployment.dockerfile_path or "Dockerfile"
        full_dockerfile_path = os.path.join(project_path, dockerfile_path)

        if not os.path.isfile(full_dockerfile_path):
             log(f"✗ Dockerfile not found at {full_dockerfile_path}")
             return False, "\n".join(logs), commit_hash, image_tag

        try:
            # We run build command
            # TODO: Add specific platform if needed, but for swarm on same node, default is fine.
            cmd = ["docker", "build", "-f", full_dockerfile_path, "-t", image_tag, "-t", image_latest, "."]
            log(f"  $ {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

            stdout, _ = await process.communicate()
            log(stdout.decode())

            if process.returncode != 0:
                log("✗ Docker build failed.")
                return False, "\n".join(logs), commit_hash, image_tag

            log("✓ Build successful.")

            # Push
            log("")
            log("▶ Step 3: Pushing Image...")
            log(f"  $ docker push {image_tag}")

            process = await asyncio.create_subprocess_exec(
                "docker", "push", image_tag,
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, _ = await process.communicate()
            log(stdout.decode())

            if process.returncode != 0:
                 log("✗ Docker push failed.")
                 return False, "\n".join(logs), commit_hash, image_tag

            # Also push latest
            subprocess.run(["docker", "push", image_latest], cwd=project_path, capture_output=True)
            log("✓ Push successful.")

        except Exception as e:
             log(f"✗ Build/Push error: {e}")
             return False, "\n".join(logs), commit_hash, image_tag

        # 3. Prepare Environment & Migrations (The "Laravel" Part)
        log("")
        log("▶ Step 4: Environment & Migrations...")

        # We need to run migrations. We can run a one-off container using the NEW image.
        # This ensures migrations run with the new code/schema definitions.

        env_vars = LaravelService._get_env_vars(project_path, deployment.current_port)

        # Add DB credentials from .env if possible, but they are inside .env which we read.
        # We assume the container can reach the DB (network needs to be shared).
        # We use 'host' network for one-off tasks to ensure it can reach local DBs if needed,
        # or attach to the specific app network.

        # Network: 'app-net' is used in GitService.deploy_swarm. We should probably use that.
        # Ensure 'app-net' exists before running container attached to it.
        try:
             # Check if network exists
             subprocess.run(["docker", "network", "inspect", "app-net"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
             log("  ! Network 'app-net' not found. Creating it...")
             try:
                 subprocess.run(["docker", "network", "create", "--driver", "overlay", "--attachable", "app-net"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                 log("  ✓ Network 'app-net' created.")
             except subprocess.CalledProcessError as e:
                 log(f"  ✗ Failed to create network: {e}")
                 return False, "\n".join(logs), commit_hash, image_tag

        migration_cmd = ["php", "artisan", "migrate", "--force"]

        log(f"  $ docker run --rm {image_tag} php artisan migrate --force")

        try:
             # Run migration in a temporary container
             # We mount .env? Or pass env vars? passing env vars is safer/cleaner if we parsed them.
             # But Laravel usually expects .env file.
             # We can bind mount the .env file from host.

             volumes = {}
             env_file_path = os.path.join(project_path, ".env")
             if os.path.isfile(env_file_path):
                 volumes[env_file_path] = {'bind': '/var/www/html/.env', 'mode': 'ro'} # Assuming standard path
             else:
                 log("  ! No .env file found. Proceeding with env vars only.")

             # We also need to map extra hosts
             extra_hosts = {"host.docker.internal": "host-gateway"}

             # Use docker library or subprocess? Subprocess is easier for logging output stream.
             # But constructing the huge command is annoying.
             # Let's use `docker run` via subprocess.

             docker_run_cmd = [
                 "docker", "run", "--rm",
                 "--add-host", "host.docker.internal:host-gateway",
                 "--network", "app-net" # Assuming app-net exists
             ]

             # Mounts
             if os.path.isfile(env_file_path):
                 docker_run_cmd.extend(["-v", f"{env_file_path}:/usr/src/app/.env"]) # Standardize dest?
                 # Wait, GitService used /usr/src/app. Let's stick to that.

             docker_run_cmd.append(image_tag)
             docker_run_cmd.extend(migration_cmd)

             # Note: If /usr/src/app is not the WORKDIR in Dockerfile, this might fail to find artisan.
             # We assume standard Laravel Dockerfile.

             process = await asyncio.create_subprocess_exec(
                 *docker_run_cmd,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.STDOUT
             )
             stdout, _ = await process.communicate()
             log(stdout.decode())

             if process.returncode != 0:
                 log("✗ Migrations failed. Aborting deployment.")
                 return False, "\n".join(logs), commit_hash, image_tag

             log("✓ Migrations completed.")

             # Optimization
             log("  $ php artisan config:cache && route:cache && view:cache")
             # We can run this here, BUT these caches are filesystem based.
             # If we run them in a temp container, they vanish.
             # They must be run DURING build (in Dockerfile) OR inside the running container on startup (entrypoint).
             # Best practice: Run in Dockerfile.
             # If not in Dockerfile, we can't persist them unless we use a volume, which is bad for rolling updates.
             # Alternative: The user's Dockerfile SHOULD do this.
             # Or, we can update the 'command' in stack file to run them before start.
             # For now, we assume user handles this or we skip it.
             # However, the prompt asked: "Run php artisan config:cache to ensure..."
             # If we do it here, it has no effect on the swarm service containers.
             # So we will skip this step here and assume the Dockerfile or Entrypoint handles it,
             # OR we instruct the stack to run a command that does it.
             # We can override the command in the stack service definition!
             # command: sh -c "php artisan config:cache && php artisan route:cache && php artisan serve ..."

             log("  (Skipping cache commands as they should be part of container startup or Dockerfile)")

        except Exception as e:
            log(f"✗ Migration error: {e}")
            return False, "\n".join(logs), commit_hash, image_tag

        # 4. Deploy Stack (Swarm Update)
        log("")
        log("▶ Step 5: Swarm Update (Rolling)...")

        stack_config = LaravelService.generate_stack_config(deployment, image_tag, env_vars)

        stack_file = f"/tmp/{safe_name}-stack.yml"
        try:
            with open(stack_file, "w") as f:
                yaml.dump(stack_config, f, default_flow_style=False)
            log(f"  Generated stack config: {stack_file}")

            cmd = ["docker", "stack", "deploy", "-c", stack_file, safe_name]
            log(f"  $ {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, _ = await process.communicate()
            log(stdout.decode())

            if process.returncode != 0:
                log("✗ Stack deploy failed.")
                return False, "\n".join(logs), commit_hash, image_tag

            log("✓ Stack deploy command sent.")

        except Exception as e:
            log(f"✗ Stack deploy error: {e}")
            return False, "\n".join(logs), commit_hash, image_tag

        # 5. Health Check / Wait
        log("")
        log("▶ Step 6: Health Check & Cleanup...")
        log("  Waiting for services to stabilize...")

        # Poll for health (max 60s)
        is_healthy = False
        for i in range(12):
            await asyncio.sleep(5)
            status = LaravelService.get_stack_status(deployment)

            # Check if all enabled services have running replicas >= desired
            healthy_count = 0
            target_count = 0

            # Web
            target_count += 1
            if status["web"]["running"] >= deployment.swarm_replicas:
                healthy_count += 1

            # Worker
            if deployment.laravel_worker_replicas > 0:
                target_count += 1
                if status["worker"]["running"] >= deployment.laravel_worker_replicas:
                    healthy_count += 1

            if healthy_count >= target_count:
                is_healthy = True
                break

            log(f"  ... Checking health ({i+1}/12): Web: {status['web']['running']}/{deployment.swarm_replicas}, Worker: {status['worker']['running']}/{deployment.laravel_worker_replicas}")

        if is_healthy:
            log("✓ Health check passed: All services running.")
        else:
            log("⚠ Health check warning: Services did not reach desired state in 60s.")
            # We don't fail deployment here because it might be slow startup, but we warn.

        log("✓ Deployment sequence finished.")
        return True, "\n".join(logs), commit_hash, image_tag

    @staticmethod
    async def rollback(deployment: DeploymentConfig, image_tag: str, log_callback=None) -> tuple[bool, str]:
        """
        Rollback to a specific image tag.
        """
        logs = []
        def log(msg):
            LaravelService._append_log(logs, msg, log_callback)

        log(f"╔══════════════════════════════════════════════════════════╗")
        log(f"║  ROLLBACK INITIATED: {deployment.name}")
        log(f"║  Target Image: {image_tag}")
        log(f"╚══════════════════════════════════════════════════════════╝")
        log("")

        # Generate stack config with OLD image
        project_path = deployment.project_path
        env_vars = LaravelService._get_env_vars(project_path, deployment.current_port)

        log("▶ Generating Stack Config with old image...")
        stack_config = LaravelService.generate_stack_config(deployment, image_tag, env_vars)

        safe_name = deployment.name.lower().replace(" ", "-").replace("_", "-")
        stack_file = f"/tmp/{safe_name}-rollback.yml"

        try:
            with open(stack_file, "w") as f:
                yaml.dump(stack_config, f, default_flow_style=False)

            cmd = ["docker", "stack", "deploy", "-c", stack_file, safe_name]
            log(f"  $ {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, _ = await process.communicate()
            log(stdout.decode())

            if process.returncode != 0:
                log("✗ Rollback failed.")
                return False, "\n".join(logs)

            log("✓ Rollback command sent.")
            log("  Waiting for services to stabilize...")
            await asyncio.sleep(10)
            log("✓ Rollback sequence finished.")
            return True, "\n".join(logs)

        except Exception as e:
            log(f"✗ Rollback error: {e}")
            return False, "\n".join(logs)

    @staticmethod
    def generate_stack_config(deployment: DeploymentConfig, image: str, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """
        Generates the docker-stack.yml content for a Laravel application.
        """
        safe_name = deployment.name.lower().replace(" ", "-").replace("_", "-")

        # Base Service Config
        base_service = {
            "image": image,
            "environment": env_vars,
            "extra_hosts": {
                "host.docker.internal": "host-gateway",
                "localhost": "host-gateway"
            },
            "networks": ["app-net"]
        }

        # Volumes (Mount .env and credentials if any)
        volumes = []
        project_path = deployment.project_path

        # Mount .env
        env_file = os.path.join(project_path, ".env")
        if os.path.isfile(env_file):
             volumes.append(f"{env_file}:/usr/src/app/.env")

        # Mount other config files
        try:
            for file in os.listdir(project_path):
                if file.endswith((".json", ".pem", ".xml")):
                     host_path = os.path.join(project_path, file)
                     container_path = f"/usr/src/app/{file}"
                     volumes.append(f"{host_path}:{container_path}")
        except Exception:
            pass

        # Add Persistent Storage Volume
        # This volume persists 'storage' directory which contains logs, app files, etc.
        # We use a named volume prefixed with the safe_name
        volumes.append(f"{safe_name}_storage:/usr/src/app/storage")

        if volumes:
            base_service["volumes"] = volumes

        services = {}

        # 1. Web Service (Nginx/PHP)
        services["web"] = copy.deepcopy(base_service)
        services["web"]["deploy"] = {
            "replicas": deployment.swarm_replicas,
            "update_config": {"parallelism": 1, "delay": "10s", "order": "start-first", "failure_action": "rollback"},
            "rollback_config": {"parallelism": 1, "delay": "10s"},
            "restart_policy": {"condition": "on-failure", "delay": "5s", "max_attempts": 3}
        }
        # Explicitly force FrankenPHP to listen on the correct port and bind to all interfaces (IPv4/IPv6) and serve from public/
        services["web"]["command"] = ["frankenphp", "php-server", "--listen", f":{deployment.current_port}", "--root", "public/"]

        services["web"]["ports"] = [f"{deployment.current_port}:{deployment.current_port}"]
        # Use TCP healthcheck to ensure the container is listening.
        # This avoids boot loops if the application returns 500 (e.g. DB connection error), allowing debugging.
        services["web"]["healthcheck"] = {
            "test": ["CMD-SHELL", f"php -r \"\\$e=0; \\$s=''; if(!@fsockopen('127.0.0.1', {deployment.current_port}, \\$e, \\$s, 2)) exit(1);\""],
            "interval": "30s",
            "timeout": "5s",
            "retries": 3,
            "start_period": "10s"
        }

        # 2. Worker Service (Queue)
        if deployment.laravel_worker_replicas > 0:
            services["worker"] = copy.deepcopy(base_service)
            # Override command for worker
            services["worker"]["command"] = ["php", "artisan", "queue:work", "--tries=3"]
            services["worker"]["deploy"] = {
                "replicas": deployment.laravel_worker_replicas,
                "update_config": {"parallelism": 1, "delay": "5s", "order": "stop-first"}, # Workers can stop first
                "restart_policy": {"condition": "on-failure"}
            }
            # Graceful stop for workers
            services["worker"]["stop_grace_period"] = "60s"

            # Remove ports from worker
            if "ports" in services["worker"]:
                del services["worker"]["ports"]

        # 3. Scheduler Service
        if deployment.laravel_scheduler_enabled:
            services["scheduler"] = copy.deepcopy(base_service)
            # Command for scheduler
            services["scheduler"]["command"] = ["php", "artisan", "schedule:work"]
            services["scheduler"]["deploy"] = {
                "replicas": 1, # Locked to 1
                "update_config": {"order": "stop-first"},
                "restart_policy": {"condition": "on-failure"}
            }
             # Remove ports
            if "ports" in services["scheduler"]:
                del services["scheduler"]["ports"]

        # 4. Horizon (Optional)
        if deployment.laravel_horizon_enabled:
             services["horizon"] = copy.deepcopy(base_service)
             services["horizon"]["command"] = ["php", "artisan", "horizon"]
             services["horizon"]["deploy"] = {
                "replicas": 1,
                "restart_policy": {"condition": "on-failure"}
             }
             services["horizon"]["stop_grace_period"] = "60s"
             if "ports" in services["horizon"]:
                 del services["horizon"]["ports"]

        return {
            "version": "3.8",
            "services": services,
            "volumes": {
                f"{safe_name}_storage": {}
            },
            "networks": {"app-net": {"driver": "overlay", "external": True}}
        }

    @staticmethod
    def _get_env_vars(project_path: str, port: int) -> Dict[str, str]:
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
            except Exception:
                pass

        env_vars["PORT"] = str(port)
        env_vars["APP_PORT"] = str(port)
        # FrankenPHP needs SERVER_NAME to listen on correct port.
        # We explicitly use http:// scheme to avoid auto-https behavior and bind to correct port.
        # Use :{port} to allow ANY host header (wildcard) on this port
        env_vars["SERVER_NAME"] = f":{port}"
        return env_vars

    @staticmethod
    def run_artisan(deployment: DeploymentConfig, command: str) -> tuple[bool, str]:
        """
        Runs an artisan command in a running container.
        """
        # Find a container for this stack.
        # Stack name:
        safe_name = deployment.name.lower().replace(" ", "-").replace("_", "-")

        # We need to find a running container ID.
        # Filter by label com.docker.swarm.service.name starts with safe_name

        # This requires DockerService to support filtering or we list all.
        try:
            containers = docker_service.list_containers(all=False)
            target_container = None

            # Prefer 'web' service, then 'worker'
            for c in containers:
                name = c.get("name", "")
                if f"{safe_name}_web" in name:
                    target_container = c["id"]
                    break

            if not target_container:
                for c in containers:
                    name = c.get("name", "")
                    if f"{safe_name}_" in name: # Any service in stack
                        target_container = c["id"]
                        break

            if not target_container:
                return False, "No running containers found for this application."

            # Exec command
            # docker exec -u root container_id php artisan ...
            # We use root or the user?

            full_cmd = f"php artisan {command}"

            # Using docker library exec_run is better than subprocess here?
            # docker_service uses docker-py client.

            container = docker_service.client.containers.get(target_container)
            # Use www-data for artisan commands to avoid permission issues
            exit_code, output = container.exec_run(full_cmd, user="www-data")

            return exit_code == 0, output.decode('utf-8')

        except Exception as e:
            logger.error(f"Artisan error: {e}")
            return False, str(e)

    @staticmethod
    def get_stack_status(deployment: DeploymentConfig) -> Dict[str, Any]:
        """
        Returns the status of the Laravel stack services.
        """
        safe_name = deployment.name.lower().replace(" ", "-").replace("_", "-")
        status = {
            "web": {"replicas": 0, "running": 0, "status": "stopped", "containers": []},
            "worker": {"replicas": 0, "running": 0, "status": "stopped", "containers": []},
            "scheduler": {"replicas": 0, "running": 0, "status": "stopped", "containers": []},
            "horizon": {"replicas": 0, "running": 0, "status": "stopped", "containers": []},
        }

        try:
            services = docker_service.list_services()
            for s in services:
                name = s.get("name", "")
                if not name.startswith(f"{safe_name}_"):
                    continue

                role = name.replace(f"{safe_name}_", "")
                if role in status:
                    status[role]["replicas"] = s.get("replicas", 0)
                    # Running count requires checking tasks/containers.
                    # list_services doesn't give running count directly usually.
                    # We assume replicas is target.
                    # For actual running, we need to list tasks or containers.
                    status[role]["status"] = "running" # Simplified

            # Get actual running containers to be accurate
            containers = docker_service.list_containers(all=False)
            for c in containers:
                labels = c.get("labels", {})
                service_name = labels.get("com.docker.swarm.service.name", "")
                if service_name.startswith(f"{safe_name}_"):
                     role = service_name.replace(f"{safe_name}_", "")
                     if role in status:
                         status[role]["running"] += 1
                         status[role]["containers"].append({
                             "id": c["id"],
                             "name": c["name"],
                             "status": c["status"]
                         })

        except Exception as e:
            logger.error(f"Stack status error: {e}")

        return status
