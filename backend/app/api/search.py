"""search endpoints"""

from dependencies import get_session
from fastapi import APIRouter, Depends, Query
from models import Person, Title
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/titles")
async def search_titles(
    q: str = Query(min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[Title]:
    """search titles"""
    like = f"%{q}%"
    stmt = select(Title).where(
        or_(
            Title.primary_title.ilike(like),  # type: ignore
            Title.original_title.ilike(like),  # type: ignore
        )
    )
    stmt = stmt.limit(size).offset((page - 1) * size)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/people")
async def search_people(
    q: str = Query(min_length=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[Person]:
    """search people"""
    like = f"%{q}%"
    stmt = select(Person).where(Person.primary_name.ilike(like))  # type: ignore
    stmt = stmt.limit(size).offset((page - 1) * size)
    result = await session.execute(stmt)
    return result.scalars().all()
