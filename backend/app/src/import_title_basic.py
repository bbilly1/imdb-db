"""import title basic dataset"""

import asyncpg
from src.import_base import IngestDataset


class IngestTitleBasics(IngestDataset):
    """ingest title basic dataset"""

    DATASET_NAME = "title.basics.tsv"

    async def create_staging_table(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            CREATE TEMP TABLE IF NOT EXISTS {self.staging_table} (
                tconst TEXT,
                title_type TEXT,
                primary_title TEXT,
                original_title TEXT,
                is_adult BOOLEAN,
                start_year SMALLINT,
                end_year SMALLINT,
                runtime_minutes BIGINT,
                genres TEXT
            ) ON COMMIT DROP
            """
        )

    async def merge_into_final(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            INSERT INTO titles (
                tconst,
                title_type,
                primary_title,
                original_title,
                is_adult,
                start_year,
                end_year,
                runtime_minutes,
                genres
            )
            SELECT
                tconst,
                title_type,
                primary_title,
                NULLIF(original_title, ''),
                is_adult,
                start_year,
                end_year,
                runtime_minutes,
                string_to_array(genres, ',')
            FROM {self.staging_table}
            ON CONFLICT (tconst) DO UPDATE
            SET
                title_type = EXCLUDED.title_type,
                primary_title = EXCLUDED.primary_title,
                original_title = EXCLUDED.original_title,
                is_adult = EXCLUDED.is_adult,
                start_year = EXCLUDED.start_year,
                end_year = EXCLUDED.end_year,
                runtime_minutes = EXCLUDED.runtime_minutes,
                genres = EXCLUDED.genres
            """
        )
