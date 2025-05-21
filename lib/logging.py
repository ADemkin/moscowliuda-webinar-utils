import sys

from loguru import logger as _logger

_logger.remove()
_logger.add(
    "app-v1.log",
    encoding="utf-8",
    serialize=True,
    rotation="10MB",
    format="{message}",
)
_logger.add(
    sys.stdout,
    serialize=True,
    format="{message}",
)

logger = _logger
