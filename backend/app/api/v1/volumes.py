from fastapi import APIRouter, HTTPException, Depends
from typing import List, Any
from app.api.deps import CurrentUser
from app.services.docker_service import docker_service
from app.schemas.docker import VolumeInfo

router = APIRouter()

@router.get("/", response_model=List[VolumeInfo])
def list_volumes(
    current_user: CurrentUser,
) -> Any:
    """
    List all volumes.
    """
    try:
        volumes = docker_service.list_volumes()
        return volumes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
