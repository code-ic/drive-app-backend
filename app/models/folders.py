from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId


class Folder(BaseModel):
    _id: str
    name: str
    owner: str
    parent_folder_id: Optional[str] = None
    shared: Optional[List[str]] = None 

class File:
    id: str
    name: str

class UserDrive(BaseModel):
    base_folder: Folder
    sub_folders: list[Folder]
    # files: list[File]
    folder_owner_username: str

    class Config:
        json_encoders = {
            ObjectId: str  # Automatically converts ObjectId to string
        }