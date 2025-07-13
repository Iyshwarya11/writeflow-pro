from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str = Field(..., alias="MONGODB_URL")
    database_name: str = Field(..., alias="DATABASE_NAME")
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field(..., alias="ALGORITHM")
    access_token_expire_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    groq_api_key: Optional[str] = Field(None, alias="GROQ_API_KEY")
    groq_model_name: Optional[str] = Field(None, alias="GROQ_MODEL_NAME")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
