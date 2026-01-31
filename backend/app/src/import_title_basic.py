"""import title basic dataset"""

from database import AsyncSessionLocal
from models import Title
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.helper import bool_match, int_or_none, list_of_str_or_none
from src.import_base import IngestDataset


class TitleBasicImport(IngestDataset):
    """ingest basic title dataset"""

    BATCH_SIZE = 2_000

    async def process_chunk(self, lines: list[str]) -> None:
        """process chunk of lines"""
        titles = []

        for line in lines:
            (
                tconst,
                title_type,
                primary_title,
                original_title,
                is_adult,
                start_year,
                end_year,
                runtime_minutes,
                genres,
            ) = line.split("\t")
            titles.append(
                {
                    "tconst": tconst,
                    "title_type": title_type,
                    "primary_title": primary_title,
                    "original_title": original_title,
                    "is_adult": bool_match(is_adult),
                    "start_year": int_or_none(start_year),
                    "end_year": int_or_none(end_year),
                    "runtime_minutes": int_or_none(runtime_minutes),
                    "genres": list_of_str_or_none(genres),
                }
            )

        print(f"processed {len(titles)} titles")
        async with AsyncSessionLocal() as session:
            for i in range(0, len(titles), self.BATCH_SIZE):
                batch = titles[i : i + self.BATCH_SIZE]
                await self._upsert_titles(session, rows=batch)

            await session.commit()

    async def _upsert_titles(
        self,
        session: AsyncSession,
        rows: list[dict],
    ) -> None:
        stmt = insert(Title).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["tconst"],
            set_={
                "title_type": stmt.excluded.title_type,
                "primary_title": stmt.excluded.primary_title,
                "original_title": stmt.excluded.original_title,
                "is_adult": stmt.excluded.is_adult,
                "start_year": stmt.excluded.start_year,
                "end_year": stmt.excluded.end_year,
                "runtime_minutes": stmt.excluded.runtime_minutes,
                "genres": stmt.excluded.genres,
            },
        )

        await session.execute(stmt)
