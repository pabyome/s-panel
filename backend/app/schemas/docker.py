from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ContainerInfo(BaseModel):
    id: str
    short_id: str
    name: str
    image: str
    status: str
    state: Dict[str, Any]
    ports: Dict[str, Any]
    created: str

class ContainerAction(BaseModel):
    action: str

class LogResponse(BaseModel):
    logs: str

class ContainerList(BaseModel):
    containers: List[ContainerInfo]

class PortMapping(BaseModel):
    container_port: int
    host_port: int
    protocol: str = "tcp"

class VolumeMapping(BaseModel):
    host_path: str
    container_path: str
    mode: str = "rw"

class ContainerCreate(BaseModel):
    image: str
    name: Optional[str] = None
    ports: List[PortMapping] = []
    volumes: List[VolumeMapping] = []
    env_vars: Dict[str, str] = {}
    restart_policy: str = "unless-stopped"

class ImageInfo(BaseModel):
    id: str
    tags: Optional[List[str]] = []
    size: Optional[int] = None
    created: Optional[str] = None

class NetworkInfo(BaseModel):
    id: str
    name: str
    driver: Optional[str] = None
    scope: Optional[str] = None
    internal: Optional[bool] = None
    attachable: Optional[bool] = None
    ingress: Optional[bool] = None
    ipam: Optional[Dict[str, Any]] = None

class VolumeInfo(BaseModel):
    name: str
    driver: Optional[str] = None
    mountpoint: Optional[str] = None
    created: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
