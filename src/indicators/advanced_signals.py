"""
Advanced Signals Module
Implements divergence detection, order book imbalance, and volume profile analysis
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AdvancedSignalScore:
    """Score for advanced signal component"""
    score: float
    max_score: float
    details: dict


class AdvancedSignals:
    """Advanced signal analysis"""
    
    def __init__(self, config=None):
        """Initialize advanced signals"""
        self.config = config
    
    def detect_divergence(self, prices: pd.Series, indicator: pd.Series, lookback: int = 50) -> AdvancedSignalScore:
        """
        Score Divergence Detection (0-8 points)
        - Bullish divergence (price down, indicator up): High score
        - Hidden bullish divergence: Medium-high score
        - No divergence: Low score
        - Bearish divergence: 0 points
        
        Args:
            prices: Price series
            indicator: Indicator series (e.g., RSI, MACD)
            lookback: Periods to look back for divergence
        """
        max_score = 8
        
        if len(prices) < lookback or len(indicator) < lookback:
            return AdvancedSignalScore(
                score=2,
                max_score=max_score,
                details={'divergence_type': 'insufficient_data'}
            )
        
        # Get recent data
        recent_prices = prices.tail(lookback)
        recent_indicator = indicator.tail(lookback)
        
        # Find local minima in price
        price_lows = []
        for i in range(2, len(recent_prices) - 2):
            if recent_prices.iloc[i] < recent_prices.iloc[i-1] and recent_prices.iloc[i] < recent_prices.iloc[i+1]:
                price_lows.append((i, recent_prices.iloc[i]))
        
        # Find local minima in indicator
        indicator_lows = []
        for i in range(2, len(recent_indicator) - 2):
            if recent_indicator.iloc[i] < recent_indicator.iloc[i-1] and recent_indicator.iloc[i] < recent_indicator.iloc[i+1]:
                indicator_lows.append((i, recent_indicator.iloc[i]))
        
        # Check for bullish divergence
        bullish_divergence = False
        if len(price_lows) >= 2 and len(indicator_lows) >= 2:
            # Latest price low is lower, but indicator low is higher
            if price_lows[-1][1] < price_lows[-2][1] and indicator_lows[-1][1] > indicator_lows[-2][1]:
                bullish_divergence = True
        
        if bullish_divergence:
            score = 8
            divergence_type = "bullish_divergence"
        elif len(price_lows) > 0 and len(indicator_lows) > 0:
            score = 4
            divergence_type = "neutral"
        else:
            score = 2
            divergence_type = "no_clear_divergence"
        
        return AdvancedSignalScore(
            score=score,
            max_score=max_score,
            details={
                'divergence_type': divergence_type,
                'price_lows_count': len(price_lows),
                'indicator_lows_count': len(indicator_lows)
            }
        )
    
    def analyze_order_book_imbalance(self, bids: list, asks: list, depth: int = 10) -> AdvancedSignalScore:
        """
        Score Order Book Imbalance (0-8 points)
        - Strong bid pressure (bid/ask ratio > 1.5): 8 points
        - Moderate bid pressure (ratio 1.2-1.5): 6 points
        - Balanced (ratio 0.8-1.2): 4 points
        - Ask pressure (ratio 0.5-0.8): 2 points
        - Strong ask pressure (ratio < 0.5): 0 points
        
        Args:
            bids: List of [price, quantity] bid orders
            asks: List of [price, quantity] ask orders
            depth: Number of orders to analyze
        """
        max_score = 8
        
        if not bids or not asks:
            return AdvancedSignalScore(
                score=4,
                max_score=max_score,
                details={'imbalance': 'no_data'}
            )
        
        # Calculate total bid and ask volume
        bid_volume = sum(float(bid[1]) for bid in bids[:depth])
        ask_volume = sum(float(ask[1]) for ask in asks[:depth])
        
        if ask_volume == 0:
            ratio = 2.0
        else:
            ratio = bid_volume / ask_volume
        
        if ratio > 1.5:
            score = 8
            imbalance = "strong_bid_pressure"
        elif ratio > 1.2:
            score = 6
            imbalance = "moderate_bid_pressure"
        elif ratio > 0.8:
            score = 4
            imbalance = "balanced"
        elif ratio > 0.5:
            score = 2
            imbalance = "ask_pressure"
        else:
            score = 0
            imbalance = "strong_ask_pressure"
        
        return AdvancedSignalScore(
            score=score,
            max_score=max_score,
            details={
                'bid_volume': bid_volume,
                'ask_volume': ask_volume,
                'ratio': ratio,
                'imbalance': imbalance
            }
        )
    
    def analyze_volume_profile(self, df: pd.DataFrame, lookback: int = 100) -> AdvancedSignalScore:
        """
        Score Volume Profile (0-9 points)
        - Price at high volume support level: 9 points
        - Price near high volume area: 7 points
        - Volume increasing on uptrend: 5 points
        - Normal volume: 3 points
        - Low volume: 0 points
        
        Args:
            df: DataFrame with ['close', 'volume'] columns
            lookback: Periods for volume analysis
        """
        max_score = 9
        
        if len(df) < lookback:
            return AdvancedSignalScore(
                score=3,
                max_score=max_score,
                details={'volume_profile': 'insufficient_data'}
            )
        
        recent_df = df.tail(lookback)
        current_price = recent_df['close'].iloc[-1]
        current_volume = recent_df['volume'].iloc[-1]
        avg_volume = recent_df['volume'].mean()
        
        # Volume ratio
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Calculate volume at different price levels (simplified Volume Profile)
        price_bins = 20
        price_range = recent_df['close'].max() - recent_df['close'].min()
        bin_size = price_range / price_bins if price_range > 0 else 1
        
        # Create price bins and sum volume
        volume_by_price = {}
        for idx, row in recent_df.iterrows():
            price_bin = int((row['close'] - recent_df['close'].min()) / bin_size) if bin_size > 0 else 0
            if price_bin not in volume_by_price:
                volume_by_price[price_bin] = 0
            volume_by_price[price_bin] += row['volume']
        
        # Find high volume nodes
        if volume_by_price:
            max_volume_bin = max(volume_by_price, key=volume_by_price.get)
            max_volume = volume_by_price[max_volume_bin]
            current_price_bin = int((current_price - recent_df['close'].min()) / bin_size) if bin_size > 0 else 0
            
            # Check if current price is at high volume area
            at_high_volume = abs(current_price_bin - max_volume_bin) <= 1
        else:
            at_high_volume = False
            max_volume = 0
        
        # Scoring logic
        if at_high_volume and volume_ratio > 1.2:
            score = 9
            profile = "high_volume_support"
        elif at_high_volume:
            score = 7
            profile = "at_high_volume_area"
        elif volume_ratio > 1.5:
            score = 5
            profile = "increasing_volume"
        elif volume_ratio > 0.7:
            score = 3
            profile = "normal_volume"
        else:
            score = 1
            profile = "low_volume"
        
        return AdvancedSignalScore(
            score=score,
            max_score=max_score,
            details={
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'profile': profile
            }
        )
    
    def calculate_all_advanced_signal_scores(
        self,
        df: pd.DataFrame,
        rsi: pd.Series,
        order_book: Optional[Dict] = None
    ) -> Dict[str, AdvancedSignalScore]:
        """
        Calculate all advanced signal scores
        
        Args:
            df: DataFrame with OHLCV data
            rsi: RSI indicator series for divergence detection
            order_book: Optional order book data with 'bids' and 'asks'
        
        Returns:
            Dictionary of advanced signal scores
        """
        scores = {}
        
        # Divergence detection
        scores['divergence'] = self.detect_divergence(df['close'], rsi)
        
        # Order book imbalance
        if order_book and 'bids' in order_book and 'asks' in order_book:
            scores['order_book'] = self.analyze_order_book_imbalance(
                order_book['bids'],
                order_book['asks']
            )
        else:
            # Default neutral score if order book not available
            scores['order_book'] = AdvancedSignalScore(
                score=4,
                max_score=8,
                details={'imbalance': 'no_orderbook_data'}
            )
        
        # Volume profile
        scores['volume_profile'] = self.analyze_volume_profile(df)
        
        return scores
    
    def get_total_advanced_signals_score(self, scores: Dict[str, AdvancedSignalScore]) -> Tuple[float, float]:
        """
        Calculate total advanced signals score
        
        Returns:
            (total_score, max_possible_score)
        """
        total_score = sum(s.score for s in scores.values())
        max_score = sum(s.max_score for s in scores.values())
        return total_score, max_score
