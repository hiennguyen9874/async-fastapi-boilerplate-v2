import json
import logging
import sys
from pathlib import Path

from loguru import logger


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[int(record.levelno)]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        # log = logger.bind(request_id="app")
        # log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class CustomizeLogger:
    @classmethod
    def make_logger(cls, config_path: Path) -> logging.Logger:
        config = cls.load_logging_config(config_path)
        logging_config = config.get("logger")
        return cls.customize_logging(
            logging_config.get("path"),  # type: ignore
            level=logging_config.get("level"),  # type: ignore
            retention=logging_config.get("retention"),  # type: ignore
            rotation=logging_config.get("rotation"),  # type: ignore
            format=logging_config.get("format"),  # type: ignore
        )

    @classmethod
    def customize_logging(  # pylint: disable=too-many-arguments,redefined-builtin
        cls, filepath: Path, level: str, rotation: str, retention: str, format: str
    ) -> logging.Logger:
        logger.remove()
        logger.add(sys.stdout, enqueue=True, backtrace=True, level=level.upper(), format=format)
        logger.add(
            str(filepath),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format,
        )
        logging.basicConfig(handlers=[InterceptHandler()], level=0)

        for _log in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi", "gunicorn"]:
            logging.getLogger(_log).handlers = [InterceptHandler()]

        # return logger.bind(request_id=None, method=None)
        return logger  # type: ignore

    @classmethod
    def load_logging_config(cls, config_path: Path) -> dict[str, dict[str, str]]:
        config = None
        with open(config_path, encoding="UTF-8") as config_file:
            config = json.load(config_file)
        return config
