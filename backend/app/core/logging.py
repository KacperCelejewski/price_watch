import sys
import os
from loguru import logger


def setup_logging() -> None:
    """Configure Loguru: stdout + rotating JSON file."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Human-readable stdout
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Structured JSON log file for scrapers
    logger.add(
        os.path.join(log_dir, "scraper.log"),
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        serialize=True,  # JSON format
        enqueue=True,    # Thread-safe
        compression="gz",
    )
