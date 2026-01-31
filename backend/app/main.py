"""app entrypoing"""

from pathlib import Path

try:
    
    from dotenv import load_dotenv

    if Path(".env").exists():
        print("loading local .env file")
        load_dotenv(".env")

except ModuleNotFoundError:
    pass

from os import environ
from typing import AsyncGenerator

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import AsyncSessionLocal
from models import Title, Person


app = FastAPI(
    title="IMDb Read-Only API",
    version="0.0.1",
)

@app.on_event("startup")
async def on_startup() -> None:
    """startup checks"""
    Path(environ["CACHE_DIR"]).mkdir(parents=True, exist_ok=True)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async database session dependency"""
    async with AsyncSessionLocal() as session:
        yield session


# ---------- Example placeholder routes ----------

@app.get("/titles/{tconst}", response_model=Title)
async def get_title(
    tconst: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Title).where(Title.tconst == tconst)
    )
    return result.scalar_one_or_none()


@app.get("/people/{nconst}", response_model=Person)
async def get_person(
    nconst: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Person).where(Person.nconst == nconst)
    )
    return result.scalar_one_or_none()
