"""
Data Provider Module
Fetches real-time and historical market data from Binance
"""
import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time


class DataProvider:
    """Fetch market data from cryptocurrency exchanges"""
    
    def __init__(self, config=None):
        """Initialize data provider"""
        self.config = config
        
        # Initialize Binance exchange
        try:
            self.exchange = ccxt.binance({
                'apiKey': config.get('api.binance.api_key') if config else None,
                'secret': config.get('api.binance.api_secret') if config else None,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',  # Use futures for leverage trading
                }
            })
            
            # Set testnet if configured
            if config and config.get('api.binance.testnet', False):
                self.exchange.set_sandbox_mode(True)
        except Exception as e:
            print(f"Warning: Could not initialize Binance API: {e}")
            self.exchange = None
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 500,
        since: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe (e.g., '5m', '15m', '1h', '4h', '1d')
            limit: Number of candles to fetch
            since: Timestamp in milliseconds (optional)
        
        Returns:
            DataFrame with OHLCV data
        """
        if not self.exchange:
            # Return simulated data if exchange not available
            return self._generate_simulated_ohlcv(symbol, timeframe, limit)
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        except Exception as e:
            print(f"Error fetching OHLCV data for {symbol}: {e}")
            return self._generate_simulated_ohlcv(symbol, timeframe, limit)
    
    def _generate_simulated_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> pd.DataFrame:
        """
        Generate simulated OHLCV data for testing
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            limit: Number of candles
        
        Returns:
            DataFrame with simulated OHLCV data
        """
        # Base prices for different symbols
        base_prices = {
            'BTC/USDT': 45000,
            'ETH/USDT': 2500,
            'BNB/USDT': 300,
            'XRP/USDT': 0.6,
            'ADA/USDT': 0.5,
            'SOL/USDT': 100,
            'DOGE/USDT': 0.08,
            'DOT/USDT': 7,
            'LTC/USDT': 70,
        }
        
        base_price = base_prices.get(symbol, 100)
        
        # Generate timestamps
        timeframe_minutes = {
            '5m': 5, '15m': 15, '1h': 60, '4h': 240, '1d': 1440
        }
        minutes = timeframe_minutes.get(timeframe, 60)
        
        timestamps = pd.date_range(
            end=datetime.now(),
            periods=limit,
            freq=f'{minutes}min'
        )
        
        # Generate price data with random walk
        np.random.seed(42)
        returns = np.random.normal(0, 0.02, limit)  # 2% volatility
        prices = base_price * np.exp(np.cumsum(returns))
        
        # Generate OHLCV
        df = pd.DataFrame({
            'open': prices,
            'high': prices * (1 + np.abs(np.random.normal(0, 0.01, limit))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.01, limit))),
            'close': prices * (1 + np.random.normal(0, 0.005, limit)),
            'volume': np.random.uniform(1000, 10000, limit)
        }, index=timestamps)
        
        return df
    
    def fetch_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """
        Fetch order book depth
        
        Args:
            symbol: Trading pair
            limit: Number of orders per side
        
        Returns:
            Dictionary with 'bids' and 'asks'
        """
        if not self.exchange:
            return self._generate_simulated_orderbook(symbol, limit)
        
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            return {
                'bids': order_book['bids'],
                'asks': order_book['asks'],
                'timestamp': order_book.get('timestamp'),
                'datetime': order_book.get('datetime')
            }
        except Exception as e:
            print(f"Error fetching order book for {symbol}: {e}")
            return self._generate_simulated_orderbook(symbol, limit)
    
    def _generate_simulated_orderbook(self, symbol: str, limit: int) -> Dict:
        """Generate simulated order book"""
        base_price = 45000  # Default price
        
        # Generate bids (buy orders below current price)
        bids = []
        for i in range(limit):
            price = base_price * (1 - (i + 1) * 0.0001)
            quantity = np.random.uniform(0.1, 2.0)
            bids.append([price, quantity])
        
        # Generate asks (sell orders above current price)
        asks = []
        for i in range(limit):
            price = base_price * (1 + (i + 1) * 0.0001)
            quantity = np.random.uniform(0.1, 2.0)
            asks.append([price, quantity])
        
        return {
            'bids': bids,
            'asks': asks,
            'timestamp': int(time.time() * 1000),
            'datetime': datetime.now().isoformat()
        }
    
    def fetch_ticker(self, symbol: str) -> Dict:
        """
        Fetch current ticker data
        
        Args:
            symbol: Trading pair
        
        Returns:
            Dictionary with ticker data
        """
        if not self.exchange:
            return self._generate_simulated_ticker(symbol)
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            return self._generate_simulated_ticker(symbol)
    
    def _generate_simulated_ticker(self, symbol: str) -> Dict:
        """Generate simulated ticker data"""
        base_price = 45000
        
        return {
            'symbol': symbol,
            'timestamp': int(time.time() * 1000),
            'datetime': datetime.now().isoformat(),
            'high': base_price * 1.02,
            'low': base_price * 0.98,
            'bid': base_price * 0.9999,
            'ask': base_price * 1.0001,
            'last': base_price,
            'close': base_price,
            'baseVolume': 1000,
            'quoteVolume': base_price * 1000
        }
    
    def fetch_multi_timeframe_data(
        self,
        symbol: str,
        timeframes: List[str] = None,
        limit: int = 500
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple timeframes
        
        Args:
            symbol: Trading pair
            timeframes: List of timeframes
            limit: Number of candles per timeframe
        
        Returns:
            Dictionary mapping timeframe to DataFrame
        """
        if timeframes is None:
            timeframes = ['5m', '15m', '1h', '4h', '1d']
        
        data = {}
        for tf in timeframes:
            try:
                df = self.fetch_ohlcv(symbol, tf, limit)
                data[tf] = df
            except Exception as e:
                print(f"Error fetching {tf} data for {symbol}: {e}")
        
        return data
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price
        
        Args:
            symbol: Trading pair
        
        Returns:
            Current price
        """
        ticker = self.fetch_ticker(symbol)
        return ticker.get('last', ticker.get('close', 0))
    
    def fetch_balance(self) -> Dict:
        """
        Fetch account balance
        
        Returns:
            Dictionary with balance information
        """
        if not self.exchange:
            return {'USDT': {'free': 10000, 'used': 0, 'total': 10000}}
        
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return {'USDT': {'free': 10000, 'used': 0, 'total': 10000}}
    
    def get_exchange_info(self, symbol: str) -> Dict:
        """
        Get exchange trading rules for symbol
        
        Args:
            symbol: Trading pair
        
        Returns:
            Dictionary with exchange information
        """
        if not self.exchange:
            return {
                'min_order_size': 0.001,
                'price_precision': 2,
                'amount_precision': 6
            }
        
        try:
            markets = self.exchange.load_markets()
            market = markets.get(symbol, {})
            
            return {
                'min_order_size': market.get('limits', {}).get('amount', {}).get('min', 0.001),
                'price_precision': market.get('precision', {}).get('price', 2),
                'amount_precision': market.get('precision', {}).get('amount', 6),
                'limits': market.get('limits', {})
            }
        except Exception as e:
            print(f"Error fetching exchange info: {e}")
            return {
                'min_order_size': 0.001,
                'price_precision': 2,
                'amount_precision': 6
            }
