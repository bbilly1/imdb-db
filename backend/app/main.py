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

from api.people import router as people_router
from api.search import router as search_router
from api.series import router as series_router
from api.titles import router as titles_router
from fastapi import FastAPI

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
