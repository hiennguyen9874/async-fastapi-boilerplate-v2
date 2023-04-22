import asyncio
from pathlib import Path

from loguru import logger

from app.custom_logging import CustomizeLogger
from app.db.init_db import init_db
from app.db.session import async_session

CustomizeLogger.make_logger(Path(__file__).with_name("api_logging.json"))


async def init() -> None:
    async with async_session() as session:
        await init_db(session)
    await session.commit()


def main() -> None:
    logger.info("Creating initial data")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    loop.close()

    logger.info("Initial data created")


if __name__ == "__main__":
    main()
