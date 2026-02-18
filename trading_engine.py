"""
Core Trading Engine
Handles order execution, trade management, and position tracking
"""
from typing import Dict, Optional, Tuple
from datetime import datetime
import time

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    print("Warning: python-binance not available. Trading features will use paper mode only.")

from config import Config
from database import DatabaseManager
from risk_management import RiskManager


class TradingEngine:
    """Core trading engine for order execution and management"""
    
    def __init__(self, db_manager: DatabaseManager, paper_trading: bool = None):
        """Initialize trading engine"""
        self.config = Config
        self.db = db_manager
        self.paper_trading = paper_trading if paper_trading is not None else Config.PAPER_TRADING
        self.client = None
        self.risk_manager = RiskManager(Config.INITIAL_CAPITAL)
        
        # Initialize Binance client for real trading
        if not self.paper_trading and BINANCE_AVAILABLE:
            try:
                self.client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET)
                print("✓ Binance API client initialized for REAL TRADING")
            except Exception as e:
                print(f"Warning: Could not initialize Binance client: {e}")
                print("Falling back to paper trading mode")
                self.paper_trading = True
        else:
            print("✓ Paper trading mode active (NO REAL MONEY)")
        
        # Paper trading state
        self.paper_balance = Config.INITIAL_CAPITAL
        self.paper_positions = {}
    
    def execute_trade(self, 
                     symbol: str,
                     signal: str,
                     score: int,
                     price: float,
                     indicators: Dict,
                     portfolio_value: float,
                     volatility: float = 0.02) -> Dict[str, any]:
        """
        Execute a trade based on signal and score
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            signal: BUY or SELL
            score: Trading score (60-100)
            price: Current price
            indicators: Technical indicators dict
            portfolio_value: Current portfolio value
            volatility: Current volatility (for position sizing)
        
        Returns:
            Dict with trade result
        """
        # Validate score
        if score < self.config.MIN_SCORE_THRESHOLD:
            return {
                'success': False,
                'error': f'Score {score} below minimum threshold {self.config.MIN_SCORE_THRESHOLD}'
            }
        
        # Get classification
        classification = self.config.get_classification(score)
        
        # Calculate position size
        position_calc = self.risk_manager.calculate_position_size(
            score, portfolio_value, price, volatility
        )
        
        if position_calc['quantity'] == 0:
            return {
                'success': False,
                'error': 'Position size calculated as zero'
            }
        
        # Check risk limits
        open_positions = self.db.get_all_positions()
        open_positions_value = sum(p.total_value for p in open_positions)
        
        risk_ok, risk_msg = self.risk_manager.check_risk_limits(
            portfolio_value,
            open_positions_value,
            position_calc['position_value']
        )
        
        if not risk_ok:
            return {
                'success': False,
                'error': risk_msg
            }
        
        # Calculate stop-loss and take-profit
        atr = indicators.get('atr', None)
        stop_loss = self.risk_manager.calculate_stop_loss(price, signal, atr)
        take_profit = self.risk_manager.calculate_take_profit(price, signal, atr)
        
        # Execute trade
        if self.paper_trading:
            result = self._execute_paper_trade(
                symbol, signal, price, position_calc['quantity'],
                stop_loss, take_profit, score, classification, indicators
            )
        else:
            result = self._execute_real_trade(
                symbol, signal, price, position_calc['quantity'],
                stop_loss, take_profit, score, classification, indicators
            )
        
        return result
    
    def _execute_paper_trade(self,
                           symbol: str,
                           side: str,
                           price: float,
                           quantity: float,
                           stop_loss: float,
                           take_profit: float,
                           score: int,
                           classification: str,
                           indicators: Dict) -> Dict[str, any]:
        """Execute a simulated paper trade"""
        total_value = price * quantity
        
        # Check if we have enough balance
        if side == 'BUY' and total_value > self.paper_balance:
            return {
                'success': False,
                'error': f'Insufficient paper balance: {self.paper_balance:.2f} USDT'
            }
        
        # Create trade record
        trade_data = {
            'symbol': symbol,
            'side': side,
            'price': price,
            'quantity': quantity,
            'total_value': total_value,
            'score': score,
            'classification': classification,
            'is_paper_trade': True,
            'order_id': f'PAPER_{symbol}_{int(time.time())}',
            'status': 'FILLED',
            'timestamp': datetime.utcnow(),
            'rsi': indicators.get('rsi'),
            'macd': indicators.get('macd'),
            'macd_signal': indicators.get('macd_signal'),
            'bb_upper': indicators.get('bb_upper'),
            'bb_lower': indicators.get('bb_lower'),
            'ema_short': indicators.get('ema_short'),
            'ema_long': indicators.get('ema_long'),
            'volume_24h': indicators.get('volume_24h'),
            'stop_loss': stop_loss,
            'take_profit': take_profit,
        }
        
        # Save trade
        trade = self.db.save_trade(trade_data)
        
        if side == 'BUY':
            # Deduct from paper balance
            self.paper_balance -= total_value
            
            # Create or update position
            position_data = {
                'symbol': symbol,
                'quantity': quantity,
                'entry_price': price,
                'current_price': price,
                'total_value': total_value,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'entry_timestamp': datetime.utcnow()
            }
            
            self.db.save_position(position_data)
            self.paper_positions[symbol] = position_data
        
        elif side == 'SELL':
            # Close position if exists
            position = self.db.get_position(symbol)
            if position:
                # Calculate PnL
                pnl = (price - position.entry_price) * quantity
                
                # Update trade with exit info
                self.db.update_trade(trade.id, {
                    'realized_pnl': pnl,
                    'exit_price': price,
                    'exit_timestamp': datetime.utcnow()
                })
                
                # Add proceeds to balance
                self.paper_balance += total_value + pnl
                
                # Close position
                self.db.close_position(symbol)
                if symbol in self.paper_positions:
                    del self.paper_positions[symbol]
        
        return {
            'success': True,
            'trade_id': trade.id,
            'order_id': trade_data['order_id'],
            'symbol': symbol,
            'side': side,
            'price': price,
            'quantity': quantity,
            'total_value': total_value,
            'classification': classification,
            'score': score,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'is_paper_trade': True,
            'paper_balance': self.paper_balance
        }
    
    def _execute_real_trade(self,
                          symbol: str,
                          side: str,
                          price: float,
                          quantity: float,
                          stop_loss: float,
                          take_profit: float,
                          score: int,
                          classification: str,
                          indicators: Dict) -> Dict[str, any]:
        """Execute a real trade on Binance"""
        if not self.client:
            return {
                'success': False,
                'error': 'Binance client not initialized'
            }
        
        try:
            # Place market order
            if side == 'BUY':
                order = self.client.create_order(
                    symbol=symbol,
                    side='BUY',
                    type='MARKET',
                    quantity=quantity
                )
            else:
                order = self.client.create_order(
                    symbol=symbol,
                    side='SELL',
                    type='MARKET',
                    quantity=quantity
                )
            
            # Extract order details
            filled_price = float(order['fills'][0]['price']) if order.get('fills') else price
            filled_quantity = float(order['executedQty'])
            order_id = str(order['orderId'])
            
            # Create trade record
            trade_data = {
                'symbol': symbol,
                'side': side,
                'price': filled_price,
                'quantity': filled_quantity,
                'total_value': filled_price * filled_quantity,
                'score': score,
                'classification': classification,
                'is_paper_trade': False,
                'order_id': order_id,
                'status': order['status'],
                'timestamp': datetime.utcnow(),
                'rsi': indicators.get('rsi'),
                'macd': indicators.get('macd'),
                'macd_signal': indicators.get('macd_signal'),
                'bb_upper': indicators.get('bb_upper'),
                'bb_lower': indicators.get('bb_lower'),
                'ema_short': indicators.get('ema_short'),
                'ema_long': indicators.get('ema_long'),
                'stop_loss': stop_loss,
                'take_profit': take_profit,
            }
            
            trade = self.db.save_trade(trade_data)
            
            # Update position
            if side == 'BUY':
                position_data = {
                    'symbol': symbol,
                    'quantity': filled_quantity,
                    'entry_price': filled_price,
                    'current_price': filled_price,
                    'total_value': filled_price * filled_quantity,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                }
                self.db.save_position(position_data)
            
            return {
                'success': True,
                'trade_id': trade.id,
                'order_id': order_id,
                'symbol': symbol,
                'side': side,
                'price': filled_price,
                'quantity': filled_quantity,
                'total_value': filled_price * filled_quantity,
                'classification': classification,
                'score': score,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'is_paper_trade': False
            }
        
        except BinanceAPIException as e:
            return {
                'success': False,
                'error': f'Binance API error: {e.message}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Trade execution error: {str(e)}'
            }
    
    def check_positions(self, current_prices: Dict[str, float]) -> list:
        """Check all positions for stop-loss or take-profit triggers"""
        actions = []
        positions = self.db.get_all_positions()
        
        for position in positions:
            symbol = position.symbol
            current_price = current_prices.get(symbol, position.current_price)
            
            # Check if position should be closed
            should_close, reason = self.risk_manager.should_close_position(
                current_price,
                position.entry_price,
                position.stop_loss,
                position.take_profit,
                'BUY'  # Assuming all positions are BUY for now
            )
            
            if should_close:
                actions.append({
                    'action': 'CLOSE',
                    'symbol': symbol,
                    'reason': reason,
                    'position': position,
                    'current_price': current_price
                })
        
        return actions
    
    def close_position(self, symbol: str, price: float, reason: str) -> Dict[str, any]:
        """Close a position"""
        position = self.db.get_position(symbol)
        
        if not position:
            return {
                'success': False,
                'error': f'No position found for {symbol}'
            }
        
        # Execute sell order
        result = self.execute_trade(
            symbol=symbol,
            signal='SELL',
            score=60,  # Minimum score for closing
            price=price,
            indicators={},
            portfolio_value=self.get_portfolio_value(),
            volatility=0.02
        )
        
        if result['success']:
            # Calculate PnL
            pnl = (price - position.entry_price) * position.quantity
            pnl_pct = (pnl / position.total_value) * 100
            
            result['pnl'] = pnl
            result['pnl_percent'] = pnl_pct
            result['reason'] = reason
        
        return result
    
    def get_portfolio_value(self) -> float:
        """Get current portfolio value"""
        if self.paper_trading:
            # Paper trading: balance + position values
            positions_value = sum(p.get('total_value', 0) for p in self.paper_positions.values())
            return self.paper_balance + positions_value
        else:
            # Real trading: would query Binance account
            if self.client:
                try:
                    account = self.client.get_account()
                    usdt_balance = float([b['free'] for b in account['balances'] if b['asset'] == 'USDT'][0])
                    return usdt_balance
                except Exception:
                    return Config.INITIAL_CAPITAL
            return Config.INITIAL_CAPITAL
    
    def get_account_summary(self) -> Dict[str, any]:
        """Get account summary"""
        portfolio_value = self.get_portfolio_value()
        positions = self.db.get_all_positions()
        trade_stats = self.db.get_trade_statistics()
        
        return {
            'portfolio_value': portfolio_value,
            'initial_capital': Config.INITIAL_CAPITAL,
            'total_pnl': portfolio_value - Config.INITIAL_CAPITAL,
            'total_pnl_percent': ((portfolio_value - Config.INITIAL_CAPITAL) / Config.INITIAL_CAPITAL) * 100,
            'paper_trading': self.paper_trading,
            'open_positions': len(positions),
            'trade_statistics': trade_stats,
            'timestamp': datetime.utcnow().isoformat()
        }
