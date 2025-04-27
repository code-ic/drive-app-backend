from app.db.mongo import client, db
from app.models.user import Users, LoginUserDetails
from fastapi import APIRouter, Depends
from fastapi import HTTPException,status
from app.routes.user import get_current_user
from app.models.folders import UserDrive, Folder
from bson import ObjectId

router = APIRouter()

# @router.get("/me/folders", response_model= UserDrive)
@router.get("/me/folders")
async def get_folder(parent_folder_id : str | None = None, current_user: dict = Depends(get_current_user)):

    try: 
        username = current_user['username']
        print("Log 1", username, parent_folder_id)
        if not parent_folder_id:
            parent_folder_cursor = await db["folders"].find_one({"parent_folder_id" : None}, {"_id" : 1, "name" : 1})
            parent_folder_id = parent_folder_cursor["_id"]
            print(parent_folder_id)
        else: 
            parent_folder_id = ObjectId(parent_folder_id)

        base_folder = await db["folders"].find_one({"_id" : parent_folder_id}, {"_id" : 1, "name" : 1})
        print(base_folder)
        base_folder["_id"] = str(base_folder["_id"])

        sub_folders = []
        sub_folder_cursor = db["folders"].find({"parent_folder_id" : parent_folder_id}, {"_id" : 1, "name" : 1})
        print(sub_folder_cursor)
        async for folder in sub_folder_cursor:
            folder["_id"] = str(folder["_id"])
            sub_folders.append(folder)

        print(sub_folders)
        result = {  "base_folder" : base_folder, 
                    "sub_folders" : sub_folders,
                    "folder_owner_username" : username
                    }

        return {"status" : 200, "result" : result }

    except Exception as e:
        print("Logging Exception : ", e)
        raise HTTPException(status_code=500, detail=str(e))