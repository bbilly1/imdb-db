"""title endpoints"""

from api.params import CategoryParams, ListTitlesParams
from dependencies import get_session
from fastapi import APIRouter, Depends, HTTPException
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
    params: ListTitlesParams = Depends(),
    session: AsyncSession = Depends(get_session),
) -> list[Title]:
    """get list of titles"""
    stmt = select(Title).options(selectinload(Title.rating))

    if params.genre:
        stmt = stmt.where(Title.genres.any(params.genre))  # type: ignore  # pylint: disable=no-member
    if params.year_from and Title.start_year:
        stmt = stmt.where(Title.start_year >= params.year_from)
    if params.title_type:
        stmt = stmt.where(Title.title_type == params.title_type)
    if params.min_rating is not None:
        stmt = stmt.join(TitleRating, TitleRating.tconst == Title.tconst).where(
            TitleRating.average_rating >= params.min_rating
        )

    stmt = stmt.limit(params.size).offset((params.page - 1) * params.size)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/titles/{tconst}/principals")
async def list_title_principals(
    tconst: str,
    params: CategoryParams = Depends(),
    session: AsyncSession = Depends(get_session),
) -> list[TitlePrincipal]:
    """get list title principal"""
    stmt = select(TitlePrincipal).where(TitlePrincipal.tconst == tconst)
    if params.category:
        stmt = stmt.where(TitlePrincipal.category == params.category)
    stmt = stmt.order_by(TitlePrincipal.ordering)

    stmt = stmt.limit(params.size).offset((params.page - 1) * params.size)
    result = await session.execute(stmt)
    return result.scalars().all()
