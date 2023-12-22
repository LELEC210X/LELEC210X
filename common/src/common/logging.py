__all__ = ["handler", "logger"]

import logging

from rich.logging import RichHandler

handler = RichHandler()

logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", handlers=[handler]
)

logger = logging.getLogger("LELEC210X")
