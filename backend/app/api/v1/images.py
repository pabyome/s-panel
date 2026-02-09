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

@router.delete("/{image_id}")
def delete_image(
    image_id: str,
    current_user: CurrentUser,
    force: bool = False,
) -> Any:
    """
    Delete a Docker image properly by ID.
    """
    try:
        success = docker_service.delete_image(image_id, force=force)
        return {"success": success}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prune")
def prune_images(
    current_user: CurrentUser,
    all: bool = False,
) -> Any:
    """
    Prune unused images.
    If all=True, delete all unused images, not just dangling ones.
    """
    try:
        filters = None
        if all:
            filters = {"dangling": False}

        result = docker_service.prune_images(filters=filters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
