"""import name basic dataset"""

import asyncpg
from src.import_base import IngestDataset


class IngestNameBasics(IngestDataset):
    """ingest dataset"""

    DATASET_NAME = "name.basics.tsv"

    async def create_staging_table(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            CREATE TEMP TABLE IF NOT EXISTS {self.staging_table} (
                nconst TEXT,
                primary_name TEXT,
                birth_year SMALLINT,
                death_year SMALLINT,
                primary_professions TEXT,
                known_for_titles TEXT
            ) ON COMMIT DROP;
            """
        )

    async def merge_into_final(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            INSERT INTO people (
                nconst,
                primary_name,
                birth_year,
                death_year,
                primary_professions,
                known_for_titles
            )
            SELECT
                nconst,
                primary_name,
                birth_year,
                death_year,
                string_to_array(primary_professions, ','),
                string_to_array(known_for_titles, ',')
            FROM {self.staging_table}
            ON CONFLICT (nconst) DO UPDATE
            SET
                primary_name = EXCLUDED.primary_name,
                birth_year = EXCLUDED.birth_year,
                death_year = EXCLUDED.death_year,
                primary_professions = EXCLUDED.primary_professions,
                known_for_titles = EXCLUDED.known_for_titles;
            """
        )
