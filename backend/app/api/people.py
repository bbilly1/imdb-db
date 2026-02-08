"""people endpoints"""

from typing import Any, Optional

from dependencies import get_session
from fastapi import APIRouter, Depends, HTTPException, Query
from models import Person, Title, TitlePrincipal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api", tags=["people"])


@router.get("/people/{nconst}")
async def get_person(
    nconst: str,
    session: AsyncSession = Depends(get_session),
) -> Person:
    """single person"""
    result = await session.execute(select(Person).where(Person.nconst == nconst))
    person = result.scalar_one_or_none()
    if person is None:
        raise HTTPException(status_code=404, detail="person not found")
    return person


@router.get("/people/{nconst}/credits")
async def list_person_credits(
    nconst: str,
    category: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    """list of credits of person"""
    stmt = (
        select(TitlePrincipal, Title)
        .join(Title, Title.tconst == TitlePrincipal.tconst)
        .where(TitlePrincipal.nconst == nconst)
        .distinct(TitlePrincipal.tconst)
        .order_by(TitlePrincipal.tconst, Title.start_year.desc(), Title.primary_title)  # type: ignore
    )
    if category:
        stmt = stmt.where(TitlePrincipal.category == category)

    stmt = stmt.limit(size).offset((page - 1) * size)
    result = await session.execute(stmt)

    people_credits: list[dict[str, Any]] = []
    for principal, title in result.all():
        people_credits.append(
            {
                "tconst": principal.tconst,
                "ordering": principal.ordering,
                "category": principal.category,
                "job": principal.job,
                "characters": principal.characters,
                "title": {
                    "tconst": title.tconst,
                    "title_type": title.title_type,
                    "primary_title": title.primary_title,
                    "original_title": title.original_title,
                    "start_year": title.start_year,
                    "end_year": title.end_year,
                },
            }
        )

    return people_credits
