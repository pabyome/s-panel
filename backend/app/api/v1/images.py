from fastapi import APIRouter, HTTPException, Depends
from typing import List, Any
from app.api.deps import CurrentUser
from app.services.docker_service import docker_service
from app.schemas.docker import ImageInfo

router = APIRouter()

@router.get("/", response_model=List[ImageInfo])
def list_images(
    current_user: CurrentUser,
) -> Any:
    """
    List all images.
    """
    try:
        images = docker_service.list_images()
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
