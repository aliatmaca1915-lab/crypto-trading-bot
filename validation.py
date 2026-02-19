"""
Validation Module
Input validation and data integrity checks
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re


class ValidationError(Exception):
    """Custom validation error"""
    pass


class Validator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """
        Validate trading symbol format
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
        
        Returns:
            True if valid, False otherwise
        
        Raises:
            ValidationError: If symbol is invalid
        """
        if not symbol:
            raise ValidationError("Symbol cannot be empty")
        
        if not isinstance(symbol, str):
            raise ValidationError("Symbol must be a string")
        
        if not symbol.isupper():
            raise ValidationError("Symbol must be uppercase")
        
        if not symbol.endswith('USDT'):
            raise ValidationError("Symbol must end with USDT")
        
        if len(symbol) < 6 or len(symbol) > 12:
            raise ValidationError("Symbol length must be between 6 and 12 characters")
        
        return True
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """
        Validate price value
        
        Args:
            price: Price value
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If price is invalid
        """
        if not isinstance(price, (int, float)):
            raise ValidationError("Price must be a number")
        
        if price <= 0:
            raise ValidationError("Price must be positive")
        
        if price > 1000000:
            raise ValidationError("Price seems unreasonably high")
        
        return True
    
    @staticmethod
    def validate_quantity(quantity: float) -> bool:
        """
        Validate quantity value
        
        Args:
            quantity: Quantity value
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If quantity is invalid
        """
        if not isinstance(quantity, (int, float)):
            raise ValidationError("Quantity must be a number")
        
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        
        if quantity > 1000000:
            raise ValidationError("Quantity seems unreasonably high")
        
        return True
    
    @staticmethod
    def validate_score(score: int) -> bool:
        """
        Validate trading score
        
        Args:
            score: Trading score (0-100)
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If score is invalid
        """
        if not isinstance(score, int):
            raise ValidationError("Score must be an integer")
        
        if score < 0 or score > 100:
            raise ValidationError("Score must be between 0 and 100")
        
        return True
    
    @staticmethod
    def validate_timeframe(timeframe: str) -> bool:
        """
        Validate timeframe format
        
        Args:
            timeframe: Timeframe string (e.g., '1h', '4h', '1d')
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If timeframe is invalid
        """
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
        
        if timeframe not in valid_timeframes:
            raise ValidationError(f"Timeframe must be one of: {', '.join(valid_timeframes)}")
        
        return True
    
    @staticmethod
    def validate_api_credentials(api_key: str, api_secret: str) -> bool:
        """
        Validate API credentials format
        
        Args:
            api_key: API key
            api_secret: API secret
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If credentials are invalid
        """
        if not api_key or not api_secret:
            raise ValidationError("API credentials cannot be empty")
        
        if not isinstance(api_key, str) or not isinstance(api_secret, str):
            raise ValidationError("API credentials must be strings")
        
        if len(api_key) < 32:
            raise ValidationError("API key seems too short")
        
        if len(api_secret) < 32:
            raise ValidationError("API secret seems too short")
        
        return True
    
    @staticmethod
    def validate_percentage(value: float, min_val: float = 0, max_val: float = 100) -> bool:
        """
        Validate percentage value
        
        Args:
            value: Percentage value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If percentage is invalid
        """
        if not isinstance(value, (int, float)):
            raise ValidationError("Percentage must be a number")
        
        if value < min_val or value > max_val:
            raise ValidationError(f"Percentage must be between {min_val} and {max_val}")
        
        return True
    
    @staticmethod
    def validate_trade_side(side: str) -> bool:
        """
        Validate trade side
        
        Args:
            side: Trade side ('BUY' or 'SELL')
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If side is invalid
        """
        if side not in ['BUY', 'SELL']:
            raise ValidationError("Trade side must be 'BUY' or 'SELL'")
        
        return True
    
    @staticmethod
    def validate_classification(classification: str) -> bool:
        """
        Validate trade classification
        
        Args:
            classification: Trade classification ('SILVER', 'GOLD', 'DIAMOND')
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If classification is invalid
        """
        if classification not in ['SILVER', 'GOLD', 'DIAMOND', 'NONE']:
            raise ValidationError("Classification must be 'SILVER', 'GOLD', 'DIAMOND', or 'NONE'")
        
        return True
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """
        Validate date range
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If date range is invalid
        """
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValidationError("Dates must be datetime objects")
        
        if start_date >= end_date:
            raise ValidationError("Start date must be before end date")
        
        if end_date > datetime.utcnow():
            raise ValidationError("End date cannot be in the future")
        
        return True
    
    @staticmethod
    def validate_dict_keys(data: Dict, required_keys: List[str]) -> bool:
        """
        Validate that dictionary contains required keys
        
        Args:
            data: Dictionary to validate
            required_keys: List of required keys
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If required keys are missing
        """
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")
        
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            raise ValidationError(f"Missing required keys: {', '.join(missing_keys)}")
        
        return True
    
    @staticmethod
    def validate_portfolio_allocation(allocations: Dict[str, float]) -> bool:
        """
        Validate portfolio allocation percentages
        
        Args:
            allocations: Dictionary of symbol -> allocation percentage
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If allocations are invalid
        """
        if not isinstance(allocations, dict):
            raise ValidationError("Allocations must be a dictionary")
        
        total = sum(allocations.values())
        
        if abs(total - 1.0) > 0.01:  # Allow small floating point errors
            raise ValidationError(f"Total allocation must equal 100% (got {total*100:.2f}%)")
        
        for symbol, allocation in allocations.items():
            if allocation < 0 or allocation > 1:
                raise ValidationError(f"Allocation for {symbol} must be between 0 and 1")
        
        return True
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """
        Sanitize string input
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Remove control characters
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        # Trim whitespace
        value = value.strip()
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def sanitize_symbol(symbol: str) -> str:
        """
        Sanitize and format trading symbol
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Sanitized symbol
        """
        # Convert to uppercase and remove whitespace
        symbol = symbol.upper().strip()
        
        # Remove any non-alphanumeric characters
        symbol = re.sub(r'[^A-Z0-9]', '', symbol)
        
        # Ensure it ends with USDT
        if not symbol.endswith('USDT'):
            symbol += 'USDT'
        
        return symbol


class TradeValidator:
    """Validate trade parameters"""
    
    @staticmethod
    def validate_trade_params(
        symbol: str,
        side: str,
        price: float,
        quantity: float,
        score: int
    ) -> bool:
        """
        Validate all trade parameters
        
        Args:
            symbol: Trading symbol
            side: Trade side
            price: Price
            quantity: Quantity
            score: Trading score
        
        Returns:
            True if all valid
        
        Raises:
            ValidationError: If any parameter is invalid
        """
        Validator.validate_symbol(symbol)
        Validator.validate_trade_side(side)
        Validator.validate_price(price)
        Validator.validate_quantity(quantity)
        Validator.validate_score(score)
        
        return True
    
    @staticmethod
    def validate_stop_loss_take_profit(
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        side: str
    ) -> bool:
        """
        Validate stop-loss and take-profit levels
        
        Args:
            entry_price: Entry price
            stop_loss: Stop-loss price
            take_profit: Take-profit price
            side: Trade side
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If levels are invalid
        """
        Validator.validate_price(entry_price)
        Validator.validate_price(stop_loss)
        Validator.validate_price(take_profit)
        Validator.validate_trade_side(side)
        
        if side == 'BUY':
            if stop_loss >= entry_price:
                raise ValidationError("Stop-loss must be below entry price for BUY")
            
            if take_profit <= entry_price:
                raise ValidationError("Take-profit must be above entry price for BUY")
        
        elif side == 'SELL':
            if stop_loss <= entry_price:
                raise ValidationError("Stop-loss must be above entry price for SELL")
            
            if take_profit >= entry_price:
                raise ValidationError("Take-profit must be below entry price for SELL")
        
        return True
    
    @staticmethod
    def validate_position_size(
        position_value: float,
        portfolio_value: float,
        max_position_pct: float = 0.25
    ) -> bool:
        """
        Validate position size
        
        Args:
            position_value: Position value in USDT
            portfolio_value: Total portfolio value
            max_position_pct: Maximum position size as percentage
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If position size is invalid
        """
        if position_value <= 0:
            raise ValidationError("Position value must be positive")
        
        if portfolio_value <= 0:
            raise ValidationError("Portfolio value must be positive")
        
        position_pct = position_value / portfolio_value
        
        if position_pct > max_position_pct:
            raise ValidationError(
                f"Position size ({position_pct*100:.1f}%) exceeds maximum "
                f"({max_position_pct*100:.1f}%)"
            )
        
        return True


class DataIntegrityChecker:
    """Check data integrity and consistency"""
    
    @staticmethod
    def check_price_data(prices: List[float]) -> bool:
        """
        Check price data for anomalies
        
        Args:
            prices: List of prices
        
        Returns:
            True if data looks valid
        
        Raises:
            ValidationError: If data integrity issues found
        """
        if not prices:
            raise ValidationError("Price data is empty")
        
        if len(prices) < 2:
            raise ValidationError("Insufficient price data")
        
        # Check for negative or zero prices
        if any(p <= 0 for p in prices):
            raise ValidationError("Found negative or zero prices")
        
        # Check for unrealistic jumps (>50% in one candle)
        for i in range(1, len(prices)):
            change = abs((prices[i] - prices[i-1]) / prices[i-1])
            if change > 0.5:
                raise ValidationError(
                    f"Unrealistic price jump detected: {change*100:.1f}% at index {i}"
                )
        
        return True
    
    @staticmethod
    def check_volume_data(volumes: List[float]) -> bool:
        """
        Check volume data for anomalies
        
        Args:
            volumes: List of volumes
        
        Returns:
            True if data looks valid
        
        Raises:
            ValidationError: If data integrity issues found
        """
        if not volumes:
            raise ValidationError("Volume data is empty")
        
        # Check for negative volumes
        if any(v < 0 for v in volumes):
            raise ValidationError("Found negative volumes")
        
        # Check for all-zero volumes
        if all(v == 0 for v in volumes):
            raise ValidationError("All volumes are zero")
        
        return True
    
    @staticmethod
    def check_indicator_data(indicators: Dict[str, float]) -> bool:
        """
        Check technical indicator data
        
        Args:
            indicators: Dictionary of indicator values
        
        Returns:
            True if data looks valid
        
        Raises:
            ValidationError: If data integrity issues found
        """
        # RSI should be 0-100
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi < 0 or rsi > 100:
                raise ValidationError(f"RSI value {rsi} is out of range (0-100)")
        
        # Stochastic should be 0-100
        if 'stoch_k' in indicators:
            stoch = indicators['stoch_k']
            if stoch < 0 or stoch > 100:
                raise ValidationError(f"Stochastic value {stoch} is out of range (0-100)")
        
        return True
