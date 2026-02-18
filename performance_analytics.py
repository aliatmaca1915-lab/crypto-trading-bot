"""
Performance Analytics Module
Generates detailed performance reports and statistics
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from tabulate import tabulate

from database import DatabaseManager
from config import Config


class PerformanceAnalytics:
    """Comprehensive performance analytics and reporting"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize performance analytics"""
        self.db = db_manager
        self.config = Config
    
    def generate_daily_report(self) -> Dict:
        """Generate daily performance report"""
        # Get today's trades
        today = datetime.utcnow().date()
        trades = self.db.get_trades(limit=1000)
        
        today_trades = [t for t in trades if t.timestamp.date() == today]
        
        if not today_trades:
            return {
                'date': today.isoformat(),
                'total_trades': 0,
                'total_pnl': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'largest_win': 0,
                'largest_loss': 0
            }
        
        # Calculate metrics
        total_pnl = sum(t.realized_pnl or 0 for t in today_trades if t.realized_pnl)
        winning = [t for t in today_trades if t.realized_pnl and t.realized_pnl > 0]
        losing = [t for t in today_trades if t.realized_pnl and t.realized_pnl < 0]
        
        largest_win = max([t.realized_pnl for t in winning]) if winning else 0
        largest_loss = min([t.realized_pnl for t in losing]) if losing else 0
        
        return {
            'date': today.isoformat(),
            'total_trades': len(today_trades),
            'total_pnl': total_pnl,
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(today_trades) * 100) if today_trades else 0,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'avg_win': np.mean([t.realized_pnl for t in winning]) if winning else 0,
            'avg_loss': np.mean([t.realized_pnl for t in losing]) if losing else 0
        }
    
    def generate_weekly_report(self) -> Dict:
        """Generate weekly performance report"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        trades = self.db.get_trades(limit=10000)
        
        week_trades = [t for t in trades if t.timestamp >= week_ago]
        
        if not week_trades:
            return self._empty_report('weekly')
        
        return self._calculate_period_metrics(week_trades, 'weekly')
    
    def generate_monthly_report(self) -> Dict:
        """Generate monthly performance report"""
        month_ago = datetime.utcnow() - timedelta(days=30)
        trades = self.db.get_trades(limit=10000)
        
        month_trades = [t for t in trades if t.timestamp >= month_ago]
        
        if not month_trades:
            return self._empty_report('monthly')
        
        return self._calculate_period_metrics(month_trades, 'monthly')
    
    def _calculate_period_metrics(self, trades: List, period: str) -> Dict:
        """Calculate metrics for a period"""
        total_trades = len(trades)
        
        # PnL metrics
        completed_trades = [t for t in trades if t.realized_pnl is not None]
        total_pnl = sum(t.realized_pnl for t in completed_trades)
        
        winning = [t for t in completed_trades if t.realized_pnl > 0]
        losing = [t for t in completed_trades if t.realized_pnl < 0]
        
        # Classification breakdown
        silver = [t for t in trades if t.classification == 'SILVER']
        gold = [t for t in trades if t.classification == 'GOLD']
        diamond = [t for t in trades if t.classification == 'DIAMOND']
        
        # Calculate win rates by classification
        silver_wins = len([t for t in silver if t.realized_pnl and t.realized_pnl > 0])
        gold_wins = len([t for t in gold if t.realized_pnl and t.realized_pnl > 0])
        diamond_wins = len([t for t in diamond if t.realized_pnl and t.realized_pnl > 0])
        
        return {
            'period': period,
            'total_trades': total_trades,
            'completed_trades': len(completed_trades),
            'total_pnl': total_pnl,
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(completed_trades) * 100) if completed_trades else 0,
            'avg_win': np.mean([t.realized_pnl for t in winning]) if winning else 0,
            'avg_loss': np.mean([t.realized_pnl for t in losing]) if losing else 0,
            'largest_win': max([t.realized_pnl for t in winning]) if winning else 0,
            'largest_loss': min([t.realized_pnl for t in losing]) if losing else 0,
            'profit_factor': abs(sum(t.realized_pnl for t in winning) / sum(t.realized_pnl for t in losing)) if losing else 0,
            'classification_breakdown': {
                'silver': {'count': len(silver), 'wins': silver_wins, 'win_rate': (silver_wins/len(silver)*100) if silver else 0},
                'gold': {'count': len(gold), 'wins': gold_wins, 'win_rate': (gold_wins/len(gold)*100) if gold else 0},
                'diamond': {'count': len(diamond), 'wins': diamond_wins, 'win_rate': (diamond_wins/len(diamond)*100) if diamond else 0}
            }
        }
    
    def _empty_report(self, period: str) -> Dict:
        """Return empty report"""
        return {
            'period': period,
            'total_trades': 0,
            'total_pnl': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'profit_factor': 0
        }
    
    def get_symbol_performance(self, days: int = 30) -> List[Dict]:
        """Get performance breakdown by symbol"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        trades = self.db.get_trades(limit=10000)
        
        recent_trades = [t for t in trades if t.timestamp >= cutoff]
        
        # Group by symbol
        symbol_data = {}
        
        for trade in recent_trades:
            symbol = trade.symbol
            
            if symbol not in symbol_data:
                symbol_data[symbol] = {
                    'symbol': symbol,
                    'trades': [],
                    'total_pnl': 0,
                    'wins': 0,
                    'losses': 0
                }
            
            symbol_data[symbol]['trades'].append(trade)
            
            if trade.realized_pnl:
                symbol_data[symbol]['total_pnl'] += trade.realized_pnl
                
                if trade.realized_pnl > 0:
                    symbol_data[symbol]['wins'] += 1
                else:
                    symbol_data[symbol]['losses'] += 1
        
        # Calculate metrics
        results = []
        for symbol, data in symbol_data.items():
            total = data['wins'] + data['losses']
            win_rate = (data['wins'] / total * 100) if total > 0 else 0
            
            results.append({
                'symbol': symbol,
                'trades': len(data['trades']),
                'total_pnl': data['total_pnl'],
                'wins': data['wins'],
                'losses': data['losses'],
                'win_rate': win_rate
            })
        
        # Sort by total PnL
        results.sort(key=lambda x: x['total_pnl'], reverse=True)
        
        return results
    
    def get_hourly_performance(self) -> Dict[int, Dict]:
        """Analyze performance by hour of day"""
        trades = self.db.get_trades(limit=10000)
        
        hourly_data = {hour: {'trades': [], 'pnl': 0, 'wins': 0, 'losses': 0} for hour in range(24)}
        
        for trade in trades:
            if not trade.realized_pnl:
                continue
            
            hour = trade.timestamp.hour
            hourly_data[hour]['trades'].append(trade)
            hourly_data[hour]['pnl'] += trade.realized_pnl
            
            if trade.realized_pnl > 0:
                hourly_data[hour]['wins'] += 1
            else:
                hourly_data[hour]['losses'] += 1
        
        # Calculate metrics
        results = {}
        for hour, data in hourly_data.items():
            total = data['wins'] + data['losses']
            results[hour] = {
                'hour': hour,
                'trades': len(data['trades']),
                'total_pnl': data['pnl'],
                'wins': data['wins'],
                'losses': data['losses'],
                'win_rate': (data['wins'] / total * 100) if total > 0 else 0
            }
        
        return results
    
    def get_drawdown_analysis(self) -> Dict:
        """Analyze drawdowns"""
        portfolio_history = self.db.get_portfolio_history(days=90)
        
        if len(portfolio_history) < 2:
            return {
                'max_drawdown': 0,
                'current_drawdown': 0,
                'drawdown_duration_days': 0,
                'recovery_factor': 0
            }
        
        values = [p.total_value for p in portfolio_history]
        
        # Calculate drawdown curve
        peak = values[0]
        max_dd = 0
        max_dd_duration = 0
        current_dd_duration = 0
        
        for i, value in enumerate(values):
            if value > peak:
                peak = value
                current_dd_duration = 0
            else:
                current_dd_duration += 1
            
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
                max_dd_duration = current_dd_duration
        
        # Current drawdown
        current_peak = max(values)
        current_value = values[-1]
        current_dd = (current_peak - current_value) / current_peak if current_peak > 0 else 0
        
        # Recovery factor (profit / max drawdown)
        total_profit = values[-1] - values[0]
        recovery_factor = total_profit / (max_dd * values[0]) if max_dd > 0 else 0
        
        return {
            'max_drawdown': max_dd * 100,
            'max_drawdown_duration_days': max_dd_duration,
            'current_drawdown': current_dd * 100,
            'recovery_factor': recovery_factor
        }
    
    def get_risk_metrics(self) -> Dict:
        """Calculate risk-adjusted performance metrics"""
        portfolio_history = self.db.get_portfolio_history(days=90)
        
        if len(portfolio_history) < 2:
            return {
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'calmar_ratio': 0,
                'var_95': 0
            }
        
        # Calculate returns
        values = [p.total_value for p in portfolio_history]
        returns = np.diff(values) / values[:-1]
        
        # Sharpe ratio
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino = np.mean(returns) / downside_std * np.sqrt(252) if downside_std > 0 else 0
        
        # Calmar ratio (return / max drawdown)
        dd_analysis = self.get_drawdown_analysis()
        total_return = (values[-1] - values[0]) / values[0] * 100
        calmar = total_return / dd_analysis['max_drawdown'] if dd_analysis['max_drawdown'] > 0 else 0
        
        # Value at Risk (95%)
        var_95 = np.percentile(returns, 5) * 100 if len(returns) > 0 else 0
        
        return {
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'var_95': abs(var_95)
        }
    
    def print_daily_report(self):
        """Print formatted daily report"""
        report = self.generate_daily_report()
        
        print("\n" + "="*80)
        print(f"📊 DAILY PERFORMANCE REPORT - {report['date']}")
        print("="*80)
        print(f"\nTrades: {report['total_trades']}")
        print(f"Total PnL: ${report['total_pnl']:+.2f}")
        print(f"Win Rate: {report['win_rate']:.1f}%")
        print(f"Winning Trades: {report['winning_trades']}")
        print(f"Losing Trades: {report['losing_trades']}")
        print(f"Largest Win: ${report['largest_win']:.2f}")
        print(f"Largest Loss: ${report['largest_loss']:.2f}")
        print("="*80 + "\n")
    
    def print_comprehensive_report(self):
        """Print comprehensive performance report"""
        daily = self.generate_daily_report()
        weekly = self.generate_weekly_report()
        monthly = self.generate_monthly_report()
        symbol_perf = self.get_symbol_performance()
        dd_analysis = self.get_drawdown_analysis()
        risk_metrics = self.get_risk_metrics()
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE PERFORMANCE REPORT")
        print("="*80)
        
        # Daily
        print("\n📅 Daily Performance:")
        print(f"  Trades: {daily['total_trades']} | PnL: ${daily['total_pnl']:+.2f} | Win Rate: {daily['win_rate']:.1f}%")
        
        # Weekly
        print("\n📅 Weekly Performance:")
        print(f"  Trades: {weekly['total_trades']} | PnL: ${weekly['total_pnl']:+.2f} | Win Rate: {weekly['win_rate']:.1f}%")
        print(f"  Profit Factor: {weekly['profit_factor']:.2f}")
        
        # Monthly
        print("\n📅 Monthly Performance:")
        print(f"  Trades: {monthly['total_trades']} | PnL: ${monthly['total_pnl']:+.2f} | Win Rate: {monthly['win_rate']:.1f}%")
        print(f"  Avg Win: ${monthly['avg_win']:.2f} | Avg Loss: ${monthly['avg_loss']:.2f}")
        
        # Classification breakdown
        print("\n💎 Classification Performance:")
        for cls, data in monthly['classification_breakdown'].items():
            print(f"  {cls.upper()}: {data['count']} trades | Win Rate: {data['win_rate']:.1f}%")
        
        # Symbol performance
        print("\n📈 Top Performing Symbols:")
        for i, perf in enumerate(symbol_perf[:5], 1):
            print(f"  {i}. {perf['symbol']}: ${perf['total_pnl']:+.2f} | {perf['trades']} trades | {perf['win_rate']:.1f}% WR")
        
        # Risk metrics
        print("\n📊 Risk Metrics:")
        print(f"  Sharpe Ratio: {risk_metrics['sharpe_ratio']:.2f}")
        print(f"  Sortino Ratio: {risk_metrics['sortino_ratio']:.2f}")
        print(f"  Calmar Ratio: {risk_metrics['calmar_ratio']:.2f}")
        print(f"  VaR (95%): {risk_metrics['var_95']:.2f}%")
        
        # Drawdown
        print("\n📉 Drawdown Analysis:")
        print(f"  Max Drawdown: {dd_analysis['max_drawdown']:.2f}%")
        print(f"  Current Drawdown: {dd_analysis['current_drawdown']:.2f}%")
        print(f"  Recovery Factor: {dd_analysis['recovery_factor']:.2f}")
        
        print("\n" + "="*80 + "\n")
