from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import Dict, List, Union
from pydantic import BaseModel
from app.services.file_manager import FileManager
from app.api.deps import CurrentUser

router = APIRouter()

class CreateItemRequest(BaseModel):
    path: str
    is_directory: bool

class WriteFileRequest(BaseModel):
    path: str
    content: str

@router.get("/list")
async def list_files(current_user: CurrentUser, path: str = Query(default="/")):
    try:
        return FileManager.list_directory(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Path not found")
    except NotADirectoryError:
        raise HTTPException(status_code=400, detail="Path is not a directory")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content")
async def get_file_content(current_user: CurrentUser, path: str = Query(...)):
    try:
        return {"content": FileManager.read_file(path)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except IsADirectoryError:
        raise HTTPException(status_code=400, detail="Path is a directory")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content")
async def save_file_content(request: WriteFileRequest, current_user: CurrentUser):
    try:
        FileManager.write_file(request.path, request.content)
        return {"message": "File saved successfully"}
    except FileNotFoundError:
         raise HTTPException(status_code=404, detail="Directory not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_item(request: CreateItemRequest, current_user: CurrentUser):
    try:
        FileManager.create_item(request.path, request.is_directory)
        return {"message": "Item created successfully"}
    except FileExistsError:
        raise HTTPException(status_code=409, detail="Item already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/")
async def delete_item(current_user: CurrentUser, path: str = Query(...)):
    try:
        FileManager.delete_item(path)
        return {"message": "Item deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Path not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
