"""import title akas"""

import asyncpg
from src.import_base import IngestDataset


class IngestTitleAkas(IngestDataset):
    """ingest dataset"""

    def __init__(self, pool: asyncpg.Pool):
        super().__init__("title.akas.tsv", pool)

    async def create_staging_table(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            CREATE TEMP TABLE IF NOT EXISTS {self.staging_table} (
                title_id TEXT,
                ordering INTEGER,
                title TEXT,
                region TEXT,
                language TEXT,
                types TEXT,
                attributes TEXT,
                is_original BOOLEAN
            ) ON COMMIT DROP;
            """
        )

    async def merge_into_final(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            INSERT INTO title_akas (
                title_id,
                ordering,
                title,
                region,
                language,
                types,
                attributes,
                is_original
            )
            SELECT
                s.title_id,
                s.ordering,
                s.title,
                s.region,
                s.language,
                CASE
                    WHEN s.types IS NULL THEN NULL
                    ELSE string_to_array(s.types, ',')
                END,
                CASE
                    WHEN s.attributes IS NULL THEN NULL
                    ELSE string_to_array(s.attributes, ',')
                END,
                s.is_original
            FROM {self.staging_table} s
            WHERE EXISTS (
                SELECT 1 FROM titles t WHERE t.tconst = s.title_id
            )
            ON CONFLICT (title_id, ordering) DO UPDATE
            SET
                title = EXCLUDED.title,
                region = EXCLUDED.region,
                language = EXCLUDED.language,
                types = EXCLUDED.types,
                attributes = EXCLUDED.attributes,
                is_original = EXCLUDED.is_original;
            """
        )
