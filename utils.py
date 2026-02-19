"""
Utilities Module
Helper functions and utilities for the trading bot
"""
import json
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from functools import wraps
import hashlib


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry a function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
                    else:
                        raise last_exception
            
            raise last_exception
        
        return wrapper
    return decorator


def measure_execution_time(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"[PERF] {func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format amount as currency string"""
    if currency == 'USD':
        return f"${amount:,.2f}"
    elif currency == 'BTC':
        return f"{amount:.8f} BTC"
    elif currency == 'ETH':
        return f"{amount:.6f} ETH"
    else:
        return f"{amount:.2f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage string"""
    return f"{value:+.{decimals}f}%"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    
    return ((new_value - old_value) / old_value) * 100


def truncate_number(value: float, decimals: int) -> float:
    """Truncate number to specified decimal places"""
    multiplier = 10 ** decimals
    return int(value * multiplier) / multiplier


def round_to_tick_size(value: float, tick_size: float) -> float:
    """Round value to nearest tick size"""
    return round(value / tick_size) * tick_size


def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format"""
    if not symbol:
        return False
    
    # Check if ends with USDT
    if not symbol.endswith('USDT'):
        return False
    
    # Check length
    if len(symbol) < 6 or len(symbol) > 12:
        return False
    
    # Check if uppercase
    if symbol != symbol.upper():
        return False
    
    return True


def sanitize_symbol(symbol: str) -> str:
    """Sanitize and format symbol"""
    symbol = symbol.upper().strip()
    
    # Add USDT if not present
    if not symbol.endswith('USDT'):
        symbol += 'USDT'
    
    return symbol


def timestamp_to_datetime(timestamp: int) -> datetime:
    """Convert millisecond timestamp to datetime"""
    return datetime.fromtimestamp(timestamp / 1000)


def datetime_to_timestamp(dt: datetime) -> int:
    """Convert datetime to millisecond timestamp"""
    return int(dt.timestamp() * 1000)


def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours ago"
    else:
        return f"{int(seconds / 86400)} days ago"


def parse_timeframe_to_seconds(timeframe: str) -> int:
    """Parse timeframe string to seconds"""
    mapping = {
        '1m': 60,
        '5m': 300,
        '15m': 900,
        '30m': 1800,
        '1h': 3600,
        '4h': 14400,
        '1d': 86400,
        '1w': 604800
    }
    
    return mapping.get(timeframe, 3600)


def calculate_lot_size(position_value: float, price: float, min_qty: float = 0.001, max_qty: float = 1000) -> float:
    """Calculate appropriate lot size for position"""
    quantity = position_value / price
    
    # Apply min/max constraints
    quantity = max(min_qty, min(quantity, max_qty))
    
    # Round to 6 decimal places
    return round(quantity, 6)


def calculate_value(quantity: float, price: float) -> float:
    """Calculate total value of position"""
    return quantity * price


def generate_trade_id() -> str:
    """Generate unique trade ID"""
    timestamp = int(time.time() * 1000)
    random_str = str(timestamp)
    
    hash_obj = hashlib.sha256(random_str.encode())
    trade_id = hash_obj.hexdigest()[:16]
    
    return f"TRADE_{trade_id.upper()}"


def is_market_open() -> bool:
    """Check if crypto market is open (always true for crypto)"""
    return True


def get_market_hours() -> Dict[str, str]:
    """Get market hours (24/7 for crypto)"""
    return {
        'open': '00:00',
        'close': '23:59',
        'timezone': 'UTC',
        'is_24_7': True
    }


def validate_api_key(api_key: str, api_secret: str) -> bool:
    """Validate API key format"""
    if not api_key or not api_secret:
        return False
    
    if len(api_key) < 32 or len(api_secret) < 32:
        return False
    
    return True


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    if denominator == 0:
        return default
    
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max"""
    return max(min_value, min(value, max_value))


def calculate_compound_return(returns: List[float]) -> float:
    """Calculate compound return from list of returns"""
    if not returns:
        return 0.0
    
    compound = 1.0
    for r in returns:
        compound *= (1 + r / 100)
    
    return (compound - 1) * 100


def calculate_moving_average(values: List[float], period: int) -> float:
    """Calculate simple moving average"""
    if not values or len(values) < period:
        return 0.0
    
    return sum(values[-period:]) / period


def calculate_exponential_moving_average(values: List[float], period: int) -> float:
    """Calculate exponential moving average"""
    if not values or len(values) < period:
        return 0.0
    
    multiplier = 2 / (period + 1)
    ema = values[0]
    
    for value in values[1:]:
        ema = (value * multiplier) + (ema * (1 - multiplier))
    
    return ema


def calculate_standard_deviation(values: List[float]) -> float:
    """Calculate standard deviation"""
    if not values or len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    
    return variance ** 0.5


def detect_outliers(values: List[float], threshold: float = 2.0) -> List[int]:
    """Detect outliers using z-score method"""
    if not values or len(values) < 3:
        return []
    
    mean = sum(values) / len(values)
    std_dev = calculate_standard_deviation(values)
    
    if std_dev == 0:
        return []
    
    outlier_indices = []
    
    for i, value in enumerate(values):
        z_score = abs((value - mean) / std_dev)
        if z_score > threshold:
            outlier_indices.append(i)
    
    return outlier_indices


def smooth_data(values: List[float], window: int = 3) -> List[float]:
    """Smooth data using moving average"""
    if not values or len(values) < window:
        return values
    
    smoothed = []
    
    for i in range(len(values)):
        if i < window - 1:
            smoothed.append(values[i])
        else:
            avg = sum(values[i-window+1:i+1]) / window
            smoothed.append(avg)
    
    return smoothed


def normalize_values(values: List[float], min_val: float = 0, max_val: float = 1) -> List[float]:
    """Normalize values to specified range"""
    if not values:
        return []
    
    data_min = min(values)
    data_max = max(values)
    
    if data_max == data_min:
        return [min_val] * len(values)
    
    range_val = data_max - data_min
    target_range = max_val - min_val
    
    normalized = []
    for value in values:
        norm_value = ((value - data_min) / range_val) * target_range + min_val
        normalized.append(norm_value)
    
    return normalized


def create_summary_dict(data: Dict[str, Any], precision: int = 2) -> Dict[str, str]:
    """Create formatted summary dictionary"""
    summary = {}
    
    for key, value in data.items():
        if isinstance(value, float):
            summary[key] = f"{value:.{precision}f}"
        elif isinstance(value, int):
            summary[key] = str(value)
        elif isinstance(value, datetime):
            summary[key] = value.isoformat()
        else:
            summary[key] = str(value)
    
    return summary


def save_to_json(data: Any, filename: str) -> bool:
    """Save data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return False


def load_from_json(filename: str) -> Any:
    """Load data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading from JSON: {e}")
        return None


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    
    for d in dicts:
        result.update(d)
    
    return result


def filter_dict_by_keys(d: Dict, keys: List[str]) -> Dict:
    """Filter dictionary by specified keys"""
    return {k: v for k, v in d.items() if k in keys}


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """Flatten nested dictionary"""
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def allow_call(self) -> bool:
        """Check if call is allowed"""
        now = time.time()
        
        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        # Check if we can make another call
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def wait_if_needed(self):
        """Wait if rate limit is reached"""
        while not self.allow_call():
            time.sleep(0.1)


class Cache:
    """Simple in-memory cache with expiration"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self.cache = {}
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set cache value"""
        if ttl is None:
            ttl = self.default_ttl
        
        expiry = time.time() + ttl
        self.cache[key] = {
            'value': value,
            'expiry': expiry
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get cache value"""
        if key not in self.cache:
            return default
        
        entry = self.cache[key]
        
        # Check if expired
        if time.time() > entry['expiry']:
            del self.cache[key]
            return default
        
        return entry['value']
    
    def delete(self, key: str):
        """Delete cache entry"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}
    
    def cleanup_expired(self):
        """Remove expired entries"""
        now = time.time()
        expired_keys = [k for k, v in self.cache.items() if now > v['expiry']]
        
        for key in expired_keys:
            del self.cache[key]
