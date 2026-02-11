"""import dataset base functionality"""

import asyncio
import gzip
import logging
import shutil
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from io import BytesIO
from os import environ
from pathlib import Path
from time import perf_counter
from typing import AsyncIterator, cast

import aiohttp
import asyncpg
from database import AsyncSessionLocal
from models import ImportTask

logger = logging.getLogger(__name__)


class IngestDataset(ABC):
    """
    Base class for IMDb dataset ingestion using COPY + staging tables.
    """

    CHUNK_SIZE_LINES = 100_000
    BASE_URL = "https://datasets.imdbws.com"
    CACHE_DIR = environ["CACHE_DIR"]

    def __init__(self, dataset_name: str, pool: asyncpg.Pool):
        self.dataset_name = dataset_name
        self.pool = pool

    @property
    def gz_path(self) -> Path:
        """gzip path"""
        return Path(self.CACHE_DIR) / f"{self.dataset_name}.gz"

    @property
    def tsv_path(self) -> Path:
        """tsv decompressed path"""
        return self.gz_path.with_suffix("")

    @property
    def gz_size(self) -> int:
        """compressed file size in bytes"""
        return self.gz_path.stat().st_size

    @property
    def tsv_size(self) -> int:
        """raw extracted file size in bytes"""
        return self.tsv_path.stat().st_size

    @property
    def url(self) -> str:
        """download url"""
        return f"{self.BASE_URL}/{self.dataset_name}.gz"

    @property
    def staging_table(self) -> str:
        """staging table"""
        return f"staging_{self.dataset_name.rstrip(".tsv").replace(".", "_")}"

    async def run(self) -> None:
        """run download and import"""
        import_start_time = datetime.now(timezone.utc)
        start = perf_counter()

        logger.info("import started dataset=%s", self.dataset_name)
        await self._download_if_needed()
        self._extract_if_needed()

        async with self.pool.acquire() as conn:
            db_conn = cast(asyncpg.Connection, conn)
            async with conn.transaction():
                await self.create_staging_table(db_conn)

                async for lines in self._read_tsv_in_chunks():
                    await self.copy_chunk(db_conn, lines)

                await self.merge_into_final(db_conn)

        await self._record_import_task(
            import_start_time=import_start_time,
            duration=perf_counter() - start,
        )

        logger.info(
            "import completed dataset=%s size_compressed=%s size_raw=%s duration=%.3fs",
            self.dataset_name,
            self.gz_size,
            self.tsv_size,
            perf_counter() - start,
        )

    async def _download_if_needed(self) -> None:
        """download if not exist on file path"""
        if self.gz_path.exists():
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                resp.raise_for_status()
                with open(self.gz_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024 * 1024):
                        f.write(chunk)

    def _extract_if_needed(self) -> None:
        """extract if not extracted"""
        if self.tsv_path.exists():
            return

        with gzip.open(self.gz_path, "rb") as gz:
            with open(self.tsv_path, "wb") as out:
                shutil.copyfileobj(gz, out)

    async def _record_import_task(
        self,
        import_start_time: datetime,
        duration: float,
    ) -> None:
        """Persist one import task row for this dataset processing run."""
        import_task = ImportTask(
            filename=self.dataset_name,
            size_compressed=self.gz_size,
            size_raw=self.tsv_size,
            import_start_time=import_start_time,
            duration=duration,
        )
        async with AsyncSessionLocal() as session:
            session.add(import_task)
            await session.commit()

    async def _read_tsv_in_chunks(self) -> AsyncIterator[list[str]]:
        """partial read tsv file"""
        loop = asyncio.get_running_loop()

        def generator():
            with open(self.tsv_path, "r", encoding="utf-8") as f:
                _ = next(f)  # skip header
                chunk = []
                for line in f:
                    chunk.append(line.rstrip("\n"))
                    if len(chunk) >= self.CHUNK_SIZE_LINES:
                        yield chunk
                        chunk = []
                if chunk:
                    yield chunk

        for chunk in await loop.run_in_executor(None, lambda: list(generator())):
            yield chunk

    async def copy_chunk(self, conn: asyncpg.Connection, lines: list[str]) -> None:
        """COPY raw TSV lines into staging table"""
        buf = BytesIO()
        for line in lines:
            buf.write(line.encode("utf-8"))
            buf.write(b"\n")
        buf.seek(0)

        await conn.copy_to_table(
            self.staging_table,
            source=buf,
            format="csv",
            delimiter="\t",
            null="\\N",
            quote="\b",
        )

    @abstractmethod
    async def create_staging_table(self, conn: asyncpg.Connection) -> None:
        """to implement: create staging table"""

    @abstractmethod
    async def merge_into_final(self, conn: asyncpg.Connection) -> None:
        """to implement: merge staging into final table"""
