"""ingest trigger endpoint"""

import logging

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException
from pydantic import BaseModel
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
