from fastapi import APIRouter, HTTPException, Depends
from typing import List, Any, Dict
from app.api.deps import CurrentUser
from app.services.docker_service import docker_service

router = APIRouter()

@router.get("/info")
def get_swarm_info(
    current_user: CurrentUser,
) -> Any:
    """
    Get Docker Swarm status and info.
    """
    return docker_service.get_swarm_info()

@router.post("/init")
def init_swarm(
    current_user: CurrentUser,
    advertise_addr: str = "eth0:2377",
) -> Any:
    """
    Initialize Docker Swarm.
    """
    try:
        node_id = docker_service.init_swarm(advertise_addr)
        return {"message": "Swarm initialized", "node_id": node_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leave")
def leave_swarm(
    current_user: CurrentUser,
    force: bool = False,
) -> Any:
    """
    Leave Docker Swarm.
    """
    try:
        success = docker_service.leave_swarm(force)
        return {"message": "Left swarm", "success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nodes")
def list_nodes(
    current_user: CurrentUser,
) -> Any:
    """
    List Swarm Nodes (Manager only).
    """
    try:
        return docker_service.list_nodes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services")
def list_services(
    current_user: CurrentUser,
) -> Any:
    """
    List Swarm Services.
    """
    try:
        return docker_service.list_services()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/services/{service_id}/scale")
def scale_service(
    service_id: str,
    replicas: int,
    current_user: CurrentUser,
) -> Any:
    """
    Scale a Swarm service.
    """
    try:
        success = docker_service.scale_service(service_id, replicas)
        return {"success": success}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/services/{service_id}")
def remove_service(
    service_id: str,
    current_user: CurrentUser,
) -> Any:
    """
    Remove a Swarm service.
    """
    try:
        success = docker_service.remove_service(service_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/services/{service_id}/restart")
def restart_service(
    service_id: str,
    current_user: CurrentUser,
) -> Any:
    """
    Restart a Swarm service (force update).
    """
    try:
        success = docker_service.restart_service(service_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_stats(
    current_user: CurrentUser,
) -> Any:
    """
    Get aggregated system stats for overview.
    """
    return docker_service.get_system_stats()
