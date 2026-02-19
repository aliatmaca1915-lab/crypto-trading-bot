"""
Advanced Scoring Algorithm (60-100 Points)
Combines Technical Indicators (45), Market Intelligence (30), and Advanced Signals (25)
"""
import pandas as pd
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from src.indicators.technical import TechnicalIndicators
from src.indicators.market_intelligence import MarketIntelligence
from src.indicators.advanced_signals import AdvancedSignals


@dataclass
class TradingScore:
    """Complete trading score with breakdown"""
    total_score: int
    technical_score: float
    market_intelligence_score: float
    advanced_signals_score: float
    classification: str
    confidence: float
    details: dict


class ScoringEngine:
    """Advanced scoring algorithm combining all analysis components"""
    
    def __init__(self, config=None):
        """Initialize scoring engine"""
        self.config = config
        self.technical = TechnicalIndicators(config)
        self.market_intel = MarketIntelligence(config)
        self.advanced = AdvancedSignals(config)
        
        # Score thresholds
        self.min_score = 60
        self.silver_range = (60, 79)
        self.gold_range = (80, 89)
        self.diamond_range = (90, 100)
    
    def calculate_score(
        self,
        df: pd.DataFrame,
        symbol: str,
        order_book: Optional[Dict] = None
    ) -> TradingScore:
        """
        Calculate comprehensive trading score (0-100 points)
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading pair symbol
            order_book: Optional order book data
        
        Returns:
            TradingScore with complete breakdown
        """
        # Calculate Technical Indicators (45 points max)
        technical_scores = self.technical.calculate_all_technical_scores(df)
        technical_total, technical_max = self.technical.get_total_technical_score(technical_scores)
        
        # Calculate Market Intelligence (30 points max)
        current_price = df['close'].iloc[-1]
        market_intel_scores = self.market_intel.calculate_all_market_intelligence_scores(
            symbol,
            current_price
        )
        market_intel_total, market_intel_max = self.market_intel.get_total_market_intelligence_score(
            market_intel_scores
        )
        
        # Calculate Advanced Signals (25 points max)
        # Need RSI for divergence detection
        rsi = self.technical.calculate_rsi(df['close'])
        advanced_scores = self.advanced.calculate_all_advanced_signal_scores(
            df,
            rsi,
            order_book
        )
        advanced_total, advanced_max = self.advanced.get_total_advanced_signals_score(
            advanced_scores
        )
        
        # Calculate total score (out of 100)
        total_score = int(technical_total + market_intel_total + advanced_total)
        max_possible = technical_max + market_intel_max + advanced_max
        
        # Determine classification
        classification = self._classify_score(total_score)
        
        # Calculate confidence (normalized score)
        confidence = (total_score / 100.0) * 100 if total_score > 0 else 0
        
        # Compile detailed breakdown
        details = {
            'technical': {
                'total': technical_total,
                'max': technical_max,
                'breakdown': {k: {'score': v.score, 'max': v.max_score, 'details': v.details} 
                            for k, v in technical_scores.items()}
            },
            'market_intelligence': {
                'total': market_intel_total,
                'max': market_intel_max,
                'breakdown': {k: {'score': v.score, 'max': v.max_score, 'details': v.details} 
                            for k, v in market_intel_scores.items()}
            },
            'advanced_signals': {
                'total': advanced_total,
                'max': advanced_max,
                'breakdown': {k: {'score': v.score, 'max': v.max_score, 'details': v.details} 
                            for k, v in advanced_scores.items()}
            },
            'symbol': symbol,
            'current_price': current_price,
            'max_possible_score': max_possible
        }
        
        return TradingScore(
            total_score=total_score,
            technical_score=technical_total,
            market_intelligence_score=market_intel_total,
            advanced_signals_score=advanced_total,
            classification=classification,
            confidence=confidence,
            details=details
        )
    
    def _classify_score(self, score: int) -> str:
        """
        Classify score into SILVER, GOLD, or DIAMOND
        
        Args:
            score: Total score (0-100)
        
        Returns:
            Classification string or None if below threshold
        """
        if score < self.min_score:
            return None  # Below minimum threshold
        elif self.silver_range[0] <= score <= self.silver_range[1]:
            return "SILVER"
        elif self.gold_range[0] <= score <= self.gold_range[1]:
            return "GOLD"
        elif self.diamond_range[0] <= score <= self.diamond_range[1]:
            return "DIAMOND"
        else:
            return None
    
    def is_tradeable(self, score: TradingScore) -> bool:
        """
        Check if score meets minimum threshold for trading
        
        Args:
            score: TradingScore object
        
        Returns:
            True if score >= 60 points
        """
        return score.total_score >= self.min_score
    
    def get_signal_type(self, score: TradingScore) -> str:
        """
        Determine signal type based on score
        
        Args:
            score: TradingScore object
        
        Returns:
            'buy', 'sell', or 'hold'
        """
        if self.is_tradeable(score):
            return 'buy'  # In this version, we focus on long positions
        else:
            return 'hold'
    
    def format_score_summary(self, score: TradingScore) -> str:
        """
        Format score summary for logging/display
        
        Args:
            score: TradingScore object
        
        Returns:
            Formatted string summary
        """
        lines = [
            f"=" * 60,
            f"TRADING SCORE SUMMARY",
            f"=" * 60,
            f"Symbol: {score.details['symbol']}",
            f"Current Price: ${score.details['current_price']:.2f}",
            f"",
            f"TOTAL SCORE: {score.total_score}/100 points",
            f"Classification: {score.classification or 'BELOW THRESHOLD'}",
            f"Confidence: {score.confidence:.1f}%",
            f"",
            f"Score Breakdown:",
            f"  Technical Indicators: {score.technical_score:.1f}/{score.details['technical']['max']} points",
            f"  Market Intelligence:  {score.market_intelligence_score:.1f}/{score.details['market_intelligence']['max']} points",
            f"  Advanced Signals:     {score.advanced_signals_score:.1f}/{score.details['advanced_signals']['max']} points",
            f"",
            f"Technical Details:",
        ]
        
        for indicator, data in score.details['technical']['breakdown'].items():
            lines.append(f"  - {indicator.upper()}: {data['score']:.1f}/{data['max']} ({data['details']})")
        
        lines.append("")
        lines.append("Market Intelligence:")
        for item, data in score.details['market_intelligence']['breakdown'].items():
            lines.append(f"  - {item.upper()}: {data['score']:.1f}/{data['max']} ({data['details']})")
        
        lines.append("")
        lines.append("Advanced Signals:")
        for signal, data in score.details['advanced_signals']['breakdown'].items():
            lines.append(f"  - {signal.upper()}: {data['score']:.1f}/{data['max']} ({data['details']})")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
