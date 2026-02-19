"""
WebSocket Data Handler
Handles real-time market data streaming from Binance WebSocket
"""
import json
import threading
import time
from typing import Dict, Callable, List
from datetime import datetime
import websocket

from config import Config


class WebSocketHandler:
    """Real-time WebSocket data handler for Binance"""
    
    def __init__(self, symbols: List[str] = None, callback: Callable = None):
        """Initialize WebSocket handler"""
        self.config = Config
        self.symbols = symbols or Config.CRYPTOCURRENCIES
        self.callback = callback
        self.ws = None
        self.ws_thread = None
        self.is_running = False
        self.reconnect_delay = Config.RECONNECT_DELAY
        self.price_data = {}
        self.ticker_data = {}
        
    def start(self):
        """Start WebSocket connection"""
        self.is_running = True
        self.ws_thread = threading.Thread(target=self._run_websocket, daemon=True)
        self.ws_thread.start()
        print("WebSocket handler started")
    
    def stop(self):
        """Stop WebSocket connection"""
        self.is_running = False
        if self.ws:
            self.ws.close()
        print("WebSocket handler stopped")
    
    def _run_websocket(self):
        """Run WebSocket connection with auto-reconnect"""
        while self.is_running:
            try:
                self._connect()
            except Exception as e:
                print(f"WebSocket error: {e}")
                if self.is_running:
                    print(f"Reconnecting in {self.reconnect_delay} seconds...")
                    time.sleep(self.reconnect_delay)
    
    def _connect(self):
        """Connect to Binance WebSocket"""
        # Create stream names for all symbols
        streams = [f"{symbol.lower()}@ticker" for symbol in self.symbols]
        stream_string = '/'.join(streams)
        
        # Binance combined streams endpoint
        ws_url = f"wss://stream.binance.com:9443/stream?streams={stream_string}"
        
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        self.ws.run_forever()
    
    def _on_open(self, ws):
        """WebSocket connection opened"""
        print("WebSocket connection established")
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            if 'stream' in data and 'data' in data:
                stream = data['stream']
                ticker_data = data['data']
                
                # Extract symbol
                symbol = ticker_data.get('s', '').upper()
                
                if symbol:
                    # Update ticker data
                    self.ticker_data[symbol] = {
                        'symbol': symbol,
                        'price': float(ticker_data.get('c', 0)),  # Current price
                        'price_change': float(ticker_data.get('p', 0)),  # Price change
                        'price_change_percent': float(ticker_data.get('P', 0)),  # Price change %
                        'high_24h': float(ticker_data.get('h', 0)),  # 24h high
                        'low_24h': float(ticker_data.get('l', 0)),  # 24h low
                        'volume_24h': float(ticker_data.get('v', 0)),  # 24h volume
                        'quote_volume_24h': float(ticker_data.get('q', 0)),  # 24h quote volume
                        'bid_price': float(ticker_data.get('b', 0)),  # Best bid
                        'ask_price': float(ticker_data.get('a', 0)),  # Best ask
                        'timestamp': datetime.utcnow()
                    }
                    
                    # Store simple price data
                    self.price_data[symbol] = float(ticker_data.get('c', 0))
                    
                    # Call callback if provided
                    if self.callback:
                        self.callback(symbol, self.ticker_data[symbol])
        
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket error handler"""
        print(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        print(f"WebSocket connection closed: {close_status_code} - {close_msg}")
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        return self.price_data.get(symbol, 0.0)
    
    def get_ticker_data(self, symbol: str) -> Dict:
        """Get full ticker data for a symbol"""
        return self.ticker_data.get(symbol, {})
    
    def get_all_prices(self) -> Dict[str, float]:
        """Get all current prices"""
        return self.price_data.copy()
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self.ws is not None and self.is_running


class MarketDataCollector:
    """Collects and aggregates market data from WebSocket"""
    
    def __init__(self, db_manager):
        """Initialize market data collector"""
        self.db_manager = db_manager
        self.ws_handler = WebSocketHandler(callback=self._on_ticker_update)
        self.candle_data = {}  # Store candle aggregation data
        self.last_save_time = {}
    
    def start(self):
        """Start collecting market data"""
        self.ws_handler.start()
        print("Market data collector started")
    
    def stop(self):
        """Stop collecting market data"""
        self.ws_handler.stop()
        print("Market data collector stopped")
    
    def _on_ticker_update(self, symbol: str, ticker_data: Dict):
        """Handle ticker updates"""
        # This could be used to aggregate candles or trigger analysis
        # For now, we'll just keep track of the latest data
        pass
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price"""
        return self.ws_handler.get_current_price(symbol)
    
    def get_ticker_data(self, symbol: str) -> Dict:
        """Get ticker data"""
        return self.ws_handler.get_ticker_data(symbol)
    
    def save_market_snapshot(self):
        """Save current market snapshot to database"""
        for symbol in Config.CRYPTOCURRENCIES:
            ticker = self.ws_handler.get_ticker_data(symbol)
            
            if ticker and ticker.get('price', 0) > 0:
                market_data = {
                    'symbol': symbol,
                    'timeframe': '1m',  # Real-time snapshot
                    'open_price': ticker['price'],
                    'high_price': ticker['high_24h'],
                    'low_price': ticker['low_24h'],
                    'close_price': ticker['price'],
                    'volume': ticker['volume_24h'],
                    'timestamp': datetime.utcnow()
                }
                
                try:
                    self.db_manager.save_market_data(market_data)
                except Exception as e:
                    print(f"Error saving market snapshot for {symbol}: {e}")
