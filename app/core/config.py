from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "sample_mflix"


    class Config:
        env_file = ".env"

settings = Settings()
