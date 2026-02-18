"""
Database Manager
Handles all database operations and connections
"""
from sqlalchemy import create_engine, desc, and_, or_, func
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd

from models import (
    Base, Trade, Position, MarketData, Signal, Portfolio,
    MarketSentiment, Alert, PredictionModel, NewsArticle, CorrelationMatrix
)
from config import Config


class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or Config.DATABASE_PATH
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self._create_tables()
    
    def _create_tables(self):
        """Create all tables if they don't exist"""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Trade Operations
    def save_trade(self, trade_data: Dict[str, Any]) -> Trade:
        """Save a new trade"""
        with self.session_scope() as session:
            trade = Trade(**trade_data)
            session.add(trade)
            session.flush()
            return trade
    
    def update_trade(self, trade_id: int, updates: Dict[str, Any]):
        """Update an existing trade"""
        with self.session_scope() as session:
            session.query(Trade).filter(Trade.id == trade_id).update(updates)
    
    def get_trades(self, symbol: str = None, limit: int = 100) -> List[Trade]:
        """Get recent trades"""
        with self.session_scope() as session:
            query = session.query(Trade).order_by(desc(Trade.timestamp))
            if symbol:
                query = query.filter(Trade.symbol == symbol)
            return query.limit(limit).all()
    
    def get_trade_statistics(self) -> Dict[str, Any]:
        """Get overall trade statistics"""
        with self.session_scope() as session:
            total_trades = session.query(func.count(Trade.id)).scalar()
            winning_trades = session.query(func.count(Trade.id)).filter(
                Trade.realized_pnl > 0
            ).scalar()
            losing_trades = session.query(func.count(Trade.id)).filter(
                Trade.realized_pnl < 0
            ).scalar()
            
            total_pnl = session.query(func.sum(Trade.realized_pnl)).scalar() or 0
            
            return {
                'total_trades': total_trades or 0,
                'winning_trades': winning_trades or 0,
                'losing_trades': losing_trades or 0,
                'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                'total_pnl': total_pnl
            }
    
    # Position Operations
    def save_position(self, position_data: Dict[str, Any]) -> Position:
        """Save or update a position"""
        with self.session_scope() as session:
            position = session.query(Position).filter(
                Position.symbol == position_data['symbol']
            ).first()
            
            if position:
                for key, value in position_data.items():
                    setattr(position, key, value)
            else:
                position = Position(**position_data)
                session.add(position)
            
            session.flush()
            return position
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol"""
        with self.session_scope() as session:
            return session.query(Position).filter(Position.symbol == symbol).first()
    
    def get_all_positions(self) -> List[Position]:
        """Get all open positions"""
        with self.session_scope() as session:
            return session.query(Position).all()
    
    def close_position(self, symbol: str):
        """Close a position"""
        with self.session_scope() as session:
            session.query(Position).filter(Position.symbol == symbol).delete()
    
    # Market Data Operations
    def save_market_data(self, data: Dict[str, Any]) -> MarketData:
        """Save market data"""
        with self.session_scope() as session:
            market_data = MarketData(**data)
            session.add(market_data)
            session.flush()
            return market_data
    
    def get_market_data(self, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        """Get market data as DataFrame"""
        with self.session_scope() as session:
            data = session.query(MarketData).filter(
                and_(
                    MarketData.symbol == symbol,
                    MarketData.timeframe == timeframe
                )
            ).order_by(desc(MarketData.timestamp)).limit(limit).all()
            
            if not data:
                return pd.DataFrame()
            
            return pd.DataFrame([{
                'timestamp': d.timestamp,
                'open': d.open_price,
                'high': d.high_price,
                'low': d.low_price,
                'close': d.close_price,
                'volume': d.volume,
                'rsi': d.rsi,
                'macd': d.macd,
                'macd_signal': d.macd_signal,
                'bb_upper': d.bb_upper,
                'bb_lower': d.bb_lower,
                'ema_short': d.ema_short,
                'ema_long': d.ema_long,
            } for d in reversed(data)])
    
    # Signal Operations
    def save_signal(self, signal_data: Dict[str, Any]) -> Signal:
        """Save a trading signal"""
        with self.session_scope() as session:
            signal = Signal(**signal_data)
            session.add(signal)
            session.flush()
            return signal
    
    def get_recent_signals(self, symbol: str = None, limit: int = 50) -> List[Signal]:
        """Get recent signals"""
        with self.session_scope() as session:
            query = session.query(Signal).order_by(desc(Signal.timestamp))
            if symbol:
                query = query.filter(Signal.symbol == symbol)
            return query.limit(limit).all()
    
    # Portfolio Operations
    def save_portfolio_snapshot(self, portfolio_data: Dict[str, Any]) -> Portfolio:
        """Save portfolio snapshot"""
        with self.session_scope() as session:
            portfolio = Portfolio(**portfolio_data)
            session.add(portfolio)
            session.flush()
            return portfolio
    
    def get_latest_portfolio(self) -> Optional[Portfolio]:
        """Get latest portfolio snapshot"""
        with self.session_scope() as session:
            return session.query(Portfolio).order_by(desc(Portfolio.timestamp)).first()
    
    def get_portfolio_history(self, days: int = 30) -> List[Portfolio]:
        """Get portfolio history"""
        with self.session_scope() as session:
            start_date = datetime.utcnow() - timedelta(days=days)
            return session.query(Portfolio).filter(
                Portfolio.timestamp >= start_date
            ).order_by(Portfolio.timestamp).all()
    
    # Market Sentiment Operations
    def save_sentiment(self, sentiment_data: Dict[str, Any]) -> MarketSentiment:
        """Save market sentiment data"""
        with self.session_scope() as session:
            sentiment = MarketSentiment(**sentiment_data)
            session.add(sentiment)
            session.flush()
            return sentiment
    
    def get_latest_sentiment(self) -> Optional[MarketSentiment]:
        """Get latest market sentiment"""
        with self.session_scope() as session:
            return session.query(MarketSentiment).order_by(
                desc(MarketSentiment.timestamp)
            ).first()
    
    # Alert Operations
    def save_alert(self, alert_data: Dict[str, Any]) -> Alert:
        """Save an alert"""
        with self.session_scope() as session:
            alert = Alert(**alert_data)
            session.add(alert)
            session.flush()
            return alert
    
    def get_unread_alerts(self, limit: int = 50) -> List[Alert]:
        """Get unread alerts"""
        with self.session_scope() as session:
            return session.query(Alert).filter(
                Alert.is_read == False
            ).order_by(desc(Alert.timestamp)).limit(limit).all()
    
    def mark_alert_read(self, alert_id: int):
        """Mark alert as read"""
        with self.session_scope() as session:
            session.query(Alert).filter(Alert.id == alert_id).update({'is_read': True})
    
    # Prediction Operations
    def save_prediction(self, prediction_data: Dict[str, Any]) -> PredictionModel:
        """Save AI prediction"""
        with self.session_scope() as session:
            prediction = PredictionModel(**prediction_data)
            session.add(prediction)
            session.flush()
            return prediction
    
    def get_recent_predictions(self, symbol: str = None, limit: int = 20) -> List[PredictionModel]:
        """Get recent predictions"""
        with self.session_scope() as session:
            query = session.query(PredictionModel).order_by(desc(PredictionModel.timestamp))
            if symbol:
                query = query.filter(PredictionModel.symbol == symbol)
            return query.limit(limit).all()
    
    # News Operations
    def save_news(self, news_data: Dict[str, Any]) -> NewsArticle:
        """Save news article"""
        with self.session_scope() as session:
            # Check if article already exists
            existing = session.query(NewsArticle).filter(
                NewsArticle.url == news_data.get('url')
            ).first()
            
            if existing:
                return existing
            
            news = NewsArticle(**news_data)
            session.add(news)
            session.flush()
            return news
    
    def get_recent_news(self, hours: int = 24, limit: int = 50) -> List[NewsArticle]:
        """Get recent news"""
        with self.session_scope() as session:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            return session.query(NewsArticle).filter(
                NewsArticle.published_at >= start_time
            ).order_by(desc(NewsArticle.published_at)).limit(limit).all()
    
    # Correlation Operations
    def save_correlation(self, correlation_data: Dict[str, Any]) -> CorrelationMatrix:
        """Save correlation data"""
        with self.session_scope() as session:
            correlation = CorrelationMatrix(**correlation_data)
            session.add(correlation)
            session.flush()
            return correlation
    
    def get_correlation(self, symbol1: str, symbol2: str, timeframe: str) -> Optional[float]:
        """Get correlation between two symbols"""
        with self.session_scope() as session:
            corr = session.query(CorrelationMatrix).filter(
                and_(
                    or_(
                        and_(CorrelationMatrix.symbol1 == symbol1, CorrelationMatrix.symbol2 == symbol2),
                        and_(CorrelationMatrix.symbol1 == symbol2, CorrelationMatrix.symbol2 == symbol1)
                    ),
                    CorrelationMatrix.timeframe == timeframe
                )
            ).order_by(desc(CorrelationMatrix.timestamp)).first()
            
            return corr.correlation if corr else None
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data to keep database size manageable"""
        with self.session_scope() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Keep trades and important data, but clean up market data
            session.query(MarketData).filter(
                MarketData.timestamp < cutoff_date
            ).delete()
            
            session.query(NewsArticle).filter(
                NewsArticle.published_at < cutoff_date
            ).delete()
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        with self.session_scope() as session:
            return {
                'trades': session.query(func.count(Trade.id)).scalar() or 0,
                'positions': session.query(func.count(Position.id)).scalar() or 0,
                'market_data_records': session.query(func.count(MarketData.id)).scalar() or 0,
                'signals': session.query(func.count(Signal.id)).scalar() or 0,
                'alerts': session.query(func.count(Alert.id)).scalar() or 0,
                'predictions': session.query(func.count(PredictionModel.id)).scalar() or 0,
            }
