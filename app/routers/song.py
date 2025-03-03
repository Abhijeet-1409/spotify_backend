from fastapi import APIRouter

router = APIRouter(
    prefix="/api/song",
    tags=["song"]
)