from fastapi import APIRouter

router = APIRouter(
    prefix="/api/album",
    tags=["album"]
)