import docker
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DockerService:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.error(f"Error connecting to Docker: {e}")
            self.client = None

    def _check_client(self):
        if not self.client:
            try:
                self.client = docker.from_env()
            except Exception as e:
                logger.error(f"Failed to reconnect to Docker: {e}")
                raise RuntimeError("Docker daemon is not available.")

    def _format_container(self, container, service_ports_map: Dict[str, Dict] = None) -> Dict[str, Any]:
        """Formats container object into a dictionary."""
        # Handle image tags safely
        image_tag = "dangling"
        try:
            if container.image and hasattr(container.image, 'tags') and container.image.tags:
                image_tag = container.image.tags[0]
            elif container.image and hasattr(container.image, 'id'):
                image_tag = container.image.id[:12]
        except docker.errors.NotFound:
            # Image might have been deleted while container is still around
            image_tag = container.attrs.get('Config', {}).get('Image', 'unknown')[:12]
        except Exception:
             pass

        # Extract ports safely
        ports = {}
        network_settings = container.attrs.get('NetworkSettings', {})
        if network_settings and 'Ports' in network_settings:
            ports = network_settings['Ports']

        # Check if ports are empty and look for Swarm service ports
        if not ports and service_ports_map:
            labels = container.attrs.get('Config', {}).get('Labels', {})
            service_id = labels.get('com.docker.swarm.service.id')
            if service_id and service_id in service_ports_map:
                # Map structured service ports to container ports format
                # Service ports: [{'Protocol': 'tcp', 'TargetPort': 3086, 'PublishedPort': 3086, 'PublishMode': 'ingress'}]
                # Container ports expected format: {'80/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '80'}]}

                swarm_ports = service_ports_map[service_id]
                for p in swarm_ports:
                    proto = p.get('Protocol', 'tcp')
                    target = p.get('TargetPort')
                    published = p.get('PublishedPort')
                    if target and published:
                        key = f"{target}/{proto}"
                        ports[key] = [{'HostIp': '0.0.0.0', 'HostPort': str(published)}]

        return {
            "id": container.id,
            "short_id": container.short_id,
            "name": container.name,
            "image": image_tag,
            "status": container.status,
            "state": container.attrs.get('State', {}),
            "ports": ports,
            "created": container.attrs.get('Created'),
            "labels": container.attrs.get('Config', {}).get('Labels', {}),
        }

    def list_containers(self, all: bool = True) -> List[Dict[str, Any]]:
        self._check_client()
        try:
            containers = self.client.containers.list(all=all)

            # Fetch services to map ports for Swarm containers
            service_ports_map = {}
            try:
                # Only if we are a manager or can list services
                services = self.client.services.list()
                for s in services:
                    endpoint = s.attrs.get('Endpoint', {})
                    if 'Ports' in endpoint:
                        service_ports_map[s.id] = endpoint['Ports']
            except:
                pass # Ignore errors if not swarm manager or API fails

            # Fetch services to map ports for Swarm containers
            service_ports_map = {}
            try:
                # Only if we are a manager or can list services
                services = self.client.services.list()
                for s in services:
                    endpoint = s.attrs.get('Endpoint', {})
                    if 'Ports' in endpoint:
                        service_ports_map[s.id] = endpoint['Ports']
            except:
                pass # Ignore errors if not swarm manager or API fails

            return [self._format_container(c, service_ports_map) for c in containers]
        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            raise

    def get_container(self, container_id: str) -> Optional[Dict[str, Any]]:
        self._check_client()
        try:
            container = self.client.containers.get(container_id)

            # Fetch service info if needed for ports
            service_ports_map = {}
            try:
                labels = container.attrs.get('Config', {}).get('Labels', {})
                service_id = labels.get('com.docker.swarm.service.id')
                if service_id:
                    service = self.client.services.get(service_id)
                    endpoint = service.attrs.get('Endpoint', {})
                    if 'Ports' in endpoint:
                        service_ports_map[service_id] = endpoint['Ports']
            except:
                pass

            # Fetch service info if needed for ports
            service_ports_map = {}
            try:
                labels = container.attrs.get('Config', {}).get('Labels', {})
                service_id = labels.get('com.docker.swarm.service.id')
                if service_id:
                    service = self.client.services.get(service_id)
                    endpoint = service.attrs.get('Endpoint', {})
                    if 'Ports' in endpoint:
                        service_ports_map[service_id] = endpoint['Ports']
            except:
                pass

            return self._format_container(container, service_ports_map)
        except docker.errors.NotFound:
            return None
        except Exception as e:
            logger.error(f"Error getting container {container_id}: {e}")
            raise

    def perform_action(self, container_id: str, action: str) -> Optional[Dict[str, Any]]:
        self._check_client()
        try:
            container = self.client.containers.get(container_id)

            if action == "start":
                container.start()
            elif action == "stop":
                container.stop()
            elif action == "restart":
                container.restart()
            elif action == "pause":
                container.pause()
            elif action == "unpause":
                container.unpause()
            elif action == "remove":
                container.remove(force=True) # Force remove for convenience
                return None
            else:
                raise ValueError(f"Invalid action: {action}")

            # Allow some time for state change or reload
            container.reload()
            return self._format_container(container)
        except docker.errors.NotFound:
            return None
        except Exception as e:
            logger.error(f"Error performing {action} on {container_id}: {e}")
            raise

    def get_logs(self, container_id: str, tail: int = 200) -> str:
        self._check_client()
        try:
            container = self.client.containers.get(container_id)
            # logs returns bytes
            logs = container.logs(tail=tail, timestamps=True)
            return logs.decode('utf-8', errors='replace')
        except docker.errors.NotFound:
            raise ValueError(f"Container {container_id} not found")
        except Exception as e:
            logger.error(f"Error getting logs for {container_id}: {e}")
            raise

    def run_container(self, data: Any) -> Dict[str, Any]:
        self._check_client()

        # Prepare ports
        ports = {}
        for p in data.ports:
            key = f"{p.container_port}/{p.protocol}"
            ports[key] = p.host_port

        # Prepare volumes
        volumes = {}
        for v in data.volumes:
            volumes[v.host_path] = {'bind': v.container_path, 'mode': v.mode}

        # Restart policy
        restart_policy = {"Name": data.restart_policy}

        try:
            # Pull image if not exists
            try:
                self.client.images.get(data.image)
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling image {data.image}...")
                self.client.images.pull(data.image)

            container = self.client.containers.run(
                image=data.image,
                name=data.name,
                ports=ports,
                volumes=volumes,
                environment=data.env_vars,
                restart_policy=restart_policy,
                detach=True
            )
            return self._format_container(container)
        except Exception as e:
            logger.error(f"Error running container: {e}")
            raise

    # --- Swarm Methods ---

    def _resolve_ip(self, addr: str) -> str:
        try:
            # Handle empty address
            if not addr:
                return addr

            # Split address and port if present
            if ':' in addr:
                parts = addr.split(':')
                host = parts[0]
                port = parts[1]
            else:
                host = addr
                port = None

            # Get interfaces
            import psutil
            import socket
            interfaces = psutil.net_if_addrs()

            # check if host is an interface name
            if host in interfaces:
                for snic in interfaces[host]:
                    if snic.family == socket.AF_INET:
                        return f"{snic.address}:{port}" if port else snic.address

            return addr
        except Exception as e:
            logger.warning(f"Failed to resolve IP for {addr}: {e}")
            return addr

    def get_swarm_info(self) -> Dict[str, Any]:
        self._check_client()
        try:
            info = self.client.info()
            swarm_info = info.get('Swarm', {})
            return {
                "active": swarm_info.get('LocalNodeState') == 'active',
                "is_manager": swarm_info.get('ControlAvailable', False),
                "nodes": swarm_info.get('Nodes', 0),
                "managers": swarm_info.get('Managers', 0),
                "cluster_id": swarm_info.get('Cluster', {}).get('ID'),
            }
        except Exception as e:
            logger.error(f"Error getting swarm info: {e}")
            return {"active": False, "error": str(e)}

    def init_swarm(self, advertise_addr: str = "eth0:2377") -> str:
        self._check_client()
        try:
            # Resolve interface name to IP if needed
            resolved_addr = self._resolve_ip(advertise_addr)
            return self.client.swarm.init(advertise_addr=resolved_addr)
        except Exception as e:
            logger.error(f"Error initializing swarm: {e}")
            raise

    def leave_swarm(self, force: bool = False) -> bool:
        self._check_client()
        try:
            return self.client.swarm.leave(force=force)
        except Exception as e:
            logger.error(f"Error leaving swarm: {e}")
            raise

    def list_nodes(self) -> List[Dict[str, Any]]:
        self._check_client()
        try:
            nodes = self.client.nodes.list()
            return [{
                "id": n.id,
                "hostname": n.attrs.get('Description', {}).get('Hostname'),
                "role": n.attrs.get('Spec', {}).get('Role'),
                "availability": n.attrs.get('Spec', {}).get('Availability'),
                "status": n.attrs.get('Status', {}).get('State'),
                "address": n.attrs.get('Status', {}).get('Addr'),
            } for n in nodes]
        except docker.errors.APIError as e:
            # If not a manager or swarm not active
            logger.warning(f"Error listing nodes (might not be manager): {e}")
            return []
        except Exception as e:
            logger.error(f"Error listing nodes: {e}")
            raise

    def list_services(self) -> List[Dict[str, Any]]:
        self._check_client()
        try:
            services = self.client.services.list()
            return [{
                "id": s.id,
                "name": s.name,
                "image": s.attrs.get('Spec', {}).get('TaskTemplate', {}).get('ContainerSpec', {}).get('Image'),
                "mode": s.attrs.get('Spec', {}).get('Mode', {}),
                "replicas": s.attrs.get('Spec', {}).get('Mode', {}).get('Replicated', {}).get('Replicas'),
                "created": s.attrs.get('CreatedAt'),
                "updated": s.attrs.get('UpdatedAt'),
            } for s in services]
        except docker.errors.APIError as e:
             logger.warning(f"Error listing services (might not be manager): {e}")
             return []
        except Exception as e:
            logger.error(f"Error listing services: {e}")
            raise

    def scale_service(self, service_id: str, replicas: int) -> bool:
        self._check_client()
        try:
            service = self.client.services.get(service_id)
            mode = service.attrs.get('Spec', {}).get('Mode', {})
            if 'Replicated' not in mode:
                raise ValueError("Service is not in replicated mode")

            service.scale(replicas)
            return True
        except Exception as e:
            logger.error(f"Error scaling service {service_id}: {e}")
            raise

    def remove_service(self, service_id: str) -> bool:
        self._check_client()
        try:
            service = self.client.services.get(service_id)
            service.remove()
            return True
        except Exception as e:
            logger.error(f"Error removing service {service_id}: {e}")
            raise

    def restart_service(self, service_id: str) -> bool:
        """Force update the service to trigger a rolling restart."""
        self._check_client()
        try:
            service = self.client.services.get(service_id)
            # Force update by updating the ForceUpdate index
            service.force_update()
            return True
        except Exception as e:
            logger.error(f"Error restarting service {service_id}: {e}")
            raise

    # --- Resources Methods ---

    def list_images(self) -> List[Dict[str, Any]]:
        self._check_client()
        try:
            images = self.client.images.list()
            return [{
                "id": img.short_id,
                "tags": img.tags,
                "size": img.attrs.get('Size'),
                "created": img.attrs.get('Created'),
            } for img in images]
        except Exception as e:
            logger.error(f"Error listing images: {e}")
            raise

    def delete_image(self, image_id: str, force: bool = False) -> bool:
        self._check_client()
        try:
            self.client.images.remove(image_id, force=force)
            return True
        except docker.errors.ImageNotFound:
            raise ValueError(f"Image {image_id} not found")
        except Exception as e:
            logger.error(f"Error deleting image {image_id}: {e}")
            raise

    def prune_images(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        self._check_client()
        try:
            # filters default to dangling=true if None
            # To prune all unused images, filters should be {'dangling': False} ? No.
            # Docker SDK Prune: filters (dict) – Filters to process on the prune list.
            # Available filters: dangling (boolean) When set to true (or 1), prune only unused and untagged images. When set to false (or 0), all unused images are pruned.
            return self.client.images.prune(filters=filters)
        except Exception as e:
            logger.error(f"Error pruning images: {e}")
            raise

    def list_networks(self) -> List[Dict[str, Any]]:
        self._check_client()
        try:
            networks = self.client.networks.list()
            return [{
                "id": net.short_id,
                "name": net.name,
                "driver": net.attrs.get('Driver'),
                "scope": net.attrs.get('Scope'),
                "internal": net.attrs.get('Internal'),
                "attachable": net.attrs.get('Attachable'),
                "ingress": net.attrs.get('Ingress'),
                "ipam": net.attrs.get('IPAM'),
            } for net in networks]
        except Exception as e:
            logger.error(f"Error listing networks: {e}")
            raise

    def list_volumes(self) -> List[Dict[str, Any]]:
        self._check_client()
        try:
            volumes = self.client.volumes.list()
            return [{
                "name": vol.name,
                "driver": vol.attrs.get('Driver'),
                "mountpoint": vol.attrs.get('Mountpoint'),
                "created": vol.attrs.get('CreatedAt'),
                "labels": vol.attrs.get('Labels') or {},
            } for vol in volumes]
        except Exception as e:
            logger.error(f"Error listing volumes: {e}")
            raise

    # --- System Stats for Dashboard ---

    def get_system_stats(self) -> Dict[str, Any]:
        self._check_client()
        try:
            # This is a bit heavy, iterating all containers to sum up usage.
            # In a real heavy production env, this should be cached or streamed.
            # For this MVP, we will fetch basic info.
            # However, getting CPU % requires monitoring over time or using stats API which is slow.
            # We'll use docker.info() for system limits and maybe just count containers for now
            # or use a very quick sample if possible.

            # Docker SDK stats() is a stream by default. Getting a single snapshot takes time.
            # Let's return basics: container counts and system memory limit.
            # Real-time CPU/Mem per container is better handled by client-side polling of individual stats or a background worker.

            # But the user asked for "CPU usage 8.3%" style.
            # We can try to get psutil info for the whole system as a proxy if running on host,
            # but inside a container (if backend is containerized) it shows container stats.

            # Let's stick to what we can get reliably.
            import psutil

            vm = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=None) # Non-blocking

            return {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": vm.total,
                    "available": vm.available,
                    "used": vm.used,
                    "percent": vm.percent
                },
                "containers": {
                    "total": len(self.client.containers.list(all=True)),
                    "running": len(self.client.containers.list(all=False))
                }
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}

docker_service = DockerService()
