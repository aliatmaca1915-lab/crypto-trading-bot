"""
Database Models
Defines all database tables and relationships
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Trade(Base):
    """Trade execution records"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # BUY or SELL
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    score = Column(Integer, nullable=False)
    classification = Column(String(10), nullable=False)  # SILVER, GOLD, DIAMOND
    is_paper_trade = Column(Boolean, default=True)
    order_id = Column(String(100))
    status = Column(String(20), default='PENDING')  # PENDING, FILLED, CANCELLED, FAILED
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Technical indicators at time of trade
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    bb_upper = Column(Float)
    bb_lower = Column(Float)
    ema_short = Column(Float)
    ema_long = Column(Float)
    volume_24h = Column(Float)
    
    # Risk management
    stop_loss = Column(Float)
    take_profit = Column(Float)
    
    # Performance tracking
    realized_pnl = Column(Float)
    exit_price = Column(Float)
    exit_timestamp = Column(DateTime)
    
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_status', 'status'),
        Index('idx_classification', 'classification'),
    )


class Position(Base):
    """Current open positions"""
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, unique=True)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    total_value = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0.0)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    entry_timestamp = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_position_symbol', 'symbol'),
    )


class MarketData(Base):
    """Historical market data"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Technical indicators
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    ema_short = Column(Float)
    ema_long = Column(Float)
    sma_short = Column(Float)
    sma_long = Column(Float)
    atr = Column(Float)
    stoch_k = Column(Float)
    stoch_d = Column(Float)
    
    __table_args__ = (
        Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )


class Signal(Base):
    """Trading signals generated"""
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    signal_type = Column(String(10), nullable=False)  # BUY or SELL
    score = Column(Integer, nullable=False)
    classification = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Signal components breakdown
    rsi_score = Column(Float)
    macd_score = Column(Float)
    bb_score = Column(Float)
    ema_score = Column(Float)
    stoch_score = Column(Float)
    volume_score = Column(Float)
    trend_score = Column(Float)
    sentiment_score = Column(Float)
    liquidity_score = Column(Float)
    momentum_score = Column(Float)
    
    # Action taken
    action_taken = Column(String(20), default='NONE')  # NONE, TRADE_EXECUTED, IGNORED
    
    __table_args__ = (
        Index('idx_signal_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_signal_score', 'score'),
    )


class Portfolio(Base):
    """Portfolio snapshots"""
    __tablename__ = 'portfolio'
    
    id = Column(Integer, primary_key=True)
    total_value = Column(Float, nullable=False)
    cash_balance = Column(Float, nullable=False)
    invested_value = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_portfolio_timestamp', 'timestamp'),
    )


class MarketSentiment(Base):
    """Market sentiment data"""
    __tablename__ = 'market_sentiment'
    
    id = Column(Integer, primary_key=True)
    fear_greed_index = Column(Integer)  # 0-100
    fear_greed_classification = Column(String(20))  # Extreme Fear, Fear, Neutral, Greed, Extreme Greed
    news_sentiment = Column(Float)  # -1 to 1
    social_sentiment = Column(Float)  # -1 to 1
    overall_sentiment = Column(Float)  # -1 to 1
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_sentiment_timestamp', 'timestamp'),
    )


class Alert(Base):
    """Trading alerts and notifications"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    alert_type = Column(String(50), nullable=False)  # TRADE_EXECUTED, STOP_LOSS, TAKE_PROFIT, etc.
    severity = Column(String(20), nullable=False)  # INFO, WARNING, CRITICAL
    symbol = Column(String(20))
    message = Column(Text, nullable=False)
    details = Column(Text)
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_alert_type_timestamp', 'alert_type', 'timestamp'),
    )


class PredictionModel(Base):
    """AI/ML model predictions"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    model_type = Column(String(50), nullable=False)  # LSTM, PATTERN_RECOGNITION, etc.
    predicted_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    prediction_horizon = Column(String(10), nullable=False)  # 1h, 4h, 1d, etc.
    confidence = Column(Float, nullable=False)  # 0-1
    prediction_direction = Column(String(10))  # UP, DOWN, NEUTRAL
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Actual outcome (filled later)
    actual_price = Column(Float)
    accuracy = Column(Float)
    
    __table_args__ = (
        Index('idx_prediction_symbol_timestamp', 'symbol', 'timestamp'),
    )


class NewsArticle(Base):
    """News articles for sentiment analysis"""
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    source = Column(String(100))
    url = Column(Text)
    published_at = Column(DateTime)
    sentiment_score = Column(Float)  # -1 to 1
    relevance_score = Column(Float)  # 0 to 1
    symbols_mentioned = Column(String(200))  # Comma-separated
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_news_published', 'published_at'),
    )


class CorrelationMatrix(Base):
    """Cryptocurrency correlation data"""
    __tablename__ = 'correlation_matrix'
    
    id = Column(Integer, primary_key=True)
    symbol1 = Column(String(20), nullable=False)
    symbol2 = Column(String(20), nullable=False)
    correlation = Column(Float, nullable=False)  # -1 to 1
    timeframe = Column(String(10), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_correlation_symbols', 'symbol1', 'symbol2'),
    )
