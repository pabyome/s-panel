from fastapi import APIRouter, HTTPException, Depends
from typing import List, Any
from app.api.deps import CurrentUser
from app.services.docker_service import docker_service
from app.schemas.docker import NetworkInfo

router = APIRouter()

@router.get("/", response_model=List[NetworkInfo])
def list_networks(
    current_user: CurrentUser,
) -> Any:
    """
    List all networks.
    """
    try:
        networks = docker_service.list_networks()
        return networks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
