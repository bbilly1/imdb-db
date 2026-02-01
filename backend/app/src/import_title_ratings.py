"""import title ratings"""

import asyncpg
from src.import_base import IngestDataset


class IngestTitleRatings(IngestDataset):
    """ingest dataset"""

    def __init__(self, pool: asyncpg.Pool):
        super().__init__("title.ratings.tsv", pool)

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
                tconst,
                average_rating,
                num_votes
            FROM {self.staging_table}
            ON CONFLICT (tconst) DO UPDATE
            SET
                average_rating = EXCLUDED.average_rating,
                num_votes = EXCLUDED.num_votes;
            """
        )
