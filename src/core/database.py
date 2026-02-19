"""
Database Management System
Handles persistence for trades, signals, and performance metrics
"""
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
import json


Base = declarative_base()


class Trade(Base):
    """Trade execution record"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # 'buy' or 'sell'
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    quantity = Column(Float, nullable=False)
    leverage = Column(Integer, nullable=False)
    position_size = Column(Float, nullable=False)
    classification = Column(String(20), nullable=False)  # 'silver', 'gold', 'diamond'
    score = Column(Integer, nullable=False)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    realized_pnl = Column(Float)
    fees = Column(Float)
    entry_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    exit_time = Column(DateTime)
    status = Column(String(20), nullable=False, default='open')  # 'open', 'closed', 'cancelled'
    mode = Column(String(10), nullable=False)  # 'paper' or 'real'
    notes = Column(Text)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'leverage': self.leverage,
            'position_size': self.position_size,
            'classification': self.classification,
            'score': self.score,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'realized_pnl': self.realized_pnl,
            'fees': self.fees,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'status': self.status,
            'mode': self.mode,
            'notes': self.notes
        }


class Signal(Base):
    """Trading signal record"""
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    score = Column(Integer, nullable=False)
    classification = Column(String(20))
    signal_type = Column(String(20), nullable=False)  # 'buy', 'sell', 'hold'
    technical_score = Column(Float)
    market_intelligence_score = Column(Float)
    advanced_signals_score = Column(Float)
    ml_confidence = Column(Float)
    timeframe_alignment = Column(Integer)
    executed = Column(Boolean, default=False)
    details = Column(Text)  # JSON string with detailed breakdown
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'score': self.score,
            'classification': self.classification,
            'signal_type': self.signal_type,
            'technical_score': self.technical_score,
            'market_intelligence_score': self.market_intelligence_score,
            'advanced_signals_score': self.advanced_signals_score,
            'ml_confidence': self.ml_confidence,
            'timeframe_alignment': self.timeframe_alignment,
            'executed': self.executed,
            'details': json.loads(self.details) if self.details else None
        }


class PerformanceMetric(Base):
    """Performance metrics record"""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    period_type = Column(String(20), nullable=False)  # 'daily', 'weekly', 'monthly'
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float)
    total_pnl = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    max_drawdown = Column(Float)
    profit_factor = Column(Float)
    average_win = Column(Float)
    average_loss = Column(Float)
    largest_win = Column(Float)
    largest_loss = Column(Float)
    current_capital = Column(Float)
    mode = Column(String(10), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'period_type': self.period_type,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'total_pnl': self.total_pnl,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'max_drawdown': self.max_drawdown,
            'profit_factor': self.profit_factor,
            'average_win': self.average_win,
            'average_loss': self.average_loss,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
            'current_capital': self.current_capital,
            'mode': self.mode
        }


class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager"""
        if db_path is None:
            # Default to data/trading_bot.db
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "trading_bot.db"
        
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine
        self.engine = create_engine(f'sqlite:///{db_path}')
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create session maker
        self.SessionMaker = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionMaker()
    
    def save_trade(self, trade_data: dict):
        """Save trade to database"""
        session = self.get_session()
        try:
            trade = Trade(**trade_data)
            session.add(trade)
            session.commit()
            return trade.id
        finally:
            session.close()
    
    def update_trade(self, trade_id: int, updates: dict):
        """Update existing trade"""
        session = self.get_session()
        try:
            trade = session.query(Trade).filter_by(id=trade_id).first()
            if trade:
                for key, value in updates.items():
                    setattr(trade, key, value)
                session.commit()
        finally:
            session.close()
    
    def save_signal(self, signal_data: dict):
        """Save signal to database"""
        session = self.get_session()
        try:
            signal = Signal(**signal_data)
            session.add(signal)
            session.commit()
            return signal.id
        finally:
            session.close()
    
    def save_performance_metric(self, metric_data: dict):
        """Save performance metric to database"""
        session = self.get_session()
        try:
            metric = PerformanceMetric(**metric_data)
            session.add(metric)
            session.commit()
            return metric.id
        finally:
            session.close()
    
    def get_open_trades(self, mode: str = None):
        """Get all open trades"""
        session = self.get_session()
        try:
            query = session.query(Trade).filter_by(status='open')
            if mode:
                query = query.filter_by(mode=mode)
            return [trade.to_dict() for trade in query.all()]
        finally:
            session.close()
    
    def get_recent_signals(self, limit: int = 100):
        """Get recent signals"""
        session = self.get_session()
        try:
            signals = session.query(Signal).order_by(Signal.timestamp.desc()).limit(limit).all()
            return [signal.to_dict() for signal in signals]
        finally:
            session.close()
    
    def get_performance_history(self, period_type: str = None, limit: int = 30):
        """Get performance history"""
        session = self.get_session()
        try:
            query = session.query(PerformanceMetric)
            if period_type:
                query = query.filter_by(period_type=period_type)
            metrics = query.order_by(PerformanceMetric.timestamp.desc()).limit(limit).all()
            return [metric.to_dict() for metric in metrics]
        finally:
            session.close()


# Global database instance
_db_instance = None


def get_database(db_path: str = None) -> DatabaseManager:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager(db_path)
    return _db_instance
