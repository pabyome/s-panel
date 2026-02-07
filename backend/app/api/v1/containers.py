from fastapi import APIRouter, HTTPException, Depends
from typing import List, Any
from app.api.deps import CurrentUser
from app.services.docker_service import docker_service
from app.schemas.docker import ContainerInfo, LogResponse, ContainerCreate

router = APIRouter()

@router.post("/run", response_model=ContainerInfo)
def run_container(
    container_in: ContainerCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Run a new container.
    """
    try:
        container = docker_service.run_container(container_in)
        return container
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ContainerInfo])
def list_containers(
    current_user: CurrentUser,
) -> Any:
    """
    List all containers.
    """
    try:
        containers = docker_service.list_containers()
        return containers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{container_id}", response_model=ContainerInfo)
def get_container(
    container_id: str,
    current_user: CurrentUser,
) -> Any:
    """
    Get container by ID.
    """
    try:
        container = docker_service.get_container(container_id)
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        return container
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{container_id}/{action}", response_model=Any)
def perform_action(
    container_id: str,
    action: str,
    current_user: CurrentUser,
) -> Any:
    """
    Perform action on container (start, stop, restart, pause, unpause, remove).
    """
    valid_actions = ["start", "stop", "restart", "pause", "unpause", "remove"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of {valid_actions}")

    try:
        container = docker_service.perform_action(container_id, action)

        if action == "remove":
             return {"message": "Container removed"}

        if not container:
             raise HTTPException(status_code=404, detail="Container not found")

        return container
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{container_id}/logs", response_model=LogResponse)
def get_logs(
    container_id: str,
    current_user: CurrentUser,
    tail: int = 200,
) -> Any:
    """
    Get container logs.
    """
    try:
        logs = docker_service.get_logs(container_id, tail=tail)
        return LogResponse(logs=logs)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
