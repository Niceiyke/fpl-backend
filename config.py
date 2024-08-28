import asyncio
import os
from enum import Enum

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    class Config:
        env_file = ".env"

settings = Settings()


