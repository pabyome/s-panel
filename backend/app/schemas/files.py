from sqlmodel import SQLModel
from typing import List, Optional

class FileItem(SQLModel):
    name: str
    is_dir: bool
    path: str
    size: int
    modified: str
    permissions: str

class FileListResponse(SQLModel):
    items: List[FileItem]
    current_path: str
    parent_path: str

class FileContentResponse(SQLModel):
    content: str
    path: str

class SaveFileRequest(SQLModel):
    path: str
    content: str

class CreateItemRequest(SQLModel):
    path: str
    is_dir: bool
