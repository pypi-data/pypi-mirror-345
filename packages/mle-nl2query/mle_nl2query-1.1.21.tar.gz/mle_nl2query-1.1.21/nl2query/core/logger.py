import logging
from pprint import pformat
import sys
from loguru import logger
from loguru._defaults import LOGURU_FORMAT


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"
    format_string += "{exception}\n"
    return format_string


def init_logging(filename: str = None):
    """
    Replaces logging handlers with a handler for using the custom handler.

    Args:
        filename (str, optional): Base filename for log files. If provided, logs will be written to
            files like `<filename>.info.log`, `<filename>.debug.log`, etc. If None, defaults to
            'logs/info.log', 'logs/debug.log', etc.
    """
    # Remove handlers from all uvicorn loggers
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    intercept_handler = InterceptHandler()
    logging.getLogger("uvicorn").handlers = [intercept_handler]

    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.propagate = True

    # Determine log file paths based on filename parameter
    base_path = filename if filename else "logs"
    info_file = f"logs/{base_path}.info.log" if filename else "logs/info.log"
    debug_file = f"logs/{base_path}.debug.log" if filename else "logs/debug.log"
    error_file = f"logs/{base_path}.error.log" if filename else "logs/error.log"

    logger.remove()
    logger.add(
        info_file,
        level="INFO",
        format=format_record,
        filter=lambda record: record["level"].name == "INFO",
    )
    logger.add(
        debug_file,
        level="DEBUG",
        format=format_record,
        filter=lambda record: record["level"].name == "DEBUG",
    )
    logger.add(
        error_file,
        level="ERROR",
        format=format_record,
        filter=lambda record: record["level"].name == "ERROR",
    )
    logger.add(sys.stdout, level="DEBUG", format=format_record, colorize=True)
