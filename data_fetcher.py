"""
Data Fetcher Module
Fetches historical and real-time data from Binance
"""
import pandas as pd
from typing import List, Dict
from datetime import datetime, timedelta
import time

try:
    from binance.client import Client
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    print("Warning: python-binance not available. Using mock data.")

from config import Config


class DataFetcher:
    """Fetches market data from Binance"""
    
    def __init__(self):
        """Initialize data fetcher"""
        self.config = Config
        self.client = None
        
        if BINANCE_AVAILABLE:
            try:
                # Use public API (no keys needed for historical data)
                self.client = Client("", "")
                print("✓ Binance data fetcher initialized")
            except Exception as e:
                print(f"Warning: Could not initialize Binance client: {e}")
    
    def fetch_historical_klines(self, 
                               symbol: str,
                               interval: str,
                               limit: int = 500,
                               start_time: datetime = None) -> pd.DataFrame:
        """
        Fetch historical candlestick data
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: Number of candles (max 1000)
            start_time: Optional start time
        
        Returns:
            DataFrame with OHLCV data
        """
        if not self.client:
            return self._get_mock_data(symbol, interval, limit)
        
        try:
            # Convert timeframe format
            interval_map = {
                '1m': Client.KLINE_INTERVAL_1MINUTE,
                '5m': Client.KLINE_INTERVAL_5MINUTE,
                '15m': Client.KLINE_INTERVAL_15MINUTE,
                '1h': Client.KLINE_INTERVAL_1HOUR,
                '4h': Client.KLINE_INTERVAL_4HOUR,
                '1d': Client.KLINE_INTERVAL_1DAY
            }
            
            binance_interval = interval_map.get(interval, Client.KLINE_INTERVAL_1HOUR)
            
            # Fetch klines
            if start_time:
                start_str = str(int(start_time.timestamp() * 1000))
                klines = self.client.get_historical_klines(
                    symbol, binance_interval, start_str, limit=limit
                )
            else:
                klines = self.client.get_klines(
                    symbol=symbol, interval=binance_interval, limit=limit
                )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            # Keep only relevant columns
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
        
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return self._get_mock_data(symbol, interval, limit)
    
    def _get_mock_data(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """Generate mock data for testing"""
        import numpy as np
        
        # Generate timestamps
        now = datetime.utcnow()
        interval_seconds = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400
        }.get(interval, 3600)
        
        timestamps = [now - timedelta(seconds=interval_seconds * i) for i in range(limit, 0, -1)]
        
        # Generate realistic price data with trend and volatility
        base_price = 50000 if 'BTC' in symbol else 2000
        prices = []
        current_price = base_price
        
        for i in range(limit):
            # Add trend and randomness
            trend = np.sin(i / 20) * 0.01  # Cyclical trend
            volatility = np.random.randn() * 0.02  # Random volatility
            change = current_price * (trend + volatility)
            current_price = current_price + change
            prices.append(current_price)
        
        # Create OHLCV data
        data = []
        for i, (ts, price) in enumerate(zip(timestamps, prices)):
            high = price * (1 + abs(np.random.randn()) * 0.01)
            low = price * (1 - abs(np.random.randn()) * 0.01)
            open_price = prices[i-1] if i > 0 else price
            close_price = price
            volume = np.random.uniform(100, 1000)
            
            data.append({
                'timestamp': ts,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close_price,
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def fetch_current_price(self, symbol: str) -> float:
        """Fetch current price for a symbol"""
        if not self.client:
            # Return mock price
            return 50000.0 if 'BTC' in symbol else 2000.0
        
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return 0.0
    
    def fetch_24h_ticker(self, symbol: str) -> Dict:
        """Fetch 24h ticker data"""
        if not self.client:
            return self._get_mock_ticker(symbol)
        
        try:
            ticker = self.client.get_ticker(symbol=symbol)
            return {
                'symbol': symbol,
                'price': float(ticker['lastPrice']),
                'price_change': float(ticker['priceChange']),
                'price_change_percent': float(ticker['priceChangePercent']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'volume_24h': float(ticker['volume']),
                'quote_volume_24h': float(ticker['quoteVolume']),
            }
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            return self._get_mock_ticker(symbol)
    
    def _get_mock_ticker(self, symbol: str) -> Dict:
        """Generate mock ticker data"""
        base_price = 50000 if 'BTC' in symbol else 2000
        return {
            'symbol': symbol,
            'price': base_price,
            'price_change': base_price * 0.02,
            'price_change_percent': 2.0,
            'high_24h': base_price * 1.05,
            'low_24h': base_price * 0.95,
            'volume_24h': 10000,
            'quote_volume_24h': base_price * 10000,
        }
    
    def fetch_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Fetch order book data"""
        if not self.client:
            return {'bids': [], 'asks': []}
        
        try:
            depth = self.client.get_order_book(symbol=symbol, limit=limit)
            return {
                'bids': [[float(price), float(qty)] for price, qty in depth['bids']],
                'asks': [[float(price), float(qty)] for price, qty in depth['asks']]
            }
        except Exception as e:
            print(f"Error fetching order book for {symbol}: {e}")
            return {'bids': [], 'asks': []}
    
    def calculate_liquidity(self, order_book: Dict) -> float:
        """Calculate liquidity from order book"""
        if not order_book or not order_book.get('bids') or not order_book.get('asks'):
            return 0.0
        
        # Sum top 10 bids and asks
        bid_liquidity = sum(price * qty for price, qty in order_book['bids'][:10])
        ask_liquidity = sum(price * qty for price, qty in order_book['asks'][:10])
        
        return (bid_liquidity + ask_liquidity) / 2
    
    def fetch_all_tickers(self) -> Dict[str, Dict]:
        """Fetch ticker data for all configured symbols"""
        tickers = {}
        
        for symbol in self.config.CRYPTOCURRENCIES:
            ticker = self.fetch_24h_ticker(symbol)
            tickers[symbol] = ticker
            time.sleep(0.1)  # Rate limiting
        
        return tickers
    
    def fetch_multi_timeframe_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple timeframes"""
        data = {}
        
        for timeframe in self.config.TIMEFRAMES:
            df = self.fetch_historical_klines(symbol, timeframe, limit=500)
            data[timeframe] = df
            time.sleep(0.2)  # Rate limiting
        
        return data
