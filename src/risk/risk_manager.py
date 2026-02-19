"""
Risk Management Module
Advanced risk management with dynamic stop-loss, multiple take-profits, and portfolio limits
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np


@dataclass
class RiskCheck:
    """Risk check result"""
    passed: bool
    reason: str
    details: dict


class RiskManager:
    """Comprehensive risk management system"""
    
    def __init__(self, config=None):
        """Initialize risk manager"""
        self.config = config
        self.leverage = 10  # Fixed 10x leverage
        
        # Risk limits
        self.liquidation_buffer_min = 0.03  # 3% minimum
        self.liquidation_buffer_max = 0.05  # 5% maximum
        self.position_limit_per_coin = 0.05  # 5% of capital
        self.daily_loss_limit = 0.05  # 5% of capital
        self.weekly_loss_limit = 0.10  # 10% of capital
        self.max_concurrent_positions = 5
        
        # Track losses
        self.daily_losses = {}
        self.weekly_losses = {}
    
    def check_position_limits(
        self,
        symbol: str,
        new_position_value: float,
        current_capital: float,
        existing_positions: List[Dict]
    ) -> RiskCheck:
        """
        Check if position size is within limits
        
        Args:
            symbol: Trading pair symbol
            new_position_value: Value of new position
            current_capital: Current available capital
            existing_positions: List of existing positions
        
        Returns:
            RiskCheck result
        """
        # Check per-coin limit
        position_pct = new_position_value / current_capital
        if position_pct > self.position_limit_per_coin:
            return RiskCheck(
                passed=False,
                reason=f"Position size exceeds {self.position_limit_per_coin * 100}% limit per coin",
                details={
                    'position_pct': position_pct,
                    'limit': self.position_limit_per_coin,
                    'position_value': new_position_value,
                    'capital': current_capital
                }
            )
        
        # Check max concurrent positions
        if len(existing_positions) >= self.max_concurrent_positions:
            return RiskCheck(
                passed=False,
                reason=f"Maximum {self.max_concurrent_positions} concurrent positions reached",
                details={
                    'current_positions': len(existing_positions),
                    'max_positions': self.max_concurrent_positions
                }
            )
        
        return RiskCheck(
            passed=True,
            reason="Position limits check passed",
            details={
                'position_pct': position_pct,
                'limit': self.position_limit_per_coin
            }
        )
    
    def check_loss_limits(
        self,
        current_capital: float,
        initial_capital: float,
        period: str = 'daily'
    ) -> RiskCheck:
        """
        Check if daily/weekly loss limits are exceeded
        
        Args:
            current_capital: Current capital amount
            initial_capital: Initial capital at period start
            period: 'daily' or 'weekly'
        
        Returns:
            RiskCheck result
        """
        loss = initial_capital - current_capital
        loss_pct = loss / initial_capital if initial_capital > 0 else 0
        
        if period == 'daily':
            limit = self.daily_loss_limit
            limit_name = "Daily"
        else:
            limit = self.weekly_loss_limit
            limit_name = "Weekly"
        
        if loss_pct > limit:
            return RiskCheck(
                passed=False,
                reason=f"{limit_name} loss limit of {limit * 100}% exceeded",
                details={
                    'loss': loss,
                    'loss_pct': loss_pct,
                    'limit': limit,
                    'current_capital': current_capital,
                    'initial_capital': initial_capital
                }
            )
        
        return RiskCheck(
            passed=True,
            reason=f"{limit_name} loss limit check passed",
            details={
                'loss_pct': loss_pct,
                'limit': limit
            }
        )
    
    def check_liquidation_buffer(
        self,
        entry_price: float,
        current_price: float,
        leverage: int = 10,
        side: str = 'long'
    ) -> RiskCheck:
        """
        Check if liquidation buffer is maintained (3-5%)
        
        Args:
            entry_price: Entry price
            current_price: Current market price
            leverage: Leverage multiplier
            side: 'long' or 'short'
        
        Returns:
            RiskCheck result
        """
        # Calculate liquidation price
        if side == 'long':
            liq_price = entry_price * (1 - (1 / leverage) + 0.005)
            buffer = (current_price - liq_price) / current_price
        else:
            liq_price = entry_price * (1 + (1 / leverage) - 0.005)
            buffer = (liq_price - current_price) / current_price
        
        if buffer < self.liquidation_buffer_min:
            return RiskCheck(
                passed=False,
                reason=f"Liquidation buffer below minimum {self.liquidation_buffer_min * 100}%",
                details={
                    'buffer': buffer,
                    'min_buffer': self.liquidation_buffer_min,
                    'liquidation_price': liq_price,
                    'current_price': current_price
                }
            )
        
        return RiskCheck(
            passed=True,
            reason="Liquidation buffer check passed",
            details={
                'buffer': buffer,
                'min_buffer': self.liquidation_buffer_min,
                'liquidation_price': liq_price
            }
        )
    
    def calculate_dynamic_stop_loss(
        self,
        entry_price: float,
        atr: float,
        support_level: Optional[float] = None,
        base_stop_pct: float = 0.025
    ) -> Dict:
        """
        Calculate dynamic stop-loss using ATR and support levels
        
        Args:
            entry_price: Entry price
            atr: Average True Range
            support_level: Optional support level
            base_stop_pct: Base stop-loss percentage
        
        Returns:
            Dictionary with stop-loss calculations
        """
        # ATR-based stop-loss (2 × ATR)
        atr_stop_price = entry_price - (atr * 2)
        atr_stop_pct = (entry_price - atr_stop_price) / entry_price
        
        # Choose appropriate stop-loss
        if support_level and support_level < entry_price:
            # Use support level if it's reasonable
            support_stop_pct = (entry_price - support_level) / entry_price
            if support_stop_pct < 0.05:  # Max 5% for support-based stop
                stop_price = support_level
                stop_pct = support_stop_pct
                method = "support_level"
            else:
                stop_price = atr_stop_price
                stop_pct = atr_stop_pct
                method = "atr_based"
        else:
            # Use ATR-based or base stop-loss
            stop_pct = max(base_stop_pct, atr_stop_pct)
            stop_price = entry_price * (1 - stop_pct)
            method = "atr_based" if atr_stop_pct > base_stop_pct else "base_percentage"
        
        return {
            'stop_price': stop_price,
            'stop_pct': stop_pct,
            'method': method,
            'atr': atr,
            'atr_stop_price': atr_stop_price,
            'support_level': support_level
        }
    
    def calculate_trailing_stop(
        self,
        entry_price: float,
        current_price: float,
        highest_price: float,
        trailing_pct: float = 0.02
    ) -> Dict:
        """
        Calculate trailing stop-loss
        
        Args:
            entry_price: Original entry price
            current_price: Current market price
            highest_price: Highest price since entry
            trailing_pct: Trailing percentage (default 2%)
        
        Returns:
            Dictionary with trailing stop calculations
        """
        # Trailing stop is % below highest price
        trailing_stop_price = highest_price * (1 - trailing_pct)
        
        # Only activate if in profit
        in_profit = current_price > entry_price
        should_trail = in_profit and (highest_price - entry_price) / entry_price > 0.03  # At least 3% profit
        
        # Stop-loss level
        if should_trail:
            stop_price = max(trailing_stop_price, entry_price)
        else:
            stop_price = entry_price * (1 - 0.025)  # Default 2.5% stop
        
        return {
            'stop_price': stop_price,
            'trailing_active': should_trail,
            'highest_price': highest_price,
            'current_price': current_price,
            'profit_pct': (current_price - entry_price) / entry_price if entry_price > 0 else 0
        }
    
    def check_correlation_limits(
        self,
        symbol: str,
        existing_positions: List[Dict],
        correlation_threshold: float = 0.7
    ) -> RiskCheck:
        """
        Check correlation-based position limits
        
        Args:
            symbol: New symbol to trade
            existing_positions: List of existing positions
            correlation_threshold: Maximum correlation allowed
        
        Returns:
            RiskCheck result
        """
        # Simplified correlation check
        # In production, fetch actual correlation data
        
        # Check if too many correlated positions (same base currency)
        base_currency = symbol.split('/')[0]
        correlated_count = sum(
            1 for pos in existing_positions 
            if pos.get('symbol', '').split('/')[0] == base_currency
        )
        
        if correlated_count >= 2:
            return RiskCheck(
                passed=False,
                reason=f"Too many correlated positions with {base_currency}",
                details={
                    'symbol': symbol,
                    'correlated_count': correlated_count,
                    'threshold': 2
                }
            )
        
        return RiskCheck(
            passed=True,
            reason="Correlation check passed",
            details={'symbol': symbol, 'correlated_count': correlated_count}
        )
    
    def comprehensive_risk_check(
        self,
        symbol: str,
        position_value: float,
        current_capital: float,
        initial_capital: float,
        existing_positions: List[Dict],
        entry_price: float,
        current_price: float
    ) -> RiskCheck:
        """
        Run comprehensive risk checks before opening position
        
        Returns:
            RiskCheck result (fails if any check fails)
        """
        checks = []
        
        # Position limits
        check1 = self.check_position_limits(symbol, position_value, current_capital, existing_positions)
        checks.append(check1)
        
        # Daily loss limit
        check2 = self.check_loss_limits(current_capital, initial_capital, 'daily')
        checks.append(check2)
        
        # Liquidation buffer
        check3 = self.check_liquidation_buffer(entry_price, current_price)
        checks.append(check3)
        
        # Correlation limits
        check4 = self.check_correlation_limits(symbol, existing_positions)
        checks.append(check4)
        
        # Check if any failed
        failed_checks = [c for c in checks if not c.passed]
        
        if failed_checks:
            return RiskCheck(
                passed=False,
                reason=f"Failed {len(failed_checks)} risk check(s): " + 
                       ", ".join(c.reason for c in failed_checks),
                details={'failed_checks': [c.__dict__ for c in failed_checks]}
            )
        
        return RiskCheck(
            passed=True,
            reason="All risk checks passed",
            details={'checks_passed': len(checks)}
        )
