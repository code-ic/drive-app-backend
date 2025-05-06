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
        user_oid = await db["users"].find_one({"username" : username},{"_id" : 1})
        # print("Inputs check : ", username, parent_folder_id, user_oid)

        if not parent_folder_id:
            parent_folder_cursor = await db["folders"].find_one({"parent_folder_id" : None, "owner" : user_oid["_id"]}, {"_id" : 1, "name" : 1})
            parent_folder_id = parent_folder_cursor["_id"]
            # print("Root Folder Present", parent_folder_id)
        else: 
            parent_folder_id = ObjectId(parent_folder_id)

        base_folder = await db["folders"].find_one({"_id" : parent_folder_id}, {"_id" : 1, "name" : 1})
        # print(base_folder)
        base_folder["_id"] = str(base_folder["_id"])

        sub_folders = []
        sub_folder_cursor = db["folders"].find({"parent_folder_id" : parent_folder_id}, {"_id" : 1, "name" : 1})
        # print(sub_folder_cursor)
        async for folder in sub_folder_cursor:
            folder["_id"] = str(folder["_id"])
            sub_folders.append(folder)

        # print(sub_folders)
        result = {  "base_folder" : base_folder, 
                    "sub_folders" : sub_folders,
                    "folder_owner_username" : username
                    }

        return {"status" : 200, "result" : result }

    except Exception as e:
        print("Logging Exception : ", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/me/folders")
async def create_folder(parent_folder_id : str, new_folder_name : str, current_user: dict = Depends(get_current_user)):
    try : 
        username = current_user['username']
        user_oid = await db["users"].find_one({"username" : username},{"_id" : 1})
        parent_folder_id = ObjectId(parent_folder_id)
        parent_folder = await db["folders"].find_one({"_id" : parent_folder_id, "owner" : user_oid["_id"]}, {"_id" : 1, "name" : 1})

        # print("Input checks : ", username, user_id, parent_folder_id, parent_folder)

        if parent_folder is None:
            raise HTTPException(status_code=401, detail= "Invalid root folder to create new folder in")


        base_folder = await db["folders"].find_one({"parent_folder_id" : parent_folder_id,
                                                    "name" : new_folder_name,
                                                    "owner" : user_oid["_id"]}, {"_id" : 1, "name" : 1})
        
        if base_folder:
            for i in range(1, 100):
                check_folder_name = new_folder_name + f" ({i})"
                base_folder = await db["folders"].find_one({"parent_folder_id" : parent_folder_id,
                                                    "name" : check_folder_name,
                                                    "owner" : user_oid["_id"]}, {"_id" : 1, "name" : 1})
               
                if not base_folder:
                    new_folder_name = check_folder_name
                    break
        
        if base_folder: raise HTTPException(status_code=401, detail= "Folder with the same name exists")
        # Check if a folder with the same name is present then create one with (1,2,3,4) whatever in front of the name

        new_folder = {
            "name" : new_folder_name,
            "owner" : user_oid["_id"],
            "parent_folder_id" : parent_folder_id,
            "shared" : []
        } 

        resultID = await db["folders"].insert_one(new_folder)

        if not resultID: 
            raise HTTPException(status_code=401, detail= "Failed to create a new folder.")

        return {"status" : 200, "result" : str(resultID)}

    except Exception as e:
        print("Logging Exception : ", e)
        raise HTTPException(status_code=500, detail=str(e))


    
@router.patch("/me/folders")
async def create_folder(folder_id : str, new_folder_name : str, current_user: dict = Depends(get_current_user)):
    try : 
        username = current_user['username']
        user_oid = await db["users"].find_one({"username" : username},{"_id" : 1})
        folder_id = ObjectId(folder_id)
        base_folder = await db["folders"].find_one({"_id" : folder_id, "owner" : user_oid["_id"]}, {"_id" : 1, "name" : 1, "parent_folder_id" : 1})
        base_folder_name = base_folder["name"]
        if base_folder_name == new_folder_name:
            return {"status" : 200, "result" : "New Folder name same as base folder name"}

        print(base_folder["name"], folder_id)

        if base_folder is None:
            raise HTTPException(status_code=401, detail= "No folder with the ID/Name exists")
        
        parent_folder_id = base_folder["parent_folder_id"]

        base_folder_new_name = await db["folders"].find_one({"parent_folder_id" : parent_folder_id,
                                                    "name" : new_folder_name,
                                                    "owner" : user_oid["_id"]}, {"_id" : 1, "name" : 1})

        if base_folder_new_name:
            for i in range(1, 100):
                check_folder_name = new_folder_name + f" ({i})"
                base_folder_new_name = await db["folders"].find_one({"parent_folder_id" : parent_folder_id,
                                                    "name" : check_folder_name,
                                                    "owner" : user_oid["_id"]}, {"_id" : 1, "name" : 1})
               
                if not base_folder_new_name:
                    new_folder_name = check_folder_name
                    break
        
        if base_folder_new_name: raise HTTPException(status_code=401, detail= "Folder with the same name exists")
        # Check if a folder with the same name is present then create one with (1,2,3,4) whatever in front of the name
        # print(base_folder_new_name) 
        resultID = await db["folders"].update_one(
            {"_id" : folder_id, "parent_folder_id" : parent_folder_id, "name" : base_folder_name},
            {"$set" : {"name" : new_folder_name}}
        )

        if not resultID: 
            raise HTTPException(status_code=401, detail= "Failed to create a new folder.")

        return {"status" : 200, "result" : str(resultID)}

    except Exception as e:
        print("Logging Exception : ", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me/folders") 
async def delete_folder(folder_id : str, current_user: dict = Depends(get_current_user)):
    try:
        username = current_user['username']
        user_oid = await db["users"].find_one({"username" : username},{"_id" : 1})
        folder_id = ObjectId(folder_id)
        base_folder = await db["folders"].find_one({"_id" : folder_id, "owner" : user_oid["_id"]}, {"_id" : 1, "parent_folder_id" : 1})

        folder_stack = [folder_id]
        iteration_stack = [folder_id]

        loop_limit = 100
        loop_init = 0
        while iteration_stack:
            loop_init += 1
            if loop_init > loop_limit: raise HTTPException(status_code=500, detail="Too Big of a folder to delete. Recursion depth reached post 100.")

            curr_folder_id = iteration_stack.pop()
            
            temp_folder = db["folders"].find({"parent_folder_id" : curr_folder_id, "owner" : user_oid["_id"]}, {"_id" : 1})           
            
            async for temp_sub_folder in temp_folder:
                iteration_stack.append(temp_sub_folder["_id"])
                folder_stack.append(temp_sub_folder["_id"])

        for _id in folder_stack:
            # print(_id)
            result = db["folders"].delete_one({"_id" : _id})

        return {"status" : 200, "result" : "Successfully deleted the folder and sub-folders"} 

    except Exception as e:
        print("Logging Exception : ", e)
        raise HTTPException(status_code=500, detail=str(e))

