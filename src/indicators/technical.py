"""
Technical Indicators Engine
Implements 20+ technical indicators for market analysis
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class IndicatorScore:
    """Score and details for a single indicator"""
    score: float
    max_score: float
    details: dict


class TechnicalIndicators:
    """Calculate technical indicators and generate scores"""
    
    def __init__(self, config=None):
        """Initialize technical indicators"""
        self.config = config
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def score_rsi(self, rsi_value: float) -> IndicatorScore:
        """
        Score RSI Analysis (0-8 points)
        - Extreme oversold (< 25): 8 points (strong buy)
        - Oversold (25-30): 6 points (buy)
        - Neutral-bullish (30-50): 4 points
        - Neutral (50-70): 2 points
        - Overbought (70-75): 1 point
        - Extreme overbought (> 75): 0 points (avoid)
        """
        max_score = 8
        
        if rsi_value < 25:
            score = 8
            signal = "extreme_oversold_buy"
        elif rsi_value < 30:
            score = 6
            signal = "oversold_buy"
        elif rsi_value < 50:
            score = 4
            signal = "neutral_bullish"
        elif rsi_value < 70:
            score = 2
            signal = "neutral"
        elif rsi_value < 75:
            score = 1
            signal = "overbought"
        else:
            score = 0
            signal = "extreme_overbought"
        
        return IndicatorScore(
            score=score,
            max_score=max_score,
            details={
                'rsi_value': rsi_value,
                'signal': signal
            }
        )
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def score_macd(self, macd: float, signal: float, histogram: float) -> IndicatorScore:
        """
        Score MACD Analysis (0-8 points)
        - Strong bullish crossover + positive histogram: 8 points
        - Bullish crossover: 6 points
        - Positive MACD and histogram: 4 points
        - Neutral: 2 points
        - Bearish: 0 points
        """
        max_score = 8
        
        if macd > signal and histogram > 0 and macd > 0:
            score = 8
            trend = "strong_bullish_crossover"
        elif macd > signal and histogram > 0:
            score = 6
            trend = "bullish_crossover"
        elif macd > 0 and histogram > 0:
            score = 4
            trend = "positive_momentum"
        elif macd > signal or histogram > 0:
            score = 2
            trend = "neutral"
        else:
            score = 0
            trend = "bearish"
        
        return IndicatorScore(
            score=score,
            max_score=max_score,
            details={
                'macd': macd,
                'signal': signal,
                'histogram': histogram,
                'trend': trend
            }
        )
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    def score_bollinger_bands(self, price: float, upper: float, middle: float, lower: float, prices: pd.Series) -> IndicatorScore:
        """
        Score Bollinger Bands (0-7 points)
        - Price at lower band with volatility squeeze: 7 points
        - Price at lower band: 5 points
        - Below middle: 3 points
        - At middle: 2 points
        - Above middle: 1 point
        - At upper band: 0 points
        """
        max_score = 7
        
        # Calculate band width for squeeze detection
        band_width = (upper - lower) / middle
        is_squeeze = band_width < 0.04  # Volatility squeeze threshold
        
        if price <= lower and is_squeeze:
            score = 7
            signal = "lower_band_squeeze"
        elif price <= lower:
            score = 5
            signal = "at_lower_band"
        elif price < middle:
            score = 3
            signal = "below_middle"
        elif abs(price - middle) / middle < 0.005:  # Within 0.5% of middle
            score = 2
            signal = "at_middle"
        elif price < upper:
            score = 1
            signal = "above_middle"
        else:
            score = 0
            signal = "at_upper_band"
        
        return IndicatorScore(
            score=score,
            max_score=max_score,
            details={
                'price': price,
                'upper': upper,
                'middle': middle,
                'lower': lower,
                'band_width': band_width,
                'signal': signal
            }
        )
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()
    
    def calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return prices.rolling(window=period).mean()
    
    def score_ema_sma_trends(self, price: float, ema9: float, ema21: float, ema50: float, sma200: float) -> IndicatorScore:
        """
        Score EMA/SMA Trends (0-8 points)
        - All EMAs bullish aligned + above SMA200: 8 points
        - All EMAs bullish aligned: 6 points
        - Price above EMA21 and EMA50: 4 points
        - Price above EMA50: 2 points
        - Otherwise: 0 points
        """
        max_score = 8
        
        ema_aligned = price > ema9 > ema21 > ema50
        above_sma200 = price > sma200
        
        if ema_aligned and above_sma200:
            score = 8
            trend = "strong_uptrend"
        elif ema_aligned:
            score = 6
            trend = "uptrend"
        elif price > ema21 and price > ema50:
            score = 4
            trend = "moderate_uptrend"
        elif price > ema50:
            score = 2
            trend = "weak_uptrend"
        else:
            score = 0
            trend = "downtrend"
        
        return IndicatorScore(
            score=score,
            max_score=max_score,
            details={
                'price': price,
                'ema9': ema9,
                'ema21': ema21,
                'ema50': ema50,
                'sma200': sma200,
                'trend': trend
            }
        )
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=d_period).mean()
        
        return k, d
    
    def score_stochastic(self, k: float, d: float) -> IndicatorScore:
        """
        Score Stochastic (0-7 points)
        - Extreme oversold (< 15): 7 points
        - Oversold (15-20): 5 points
        - Below 50 with K > D: 3 points
        - Neutral: 2 points
        - Otherwise: 0 points
        """
        max_score = 7
        
        if k < 15 and d < 15:
            score = 7
            signal = "extreme_oversold"
        elif k < 20:
            score = 5
            signal = "oversold"
        elif k < 50 and k > d:
            score = 3
            signal = "bullish_momentum"
        elif k < 50:
            score = 2
            signal = "neutral"
        else:
            score = 0
            signal = "overbought"
        
        return IndicatorScore(
            score=score,
            max_score=max_score,
            details={
                'k': k,
                'd': d,
                'signal': signal
            }
        )
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def score_atr_volatility(self, atr: float, price: float, historical_atr: pd.Series) -> IndicatorScore:
        """
        Score ATR Volatility (0-7 points)
        - Low volatility (bottom 20%): 7 points (good for entry)
        - Below average volatility: 5 points
        - Average volatility: 3 points
        - Above average: 1 point
        - High volatility (top 20%): 0 points
        """
        max_score = 7
        
        atr_percentile = (historical_atr < atr).sum() / len(historical_atr)
        atr_percent = (atr / price) * 100
        
        if atr_percentile < 0.20:
            score = 7
            volatility = "very_low"
        elif atr_percentile < 0.40:
            score = 5
            volatility = "low"
        elif atr_percentile < 0.60:
            score = 3
            volatility = "normal"
        elif atr_percentile < 0.80:
            score = 1
            volatility = "high"
        else:
            score = 0
            volatility = "very_high"
        
        return IndicatorScore(
            score=score,
            max_score=max_score,
            details={
                'atr': atr,
                'atr_percent': atr_percent,
                'atr_percentile': atr_percentile,
                'volatility': volatility
            }
        )
    
    def calculate_all_technical_scores(self, df: pd.DataFrame) -> Dict[str, IndicatorScore]:
        """
        Calculate all technical indicator scores
        
        Args:
            df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        
        Returns:
            Dictionary of indicator scores
        """
        scores = {}
        
        # RSI
        rsi = self.calculate_rsi(df['close'])
        scores['rsi'] = self.score_rsi(rsi.iloc[-1])
        
        # MACD
        macd, signal, histogram = self.calculate_macd(df['close'])
        scores['macd'] = self.score_macd(macd.iloc[-1], signal.iloc[-1], histogram.iloc[-1])
        
        # Bollinger Bands
        upper, middle, lower = self.calculate_bollinger_bands(df['close'])
        scores['bollinger_bands'] = self.score_bollinger_bands(
            df['close'].iloc[-1],
            upper.iloc[-1],
            middle.iloc[-1],
            lower.iloc[-1],
            df['close']
        )
        
        # EMA/SMA Trends
        ema9 = self.calculate_ema(df['close'], 9)
        ema21 = self.calculate_ema(df['close'], 21)
        ema50 = self.calculate_ema(df['close'], 50)
        sma200 = self.calculate_sma(df['close'], 200)
        scores['ema_sma'] = self.score_ema_sma_trends(
            df['close'].iloc[-1],
            ema9.iloc[-1],
            ema21.iloc[-1],
            ema50.iloc[-1],
            sma200.iloc[-1]
        )
        
        # Stochastic
        k, d = self.calculate_stochastic(df['high'], df['low'], df['close'])
        scores['stochastic'] = self.score_stochastic(k.iloc[-1], d.iloc[-1])
        
        # ATR
        atr = self.calculate_atr(df['high'], df['low'], df['close'])
        scores['atr'] = self.score_atr_volatility(atr.iloc[-1], df['close'].iloc[-1], atr)
        
        return scores
    
    def get_total_technical_score(self, scores: Dict[str, IndicatorScore]) -> Tuple[float, float]:
        """
        Calculate total technical score and maximum possible
        
        Returns:
            (total_score, max_possible_score)
        """
        total_score = sum(s.score for s in scores.values())
        max_score = sum(s.max_score for s in scores.values())
        return total_score, max_score
