"""import interface"""

import logging
from os import environ
from typing import Type

import asyncpg
from src.import_base import IngestDataset
from src.import_name_basic import IngestNameBasics
from src.import_title_akas import IngestTitleAkas
from src.import_title_basic import IngestTitleBasics
from src.import_title_episode import IngestTitleEpisodes
from src.import_title_principals import IngestTitlePrincipals
from src.import_title_ratings import IngestTitleRatings

logger = logging.getLogger(__name__)

INGEST_CLASSES: tuple[Type[IngestDataset], ...] = (
    IngestTitleBasics,
    IngestNameBasics,
    IngestTitleRatings,
    IngestTitleEpisodes,
    IngestTitleAkas,
    IngestTitlePrincipals,
)
INGEST_BY_DATASET_NAME: dict[str, Type[IngestDataset]] = {
    ingest_class.DATASET_NAME: ingest_class for ingest_class in INGEST_CLASSES
}
SUPPORTED_DATASET_NAMES: tuple[str, ...] = tuple(INGEST_BY_DATASET_NAME.keys())


def resolve_datasets(
    dataset_names: list[str] | None,
) -> tuple[list[Type[IngestDataset]], list[str]]:
    """resolve and validate selected dataset names"""
    if dataset_names is None:
        return list(INGEST_BY_DATASET_NAME.values()), list(SUPPORTED_DATASET_NAMES)

    selected_classes: list[Type[IngestDataset]] = []
    selected_dataset_names: list[str] = []
    for dataset_name in dataset_names:
        ingest_class = INGEST_BY_DATASET_NAME.get(dataset_name)
        if ingest_class is None:
            raise ValueError(f"Unsupported dataset_name: {dataset_name}")
        selected_classes.append(ingest_class)
        selected_dataset_names.append(dataset_name)

    return selected_classes, selected_dataset_names


async def import_datasets(dataset_names: list[str] | None = None) -> None:
    """run all imports, or selected imports by dataset names"""

    pool = await asyncpg.create_pool(dsn=environ["DATABASE_URL_SYNC"])
    try:
        selected_classes, selected_dataset_names = resolve_datasets(dataset_names)

        logger.info(
            "Starting dataset imports datasets=%s",
            ", ".join(selected_dataset_names),
        )

        for ingest_class in selected_classes:
            await ingest_class(pool=pool).run()
    finally:
        await pool.close()
