import bcrypt
bcrypt.__about__ = bcrypt
import jwt
from typing import Union
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from fastapi import Header, HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
default_timedelta = timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
hash_saltKey = settings.SECRET_KEY
hash_algorithm = settings.ALGORITHM

def get_hashed_password(plain_password):
    return pwd_context.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data : dict, expires_delta : timedelta | None = None):
    to_encode = data.copy()
    if not expires_delta: expires_delta = default_timedelta
    timeToExpire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": timeToExpire})
    encoded_jwt = jwt.encode(to_encode, hash_saltKey, algorithm=hash_algorithm)
    return encoded_jwt

def decode_access_token(token : str):
    payload = jwt.decode(token, hash_saltKey, algorithms=hash_algorithm)
    return payload

