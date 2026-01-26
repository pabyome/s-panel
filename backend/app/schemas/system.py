from sqlmodel import SQLModel
from typing import List

class FileItem(SQLModel):
    name: str
    is_dir: bool
    path: str

class PathListResponse(SQLModel):
    items: List[FileItem]
    current_path: str
    parent_path: str
