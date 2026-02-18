"""
Configuration Management Module
Handles all configuration settings and environment variables
"""
import os
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for the trading bot"""
    
    # Trading Mode
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
    
    # API Keys
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    # Trading Parameters
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '10000.0'))
    MIN_SCORE_THRESHOLD = int(os.getenv('MIN_SCORE_THRESHOLD', '60'))
    RISK_PER_TRADE_MIN = float(os.getenv('RISK_PER_TRADE_MIN', '0.10'))
    RISK_PER_TRADE_MAX = float(os.getenv('RISK_PER_TRADE_MAX', '0.25'))
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'trading_bot.db')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'trading_bot.log')
    
    # Cryptocurrencies to Track
    CRYPTOCURRENCIES = [
        'BTCUSDT',   # Bitcoin
        'ETHUSDT',   # Ethereum
        'BNBUSDT',   # Binance Coin
        'XRPUSDT',   # Ripple
        'ADAUSDT',   # Cardano
        'SOLUSDT',   # Solana
        'DOGEUSDT',  # Dogecoin
        'DOTUSDT',   # Polkadot
        'LTCUSDT',   # Litecoin
        'AVAXUSDT',  # Avalanche (Alternative for CARDANO duplicate)
    ]
    
    # Timeframes for Multi-timeframe Analysis
    TIMEFRAMES = ['5m', '15m', '1h', '4h', '1d']
    
    # Technical Indicators Settings
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    BB_PERIOD = 20
    BB_STD = 2
    
    EMA_SHORT = 12
    EMA_LONG = 26
    
    SMA_SHORT = 20
    SMA_LONG = 50
    
    ATR_PERIOD = 14
    
    STOCH_K_PERIOD = 14
    STOCH_D_PERIOD = 3
    
    # Classification Thresholds
    SILVER_MIN = 60
    SILVER_MAX = 80
    GOLD_MIN = 81
    GOLD_MAX = 89
    DIAMOND_MIN = 90
    DIAMOND_MAX = 100
    
    # Position Sizing by Classification
    SILVER_POSITION_SIZE = 0.10  # 10% of portfolio
    GOLD_POSITION_SIZE = 0.15    # 15% of portfolio
    DIAMOND_POSITION_SIZE = 0.25 # 25% of portfolio
    
    # Risk Management
    MAX_DRAWDOWN = 0.20  # 20%
    STOP_LOSS_PERCENT = 0.02  # 2%
    TAKE_PROFIT_PERCENT = 0.05  # 5%
    
    # Order Book Settings
    ORDER_BOOK_DEPTH = 20
    MIN_LIQUIDITY_USDT = 50000  # Minimum liquidity in USDT
    
    # WebSocket Settings
    WEBSOCKET_TIMEOUT = 60
    RECONNECT_DELAY = 5
    
    # Alert Settings
    ENABLE_ALERTS = True
    ALERT_COOLDOWN = 300  # 5 minutes between similar alerts
    
    # Backtesting Settings
    BACKTEST_START_DATE = '2023-01-01'
    BACKTEST_INITIAL_CAPITAL = 10000.0
    
    # AI/ML Settings
    LSTM_LOOKBACK = 60
    LSTM_EPOCHS = 50
    LSTM_BATCH_SIZE = 32
    PREDICTION_CONFIDENCE_THRESHOLD = 0.6
    
    # Market Sentiment
    FEAR_GREED_UPDATE_INTERVAL = 3600  # 1 hour
    NEWS_UPDATE_INTERVAL = 1800  # 30 minutes
    
    @classmethod
    def get_position_size(cls, score: int, portfolio_value: float) -> float:
        """Get position size based on classification score"""
        if cls.DIAMOND_MIN <= score <= cls.DIAMOND_MAX:
            return portfolio_value * cls.DIAMOND_POSITION_SIZE
        elif cls.GOLD_MIN <= score <= cls.GOLD_MAX:
            return portfolio_value * cls.GOLD_POSITION_SIZE
        elif cls.SILVER_MIN <= score <= cls.SILVER_MAX:
            return portfolio_value * cls.SILVER_POSITION_SIZE
        else:
            return 0.0
    
    @classmethod
    def get_classification(cls, score: int) -> str:
        """Get classification based on score"""
        if cls.DIAMOND_MIN <= score <= cls.DIAMOND_MAX:
            return 'DIAMOND'
        elif cls.GOLD_MIN <= score <= cls.GOLD_MAX:
            return 'GOLD'
        elif cls.SILVER_MIN <= score <= cls.SILVER_MAX:
            return 'SILVER'
        else:
            return 'NONE'
    
    @classmethod
    def is_valid_score(cls, score: int) -> bool:
        """Check if score is valid for trading"""
        return score >= cls.MIN_SCORE_THRESHOLD
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        if not cls.PAPER_TRADING:
            if not cls.BINANCE_API_KEY or not cls.BINANCE_API_SECRET:
                raise ValueError("API keys required for real trading mode")
        return True


# Initialize and validate configuration
Config.validate_config()
