from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.stat import Stats
from app.services.stat import StatService
from app.dependencies.dependencies import (
    require_admin,
    get_stat_service
)


router = APIRouter(
    prefix="/api/stats",
    tags=["stats"],
    dependencies=[Depends(require_admin)]
)


@router.get("/")
async def get_stats(stat_service: Annotated[StatService, Depends(get_stat_service)]) -> Stats:

    stats: Stats = await stat_service.fetch_stats()

    return stats