"""app dependencies"""

from typing import AsyncGenerator

from database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async database session dependency"""
    async with AsyncSessionLocal() as session:
        yield session
