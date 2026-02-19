"""
Technical Analysis Module
Implements all technical indicators and analysis tools
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import ta
from config import Config


class TechnicalAnalyzer:
    """Technical analysis and indicator calculation"""
    
    def __init__(self):
        """Initialize technical analyzer"""
        self.config = Config
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators for a dataframe"""
        if df.empty or len(df) < 50:
            return df
        
        df = df.copy()
        
        # RSI
        df = self._calculate_rsi(df)
        
        # MACD
        df = self._calculate_macd(df)
        
        # Bollinger Bands
        df = self._calculate_bollinger_bands(df)
        
        # EMA
        df = self._calculate_ema(df)
        
        # SMA
        df = self._calculate_sma(df)
        
        # ATR
        df = self._calculate_atr(df)
        
        # Stochastic
        df = self._calculate_stochastic(df)
        
        # Volume indicators
        df = self._calculate_volume_indicators(df)
        
        # Trend indicators
        df = self._calculate_trend_indicators(df)
        
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI indicator"""
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'],
            window=self.config.RSI_PERIOD
        ).rsi()
        return df
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator"""
        macd = ta.trend.MACD(
            close=df['close'],
            window_fast=self.config.MACD_FAST,
            window_slow=self.config.MACD_SLOW,
            window_sign=self.config.MACD_SIGNAL
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_hist'] = macd.macd_diff()
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        bb = ta.volatility.BollingerBands(
            close=df['close'],
            window=self.config.BB_PERIOD,
            window_dev=self.config.BB_STD
        )
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        return df
    
    def _calculate_ema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate EMA"""
        df['ema_short'] = ta.trend.EMAIndicator(
            close=df['close'],
            window=self.config.EMA_SHORT
        ).ema_indicator()
        df['ema_long'] = ta.trend.EMAIndicator(
            close=df['close'],
            window=self.config.EMA_LONG
        ).ema_indicator()
        return df
    
    def _calculate_sma(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate SMA"""
        df['sma_short'] = ta.trend.SMAIndicator(
            close=df['close'],
            window=self.config.SMA_SHORT
        ).sma_indicator()
        df['sma_long'] = ta.trend.SMAIndicator(
            close=df['close'],
            window=self.config.SMA_LONG
        ).sma_indicator()
        return df
    
    def _calculate_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate ATR (Average True Range)"""
        df['atr'] = ta.volatility.AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=self.config.ATR_PERIOD
        ).average_true_range()
        return df
    
    def _calculate_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        stoch = ta.momentum.StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=self.config.STOCH_K_PERIOD,
            smooth_window=self.config.STOCH_D_PERIOD
        )
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based indicators"""
        # Volume Moving Average
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        
        # On-Balance Volume
        df['obv'] = ta.volume.OnBalanceVolumeIndicator(
            close=df['close'],
            volume=df['volume']
        ).on_balance_volume()
        
        # Volume Rate of Change
        df['volume_roc'] = df['volume'].pct_change(periods=10) * 100
        
        return df
    
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate trend strength indicators"""
        # ADX (Average Directional Index)
        adx = ta.trend.ADXIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14
        )
        df['adx'] = adx.adx()
        df['adx_pos'] = adx.adx_pos()
        df['adx_neg'] = adx.adx_neg()
        
        # Price Rate of Change
        df['price_roc'] = df['close'].pct_change(periods=10) * 100
        
        return df
    
    def analyze_rsi(self, rsi: float) -> Tuple[float, str]:
        """
        Analyze RSI and return score (0-20) and signal
        
        Scoring:
        - Extreme oversold (0-20): 20 points (strong buy)
        - Oversold (20-30): 15 points (buy)
        - Neutral low (30-40): 10 points
        - Neutral (40-60): 5 points
        - Neutral high (60-70): 10 points
        - Overbought (70-80): 15 points (sell)
        - Extreme overbought (80-100): 20 points (strong sell)
        """
        if pd.isna(rsi):
            return 0, 'NEUTRAL'
        
        if rsi < 20:
            return 20, 'STRONG_BUY'
        elif rsi < 30:
            return 15, 'BUY'
        elif rsi < 40:
            return 10, 'WEAK_BUY'
        elif rsi < 60:
            return 5, 'NEUTRAL'
        elif rsi < 70:
            return 10, 'WEAK_SELL'
        elif rsi < 80:
            return 15, 'SELL'
        else:
            return 20, 'STRONG_SELL'
    
    def analyze_macd(self, macd: float, macd_signal: float, macd_hist: float) -> Tuple[float, str]:
        """
        Analyze MACD and return score (0-15) and signal
        
        Scoring based on:
        - MACD crossing signal line
        - Histogram strength
        - Trend direction
        """
        if pd.isna(macd) or pd.isna(macd_signal):
            return 0, 'NEUTRAL'
        
        score = 0
        signal = 'NEUTRAL'
        
        # Bullish crossover
        if macd > macd_signal and macd_hist > 0:
            score = 15 if abs(macd_hist) > 0.1 else 12
            signal = 'BUY'
        # Bearish crossover
        elif macd < macd_signal and macd_hist < 0:
            score = 15 if abs(macd_hist) > 0.1 else 12
            signal = 'SELL'
        # Weak signals
        elif macd > macd_signal:
            score = 8
            signal = 'WEAK_BUY'
        else:
            score = 8
            signal = 'WEAK_SELL'
        
        return score, signal
    
    def analyze_bollinger_bands(self, close: float, bb_upper: float, bb_lower: float, bb_middle: float) -> Tuple[float, str]:
        """
        Analyze Bollinger Bands and return score (0-15) and signal
        
        Scoring:
        - Price near/below lower band: Buy signal
        - Price near/above upper band: Sell signal
        - Price in middle: Neutral
        """
        if pd.isna(close) or pd.isna(bb_upper) or pd.isna(bb_lower):
            return 0, 'NEUTRAL'
        
        bb_range = bb_upper - bb_lower
        position = (close - bb_lower) / bb_range if bb_range > 0 else 0.5
        
        if position < 0.1:  # Near lower band
            return 15, 'STRONG_BUY'
        elif position < 0.3:
            return 12, 'BUY'
        elif position > 0.9:  # Near upper band
            return 15, 'STRONG_SELL'
        elif position > 0.7:
            return 12, 'SELL'
        else:
            return 5, 'NEUTRAL'
    
    def analyze_ema_trend(self, close: float, ema_short: float, ema_long: float) -> Tuple[float, str]:
        """
        Analyze EMA trend and return score (0-20) and signal
        
        Scoring:
        - Strong bullish trend: 20 points
        - Bullish trend: 15 points
        - Weak bullish: 10 points
        - Neutral: 5 points
        - Weak bearish: 10 points
        - Bearish trend: 15 points
        - Strong bearish: 20 points
        """
        if pd.isna(ema_short) or pd.isna(ema_long):
            return 0, 'NEUTRAL'
        
        ema_diff_pct = ((ema_short - ema_long) / ema_long) * 100
        price_vs_short = ((close - ema_short) / ema_short) * 100
        
        # Strong bullish
        if ema_short > ema_long and ema_diff_pct > 2 and price_vs_short > 1:
            return 20, 'STRONG_BUY'
        # Bullish
        elif ema_short > ema_long and ema_diff_pct > 1:
            return 15, 'BUY'
        # Weak bullish
        elif ema_short > ema_long:
            return 10, 'WEAK_BUY'
        # Strong bearish
        elif ema_short < ema_long and ema_diff_pct < -2 and price_vs_short < -1:
            return 20, 'STRONG_SELL'
        # Bearish
        elif ema_short < ema_long and ema_diff_pct < -1:
            return 15, 'SELL'
        # Weak bearish
        elif ema_short < ema_long:
            return 10, 'WEAK_SELL'
        else:
            return 5, 'NEUTRAL'
    
    def analyze_stochastic(self, stoch_k: float, stoch_d: float) -> Tuple[float, str]:
        """
        Analyze Stochastic Oscillator and return score (0-15) and signal
        """
        if pd.isna(stoch_k) or pd.isna(stoch_d):
            return 0, 'NEUTRAL'
        
        # Oversold
        if stoch_k < 20 and stoch_d < 20:
            return 15, 'STRONG_BUY'
        elif stoch_k < 30:
            return 12, 'BUY'
        # Overbought
        elif stoch_k > 80 and stoch_d > 80:
            return 15, 'STRONG_SELL'
        elif stoch_k > 70:
            return 12, 'SELL'
        # Bullish crossover
        elif stoch_k > stoch_d and stoch_k < 50:
            return 10, 'BUY'
        # Bearish crossover
        elif stoch_k < stoch_d and stoch_k > 50:
            return 10, 'SELL'
        else:
            return 5, 'NEUTRAL'
    
    def analyze_volume(self, volume: float, volume_sma: float, volume_roc: float) -> Tuple[float, str]:
        """
        Analyze volume and return score (0-15) and signal
        """
        if pd.isna(volume) or pd.isna(volume_sma):
            return 0, 'NEUTRAL'
        
        volume_ratio = volume / volume_sma if volume_sma > 0 else 1
        
        # High volume with positive trend
        if volume_ratio > 2 and volume_roc > 50:
            return 15, 'STRONG'
        elif volume_ratio > 1.5 and volume_roc > 20:
            return 12, 'MODERATE'
        elif volume_ratio > 1:
            return 8, 'NORMAL'
        else:
            return 5, 'WEAK'
    
    def analyze_trend_strength(self, adx: float, price_roc: float) -> Tuple[float, str]:
        """
        Analyze trend strength using ADX and return score (0-15) and signal
        """
        if pd.isna(adx):
            return 0, 'NO_TREND'
        
        # Strong trend
        if adx > 50:
            score = 15
            signal = 'VERY_STRONG'
        elif adx > 40:
            score = 12
            signal = 'STRONG'
        elif adx > 25:
            score = 10
            signal = 'MODERATE'
        elif adx > 20:
            score = 7
            signal = 'WEAK'
        else:
            score = 3
            signal = 'NO_TREND'
        
        return score, signal
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        if df.empty or len(df) < window:
            return {'support': 0, 'resistance': 0}
        
        recent_data = df.tail(window)
        support = recent_data['low'].min()
        resistance = recent_data['high'].max()
        
        return {
            'support': support,
            'resistance': resistance,
            'range': resistance - support
        }
    
    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Detect common chart patterns"""
        if df.empty or len(df) < 20:
            return {}
        
        patterns = {
            'bullish_engulfing': self._detect_bullish_engulfing(df),
            'bearish_engulfing': self._detect_bearish_engulfing(df),
            'hammer': self._detect_hammer(df),
            'shooting_star': self._detect_shooting_star(df),
            'doji': self._detect_doji(df),
        }
        
        return patterns
    
    def _detect_bullish_engulfing(self, df: pd.DataFrame) -> bool:
        """Detect bullish engulfing pattern"""
        if len(df) < 2:
            return False
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        return (
            previous['close'] < previous['open'] and  # Previous bearish
            current['close'] > current['open'] and    # Current bullish
            current['close'] > previous['open'] and   # Engulfs previous
            current['open'] < previous['close']
        )
    
    def _detect_bearish_engulfing(self, df: pd.DataFrame) -> bool:
        """Detect bearish engulfing pattern"""
        if len(df) < 2:
            return False
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        return (
            previous['close'] > previous['open'] and  # Previous bullish
            current['close'] < current['open'] and    # Current bearish
            current['close'] < previous['open'] and   # Engulfs previous
            current['open'] > previous['close']
        )
    
    def _detect_hammer(self, df: pd.DataFrame) -> bool:
        """Detect hammer pattern (bullish reversal)"""
        if df.empty:
            return False
        
        candle = df.iloc[-1]
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        
        return (
            lower_shadow > body * 2 and
            upper_shadow < body * 0.3
        )
    
    def _detect_shooting_star(self, df: pd.DataFrame) -> bool:
        """Detect shooting star pattern (bearish reversal)"""
        if df.empty:
            return False
        
        candle = df.iloc[-1]
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        
        return (
            upper_shadow > body * 2 and
            lower_shadow < body * 0.3
        )
    
    def _detect_doji(self, df: pd.DataFrame) -> bool:
        """Detect doji pattern (indecision)"""
        if df.empty:
            return False
        
        candle = df.iloc[-1]
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        return body < total_range * 0.1 if total_range > 0 else False
