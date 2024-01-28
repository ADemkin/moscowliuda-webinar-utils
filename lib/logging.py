from loguru import logger

logger.add("app.log", encoding="utf-8", rotation="10MB")
