"""import title ratings"""

import asyncpg
from src.import_base import IngestDataset


class IngestTitleRatings(IngestDataset):
    """ingest dataset"""

    DATASET_NAME = "title.ratings.tsv"

    async def create_staging_table(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            CREATE TEMP TABLE IF NOT EXISTS {self.staging_table} (
                tconst TEXT,
                average_rating REAL,
                num_votes INT
            ) ON COMMIT DROP;
            """
        )

    async def merge_into_final(self, conn: asyncpg.Connection) -> None:
        await conn.execute(
            f"""
            INSERT INTO title_ratings (tconst, average_rating, num_votes)
            SELECT
                s.tconst,
                s.average_rating,
                s.num_votes
            FROM {self.staging_table} s
            WHERE EXISTS (
                SELECT 1 FROM titles t WHERE t.tconst = s.tconst
            )
            ON CONFLICT (tconst) DO UPDATE
            SET
                average_rating = EXCLUDED.average_rating,
                num_votes = EXCLUDED.num_votes;
            """
        )
