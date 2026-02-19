"""
Logging System
Provides comprehensive logging for the trading bot
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
import colorlog


class LoggerManager:
    """Manages logging for the trading bot"""
    
    def __init__(self, name: str = "CryptoBot", config=None):
        """Initialize logger manager"""
        self.name = name
        self.config = config
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup and configure logger"""
        logger = logging.getLogger(self.name)
        
        # Get log level from config
        if self.config:
            level_str = self.config.get('logging.level', 'INFO')
        else:
            level_str = os.getenv('LOG_LEVEL', 'INFO')
        
        level = getattr(logging, level_str.upper(), logging.INFO)
        logger.setLevel(level)
        
        # Remove existing handlers
        logger.handlers = []
        
        # Console handler with colors
        if not self.config or self.config.get('logging.console_logging', True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # Colored formatter
            color_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(color_formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if not self.config or self.config.get('logging.file_logging', True):
            # Create logs directory if it doesn't exist
            log_dir = Path(__file__).parent.parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            
            log_file = self.config.get('logging.log_file', 'logs/trading_bot.log') if self.config else 'logs/trading_bot.log'
            log_path = Path(__file__).parent.parent.parent / log_file
            
            max_bytes = self.config.get('logging.max_file_size', 10485760) if self.config else 10485760
            backup_count = self.config.get('logging.backup_count', 5) if self.config else 5
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(level)
            
            # File formatter (no colors)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """Log exception with traceback"""
        self.logger.exception(message)
    
    def log_trade(self, trade_info: dict):
        """Log trade information"""
        self.info(f"TRADE: {trade_info}")
    
    def log_signal(self, signal_info: dict):
        """Log signal information"""
        self.info(f"SIGNAL: {signal_info}")
    
    def log_score(self, score_info: dict):
        """Log scoring information"""
        self.info(f"SCORE: {score_info}")
    
    def log_position(self, position_info: dict):
        """Log position information"""
        self.info(f"POSITION: {position_info}")
    
    def log_risk(self, risk_info: dict):
        """Log risk information"""
        self.warning(f"RISK: {risk_info}")


# Global logger instance
_logger_instance = None


def get_logger(name: str = "CryptoBot", config=None) -> LoggerManager:
    """Get logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = LoggerManager(name, config)
    return _logger_instance


def reset_logger():
    """Reset logger instance"""
    global _logger_instance
    _logger_instance = None
