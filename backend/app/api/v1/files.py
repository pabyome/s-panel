from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
from app.api.deps import CurrentAdmin
from app.services.file_manager import FileManager

router = APIRouter()

class FileItem(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int
    modified: float
    permissions: str
    owner: str
    group: str

class PathRequest(BaseModel):
    path: str

class FileContent(BaseModel):
    path: str
    content: str

@router.get("/list", response_model=List[FileItem])
def list_files(current_user: CurrentAdmin, path: str = Query(..., min_length=1)):
    try:
        return FileManager.list_directory(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content")
def get_file_content(current_user: CurrentAdmin, path: str = Query(..., min_length=1)):
    try:
        content = FileManager.read_file(path)
        return {"content": content}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content")
def save_file_content(current_user: CurrentAdmin, data: FileContent):
    try:
        FileManager.write_file(data.path, data.content)
        return {"message": "File saved successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
def upload_file(
    current_user: CurrentAdmin,
    path: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        FileManager.save_upload(path, file.file, file.filename)
        return {"message": "File uploaded successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/directory")
def create_directory(current_user: CurrentAdmin, data: PathRequest):
    try:
        FileManager.create_directory(data.path)
        return {"message": "Directory created successfully"}
    except FileExistsError:
        raise HTTPException(status_code=400, detail="Directory already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete")
def delete_item(current_user: CurrentAdmin, data: PathRequest):
    try:
        FileManager.delete_item(data.path)
        return {"message": "Item deleted successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
