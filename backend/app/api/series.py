"""series endpoints"""

from api.params import ListSeriesEpisodesParams
from dependencies import get_session
from fastapi import APIRouter, Depends, HTTPException
from models import Episode, Title
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/api", tags=["series"])


@router.get("/series/{tconst}/episodes")
async def list_series_episodes(
    tconst: str,
    params: ListSeriesEpisodesParams = Depends(),
    session: AsyncSession = Depends(get_session),
) -> list[Episode]:
    """episodes in series"""
    parent_result = await session.execute(select(Title).where(Title.tconst == tconst))
    parent = parent_result.scalar_one_or_none()
    if parent is None:
        raise HTTPException(status_code=404, detail="series not found")

    stmt = (
        select(Episode)
        .options(selectinload(Episode.parent))
        .where(Episode.parent_tconst == tconst)
        .order_by(Episode.season_number, Episode.episode_number)
    )
    if params.season:
        stmt = stmt.where(Episode.season_number == params.season)

    stmt = stmt.limit(params.size).offset((params.page - 1) * params.size)
    result = await session.execute(stmt)
    return result.scalars().all()
