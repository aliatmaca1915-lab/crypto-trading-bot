"""
AI/ML Engine Module
Implements LSTM Neural Networks, Pattern Recognition, and Predictive Models
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    # Try Keras 3.x standalone first
    try:
        import keras
        from keras.models import Sequential, load_model
        from keras.layers import LSTM, Dense, Dropout
        from keras.optimizers import Adam
    except ImportError:
        # Fallback to tensorflow.keras for compatibility
        from tensorflow import keras
        from tensorflow.keras.models import Sequential, load_model
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from tensorflow.keras.optimizers import Adam
    
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.model_selection import train_test_split
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow/Keras not available. ML features will be limited.")

from config import Config


class AIEngine:
    """AI/ML engine for price prediction and pattern recognition"""
    
    def __init__(self):
        """Initialize AI engine"""
        self.config = Config
        self.models = {}
        self.scalers = {}
        self.tensorflow_available = TENSORFLOW_AVAILABLE
    
    def prepare_data(self, df: pd.DataFrame, lookback: int = None) -> Tuple[np.ndarray, np.ndarray, MinMaxScaler]:
        """Prepare data for LSTM training"""
        if lookback is None:
            lookback = self.config.LSTM_LOOKBACK
        
        if len(df) < lookback + 10:
            return None, None, None
        
        # Use close price for prediction
        data = df['close'].values.reshape(-1, 1)
        
        # Scale data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y, scaler
    
    def build_lstm_model(self, lookback: int = None) -> Optional['Sequential']:
        """Build LSTM model architecture"""
        if not self.tensorflow_available:
            return None
        
        if lookback is None:
            lookback = self.config.LSTM_LOOKBACK
        
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        return model
    
    def train_lstm_model(self, symbol: str, df: pd.DataFrame, epochs: int = None, batch_size: int = None) -> Dict[str, any]:
        """Train LSTM model for a symbol"""
        if not self.tensorflow_available:
            return {'success': False, 'error': 'TensorFlow not available'}
        
        if epochs is None:
            epochs = self.config.LSTM_EPOCHS
        if batch_size is None:
            batch_size = self.config.LSTM_BATCH_SIZE
        
        # Prepare data
        X, y, scaler = self.prepare_data(df)
        
        if X is None:
            return {'success': False, 'error': 'Insufficient data'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Build and train model
        model = self.build_lstm_model()
        
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            verbose=0
        )
        
        # Save model and scaler
        self.models[symbol] = model
        self.scalers[symbol] = scaler
        
        # Calculate training metrics
        train_loss = history.history['loss'][-1]
        val_loss = history.history['val_loss'][-1]
        
        return {
            'success': True,
            'train_loss': float(train_loss),
            'val_loss': float(val_loss),
            'epochs_trained': epochs
        }
    
    def predict_price(self, symbol: str, df: pd.DataFrame, horizon: str = '1h') -> Dict[str, any]:
        """Predict future price using LSTM"""
        if not self.tensorflow_available:
            return self._simple_prediction(df, horizon)
        
        if symbol not in self.models or symbol not in self.scalers:
            # Train model if not exists
            train_result = self.train_lstm_model(symbol, df)
            if not train_result['success']:
                return self._simple_prediction(df, horizon)
        
        model = self.models[symbol]
        scaler = self.scalers[symbol]
        
        # Prepare last sequence
        lookback = self.config.LSTM_LOOKBACK
        if len(df) < lookback:
            return self._simple_prediction(df, horizon)
        
        last_sequence = df['close'].tail(lookback).values.reshape(-1, 1)
        scaled_sequence = scaler.transform(last_sequence)
        scaled_sequence = scaled_sequence.reshape(1, lookback, 1)
        
        # Predict
        predicted_scaled = model.predict(scaled_sequence, verbose=0)
        predicted_price = scaler.inverse_transform(predicted_scaled)[0][0]
        
        current_price = df['close'].iloc[-1]
        price_change = ((predicted_price - current_price) / current_price) * 100
        
        # Calculate confidence based on recent prediction accuracy
        confidence = self._calculate_prediction_confidence(df, model, scaler)
        
        # Determine direction
        if price_change > 1:
            direction = 'UP'
        elif price_change < -1:
            direction = 'DOWN'
        else:
            direction = 'NEUTRAL'
        
        return {
            'model_type': 'LSTM',
            'predicted_price': float(predicted_price),
            'current_price': float(current_price),
            'price_change_percent': float(price_change),
            'direction': direction,
            'confidence': float(confidence),
            'horizon': horizon
        }
    
    def _calculate_prediction_confidence(self, df: pd.DataFrame, model, scaler) -> float:
        """Calculate prediction confidence based on recent accuracy"""
        if len(df) < 100:
            return 0.5
        
        try:
            # Test on recent data
            X, y, _ = self.prepare_data(df.tail(100))
            if X is None:
                return 0.5
            
            predictions = model.predict(X, verbose=0)
            predictions = scaler.inverse_transform(predictions)
            actuals = scaler.inverse_transform(y.reshape(-1, 1))
            
            # Calculate MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100
            
            # Convert MAPE to confidence (lower MAPE = higher confidence)
            confidence = max(0, 1 - (mape / 100))
            
            return min(confidence, 0.95)  # Cap at 95%
        except Exception:
            return 0.5
    
    def _simple_prediction(self, df: pd.DataFrame, horizon: str) -> Dict[str, any]:
        """Simple trend-based prediction when LSTM is not available"""
        if len(df) < 20:
            return {
                'model_type': 'SIMPLE_TREND',
                'predicted_price': float(df['close'].iloc[-1]),
                'current_price': float(df['close'].iloc[-1]),
                'price_change_percent': 0.0,
                'direction': 'NEUTRAL',
                'confidence': 0.3,
                'horizon': horizon
            }
        
        # Calculate simple moving average trend
        recent_prices = df['close'].tail(20).values
        trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
        
        current_price = df['close'].iloc[-1]
        
        # Predict based on trend
        horizon_multiplier = {'5m': 1, '15m': 3, '1h': 12, '4h': 48, '1d': 288}.get(horizon, 1)
        predicted_price = current_price + (trend * horizon_multiplier)
        
        price_change = ((predicted_price - current_price) / current_price) * 100
        
        if price_change > 0.5:
            direction = 'UP'
        elif price_change < -0.5:
            direction = 'DOWN'
        else:
            direction = 'NEUTRAL'
        
        return {
            'model_type': 'SIMPLE_TREND',
            'predicted_price': float(predicted_price),
            'current_price': float(current_price),
            'price_change_percent': float(price_change),
            'direction': direction,
            'confidence': 0.4,
            'horizon': horizon
        }
    
    def recognize_patterns(self, df: pd.DataFrame) -> Dict[str, float]:
        """Advanced pattern recognition using ML techniques"""
        if len(df) < 50:
            return {}
        
        patterns = {}
        
        # Calculate pattern scores
        patterns['momentum_strength'] = self._analyze_momentum(df)
        patterns['volatility_pattern'] = self._analyze_volatility(df)
        patterns['volume_pattern'] = self._analyze_volume_pattern(df)
        patterns['trend_reversal_probability'] = self._analyze_reversal_probability(df)
        patterns['breakout_probability'] = self._analyze_breakout_probability(df)
        
        return patterns
    
    def _analyze_momentum(self, df: pd.DataFrame) -> float:
        """Analyze momentum strength (0-1)"""
        if 'rsi' not in df.columns or df['rsi'].isna().all():
            return 0.5
        
        rsi = df['rsi'].iloc[-1]
        
        # Normalize RSI to 0-1 scale
        if rsi > 50:
            momentum = (rsi - 50) / 50  # 0 to 1 for bullish momentum
        else:
            momentum = (50 - rsi) / 50 * -1  # 0 to -1 for bearish momentum
        
        return momentum
    
    def _analyze_volatility(self, df: pd.DataFrame) -> float:
        """Analyze volatility pattern (0-1)"""
        if 'atr' not in df.columns or df['atr'].isna().all():
            # Calculate simple volatility
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(len(returns))
            return min(volatility * 10, 1.0)  # Normalize
        
        atr = df['atr'].iloc[-1]
        price = df['close'].iloc[-1]
        
        # ATR as percentage of price
        atr_pct = (atr / price) * 100
        
        # Normalize to 0-1 (assuming 5% ATR is high)
        return min(atr_pct / 5, 1.0)
    
    def _analyze_volume_pattern(self, df: pd.DataFrame) -> float:
        """Analyze volume pattern (0-1)"""
        if 'volume' not in df.columns:
            return 0.5
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].tail(20).mean()
        
        if avg_volume == 0:
            return 0.5
        
        volume_ratio = current_volume / avg_volume
        
        # Normalize (ratio of 2 or more is considered high)
        return min(volume_ratio / 2, 1.0)
    
    def _analyze_reversal_probability(self, df: pd.DataFrame) -> float:
        """Analyze trend reversal probability (0-1)"""
        if len(df) < 20:
            return 0.5
        
        score = 0
        factors = 0
        
        # RSI divergence
        if 'rsi' in df.columns and not df['rsi'].isna().all():
            rsi = df['rsi'].iloc[-1]
            if rsi > 70 or rsi < 30:
                score += 1
            factors += 1
        
        # MACD histogram
        if 'macd_hist' in df.columns and not df['macd_hist'].isna().all():
            macd_hist = df['macd_hist'].tail(5).values
            if len(macd_hist) >= 5:
                # Check for weakening momentum
                if abs(macd_hist[-1]) < abs(macd_hist[-5]):
                    score += 1
                factors += 1
        
        # Price near support/resistance
        high_20 = df['high'].tail(20).max()
        low_20 = df['low'].tail(20).min()
        current = df['close'].iloc[-1]
        
        range_20 = high_20 - low_20
        if range_20 > 0:
            position = (current - low_20) / range_20
            if position < 0.1 or position > 0.9:
                score += 1
            factors += 1
        
        return score / factors if factors > 0 else 0.5
    
    def _analyze_breakout_probability(self, df: pd.DataFrame) -> float:
        """Analyze breakout probability (0-1)"""
        if len(df) < 20:
            return 0.5
        
        # Bollinger Band squeeze
        if 'bb_width' in df.columns and not df['bb_width'].isna().all():
            bb_width = df['bb_width'].tail(20)
            current_width = bb_width.iloc[-1]
            avg_width = bb_width.mean()
            
            # Low volatility (squeeze) suggests potential breakout
            if current_width < avg_width * 0.7:
                return 0.8
        
        # Volume increase
        if 'volume' in df.columns:
            recent_volume = df['volume'].tail(5).mean()
            avg_volume = df['volume'].tail(20).mean()
            
            if recent_volume > avg_volume * 1.5:
                return 0.7
        
        return 0.3
    
    def calculate_ml_score(self, df: pd.DataFrame, prediction: Dict, patterns: Dict) -> float:
        """Calculate ML contribution to overall trading score (0-10)"""
        score = 0
        
        # Prediction confidence (0-5 points)
        if prediction and 'confidence' in prediction:
            confidence = prediction['confidence']
            direction = prediction.get('direction', 'NEUTRAL')
            
            if direction in ['UP', 'DOWN']:
                score += confidence * 5
        
        # Pattern strength (0-5 points)
        if patterns:
            momentum = patterns.get('momentum_strength', 0)
            breakout = patterns.get('breakout_probability', 0)
            
            pattern_score = (abs(momentum) + breakout) / 2 * 5
            score += pattern_score
        
        return min(score, 10)
    
    def get_prediction_summary(self, symbol: str, df: pd.DataFrame) -> Dict[str, any]:
        """Get comprehensive ML prediction summary"""
        prediction = self.predict_price(symbol, df, '1h')
        patterns = self.recognize_patterns(df)
        ml_score = self.calculate_ml_score(df, prediction, patterns)
        
        return {
            'symbol': symbol,
            'prediction': prediction,
            'patterns': patterns,
            'ml_score': ml_score,
            'timestamp': datetime.utcnow().isoformat()
        }
