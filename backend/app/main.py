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

from api.params import PaginationParams
from api.people import router as people_router
from api.search import router as search_router
from api.series import router as series_router
from api.titles import router as titles_router
from dependencies import get_session
from fastapi import Depends, FastAPI
from models import ImportTask
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(
    title="IMDb Read-Only API",
    version="0.0.1",
)

app.include_router(titles_router)
app.include_router(series_router)
app.include_router(people_router)
app.include_router(search_router)


@app.on_event("startup")
async def on_startup() -> None:
    """startup checks"""
    Path(environ["CACHE_DIR"]).mkdir(parents=True, exist_ok=True)


@app.get("/api")
async def api_is_up():
    """hello world"""
    return {"ping": "pong"}


@app.get("/api/import-tasks")
async def list_import_tasks(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """list paginated import task records"""
    stmt = (
        select(ImportTask)
        .order_by(ImportTask.import_start_time)
        .limit(params.size)
        .offset((params.page - 1) * params.size)
    )
    result = await session.execute(stmt)
    tasks = list(result.scalars().all())
    return [
        {
            **task.model_dump(),
            "size_compressed_mb": round(task.size_compressed / (1024 * 1024), 2),
            "size_raw_mb": round(task.size_raw / (1024 * 1024), 2),
        }
        for task in tasks
    ]
