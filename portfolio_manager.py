"""
Portfolio Management Module
Handles portfolio balancing, correlation analysis, and performance tracking
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta

from database import DatabaseManager
from config import Config


class PortfolioManager:
    """Manages portfolio balancing and correlation analysis"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize portfolio manager"""
        self.db = db_manager
        self.config = Config
    
    def calculate_correlation_matrix(self, symbols: List[str], timeframe: str = '1h', days: int = 30) -> pd.DataFrame:
        """Calculate correlation matrix between cryptocurrencies"""
        # Get price data for all symbols
        price_data = {}
        
        for symbol in symbols:
            df = self.db.get_market_data(symbol, timeframe, limit=days * 24)
            if not df.empty:
                price_data[symbol] = df.set_index('timestamp')['close']
        
        if not price_data:
            return pd.DataFrame()
        
        # Create DataFrame from price data
        df = pd.DataFrame(price_data)
        
        # Calculate correlation
        correlation_matrix = df.corr()
        
        # Save correlations to database
        for symbol1 in symbols:
            for symbol2 in symbols:
                if symbol1 != symbol2 and symbol1 in correlation_matrix.index and symbol2 in correlation_matrix.columns:
                    corr_value = correlation_matrix.loc[symbol1, symbol2]
                    
                    self.db.save_correlation({
                        'symbol1': symbol1,
                        'symbol2': symbol2,
                        'correlation': float(corr_value),
                        'timeframe': timeframe,
                        'timestamp': datetime.utcnow()
                    })
        
        return correlation_matrix
    
    def get_diversification_score(self, positions: List[Dict]) -> float:
        """Calculate diversification score (0-1)"""
        if not positions or len(positions) < 2:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        total_value = sum(p['total_value'] for p in positions)
        
        if total_value == 0:
            return 0.0
        
        # Calculate market shares
        shares = [(p['total_value'] / total_value) ** 2 for p in positions]
        hhi = sum(shares)
        
        # Convert HHI to diversification score (1 = perfectly diversified, 0 = concentrated)
        # HHI ranges from 1/n (perfectly diversified) to 1 (single asset)
        n = len(positions)
        min_hhi = 1 / n
        max_hhi = 1
        
        if max_hhi == min_hhi:
            return 1.0
        
        diversification = (max_hhi - hhi) / (max_hhi - min_hhi)
        return max(0, min(1, diversification))
    
    def rebalance_portfolio(self, target_allocation: Dict[str, float] = None) -> List[Dict]:
        """Generate rebalancing recommendations"""
        positions = self.db.get_all_positions()
        
        if not positions:
            return []
        
        # Calculate current allocation
        total_value = sum(p.total_value for p in positions)
        current_allocation = {p.symbol: p.total_value / total_value for p in positions}
        
        # Use equal weight if no target provided
        if not target_allocation:
            target_weight = 1 / len(positions)
            target_allocation = {p.symbol: target_weight for p in positions}
        
        # Generate rebalancing actions
        recommendations = []
        
        for symbol, target_weight in target_allocation.items():
            current_weight = current_allocation.get(symbol, 0)
            weight_diff = target_weight - current_weight
            
            if abs(weight_diff) > 0.05:  # 5% threshold
                value_diff = weight_diff * total_value
                
                recommendations.append({
                    'symbol': symbol,
                    'action': 'BUY' if weight_diff > 0 else 'SELL',
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'weight_diff': weight_diff,
                    'value_diff': value_diff
                })
        
        return recommendations
    
    def calculate_portfolio_performance(self, days: int = 30) -> Dict[str, any]:
        """Calculate portfolio performance metrics"""
        # Get portfolio history
        portfolio_history = self.db.get_portfolio_history(days)
        
        if len(portfolio_history) < 2:
            return {
                'total_return': 0,
                'annualized_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0
            }
        
        # Extract values
        values = [p.total_value for p in portfolio_history]
        initial_value = values[0]
        final_value = values[-1]
        
        # Calculate returns
        returns = np.diff(values) / values[:-1]
        
        # Total return
        total_return = (final_value - initial_value) / initial_value
        
        # Annualized return
        days_actual = len(portfolio_history)
        annualized_return = ((1 + total_return) ** (365 / days_actual)) - 1
        
        # Volatility (annualized)
        volatility = np.std(returns) * np.sqrt(365)
        
        # Sharpe ratio
        risk_free_rate = 0.02  # 2% annual
        excess_return = annualized_return - risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        # Max drawdown
        peak = values[0]
        max_drawdown = 0
        
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Get trade statistics
        trade_stats = self.db.get_trade_statistics()
        
        return {
            'total_return': total_return * 100,
            'annualized_return': annualized_return * 100,
            'volatility': volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,
            'win_rate': trade_stats.get('win_rate', 0),
            'total_trades': trade_stats.get('total_trades', 0),
            'winning_trades': trade_stats.get('winning_trades', 0),
            'losing_trades': trade_stats.get('losing_trades', 0)
        }
    
    def save_portfolio_snapshot(self, portfolio_value: float, cash_balance: float, 
                               invested_value: float, unrealized_pnl: float, 
                               realized_pnl: float):
        """Save current portfolio snapshot"""
        trade_stats = self.db.get_trade_statistics()
        
        portfolio_data = {
            'total_value': portfolio_value,
            'cash_balance': cash_balance,
            'invested_value': invested_value,
            'unrealized_pnl': unrealized_pnl,
            'realized_pnl': realized_pnl,
            'total_pnl': unrealized_pnl + realized_pnl,
            'total_trades': trade_stats.get('total_trades', 0),
            'winning_trades': trade_stats.get('winning_trades', 0),
            'losing_trades': trade_stats.get('losing_trades', 0),
            'win_rate': trade_stats.get('win_rate', 0),
            'max_drawdown': 0,  # Would need historical tracking
            'timestamp': datetime.utcnow()
        }
        
        self.db.save_portfolio_snapshot(portfolio_data)
    
    def get_position_summary(self) -> List[Dict]:
        """Get summary of all positions"""
        positions = self.db.get_all_positions()
        
        summary = []
        total_value = sum(p.total_value for p in positions)
        
        for position in positions:
            allocation = (position.total_value / total_value * 100) if total_value > 0 else 0
            unrealized_pnl = position.unrealized_pnl or 0
            unrealized_pnl_pct = (unrealized_pnl / position.total_value * 100) if position.total_value > 0 else 0
            
            summary.append({
                'symbol': position.symbol,
                'quantity': position.quantity,
                'entry_price': position.entry_price,
                'current_price': position.current_price,
                'total_value': position.total_value,
                'allocation': allocation,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_percent': unrealized_pnl_pct,
                'stop_loss': position.stop_loss,
                'take_profit': position.take_profit,
                'entry_timestamp': position.entry_timestamp.isoformat() if position.entry_timestamp else None
            })
        
        return summary
