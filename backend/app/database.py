"""connect to PG"""

from os import environ
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = environ["DATABASE_URL"]

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def init_db() -> None:
    """async init db"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
