"""import title principals"""

import asyncpg
from src.import_base import IngestDataset


class IngestTitlePrincipals(IngestDataset):
    """ingest dataset"""

    DATASET_NAME = "title.principals.tsv"

    async def create_staging_table(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            CREATE TEMP TABLE IF NOT EXISTS {self.staging_table} (
                tconst TEXT,
                ordering INTEGER,
                nconst TEXT,
                category TEXT,
                job TEXT,
                characters TEXT
            ) ON COMMIT DROP;
            """
        )

    async def merge_into_final(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            INSERT INTO title_principals (
                tconst,
                ordering,
                nconst,
                category,
                job,
                characters
            )
            SELECT
                s.tconst,
                s.ordering,
                s.nconst,
                s.category,
                s.job,
                CASE
                    WHEN s.characters IS NULL THEN NULL
                    ELSE (
                        SELECT array_agg(value)
                        FROM jsonb_array_elements_text(s.characters::jsonb)
                    )
                END
            FROM {self.staging_table} s
            WHERE EXISTS (
                SELECT 1 FROM titles t WHERE t.tconst = s.tconst
            )
            AND EXISTS (
                SELECT 1 FROM people p WHERE p.nconst = s.nconst
            )
            ON CONFLICT (tconst, ordering) DO UPDATE
            SET
                nconst = EXCLUDED.nconst,
                category = EXCLUDED.category,
                job = EXCLUDED.job,
                characters = EXCLUDED.characters;
            """
        )
