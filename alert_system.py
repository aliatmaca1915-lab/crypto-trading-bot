"""
Alert and Notification System
Handles real-time alerts for trading events
"""
from typing import Dict
from datetime import datetime, timedelta
from colorama import Fore, Style, init

from database import DatabaseManager
from config import Config

# Initialize colorama
init(autoreset=True)


class AlertSystem:
    """Alert and notification system"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize alert system"""
        self.db = db_manager
        self.config = Config
        self.last_alert_time = {}
    
    def send_alert(self, 
                   alert_type: str,
                   severity: str,
                   message: str,
                   symbol: str = None,
                   details: str = None,
                   force: bool = False) -> bool:
        """
        Send an alert
        
        Args:
            alert_type: Type of alert (TRADE_EXECUTED, STOP_LOSS, etc.)
            severity: INFO, WARNING, or CRITICAL
            message: Alert message
            symbol: Optional symbol
            details: Optional additional details
            force: Force alert even if cooldown hasn't passed
        
        Returns:
            True if alert was sent, False if suppressed
        """
        if not self.config.ENABLE_ALERTS:
            return False
        
        # Check cooldown (unless forced)
        if not force:
            alert_key = f"{alert_type}_{symbol}" if symbol else alert_type
            if alert_key in self.last_alert_time:
                time_since_last = (datetime.utcnow() - self.last_alert_time[alert_key]).total_seconds()
                if time_since_last < self.config.ALERT_COOLDOWN:
                    return False  # Suppress duplicate alert
        
        # Save alert to database
        alert_data = {
            'alert_type': alert_type,
            'severity': severity,
            'symbol': symbol,
            'message': message,
            'details': details,
            'is_read': False,
            'timestamp': datetime.utcnow()
        }
        
        self.db.save_alert(alert_data)
        
        # Print to console with color
        self._print_alert(alert_type, severity, message, symbol)
        
        # Update last alert time
        alert_key = f"{alert_type}_{symbol}" if symbol else alert_type
        self.last_alert_time[alert_key] = datetime.utcnow()
        
        return True
    
    def _print_alert(self, alert_type: str, severity: str, message: str, symbol: str = None):
        """Print colored alert to console"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        # Choose color based on severity
        if severity == 'CRITICAL':
            color = Fore.RED
            icon = '🔴'
        elif severity == 'WARNING':
            color = Fore.YELLOW
            icon = '⚠️'
        else:
            color = Fore.GREEN
            icon = '✓'
        
        # Format message
        symbol_str = f"[{symbol}]" if symbol else ""
        print(f"{color}{icon} [{timestamp}] {alert_type} {symbol_str}: {message}{Style.RESET_ALL}")
    
    def alert_trade_executed(self, trade_result: Dict):
        """Alert for trade execution"""
        symbol = trade_result.get('symbol', 'UNKNOWN')
        side = trade_result.get('side', 'UNKNOWN')
        price = trade_result.get('price', 0)
        quantity = trade_result.get('quantity', 0)
        classification = trade_result.get('classification', 'UNKNOWN')
        score = trade_result.get('score', 0)
        
        message = f"{side} {quantity:.6f} @ ${price:.2f} | {classification} ({score} points)"
        details = f"Total: ${trade_result.get('total_value', 0):.2f} | SL: ${trade_result.get('stop_loss', 0):.2f} | TP: ${trade_result.get('take_profit', 0):.2f}"
        
        self.send_alert(
            'TRADE_EXECUTED',
            'INFO',
            message,
            symbol,
            details,
            force=True
        )
    
    def alert_stop_loss(self, symbol: str, entry_price: float, exit_price: float, pnl: float):
        """Alert for stop-loss trigger"""
        message = f"Stop-loss triggered | Entry: ${entry_price:.2f} | Exit: ${exit_price:.2f} | PnL: ${pnl:.2f}"
        
        self.send_alert(
            'STOP_LOSS',
            'WARNING',
            message,
            symbol,
            force=True
        )
    
    def alert_take_profit(self, symbol: str, entry_price: float, exit_price: float, pnl: float):
        """Alert for take-profit trigger"""
        message = f"Take-profit triggered | Entry: ${entry_price:.2f} | Exit: ${exit_price:.2f} | PnL: ${pnl:.2f}"
        
        self.send_alert(
            'TAKE_PROFIT',
            'INFO',
            message,
            symbol,
            force=True
        )
    
    def alert_high_score_signal(self, symbol: str, score: int, classification: str, signal: str):
        """Alert for high-scoring trading signal"""
        if score >= 85:
            message = f"High-score signal detected | Score: {score} ({classification}) | Signal: {signal}"
            
            self.send_alert(
                'HIGH_SCORE_SIGNAL',
                'INFO',
                message,
                symbol
            )
    
    def alert_risk_limit(self, message: str):
        """Alert for risk limit violations"""
        self.send_alert(
            'RISK_LIMIT',
            'WARNING',
            message,
            force=True
        )
    
    def alert_system_error(self, error_message: str):
        """Alert for system errors"""
        self.send_alert(
            'SYSTEM_ERROR',
            'CRITICAL',
            error_message,
            force=True
        )
    
    def alert_market_sentiment(self, sentiment_data: Dict):
        """Alert for extreme market sentiment"""
        fg_value = sentiment_data.get('fear_greed_value', 50)
        fg_class = sentiment_data.get('fear_greed_classification', 'Neutral')
        
        # Alert on extreme fear or greed
        if fg_value <= 20:
            message = f"Extreme Fear detected | F&G Index: {fg_value} ({fg_class})"
            self.send_alert('MARKET_SENTIMENT', 'WARNING', message)
        elif fg_value >= 80:
            message = f"Extreme Greed detected | F&G Index: {fg_value} ({fg_class})"
            self.send_alert('MARKET_SENTIMENT', 'WARNING', message)
    
    def get_unread_alerts(self, limit: int = 50) -> list:
        """Get unread alerts"""
        return self.db.get_unread_alerts(limit)
    
    def mark_alerts_read(self, alert_ids: list = None):
        """Mark alerts as read"""
        if alert_ids:
            for alert_id in alert_ids:
                self.db.mark_alert_read(alert_id)
        else:
            # Mark all unread as read
            unread = self.get_unread_alerts()
            for alert in unread:
                self.db.mark_alert_read(alert.id)
