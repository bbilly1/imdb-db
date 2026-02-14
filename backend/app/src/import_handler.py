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


async def import_datasets(dataset_names: list[str] | None = None) -> None:
    """run all imports, or selected imports by dataset names"""

    ingest_classes: list[Type[IngestDataset]] = [
        IngestTitleBasics,
        IngestNameBasics,
        IngestTitleRatings,
        IngestTitleEpisodes,
        IngestTitleAkas,
        IngestTitlePrincipals,
    ]
    ingest_by_dataset_name: dict[str, Type[IngestDataset]] = {
        ingest_class.DATASET_NAME: ingest_class for ingest_class in ingest_classes
    }

    pool = await asyncpg.create_pool(dsn=environ["DATABASE_URL_SYNC"])
    try:
        if dataset_names is None:
            selected_classes = list(ingest_by_dataset_name.values())
            selected_dataset_names = list(ingest_by_dataset_name.keys())
        else:
            selected_classes = []
            selected_dataset_names = []
            for dataset_name in dataset_names:
                ingest_class = ingest_by_dataset_name.get(dataset_name)
                if ingest_class is None:
                    raise ValueError(f"Unsupported dataset_name: {dataset_name}")

                selected_classes.append(ingest_class)
                selected_dataset_names.append(dataset_name)

        logger.info(
            "Starting dataset imports datasets=%s",
            ", ".join(selected_dataset_names),
        )

        for ingest_class in selected_classes:
            await ingest_class(pool=pool).run()
    finally:
        await pool.close()
