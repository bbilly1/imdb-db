"""import base class"""

import asyncio
import gzip
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncIterator
from os import environ

import aiohttp


class IngestDataset(ABC):
    """
    Base class for IMDb dataset ingestion.
    """

    CHUNK_SIZE_LINES = 100_000
    BASE_URL = "https://datasets.imdbws.com"
    CACHE_DIR = environ["CACHE_DIR"]

    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name

    @property
    def gz_path(self) -> Path:
        """gzip path"""
        return Path(self.CACHE_DIR) / f"{self.dataset_name}.gz"

    @property
    def tsv_path(self) -> Path:
        """tsv file path"""
        return self.gz_path.with_suffix("")

    @property
    def url(self) -> str:
        """url to download"""
        return f"{self.BASE_URL}/{self.dataset_name}.gz"

    async def run(self) -> None:
        """run ingest"""
        await self._download_if_needed()
        self._extract_if_needed()

        async for lines in self._read_tsv_in_chunks():
            await self.process_chunk(lines)

    async def _download_if_needed(self) -> None:
        """download if not exist"""
        if self.gz_path.exists():
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                resp.raise_for_status()
                with open(self.gz_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024 * 1024):
                        f.write(chunk)

    def _extract_if_needed(self) -> None:
        """extract if not exist"""
        if self.tsv_path.exists():
            return

        with gzip.open(self.gz_path, "rb") as gz:
            with open(self.tsv_path, "wb") as out:
                shutil.copyfileobj(gz, out)

    async def _read_tsv_in_chunks(self) -> AsyncIterator[list[str]]:
        """
        Yields lists of raw TSV lines (excluding header).
        """
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

    @abstractmethod
    async def process_chunk(self, lines: list[str]) -> None:
        """
        Parse TSV lines and persist to DB.
        Must be idempotent. implement in base class
        """
