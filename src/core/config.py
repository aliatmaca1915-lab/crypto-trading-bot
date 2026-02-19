"""
Configuration Management System
Handles loading and validation of bot configuration
"""
import yaml
import os
from typing import Dict, Any, List
from pathlib import Path


class ConfigManager:
    """Manages bot configuration from YAML file"""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration manager"""
        if config_path is None:
            # Default to config/config.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration file: {e}")
    
    def _validate_config(self):
        """Validate critical configuration parameters"""
        # Check trading mode
        if self.config.get('mode') not in ['paper', 'real']:
            raise ValueError("Trading mode must be 'paper' or 'real'")
        
        # Check leverage
        leverage = self.config.get('leverage', {}).get('fixed_leverage', 0)
        if leverage != 10:
            raise ValueError("Fixed leverage must be 10x")
        
        # Check minimum score
        min_score = self.config.get('scoring', {}).get('minimum_score', 0)
        if min_score < 60:
            raise ValueError("Minimum score must be at least 60")
        
        # Validate cryptocurrencies list
        cryptos = self.config.get('cryptocurrencies', [])
        if not cryptos:
            raise ValueError("At least one cryptocurrency must be configured")
        
        # Remove duplicates
        self.config['cryptocurrencies'] = list(set(cryptos))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports nested keys with dot notation)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    def is_paper_trading(self) -> bool:
        """Check if in paper trading mode"""
        return self.config.get('mode', 'paper') == 'paper'
    
    def is_real_trading(self) -> bool:
        """Check if in real trading mode"""
        return self.config.get('mode', 'paper') == 'real'
    
    def get_leverage(self) -> int:
        """Get fixed leverage value"""
        return self.config.get('leverage', {}).get('fixed_leverage', 10)
    
    def get_cryptocurrencies(self) -> List[str]:
        """Get list of cryptocurrencies to trade"""
        return self.config.get('cryptocurrencies', [])
    
    def get_minimum_score(self) -> int:
        """Get minimum score threshold"""
        return self.config.get('scoring', {}).get('minimum_score', 60)
    
    def get_position_size(self, classification: str) -> Dict[str, float]:
        """Get position sizing parameters for classification"""
        sizing = self.config.get('position_sizing', {})
        return sizing.get(classification.lower(), {})
    
    def get_timeframes(self) -> List[str]:
        """Get list of timeframes for multi-timeframe analysis"""
        return self.config.get('timeframes', [])
    
    def get_initial_capital(self) -> float:
        """Get initial capital amount"""
        return self.config.get('capital', {}).get('initial_capital', 10000)
    
    def get_daily_loss_limit(self) -> float:
        """Get daily loss limit as percentage"""
        return self.config.get('capital', {}).get('daily_loss_limit', 0.05)
    
    def get_weekly_loss_limit(self) -> float:
        """Get weekly loss limit as percentage"""
        return self.config.get('capital', {}).get('weekly_loss_limit', 0.10)
    
    def __repr__(self) -> str:
        """String representation"""
        mode = "PAPER TRADING" if self.is_paper_trading() else "REAL TRADING"
        return f"ConfigManager(mode={mode}, leverage={self.get_leverage()}x)"


# Global config instance
_config_instance = None


def get_config() -> ConfigManager:
    """Get global configuration instance (singleton pattern)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def reset_config():
    """Reset global configuration instance"""
    global _config_instance
    _config_instance = None
