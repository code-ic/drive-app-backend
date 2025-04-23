from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "sample_mflix"
    SECRET_KEY:str = "dummyhash"
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:str = "30"

    class Config:
        env_file = ".env"

settings = Settings()
