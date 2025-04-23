from pydantic import BaseModel, EmailStr

class Users(BaseModel):
    username: str
    password: str
    email: EmailStr 

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginUserDetails(BaseModel):
    username : str
    password : str

class currentUser(BaseModel):
    username : str
    email : str