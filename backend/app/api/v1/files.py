from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel
from app.services.file_manager import FileManager
from app.api.deps import CurrentUser

router = APIRouter()

class FolderCreate(BaseModel):
    path: str

class FileContent(BaseModel):
    path: str
    content: str

@router.get("/list")
def list_directory(
    current_user: CurrentUser,
    path: str = Query(default="/")
):
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
def read_file(
    current_user: CurrentUser,
    path: str = Query(...)
):
    try:
        content = FileManager.read_file(path)
        return {"content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except IsADirectoryError:
        raise HTTPException(status_code=400, detail="Path is a directory")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/folder")
def create_folder(
    data: FolderCreate,
    current_user: CurrentUser
):
    try:
        FileManager.create_directory(data.path)
        return {"message": "Folder created successfully"}
    except FileExistsError:
        raise HTTPException(status_code=409, detail="Path already exists")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content")
def save_file(
    data: FileContent,
    current_user: CurrentUser
):
    try:
        FileManager.save_file(data.path, data.content)
        return {"message": "File saved successfully"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/")
def delete_item(
    current_user: CurrentUser,
    path: str = Query(...)
):
    try:
        FileManager.delete_item(path)
        return {"message": "Item deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Path not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
