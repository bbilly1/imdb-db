"""title endpoints"""

from typing import Optional

from dependencies import get_session
from fastapi import APIRouter, Depends, HTTPException, Query
from models import Title, TitlePrincipal, TitleRating
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/api", tags=["titles"])


@router.get("/titles/{tconst}")
async def get_title(
    tconst: str,
    session: AsyncSession = Depends(get_session),
) -> Title:
    """get single title"""
    result = await session.execute(select(Title).options(selectinload(Title.rating)).where(Title.tconst == tconst))
    title = result.scalar_one_or_none()
    if title is None:
        raise HTTPException(status_code=404, detail="title not found")
    return title


@router.get("/titles")
async def list_titles(
    genre: Optional[str] = Query(default=None),
    year_from: Optional[int] = Query(default=None, ge=1800),
    min_rating: Optional[float] = Query(default=None, ge=0.0, le=10.0),
    title_type: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[Title]:
    """get list of titles"""
    stmt = select(Title).options(selectinload(Title.rating))

    if genre:
        stmt = stmt.where(Title.genres.any(genre))  # type: ignore  # pylint: disable=no-member
    if year_from and Title.start_year:
        stmt = stmt.where(Title.start_year >= year_from)
    if title_type:
        stmt = stmt.where(Title.title_type == title_type)
    if min_rating is not None:
        stmt = stmt.join(TitleRating, TitleRating.tconst == Title.tconst).where(
            TitleRating.average_rating >= min_rating
        )

    stmt = stmt.limit(size).offset((page - 1) * size)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/titles/{tconst}/principals")
async def list_title_principals(
    tconst: str,
    category: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[TitlePrincipal]:
    """get list title principal"""
    stmt = select(TitlePrincipal).where(TitlePrincipal.tconst == tconst)
    if category:
        stmt = stmt.where(TitlePrincipal.category == category)
    stmt = stmt.order_by(TitlePrincipal.ordering)

    stmt = stmt.limit(size).offset((page - 1) * size)
    result = await session.execute(stmt)
    return result.scalars().all()
