"""app entrypoing"""

import logging
from pathlib import Path

try:

    from dotenv import load_dotenv

    if Path(".env").exists():
        print("loading local .env file")
        load_dotenv(".env")

except ModuleNotFoundError:
    pass

from os import environ

from api.ingest import router as ingest_router
from api.people import router as people_router
from api.search import router as search_router
from api.series import router as series_router
from api.titles import router as titles_router
from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
)
logging.getLogger().setLevel(logging.INFO)

git_tag = environ.get("GIT_TAG", "dev")
git_commit = environ.get("GIT_COMMIT", "unknown")

app = FastAPI(
    title="IMDb Read-Only API",
    version=git_tag,
    description=f"build tag={git_tag} commit={git_commit}",
)

app.include_router(titles_router)
app.include_router(series_router)
app.include_router(people_router)
app.include_router(search_router)
app.include_router(ingest_router)


@app.on_event("startup")
async def on_startup() -> None:
    """startup checks"""
    Path(environ["CACHE_DIR"]).mkdir(parents=True, exist_ok=True)


@app.get("/api")
async def api_is_up():
    """hello world"""
    return {
        "ping": "pong",
        "git_tag": git_tag,
        "git_commit": git_commit,
    }
