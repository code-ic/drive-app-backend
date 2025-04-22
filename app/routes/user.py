
from app.db.mongo import client, db
from app.models.user import Users, LoginUserDetails
from fastapi import APIRouter
from fastapi import HTTPException
from app.services.auth_service import get_hashed_password, verify_password

router = APIRouter()

@router.get("/users", response_model=list[Users])
async def get_users():
    try: 
        users_cursor = db['users'].find()
        users = []
        async for user in users_cursor:
            user.pop("_id", None)
            users.append(user)

        return users

    except Exception as e:
        print("Log Exception : ", e)
        raise HTTPException(status_code=500, detail="Unable to Fetch Users") 
    
@router.post("/user/register")
async def add_user(user_details : Users):
    try :
        user_details.password = get_hashed_password(user_details.password) # hash the password before writing to DB
        new_user = dict(user_details)
        resultID = await db["users"].insert_one(new_user)
        print("Result ID : ", resultID)
        return {"status" : 200, "message" : f"User {new_user["username"]} added successfully"}
    except Exception as e:
        print("Logging Exception : ", e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/user/login")
async def add_user(loginDetails : LoginUserDetails):
    try :
        userRecords = await db["users"].find_one({"username" : loginDetails.username})
        if not userRecords or not verify_password(loginDetails.password, userRecords["password"]):
            raise HTTPException(status_code=401, detail= f"Invalid login details for {loginDetails.username}")
        return {"status" : 200, "message" : f"User {loginDetails.username} logged in successfully"}
    except Exception as e:
        print("Logging Exception : ", e)
        raise HTTPException(status_code=500, detail=str(e))

