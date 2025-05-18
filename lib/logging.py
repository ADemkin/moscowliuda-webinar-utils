import sys

from loguru import logger as _logger


def _format(record: dict) -> str:
    base = f"{record['time']} {record['level'].name} {record['message']}"
    extras = "\n".join(f"   {k} = {v}" for k, v in record["extra"].items())
    if extras:
        extras = f"{extras}\n"
    return f"{base}\n{extras}"


_logger.remove()
_logger.add(
    "app.log",
    encoding="utf-8",
    rotation="10MB",
    format=_format,  # type: ignore[arg-type]
)
_logger.add(
    sys.stdout,
    format=_format,  # type: ignore[arg-type]
)

logger = _logger
