
from app.db.mongo import client, db
from app.models.user import Users, LoginUserDetails
from fastapi import APIRouter
from fastapi import HTTPException,status
from app.services.auth_service import get_hashed_password, verify_password, create_access_token, decode_access_token

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
async def authenticate_user(loginDetails : LoginUserDetails):
    try :
        userRecords = await db["users"].find_one({"username" : loginDetails.username})
        if not userRecords or not verify_password(loginDetails.password, userRecords["password"]):
            raise HTTPException(status_code=401, detail= f"Invalid login details for {loginDetails.username}")
        
        token_body = {"username" : loginDetails.username}
        access_token = create_access_token(token_body)
        return {"status" : 200, "access_token" : access_token, "token_type": "bearer"}
    except Exception as e:
        print("Logging Exception : ", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/me')
async def get_current_user(accessToken):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials") 

    try:
        payload = decode_access_token(accessToken)
        username = payload.get("username")
        if not username: 
            raise credentials_exception 
        userRecords = await db["users"].find_one({"username" : username})
        if not userRecords:
            raise credentials_exception

        return {"username" : userRecords["username"], "email" : userRecords["email"]}

    except Exception as e:
        print("Logging Exception : ", e)
        raise HTTPException(status_code=500, detail=str(e))

    
