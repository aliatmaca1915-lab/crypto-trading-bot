"""
Order Execution Module
Handles both paper trading and real trading execution
"""
import ccxt
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Order:
    """Order representation"""
    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    order_type: str  # 'market', 'limit'
    quantity: float
    price: Optional[float]
    leverage: int
    status: str  # 'pending', 'filled', 'cancelled', 'failed'
    filled_price: Optional[float]
    filled_quantity: float
    timestamp: datetime
    mode: str  # 'paper' or 'real'
    fees: float
    notes: str


class OrderExecutor:
    """Execute orders in paper or real trading mode"""
    
    def __init__(self, config=None, data_provider=None):
        """Initialize order executor"""
        self.config = config
        self.data_provider = data_provider
        self.mode = config.get('mode', 'paper') if config else 'paper'
        
        # Paper trading state
        self.paper_orders = []
        self.paper_positions = []
        
        # Exchange for real trading
        if self.mode == 'real' and data_provider and data_provider.exchange:
            self.exchange = data_provider.exchange
        else:
            self.exchange = None
    
    def execute_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        leverage: int = 10,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Order:
        """
        Execute market order
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            quantity: Order quantity
            leverage: Leverage multiplier
            stop_loss: Optional stop-loss price
            take_profit: Optional take-profit price
        
        Returns:
            Order object
        """
        if self.mode == 'paper':
            return self._execute_paper_market_order(
                symbol, side, quantity, leverage, stop_loss, take_profit
            )
        else:
            return self._execute_real_market_order(
                symbol, side, quantity, leverage, stop_loss, take_profit
            )
    
    def _execute_paper_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        leverage: int,
        stop_loss: Optional[float],
        take_profit: Optional[float]
    ) -> Order:
        """Execute paper trading market order"""
        # Get current price
        current_price = self.data_provider.get_current_price(symbol) if self.data_provider else 45000
        
        # Simulate slippage (0.05%)
        slippage = 0.0005
        if side == 'buy':
            filled_price = current_price * (1 + slippage)
        else:
            filled_price = current_price * (1 - slippage)
        
        # Simulate fees (0.1%)
        fees = quantity * filled_price * 0.001
        
        # Create order
        order = Order(
            order_id=f"PAPER_{uuid.uuid4().hex[:12]}",
            symbol=symbol,
            side=side,
            order_type='market',
            quantity=quantity,
            price=None,
            leverage=leverage,
            status='filled',
            filled_price=filled_price,
            filled_quantity=quantity,
            timestamp=datetime.now(),
            mode='paper',
            fees=fees,
            notes=f"Paper trading order - SL: {stop_loss}, TP: {take_profit}"
        )
        
        # Store order
        self.paper_orders.append(order)
        
        # Create position if buy
        if side == 'buy':
            position = {
                'symbol': symbol,
                'entry_price': filled_price,
                'quantity': quantity,
                'leverage': leverage,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'entry_time': datetime.now(),
                'order_id': order.order_id
            }
            self.paper_positions.append(position)
        
        return order
    
    def _execute_real_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        leverage: int,
        stop_loss: Optional[float],
        take_profit: Optional[float]
    ) -> Order:
        """Execute real trading market order"""
        if not self.exchange:
            raise RuntimeError("Exchange not initialized for real trading")
        
        try:
            # Set leverage
            self.exchange.set_leverage(leverage, symbol)
            
            # Create market order
            order_result = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=quantity
            )
            
            # Create stop-loss order if specified
            if stop_loss and side == 'buy':
                self.exchange.create_order(
                    symbol=symbol,
                    type='stop_market',
                    side='sell',
                    amount=quantity,
                    params={'stopPrice': stop_loss}
                )
            
            # Create take-profit order if specified
            if take_profit and side == 'buy':
                self.exchange.create_order(
                    symbol=symbol,
                    type='take_profit_market',
                    side='sell',
                    amount=quantity,
                    params={'stopPrice': take_profit}
                )
            
            # Create order object
            order = Order(
                order_id=order_result['id'],
                symbol=symbol,
                side=side,
                order_type='market',
                quantity=quantity,
                price=None,
                leverage=leverage,
                status=order_result['status'],
                filled_price=order_result.get('average', order_result.get('price')),
                filled_quantity=order_result.get('filled', quantity),
                timestamp=datetime.now(),
                mode='real',
                fees=order_result.get('fee', {}).get('cost', 0),
                notes=f"Real trading order - SL: {stop_loss}, TP: {take_profit}"
            )
            
            return order
            
        except Exception as e:
            # Create failed order
            order = Order(
                order_id=f"FAILED_{uuid.uuid4().hex[:12]}",
                symbol=symbol,
                side=side,
                order_type='market',
                quantity=quantity,
                price=None,
                leverage=leverage,
                status='failed',
                filled_price=None,
                filled_quantity=0,
                timestamp=datetime.now(),
                mode='real',
                fees=0,
                notes=f"Order failed: {str(e)}"
            )
            
            print(f"Real order execution failed: {e}")
            return order
    
    def close_position(
        self,
        symbol: str,
        quantity: float,
        reason: str = "manual_close"
    ) -> Order:
        """
        Close a position
        
        Args:
            symbol: Trading pair
            quantity: Quantity to close
            reason: Reason for closing
        
        Returns:
            Order object
        """
        # Execute sell order to close
        return self.execute_market_order(
            symbol=symbol,
            side='sell',
            quantity=quantity,
            leverage=1  # Leverage not relevant for closing
        )
    
    def get_open_positions(self) -> List[Dict]:
        """
        Get all open positions
        
        Returns:
            List of position dictionaries
        """
        if self.mode == 'paper':
            return self.paper_positions
        else:
            if not self.exchange:
                return []
            
            try:
                positions = self.exchange.fetch_positions()
                # Filter open positions
                return [p for p in positions if float(p.get('contracts', 0)) > 0]
            except Exception as e:
                print(f"Error fetching positions: {e}")
                return []
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            symbol: Trading pair
        
        Returns:
            True if successful
        """
        if self.mode == 'paper':
            # Find and cancel paper order
            for order in self.paper_orders:
                if order.order_id == order_id and order.status == 'pending':
                    order.status = 'cancelled'
                    return True
            return False
        else:
            if not self.exchange:
                return False
            
            try:
                self.exchange.cancel_order(order_id, symbol)
                return True
            except Exception as e:
                print(f"Error cancelling order: {e}")
                return False
    
    def get_order_status(self, order_id: str, symbol: str) -> Optional[str]:
        """
        Get order status
        
        Args:
            order_id: Order ID
            symbol: Trading pair
        
        Returns:
            Order status or None
        """
        if self.mode == 'paper':
            order = next((o for o in self.paper_orders if o.order_id == order_id), None)
            return order.status if order else None
        else:
            if not self.exchange:
                return None
            
            try:
                order = self.exchange.fetch_order(order_id, symbol)
                return order.get('status')
            except Exception as e:
                print(f"Error fetching order status: {e}")
                return None
