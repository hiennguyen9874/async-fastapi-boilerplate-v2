# pylint: disable=duplicate-code
import asyncio
from pathlib import Path

from loguru import logger
from sqlalchemy import text
from tenacity import retry
from tenacity.after import after_log
from tenacity.before import before_log
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from app.custom_logging import CustomizeLogger
from app.db.session import async_session

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

CustomizeLogger.make_logger(Path(__file__).with_name("api_logging.json"))


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, "INFO"),  # type: ignore
    after=after_log(logger, "WARNING"),  # type: ignore
)
async def init() -> None:
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        await session.commit()

    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    loop.close()

    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
