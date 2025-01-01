from loguru import logger as _logger

_logger.add("app.log", encoding="utf-8", rotation="10MB")

logger = _logger
