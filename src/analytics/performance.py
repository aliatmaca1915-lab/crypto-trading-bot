"""
Performance Analytics Module
Calculates performance metrics and generates reports
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class PerformanceMetrics:
    """Performance metrics for trading"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    calmar_ratio: float
    recovery_factor: float


class PerformanceAnalyzer:
    """Analyze trading performance and generate metrics"""
    
    def __init__(self, config=None):
        """Initialize performance analyzer"""
        self.config = config
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def calculate_metrics(
        self,
        trades: List[Dict],
        capital_history: List[float]
    ) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics
        
        Args:
            trades: List of trade dictionaries with PnL
            capital_history: List of capital values over time
        
        Returns:
            PerformanceMetrics object
        """
        if not trades:
            return self._empty_metrics()
        
        # Extract trade PnLs
        trade_pnls = [t.get('realized_pnl', 0) for t in trades if t.get('status') == 'closed']
        
        if not trade_pnls:
            return self._empty_metrics()
        
        # Basic metrics
        total_trades = len(trade_pnls)
        winning_trades = len([pnl for pnl in trade_pnls if pnl > 0])
        losing_trades = len([pnl for pnl in trade_pnls if pnl < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(trade_pnls)
        
        # Win/Loss statistics
        wins = [pnl for pnl in trade_pnls if pnl > 0]
        losses = [pnl for pnl in trade_pnls if pnl < 0]
        
        average_win = np.mean(wins) if wins else 0
        average_loss = np.mean(losses) if losses else 0
        largest_win = max(wins) if wins else 0
        largest_loss = min(losses) if losses else 0
        
        # Profit factor
        total_wins = sum(wins) if wins else 0
        total_losses = abs(sum(losses)) if losses else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Sharpe Ratio
        sharpe_ratio = self._calculate_sharpe_ratio(trade_pnls)
        
        # Sortino Ratio
        sortino_ratio = self._calculate_sortino_ratio(trade_pnls)
        
        # Maximum Drawdown
        max_drawdown = self._calculate_max_drawdown(capital_history)
        
        # Calmar Ratio
        annual_return = total_pnl / capital_history[0] if capital_history else 0
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Recovery Factor
        recovery_factor = total_pnl / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return PerformanceMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            profit_factor=profit_factor,
            average_win=average_win,
            average_loss=average_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            calmar_ratio=calmar_ratio,
            recovery_factor=recovery_factor
        )
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty metrics"""
        return PerformanceMetrics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            total_pnl=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            max_drawdown=0,
            profit_factor=0,
            average_win=0,
            average_loss=0,
            largest_win=0,
            largest_loss=0,
            calmar_ratio=0,
            recovery_factor=0
        )
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            returns: List of trade returns
        
        Returns:
            Sharpe ratio
        """
        if not returns or len(returns) < 2:
            return 0
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        if std_return == 0:
            return 0
        
        # Annualized Sharpe ratio (assuming daily trades)
        sharpe = (mean_return - self.risk_free_rate / 252) / std_return * np.sqrt(252)
        return sharpe
    
    def _calculate_sortino_ratio(self, returns: List[float]) -> float:
        """
        Calculate Sortino Ratio (uses downside deviation only)
        
        Args:
            returns: List of trade returns
        
        Returns:
            Sortino ratio
        """
        if not returns or len(returns) < 2:
            return 0
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        
        # Downside deviation (only negative returns)
        downside_returns = returns_array[returns_array < 0]
        if len(downside_returns) == 0:
            return 0
        
        downside_deviation = np.std(downside_returns)
        
        if downside_deviation == 0:
            return 0
        
        # Annualized Sortino ratio
        sortino = (mean_return - self.risk_free_rate / 252) / downside_deviation * np.sqrt(252)
        return sortino
    
    def _calculate_max_drawdown(self, capital_history: List[float]) -> float:
        """
        Calculate maximum drawdown
        
        Args:
            capital_history: List of capital values over time
        
        Returns:
            Maximum drawdown as percentage
        """
        if not capital_history or len(capital_history) < 2:
            return 0
        
        capital_array = np.array(capital_history)
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(capital_array)
        
        # Calculate drawdown at each point
        drawdown = (capital_array - running_max) / running_max
        
        # Maximum drawdown
        max_dd = np.min(drawdown)
        
        return abs(max_dd)
    
    def generate_daily_report(
        self,
        trades: List[Dict],
        current_capital: float,
        initial_capital: float,
        date: datetime = None
    ) -> Dict:
        """
        Generate daily performance report
        
        Args:
            trades: List of trades for the day
            current_capital: Current capital amount
            initial_capital: Initial capital at day start
            date: Report date
        
        Returns:
            Dictionary with daily report data
        """
        if date is None:
            date = datetime.now()
        
        # Filter trades for the day
        day_trades = [
            t for t in trades
            if t.get('entry_time') and 
            t['entry_time'].date() == date.date()
        ]
        
        # Calculate metrics
        total_trades = len(day_trades)
        closed_trades = [t for t in day_trades if t.get('status') == 'closed']
        
        total_pnl = sum(t.get('realized_pnl', 0) for t in closed_trades)
        
        wins = [t for t in closed_trades if t.get('realized_pnl', 0) > 0]
        losses = [t for t in closed_trades if t.get('realized_pnl', 0) < 0]
        
        win_rate = len(wins) / len(closed_trades) if closed_trades else 0
        
        avg_win = np.mean([t['realized_pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['realized_pnl'] for t in losses]) if losses else 0
        
        largest_win = max([t['realized_pnl'] for t in wins]) if wins else 0
        largest_loss = min([t['realized_pnl'] for t in losses]) if losses else 0
        
        daily_return = (current_capital - initial_capital) / initial_capital if initial_capital > 0 else 0
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'total_trades': total_trades,
            'closed_trades': len(closed_trades),
            'total_pnl': total_pnl,
            'daily_return_pct': daily_return * 100,
            'win_rate': win_rate * 100,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'current_capital': current_capital,
            'capital_change': current_capital - initial_capital
        }
    
    def format_performance_summary(self, metrics: PerformanceMetrics) -> str:
        """
        Format performance metrics summary
        
        Args:
            metrics: PerformanceMetrics object
        
        Returns:
            Formatted string summary
        """
        lines = [
            f"=" * 60,
            f"PERFORMANCE SUMMARY",
            f"=" * 60,
            f"",
            f"Total Trades: {metrics.total_trades}",
            f"  Winning: {metrics.winning_trades} ({metrics.win_rate*100:.1f}%)",
            f"  Losing: {metrics.losing_trades} ({(1-metrics.win_rate)*100:.1f}%)",
            f"",
            f"Profit & Loss:",
            f"  Total P&L: ${metrics.total_pnl:,.2f}",
            f"  Average Win: ${metrics.average_win:,.2f}",
            f"  Average Loss: ${metrics.average_loss:,.2f}",
            f"  Largest Win: ${metrics.largest_win:,.2f}",
            f"  Largest Loss: ${metrics.largest_loss:,.2f}",
            f"  Profit Factor: {metrics.profit_factor:.2f}",
            f"",
            f"Risk Metrics:",
            f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}",
            f"  Sortino Ratio: {metrics.sortino_ratio:.2f}",
            f"  Max Drawdown: {metrics.max_drawdown*100:.2f}%",
            f"  Calmar Ratio: {metrics.calmar_ratio:.2f}",
            f"  Recovery Factor: {metrics.recovery_factor:.2f}",
            f"=" * 60
        ]
        
        return "\n".join(lines)
