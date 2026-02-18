"""
Intelligent Scoring System
Calculates trading scores (20-100 points) based on multiple factors
"""
from typing import Dict, Tuple
import pandas as pd
from datetime import datetime

from technical_analysis import TechnicalAnalyzer
from market_intelligence import MarketIntelligence
from ai_engine import AIEngine
from config import Config


class ScoringSystem:
    """
    Intelligent scoring system for trading signals
    
    Score Breakdown (Total: 100 points):
    - RSI Analysis: 0-20 points
    - MACD Analysis: 0-15 points
    - Bollinger Bands: 0-15 points
    - EMA/SMA Trends: 0-20 points
    - Stochastic Indicator: 0-15 points
    - Volume Analysis: 0-15 points
    - Trend Strength: 0-15 points (ADX)
    - Market Sentiment: 0-20 points
    - Liquidity Score: 0-10 points
    - Momentum (ML): 0-10 points
    ────────────────────────
    TOTAL: 20-100 points
    
    Trading Rule: Execute only when score >= 60 points
    """
    
    def __init__(self):
        """Initialize scoring system"""
        self.config = Config
        self.technical_analyzer = TechnicalAnalyzer()
        self.market_intelligence = MarketIntelligence()
        self.ai_engine = AIEngine()
    
    def calculate_comprehensive_score(self, 
                                     symbol: str,
                                     df: pd.DataFrame,
                                     current_price: float,
                                     volume_24h: float = None,
                                     liquidity_usdt: float = None) -> Dict[str, any]:
        """
        Calculate comprehensive trading score for a symbol
        
        Returns:
            Dict containing:
            - total_score: Overall score (20-100)
            - classification: SILVER/GOLD/DIAMOND/NONE
            - signal: BUY/SELL/NEUTRAL
            - breakdown: Score breakdown by component
            - recommendation: Trading recommendation
        """
        if df.empty or len(df) < 50:
            return self._get_insufficient_data_result()
        
        # Ensure indicators are calculated
        df = self.technical_analyzer.calculate_all_indicators(df)
        
        # Get latest values
        latest = df.iloc[-1]
        
        # Initialize score breakdown
        breakdown = {}
        
        # 1. RSI Analysis (0-20 points)
        rsi_score, rsi_signal = self.technical_analyzer.analyze_rsi(latest.get('rsi', 50))
        breakdown['rsi'] = {
            'score': rsi_score,
            'signal': rsi_signal,
            'value': latest.get('rsi', 50)
        }
        
        # 2. MACD Analysis (0-15 points)
        macd_score, macd_signal = self.technical_analyzer.analyze_macd(
            latest.get('macd', 0),
            latest.get('macd_signal', 0),
            latest.get('macd_hist', 0)
        )
        breakdown['macd'] = {
            'score': macd_score,
            'signal': macd_signal,
            'macd': latest.get('macd', 0),
            'signal_line': latest.get('macd_signal', 0)
        }
        
        # 3. Bollinger Bands (0-15 points)
        bb_score, bb_signal = self.technical_analyzer.analyze_bollinger_bands(
            current_price,
            latest.get('bb_upper', current_price),
            latest.get('bb_lower', current_price),
            latest.get('bb_middle', current_price)
        )
        breakdown['bollinger_bands'] = {
            'score': bb_score,
            'signal': bb_signal,
            'position': 'Unknown'
        }
        
        # 4. EMA/SMA Trends (0-20 points)
        ema_score, ema_signal = self.technical_analyzer.analyze_ema_trend(
            current_price,
            latest.get('ema_short', current_price),
            latest.get('ema_long', current_price)
        )
        breakdown['ema_trend'] = {
            'score': ema_score,
            'signal': ema_signal,
            'ema_short': latest.get('ema_short', 0),
            'ema_long': latest.get('ema_long', 0)
        }
        
        # 5. Stochastic Indicator (0-15 points)
        stoch_score, stoch_signal = self.technical_analyzer.analyze_stochastic(
            latest.get('stoch_k', 50),
            latest.get('stoch_d', 50)
        )
        breakdown['stochastic'] = {
            'score': stoch_score,
            'signal': stoch_signal,
            'k': latest.get('stoch_k', 50),
            'd': latest.get('stoch_d', 50)
        }
        
        # 6. Volume Analysis (0-15 points)
        volume_score, volume_signal = self.technical_analyzer.analyze_volume(
            latest.get('volume', 0),
            latest.get('volume_sma', 1),
            latest.get('volume_roc', 0)
        )
        breakdown['volume'] = {
            'score': volume_score,
            'signal': volume_signal,
            'current': latest.get('volume', 0),
            'average': latest.get('volume_sma', 0)
        }
        
        # 7. Trend Strength (0-15 points) - using ADX
        trend_score, trend_signal = self.technical_analyzer.analyze_trend_strength(
            latest.get('adx', 20),
            latest.get('price_roc', 0)
        )
        breakdown['trend_strength'] = {
            'score': trend_score,
            'signal': trend_signal,
            'adx': latest.get('adx', 20)
        }
        
        # 8. Market Sentiment (0-20 points)
        try:
            sentiment = self.market_intelligence.get_overall_sentiment()
            sentiment_score, sentiment_signal = self.market_intelligence.calculate_sentiment_score(sentiment)
        except Exception as e:
            print(f"Error getting sentiment: {e}")
            sentiment_score = 10
            sentiment_signal = 'NEUTRAL'
        
        breakdown['market_sentiment'] = {
            'score': sentiment_score,
            'signal': sentiment_signal,
            'value': sentiment.get('overall_sentiment', 0) if isinstance(sentiment, dict) else 0
        }
        
        # 9. Liquidity Score (0-10 points)
        liquidity_score = self._calculate_liquidity_score(liquidity_usdt, volume_24h)
        breakdown['liquidity'] = {
            'score': liquidity_score,
            'liquidity_usdt': liquidity_usdt or 0,
            'volume_24h': volume_24h or 0
        }
        
        # 10. Momentum (ML-based) (0-10 points)
        try:
            ml_prediction = self.ai_engine.predict_price(symbol, df)
            ml_patterns = self.ai_engine.recognize_patterns(df)
            momentum_score = self.ai_engine.calculate_ml_score(df, ml_prediction, ml_patterns)
        except Exception as e:
            print(f"Error in ML analysis: {e}")
            momentum_score = 5
            ml_prediction = {'direction': 'NEUTRAL', 'confidence': 0.5}
        
        breakdown['ml_momentum'] = {
            'score': momentum_score,
            'prediction': ml_prediction.get('direction', 'NEUTRAL') if isinstance(ml_prediction, dict) else 'NEUTRAL',
            'confidence': ml_prediction.get('confidence', 0.5) if isinstance(ml_prediction, dict) else 0.5
        }
        
        # Calculate total score
        total_score = (
            rsi_score + macd_score + bb_score + ema_score +
            stoch_score + volume_score + trend_score + 
            sentiment_score + liquidity_score + momentum_score
        )
        
        # Ensure score is in valid range (20-100)
        total_score = max(20, min(100, total_score))
        
        # Determine classification
        classification = self.config.get_classification(int(total_score))
        
        # Determine overall signal
        signal = self._determine_signal(breakdown, total_score)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(total_score, classification, signal, breakdown)
        
        return {
            'symbol': symbol,
            'total_score': int(total_score),
            'classification': classification,
            'signal': signal,
            'breakdown': breakdown,
            'recommendation': recommendation,
            'is_tradeable': total_score >= self.config.MIN_SCORE_THRESHOLD,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_liquidity_score(self, liquidity_usdt: float = None, volume_24h: float = None) -> float:
        """Calculate liquidity score (0-10 points)"""
        if not liquidity_usdt and not volume_24h:
            return 5  # Neutral when data unavailable
        
        # Use volume_24h as proxy if liquidity not available
        liquidity = liquidity_usdt if liquidity_usdt else (volume_24h or 0)
        
        # Score based on liquidity thresholds
        if liquidity >= 1000000:  # >= $1M
            return 10
        elif liquidity >= 500000:  # >= $500K
            return 8
        elif liquidity >= 100000:  # >= $100K
            return 6
        elif liquidity >= 50000:   # >= $50K
            return 4
        else:
            return 2
    
    def _determine_signal(self, breakdown: Dict, total_score: int) -> str:
        """Determine overall signal from breakdown"""
        # Count bullish and bearish signals
        bullish_signals = 0
        bearish_signals = 0
        
        for component, data in breakdown.items():
            signal = data.get('signal', 'NEUTRAL')
            
            if 'BUY' in signal:
                bullish_signals += 1
            elif 'SELL' in signal:
                bearish_signals += 1
        
        # Determine overall signal
        if bullish_signals > bearish_signals * 1.5 and total_score >= 60:
            return 'BUY'
        elif bearish_signals > bullish_signals * 1.5:
            return 'SELL'
        else:
            return 'NEUTRAL'
    
    def _generate_recommendation(self, score: int, classification: str, 
                                signal: str, breakdown: Dict) -> str:
        """Generate trading recommendation"""
        if score < self.config.MIN_SCORE_THRESHOLD:
            return "AVOID - Score below minimum threshold"
        
        if signal == 'BUY':
            if classification == 'DIAMOND':
                return f"STRONG BUY - {classification} ({score} points) - Consider 25% position"
            elif classification == 'GOLD':
                return f"BUY - {classification} ({score} points) - Consider 15% position"
            elif classification == 'SILVER':
                return f"MODERATE BUY - {classification} ({score} points) - Consider 10% position"
        elif signal == 'SELL':
            return f"SELL SIGNAL - Score: {score} - Consider closing positions"
        else:
            return f"HOLD - Score: {score} - Wait for clearer signals"
        
        return f"NEUTRAL - Score: {score}"
    
    def _get_insufficient_data_result(self) -> Dict[str, any]:
        """Return result for insufficient data"""
        return {
            'symbol': 'UNKNOWN',
            'total_score': 0,
            'classification': 'NONE',
            'signal': 'NEUTRAL',
            'breakdown': {},
            'recommendation': 'INSUFFICIENT DATA - Cannot analyze',
            'is_tradeable': False,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def quick_score(self, symbol: str, df: pd.DataFrame) -> int:
        """Get quick score without full breakdown (faster)"""
        result = self.calculate_comprehensive_score(symbol, df, df['close'].iloc[-1] if not df.empty else 0)
        return result['total_score']
