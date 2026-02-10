"""search endpoints"""

from api.params import SearchParams
from dependencies import get_session
from fastapi import APIRouter, Depends
from models import Person, Title
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/titles")
async def search_titles(
    params: SearchParams = Depends(),
    session: AsyncSession = Depends(get_session),
) -> list[Title]:
    """search titles"""
    like = f"%{params.q}%"
    stmt = select(Title).where(
        or_(
            Title.primary_title.ilike(like),  # type: ignore
            Title.original_title.ilike(like),  # type: ignore
        )
    )
    if params.title_type:
        stmt = stmt.where(Title.title_type == params.title_type)
    if params.year_from and Title.start_year:
        stmt = stmt.where(Title.start_year >= params.year_from)
    stmt = stmt.limit(params.size).offset((params.page - 1) * params.size)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/people")
async def search_people(
    params: SearchParams = Depends(),
    session: AsyncSession = Depends(get_session),
) -> list[Person]:
    """search people"""
    like = f"%{params.q}%"
    stmt = select(Person).where(Person.primary_name.ilike(like))  # type: ignore
    stmt = stmt.limit(params.size).offset((params.page - 1) * params.size)
    result = await session.execute(stmt)
    return result.scalars().all()
