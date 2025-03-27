from typing import Annotated
from functools import lru_cache
from app.core.config import Settings
from app.db.connection import DatabaseConnection
from fastapi import Depends


@lru_cache
def get_settings() -> Settings:
    return Settings()

def get_database_connection(settings: Annotated[Settings, Depends(get_settings)]) -> DatabaseConnection:
    return DatabaseConnection(settings=settings)

