"""
Position Sizing Module
Calculates position sizes based on classification (SILVER, GOLD, DIAMOND) with 10x fixed leverage
"""
from typing import Dict, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class PositionSize:
    """Position size calculation result"""
    classification: str
    base_percentage: float
    leverage: int
    effective_position: float
    position_value: float
    quantity: float
    risk_per_trade: float
    stop_loss_pct: float
    take_profit_pct: float
    details: dict


class PositionSizer:
    """Calculate position sizes with 10x fixed leverage"""
    
    def __init__(self, config=None):
        """Initialize position sizer"""
        self.config = config
        self.leverage = 10  # Fixed 10x leverage
        
        # Position sizing parameters
        self.silver_params = {
            'base_percentage': 0.10,  # 10% of capital
            'effective_position': 1.0,  # 100% (10% × 10x)
            'risk_per_trade': 0.025,  # 2.5% average
            'stop_loss_pct': 0.025,  # 2.5% average
            'take_profit_pct': 0.09,  # 9% average
        }
        
        self.gold_params = {
            'base_percentage': 0.15,  # 15% of capital
            'effective_position': 1.5,  # 150% (15% × 10x)
            'risk_per_trade': 0.035,  # 3.5% average
            'stop_loss_pct': 0.03,  # 3% average
            'take_profit_pct': 0.135,  # 13.5% average
        }
        
        self.diamond_params = {
            'base_percentage': 0.20,  # 20% of capital
            'effective_position': 2.0,  # 200% (20% × 10x)
            'risk_per_trade': 0.045,  # 4.5% average
            'stop_loss_pct': 0.025,  # 2.5% average
            'take_profit_pct': 0.175,  # 17.5% average
        }
    
    def calculate_position_size(
        self,
        classification: str,
        capital: float,
        current_price: float,
        atr: Optional[float] = None
    ) -> PositionSize:
        """
        Calculate position size based on classification
        
        Args:
            classification: 'SILVER', 'GOLD', or 'DIAMOND'
            capital: Total available capital
            current_price: Current asset price
            atr: Average True Range for dynamic stop-loss (optional)
        
        Returns:
            PositionSize object with all calculations
        """
        # Get parameters for classification
        if classification == "SILVER":
            params = self.silver_params
        elif classification == "GOLD":
            params = self.gold_params
        elif classification == "DIAMOND":
            params = self.diamond_params
        else:
            raise ValueError(f"Invalid classification: {classification}")
        
        # Calculate position value
        base_amount = capital * params['base_percentage']
        position_value = base_amount * self.leverage
        
        # Calculate quantity
        quantity = position_value / current_price
        
        # Adjust stop-loss if ATR provided
        if atr is not None:
            # Dynamic stop-loss: 2 × ATR
            atr_stop_pct = (atr * 2) / current_price
            stop_loss_pct = max(params['stop_loss_pct'], atr_stop_pct)
        else:
            stop_loss_pct = params['stop_loss_pct']
        
        # Calculate actual risk per trade
        risk_per_trade = params['base_percentage'] * stop_loss_pct * self.leverage
        
        return PositionSize(
            classification=classification,
            base_percentage=params['base_percentage'],
            leverage=self.leverage,
            effective_position=params['effective_position'],
            position_value=position_value,
            quantity=quantity,
            risk_per_trade=risk_per_trade,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=params['take_profit_pct'],
            details={
                'base_amount': base_amount,
                'capital': capital,
                'current_price': current_price,
                'atr': atr,
                'params': params
            }
        )
    
    def calculate_stop_loss_price(self, entry_price: float, stop_loss_pct: float, side: str = 'long') -> float:
        """
        Calculate stop-loss price
        
        Args:
            entry_price: Entry price
            stop_loss_pct: Stop-loss percentage (decimal)
            side: 'long' or 'short'
        
        Returns:
            Stop-loss price
        """
        if side == 'long':
            return entry_price * (1 - stop_loss_pct)
        else:
            return entry_price * (1 + stop_loss_pct)
    
    def calculate_take_profit_price(self, entry_price: float, take_profit_pct: float, side: str = 'long') -> float:
        """
        Calculate take-profit price
        
        Args:
            entry_price: Entry price
            take_profit_pct: Take-profit percentage (decimal)
            side: 'long' or 'short'
        
        Returns:
            Take-profit price
        """
        if side == 'long':
            return entry_price * (1 + take_profit_pct)
        else:
            return entry_price * (1 - take_profit_pct)
    
    def calculate_multiple_take_profits(
        self,
        entry_price: float,
        take_profit_pct: float,
        quantity: float,
        side: str = 'long'
    ) -> list:
        """
        Calculate multiple take-profit levels (TP1, TP2, TP3)
        
        Args:
            entry_price: Entry price
            take_profit_pct: Base take-profit percentage
            quantity: Total position quantity
            side: 'long' or 'short'
        
        Returns:
            List of (price, quantity) tuples for each TP level
        """
        # TP1: 40% of position at base TP price
        tp1_price = self.calculate_take_profit_price(entry_price, take_profit_pct * 0.6, side)
        tp1_qty = quantity * 0.4
        
        # TP2: 30% of position at 1.5x base TP price
        tp2_price = self.calculate_take_profit_price(entry_price, take_profit_pct * 1.0, side)
        tp2_qty = quantity * 0.3
        
        # TP3: 30% of position at 2x base TP price
        tp3_price = self.calculate_take_profit_price(entry_price, take_profit_pct * 1.5, side)
        tp3_qty = quantity * 0.3
        
        return [
            {'level': 'TP1', 'price': tp1_price, 'quantity': tp1_qty, 'percentage': 40},
            {'level': 'TP2', 'price': tp2_price, 'quantity': tp2_qty, 'percentage': 30},
            {'level': 'TP3', 'price': tp3_price, 'quantity': tp3_qty, 'percentage': 30}
        ]
    
    def calculate_liquidation_price(
        self,
        entry_price: float,
        leverage: int,
        side: str = 'long',
        maintenance_margin: float = 0.005
    ) -> float:
        """
        Calculate liquidation price for leveraged position
        
        Args:
            entry_price: Entry price
            leverage: Leverage multiplier
            side: 'long' or 'short'
            maintenance_margin: Maintenance margin rate (default 0.5%)
        
        Returns:
            Liquidation price
        """
        if side == 'long':
            # For long: liquidation when price drops to entry × (1 - 1/leverage + maintenance_margin)
            liquidation_price = entry_price * (1 - (1 / leverage) + maintenance_margin)
        else:
            # For short: liquidation when price rises to entry × (1 + 1/leverage - maintenance_margin)
            liquidation_price = entry_price * (1 + (1 / leverage) - maintenance_margin)
        
        return liquidation_price
    
    def check_liquidation_buffer(
        self,
        entry_price: float,
        current_price: float,
        leverage: int,
        side: str = 'long',
        min_buffer: float = 0.04
    ) -> Dict:
        """
        Check if liquidation buffer is maintained
        
        Args:
            entry_price: Entry price
            current_price: Current market price
            leverage: Leverage multiplier
            side: 'long' or 'short'
            min_buffer: Minimum required buffer (default 4%)
        
        Returns:
            Dictionary with liquidation analysis
        """
        liq_price = self.calculate_liquidation_price(entry_price, leverage, side)
        
        if side == 'long':
            distance_to_liquidation = (current_price - liq_price) / current_price
        else:
            distance_to_liquidation = (liq_price - current_price) / current_price
        
        buffer_ok = distance_to_liquidation >= min_buffer
        
        return {
            'liquidation_price': liq_price,
            'current_price': current_price,
            'distance_pct': distance_to_liquidation,
            'min_buffer': min_buffer,
            'buffer_ok': buffer_ok,
            'warning': not buffer_ok
        }
