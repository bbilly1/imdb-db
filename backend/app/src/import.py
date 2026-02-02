"""import interface"""

from os import environ

import asyncpg
from src.import_name_basic import IngestNameBasics
from src.import_title_akas import IngestTitleAkas
from src.import_title_basic import IngestTitleBasics
from src.import_title_episode import IngestTitleEpisodes
from src.import_title_principals import IngestTitlePrincipals
from src.import_title_ratings import IngestTitleRatings


async def import_datasets():
    """run all imports"""

    pool = await asyncpg.create_pool(dsn=environ["DATABASE_URL_SYNC"])

    await IngestTitleBasics(pool=pool).run()
    await IngestNameBasics(pool=pool).run()
    await IngestTitleRatings(pool=pool).run()
    await IngestTitleEpisodes(pool=pool).run()
    await IngestTitleAkas(pool=pool).run()
    await IngestTitlePrincipals(pool=pool).run()
