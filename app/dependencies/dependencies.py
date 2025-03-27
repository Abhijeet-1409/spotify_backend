from typing import Annotated

from functools import lru_cache

from fastapi import Depends

from app.core.config import Settings
from app.db.connection import DatabaseConnection
from app.services.auth import AuthService


@lru_cache
def get_settings() -> Settings:
    return Settings()

def get_database_connection(settings: Annotated[Settings, Depends(get_settings)]) -> DatabaseConnection:
    return DatabaseConnection(settings=settings)

def get_auth_service(db_instance: Annotated[DatabaseConnection, Depends(get_database_connection)]) -> AuthService:
    return AuthService(db_instance=db_instance)
