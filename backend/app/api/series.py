"""series endpoints"""

from typing import Optional

from dependencies import get_session
from fastapi import APIRouter, Depends, HTTPException, Query
from models import Episode, Title
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/api", tags=["series"])


@router.get("/series/{tconst}/episodes")
async def list_series_episodes(
    tconst: str,
    season: Optional[int] = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=500),
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
    if season:
        stmt = stmt.where(Episode.season_number == season)

    stmt = stmt.limit(size).offset((page - 1) * size)
    result = await session.execute(stmt)
    return result.scalars().all()
