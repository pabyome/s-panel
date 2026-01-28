from fastapi import APIRouter, Query, Body, HTTPException
from app.api.deps import CurrentUser
from app.services.file_manager import FileManager
from app.schemas.files import FileListResponse, FileContentResponse, SaveFileRequest, CreateItemRequest

router = APIRouter()

@router.get("/list", response_model=FileListResponse)
def list_files(
    path: str = Query(default="/", description="Absolute path to list"),
    current_user: CurrentUser = None
):
    return FileManager.list_directory(path)

@router.get("/content", response_model=FileContentResponse)
def get_content(
    path: str = Query(..., description="Absolute path to file"),
    current_user: CurrentUser = None
):
    content = FileManager.read_file(path)
    return FileContentResponse(content=content, path=path)

@router.post("/content")
def save_content(
    request: SaveFileRequest,
    current_user: CurrentUser = None
):
    FileManager.save_file(request.path, request.content)
    return {"message": "File saved successfully"}

@router.post("/create")
def create_item(
    request: CreateItemRequest,
    current_user: CurrentUser = None
):
    FileManager.create_item(request.path, request.is_dir)
    return {"message": "Item created successfully"}

@router.delete("/delete")
def delete_item(
    path: str = Query(..., description="Absolute path to delete"),
    current_user: CurrentUser = None
):
    FileManager.delete_item(path)
    return {"message": "Item deleted successfully"}
