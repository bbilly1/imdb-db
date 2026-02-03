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

from database import AsyncSessionLocal
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

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


@app.get("/api")
async def api_is_up():
    """hello world"""
    return {"ping": "pong"}
