"""ingest trigger endpoint"""

import logging
from typing import Any

from api.params import PaginationParams
from dependencies import get_session
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException
from models import ImportTask
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.import_handler import SUPPORTED_DATASET_NAMES, import_datasets, resolve_datasets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ingest"])


class TriggerIngestRequest(BaseModel):
    """request model for import trigger"""

    data_set: list[str] | None = None


async def _run_ingest_task(dataset_names: list[str] | None) -> None:
    """background task wrapper with logging"""
    try:
        await import_datasets(dataset_names=dataset_names)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("dataset ingest task failed datasets=%s", dataset_names)


@router.post("/ingest")
async def trigger_ingest(
    background_tasks: BackgroundTasks,
    payload: TriggerIngestRequest | None = Body(default=None),
) -> dict[str, object]:
    """spawn ingest background task and return immediately"""
    dataset_names = payload.data_set if payload else None

    try:
        _, selected_dataset_names = resolve_datasets(dataset_names)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "supported_data_set": list(SUPPORTED_DATASET_NAMES),
            },
        ) from exc

    background_tasks.add_task(_run_ingest_task, dataset_names)
    return {
        "message": "Ingest task scheduled",
        "data_set": selected_dataset_names,
    }


@router.get("/import-tasks")
async def list_import_tasks(
    params: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
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
