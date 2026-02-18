"""
Risk Management System
Handles position sizing, stop-loss, take-profit, and portfolio risk
"""
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime

from config import Config


class RiskManager:
    """Risk management for trading operations"""
    
    def __init__(self, initial_capital: float = None):
        """Initialize risk manager"""
        self.config = Config
        self.initial_capital = initial_capital or Config.INITIAL_CAPITAL
        self.max_drawdown = Config.MAX_DRAWDOWN
    
    def calculate_position_size(self, 
                               score: int,
                               portfolio_value: float,
                               price: float,
                               volatility: float = 0.02) -> Dict[str, float]:
        """
        Calculate position size based on score classification and risk
        
        Returns:
            Dict with quantity, position_value, risk_amount
        """
        # Get base position size from classification
        base_position_value = self.config.get_position_size(score, portfolio_value)
        
        if base_position_value == 0:
            return {
                'quantity': 0,
                'position_value': 0,
                'risk_amount': 0,
                'classification': 'NONE'
            }
        
        # Adjust for volatility
        volatility_adjustment = self._calculate_volatility_adjustment(volatility)
        adjusted_position_value = base_position_value * volatility_adjustment
        
        # Calculate quantity
        quantity = adjusted_position_value / price
        
        # Calculate risk amount (potential loss with stop-loss)
        risk_amount = adjusted_position_value * self.config.STOP_LOSS_PERCENT
        
        classification = self.config.get_classification(score)
        
        return {
            'quantity': quantity,
            'position_value': adjusted_position_value,
            'risk_amount': risk_amount,
            'classification': classification,
            'volatility_adjustment': volatility_adjustment
        }
    
    def _calculate_volatility_adjustment(self, volatility: float) -> float:
        """Adjust position size based on volatility"""
        # Lower volatility = larger position, higher volatility = smaller position
        base_volatility = 0.02  # 2% baseline
        
        if volatility <= 0:
            return 1.0
        
        adjustment = base_volatility / volatility
        
        # Limit adjustment between 0.5 and 1.5
        return max(0.5, min(1.5, adjustment))
    
    def calculate_stop_loss(self, 
                           entry_price: float,
                           side: str,
                           atr: float = None) -> float:
        """Calculate stop-loss price"""
        if atr and atr > 0:
            # ATR-based stop-loss (more dynamic)
            stop_distance = atr * 2
        else:
            # Percentage-based stop-loss
            stop_distance = entry_price * self.config.STOP_LOSS_PERCENT
        
        if side == 'BUY':
            return entry_price - stop_distance
        else:  # SELL
            return entry_price + stop_distance
    
    def calculate_take_profit(self,
                             entry_price: float,
                             side: str,
                             atr: float = None,
                             risk_reward_ratio: float = 2.5) -> float:
        """Calculate take-profit price"""
        if atr and atr > 0:
            # ATR-based take-profit
            profit_distance = atr * 2 * risk_reward_ratio
        else:
            # Percentage-based take-profit
            profit_distance = entry_price * self.config.TAKE_PROFIT_PERCENT
        
        if side == 'BUY':
            return entry_price + profit_distance
        else:  # SELL
            return entry_price - profit_distance
    
    def check_risk_limits(self,
                         portfolio_value: float,
                         open_positions_value: float,
                         new_position_value: float) -> Tuple[bool, str]:
        """Check if new position violates risk limits"""
        # Check if total exposure exceeds limit
        total_exposure = (open_positions_value + new_position_value) / portfolio_value
        
        if total_exposure > 0.8:  # Max 80% exposure
            return False, "Total exposure would exceed 80% of portfolio"
        
        # Check single position size
        position_pct = new_position_value / portfolio_value
        if position_pct > 0.25:  # Max 25% per position
            return False, "Single position exceeds 25% of portfolio"
        
        # Check drawdown
        drawdown = (self.initial_capital - portfolio_value) / self.initial_capital
        if drawdown > self.max_drawdown:
            return False, f"Portfolio drawdown ({drawdown:.1%}) exceeds maximum ({self.max_drawdown:.1%})"
        
        return True, "Risk limits OK"
    
    def calculate_portfolio_risk(self,
                                positions: list,
                                portfolio_value: float) -> Dict[str, float]:
        """Calculate overall portfolio risk metrics"""
        if not positions:
            return {
                'total_exposure': 0,
                'total_risk': 0,
                'risk_percentage': 0,
                'concentration_risk': 0
            }
        
        total_position_value = sum(p['total_value'] for p in positions)
        total_risk = sum(p.get('risk_amount', 0) for p in positions)
        
        # Calculate concentration (largest position as % of total)
        if positions:
            largest_position = max(p['total_value'] for p in positions)
            concentration = largest_position / total_position_value if total_position_value > 0 else 0
        else:
            concentration = 0
        
        return {
            'total_exposure': total_position_value,
            'exposure_percentage': (total_position_value / portfolio_value) * 100 if portfolio_value > 0 else 0,
            'total_risk': total_risk,
            'risk_percentage': (total_risk / portfolio_value) * 100 if portfolio_value > 0 else 0,
            'concentration_risk': concentration * 100,
            'number_of_positions': len(positions)
        }
    
    def should_close_position(self,
                             current_price: float,
                             entry_price: float,
                             stop_loss: float,
                             take_profit: float,
                             side: str) -> Tuple[bool, str]:
        """Determine if position should be closed"""
        if side == 'BUY':
            if current_price <= stop_loss:
                return True, 'STOP_LOSS'
            elif current_price >= take_profit:
                return True, 'TAKE_PROFIT'
        else:  # SELL
            if current_price >= stop_loss:
                return True, 'STOP_LOSS'
            elif current_price <= take_profit:
                return True, 'TAKE_PROFIT'
        
        return False, 'HOLD'
    
    def calculate_drawdown(self,
                          current_value: float,
                          peak_value: float) -> float:
        """Calculate drawdown from peak"""
        if peak_value <= 0:
            return 0
        
        drawdown = (peak_value - current_value) / peak_value
        return max(0, drawdown)
    
    def calculate_sharpe_ratio(self,
                              returns: list,
                              risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not returns or len(returns) < 2:
            return 0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate
        
        if len(excess_returns) == 0 or np.std(excess_returns) == 0:
            return 0
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return sharpe
    
    def calculate_sortino_ratio(self,
                               returns: list,
                               risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio (focuses on downside risk)"""
        if not returns or len(returns) < 2:
            return 0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - (risk_free_rate / 252)
        
        # Calculate downside deviation
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return 0
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0
        
        sortino = np.mean(excess_returns) / downside_std * np.sqrt(252)
        return sortino
    
    def calculate_var(self,
                     returns: list,
                     confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk (VaR)"""
        if not returns or len(returns) < 10:
            return 0
        
        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence_level) * 100)
        return abs(var)
    
    def calculate_kelly_criterion(self,
                                  win_rate: float,
                                  avg_win: float,
                                  avg_loss: float) -> float:
        """Calculate Kelly Criterion for optimal position sizing"""
        if avg_loss == 0 or win_rate == 0 or win_rate == 1:
            return 0
        
        win_loss_ratio = abs(avg_win / avg_loss)
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Use half-Kelly for safety
        return max(0, min(kelly * 0.5, 0.25))  # Cap at 25%
    
    def get_risk_assessment(self, score: int, volatility: float, market_sentiment: float = 0) -> Dict[str, any]:
        """Get comprehensive risk assessment for a trade"""
        classification = self.config.get_classification(score)
        
        # Base risk level
        if classification == 'DIAMOND':
            base_risk = 'LOW'
            risk_score = 3
        elif classification == 'GOLD':
            base_risk = 'MODERATE'
            risk_score = 5
        elif classification == 'SILVER':
            base_risk = 'MODERATE_HIGH'
            risk_score = 6
        else:
            base_risk = 'HIGH'
            risk_score = 8
        
        # Adjust for volatility
        if volatility > 0.05:  # High volatility
            risk_score += 2
            base_risk = 'HIGH'
        elif volatility > 0.03:
            risk_score += 1
        
        # Adjust for market sentiment
        if market_sentiment < -0.5:  # Extreme fear
            risk_score += 1
        elif market_sentiment > 0.5:  # Extreme greed
            risk_score += 1
        
        risk_score = min(risk_score, 10)
        
        return {
            'classification': classification,
            'risk_level': base_risk,
            'risk_score': risk_score,
            'volatility': volatility,
            'recommendation': 'PROCEED' if risk_score < 7 else 'CAUTION' if risk_score < 9 else 'AVOID'
        }
