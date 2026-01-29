from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from pydantic import BaseModel
from app.api.deps import CurrentUser
from app.services.file_manager import FileManager

router = APIRouter()

class FileItem(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int
    mtime: float

class FileContent(BaseModel):
    content: str

class CreateItem(BaseModel):
    path: str
    is_dir: bool = False

class DeleteItem(BaseModel):
    path: str

class UpdateItem(BaseModel):
    path: str
    content: str

@router.get("/list", response_model=List[FileItem])
def list_files(current_user: CurrentUser, path: str = Query("/", description="Path to list")):
    try:
        # If path is empty, default to /
        if not path:
            path = "/"
        return FileManager.list_directory(path)
    except ValueError as e:
        if "Access denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        if "Permission denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content", response_model=FileContent)
def get_file_content(current_user: CurrentUser, path: str = Query(..., description="Path to file")):
    try:
        content = FileManager.read_file(path)
        return FileContent(content=content)
    except ValueError as e:
        if "Access denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        if "Permission denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        if "File too large" in str(e):
            raise HTTPException(status_code=413, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
def create_item(item: CreateItem, current_user: CurrentUser):
    try:
        FileManager.create_item(item.path, item.is_dir)
        return {"status": "created", "path": item.path}
    except ValueError as e:
        if "Access denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        if "Permission denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete")
def delete_item(item: DeleteItem, current_user: CurrentUser):
    try:
        FileManager.delete_item(item.path)
        return {"status": "deleted", "path": item.path}
    except ValueError as e:
        if "Access denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        if "Permission denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
def save_file(item: UpdateItem, current_user: CurrentUser):
    try:
        FileManager.write_file(item.path, item.content)
        return {"status": "saved", "path": item.path}
    except ValueError as e:
        if "Access denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        if "Permission denied" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
