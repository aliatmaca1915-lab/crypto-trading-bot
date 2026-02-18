"""
Backtesting Framework
Test trading strategies on historical data
"""
import pandas as pd
from typing import Dict, List
from datetime import datetime
import numpy as np

from data_fetcher import DataFetcher
from technical_analysis import TechnicalAnalyzer
from scoring_system import ScoringSystem
from risk_management import RiskManager
from config import Config


class Backtester:
    """Backtesting engine for strategy validation"""
    
    def __init__(self, initial_capital: float = None):
        """Initialize backtester"""
        self.config = Config
        self.initial_capital = initial_capital or Config.BACKTEST_INITIAL_CAPITAL
        self.data_fetcher = DataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        self.scoring_system = ScoringSystem()
        self.risk_manager = RiskManager(self.initial_capital)
        
        # Backtesting state
        self.cash = self.initial_capital
        self.positions = {}
        self.trades = []
        self.portfolio_values = []
    
    def run_backtest(self, 
                    symbol: str,
                    timeframe: str = '1h',
                    days: int = 90) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            symbol: Trading pair
            timeframe: Candlestick timeframe
            days: Number of days to backtest
        
        Returns:
            Dict with backtest results
        """
        print(f"Running backtest for {symbol} on {timeframe} timeframe...")
        
        # Fetch historical data
        limit = self._get_limit_for_days(timeframe, days)
        df = self.data_fetcher.fetch_historical_klines(symbol, timeframe, limit=limit)
        
        if df.empty or len(df) < 100:
            return {
                'success': False,
                'error': 'Insufficient historical data'
            }
        
        # Calculate indicators
        df = self.technical_analyzer.calculate_all_indicators(df)
        
        # Reset state
        self.cash = self.initial_capital
        self.positions = {}
        self.trades = []
        self.portfolio_values = []
        
        # Run through each candle
        for i in range(100, len(df)):  # Start after warm-up period
            current_data = df.iloc[:i+1].copy()
            current_price = current_data['close'].iloc[-1]
            current_time = current_data['timestamp'].iloc[-1]
            
            # Calculate portfolio value
            portfolio_value = self._calculate_portfolio_value(current_price)
            self.portfolio_values.append({
                'timestamp': current_time,
                'value': portfolio_value
            })
            
            # Check for exit signals (stop-loss, take-profit)
            self._check_exits(symbol, current_price, current_time)
            
            # Check for entry signals
            if symbol not in self.positions:
                self._check_entry(symbol, current_data, current_price, current_time, portfolio_value)
        
        # Close any remaining positions
        final_price = df['close'].iloc[-1]
        if symbol in self.positions:
            self._close_position(symbol, final_price, df['timestamp'].iloc[-1], 'BACKTEST_END')
        
        # Calculate performance metrics
        results = self._calculate_results(df['timestamp'].iloc[0], df['timestamp'].iloc[-1])
        
        print(f"Backtest complete: {len(self.trades)} trades, Final: ${results['final_value']:.2f}")
        
        return results
    
    def _get_limit_for_days(self, timeframe: str, days: int) -> int:
        """Calculate number of candles needed for given days"""
        candles_per_day = {
            '1m': 1440,
            '5m': 288,
            '15m': 96,
            '1h': 24,
            '4h': 6,
            '1d': 1
        }
        
        return min(candles_per_day.get(timeframe, 24) * days, 1000)
    
    def _calculate_portfolio_value(self, current_price: float) -> float:
        """Calculate total portfolio value"""
        position_value = 0
        
        for symbol, position in self.positions.items():
            position_value += position['quantity'] * current_price
        
        return self.cash + position_value
    
    def _check_entry(self, symbol: str, df: pd.DataFrame, price: float, 
                    timestamp: datetime, portfolio_value: float):
        """Check for entry signal"""
        # Calculate score
        score_result = self.scoring_system.calculate_comprehensive_score(
            symbol, df, price
        )
        
        if not score_result['is_tradeable']:
            return
        
        if score_result['signal'] != 'BUY':
            return
        
        # Calculate position size
        score = score_result['total_score']
        classification = score_result['classification']
        
        position_calc = self.risk_manager.calculate_position_size(
            score, portfolio_value, price
        )
        
        position_value = position_calc['position_value']
        quantity = position_calc['quantity']
        
        # Check if we have enough cash
        if position_value > self.cash:
            return
        
        # Calculate stop-loss and take-profit
        stop_loss = self.risk_manager.calculate_stop_loss(price, 'BUY')
        take_profit = self.risk_manager.calculate_take_profit(price, 'BUY')
        
        # Execute trade
        self.cash -= position_value
        
        self.positions[symbol] = {
            'quantity': quantity,
            'entry_price': price,
            'entry_time': timestamp,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'score': score,
            'classification': classification
        }
        
        self.trades.append({
            'type': 'BUY',
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
            'value': position_value,
            'timestamp': timestamp,
            'score': score,
            'classification': classification
        })
    
    def _check_exits(self, symbol: str, price: float, timestamp: datetime):
        """Check for exit signals"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Check stop-loss
        if price <= position['stop_loss']:
            self._close_position(symbol, price, timestamp, 'STOP_LOSS')
            return
        
        # Check take-profit
        if price >= position['take_profit']:
            self._close_position(symbol, price, timestamp, 'TAKE_PROFIT')
            return
    
    def _close_position(self, symbol: str, price: float, timestamp: datetime, reason: str):
        """Close a position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        quantity = position['quantity']
        entry_price = position['entry_price']
        
        # Calculate proceeds
        proceeds = quantity * price
        self.cash += proceeds
        
        # Calculate PnL
        cost = quantity * entry_price
        pnl = proceeds - cost
        pnl_pct = (pnl / cost) * 100
        
        # Record trade
        self.trades.append({
            'type': 'SELL',
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
            'value': proceeds,
            'timestamp': timestamp,
            'pnl': pnl,
            'pnl_percent': pnl_pct,
            'reason': reason,
            'holding_period': (timestamp - position['entry_time']).total_seconds() / 3600  # hours
        })
        
        # Remove position
        del self.positions[symbol]
    
    def _calculate_results(self, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate backtest performance metrics"""
        final_value = self.cash
        
        # Add value of open positions (shouldn't be any)
        for position in self.positions.values():
            final_value += position['quantity'] * position['entry_price']
        
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        # Trade statistics
        completed_trades = [t for t in self.trades if t['type'] == 'SELL']
        total_trades = len(completed_trades)
        
        if total_trades > 0:
            winning_trades = [t for t in completed_trades if t['pnl'] > 0]
            losing_trades = [t for t in completed_trades if t['pnl'] < 0]
            
            win_rate = (len(winning_trades) / total_trades) * 100
            
            avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
            
            profit_factor = abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)) if losing_trades else 0
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0
        
        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        # Calculate Sharpe ratio
        returns = [t['pnl_percent'] for t in completed_trades]
        sharpe = self.risk_manager.calculate_sharpe_ratio(returns) if returns else 0
        
        return {
            'success': True,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades) if total_trades > 0 else 0,
            'losing_trades': len(losing_trades) if total_trades > 0 else 0,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe,
            'start_date': start_date.isoformat() if isinstance(start_date, datetime) else start_date,
            'end_date': end_date.isoformat() if isinstance(end_date, datetime) else end_date,
            'trades': completed_trades
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.portfolio_values:
            return 0
        
        values = [pv['value'] for pv in self.portfolio_values]
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd * 100
