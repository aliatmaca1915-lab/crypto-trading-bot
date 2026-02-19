"""
Logging Configuration
Centralized logging for the trading bot
"""
import sys
from loguru import logger
from config import Config


def setup_logging():
    """Configure logging for the application"""
    # Remove default handler
    logger.remove()
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level=Config.LOG_LEVEL,
        colorize=True
    )
    
    # File handler with rotation
    logger.add(
        Config.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=Config.LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logging system initialized")
    
    return logger


# Initialize logger
log = setup_logging()
