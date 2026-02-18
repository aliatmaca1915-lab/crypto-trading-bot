"""
Multi-Timeframe Analysis Module
Analyzes multiple timeframes and aggregates signals
"""
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
from src.core.scoring import ScoringEngine


@dataclass
class TimeframeSignal:
    """Signal from a single timeframe"""
    timeframe: str
    score: int
    classification: str
    signal: str
    confidence: float


@dataclass
class MultiTimeframeAnalysis:
    """Multi-timeframe analysis result"""
    aligned: bool
    alignment_count: int
    required_alignment: int
    signals: List[TimeframeSignal]
    weighted_score: float
    final_signal: str
    details: dict


class MultiTimeframeAnalyzer:
    """Analyze multiple timeframes and aggregate signals"""
    
    def __init__(self, config=None):
        """Initialize multi-timeframe analyzer"""
        self.config = config
        self.scoring_engine = ScoringEngine(config)
        
        # Timeframe weights (longer timeframes have more weight)
        self.timeframe_weights = {
            '5m': 0.10,   # 5-minute: Entry confirmation
            '15m': 0.15,  # 15-minute: Trend validation
            '1h': 0.25,   # 1-hour: Major trend
            '4h': 0.30,   # 4-hour: Key support/resistance
            '1d': 0.20    # 1-day: Overall market direction
        }
        
        self.minimum_alignment = 3  # At least 3 timeframes must agree
    
    def analyze_timeframes(
        self,
        symbol: str,
        timeframe_data: Dict[str, pd.DataFrame],
        order_book: dict = None
    ) -> MultiTimeframeAnalysis:
        """
        Analyze multiple timeframes and aggregate signals
        
        Args:
            symbol: Trading pair symbol
            timeframe_data: Dictionary mapping timeframe to DataFrame
            order_book: Optional order book data
        
        Returns:
            MultiTimeframeAnalysis result
        """
        signals = []
        
        # Analyze each timeframe
        for timeframe, df in timeframe_data.items():
            if df is not None and len(df) >= 200:  # Need enough data
                try:
                    # Calculate score for this timeframe
                    score_result = self.scoring_engine.calculate_score(
                        df, symbol, order_book
                    )
                    
                    # Determine signal
                    if score_result.total_score >= 60:
                        signal = 'buy'
                    else:
                        signal = 'hold'
                    
                    signals.append(TimeframeSignal(
                        timeframe=timeframe,
                        score=score_result.total_score,
                        classification=score_result.classification,
                        signal=signal,
                        confidence=score_result.confidence
                    ))
                except Exception as e:
                    print(f"Error analyzing timeframe {timeframe}: {e}")
        
        # Check alignment
        buy_signals = [s for s in signals if s.signal == 'buy']
        alignment_count = len(buy_signals)
        aligned = alignment_count >= self.minimum_alignment
        
        # Calculate weighted score
        weighted_score = self._calculate_weighted_score(signals)
        
        # Determine final signal
        final_signal = self._determine_final_signal(signals, aligned)
        
        # Veto if daily trend is against
        daily_signal = next((s for s in signals if s.timeframe == '1d'), None)
        if daily_signal and daily_signal.signal != 'buy' and final_signal == 'buy':
            # Daily veto
            final_signal = 'hold'
            veto_applied = True
        else:
            veto_applied = False
        
        return MultiTimeframeAnalysis(
            aligned=aligned,
            alignment_count=alignment_count,
            required_alignment=self.minimum_alignment,
            signals=signals,
            weighted_score=weighted_score,
            final_signal=final_signal,
            details={
                'buy_signals_count': alignment_count,
                'total_timeframes': len(signals),
                'daily_veto_applied': veto_applied,
                'timeframe_weights': self.timeframe_weights
            }
        )
    
    def _calculate_weighted_score(self, signals: List[TimeframeSignal]) -> float:
        """
        Calculate weighted average score across timeframes
        
        Args:
            signals: List of timeframe signals
        
        Returns:
            Weighted score (0-100)
        """
        total_weight = 0
        weighted_sum = 0
        
        for signal in signals:
            weight = self.timeframe_weights.get(signal.timeframe, 0.2)
            weighted_sum += signal.score * weight
            total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return 0
    
    def _determine_final_signal(
        self,
        signals: List[TimeframeSignal],
        aligned: bool
    ) -> str:
        """
        Determine final signal based on timeframe alignment
        
        Args:
            signals: List of timeframe signals
            aligned: Whether minimum alignment is met
        
        Returns:
            Final signal: 'buy' or 'hold'
        """
        if not aligned:
            return 'hold'
        
        # Count buy signals
        buy_count = sum(1 for s in signals if s.signal == 'buy')
        
        # If majority says buy and alignment met, return buy
        if buy_count >= self.minimum_alignment:
            return 'buy'
        else:
            return 'hold'
    
    def get_strongest_timeframe(self, signals: List[TimeframeSignal]) -> TimeframeSignal:
        """
        Get timeframe with strongest signal
        
        Args:
            signals: List of timeframe signals
        
        Returns:
            Strongest timeframe signal
        """
        if not signals:
            return None
        
        # Weight score by timeframe weight
        weighted_signals = [
            (s, s.score * self.timeframe_weights.get(s.timeframe, 0.2))
            for s in signals
        ]
        
        return max(weighted_signals, key=lambda x: x[1])[0]
    
    def format_analysis_summary(self, analysis: MultiTimeframeAnalysis) -> str:
        """
        Format multi-timeframe analysis summary
        
        Args:
            analysis: MultiTimeframeAnalysis result
        
        Returns:
            Formatted string summary
        """
        lines = [
            f"=" * 60,
            f"MULTI-TIMEFRAME ANALYSIS",
            f"=" * 60,
            f"",
            f"Alignment: {'YES' if analysis.aligned else 'NO'} ({analysis.alignment_count}/{len(analysis.signals)} timeframes agree)",
            f"Required Alignment: {analysis.required_alignment} timeframes",
            f"Weighted Score: {analysis.weighted_score:.1f}/100",
            f"Final Signal: {analysis.final_signal.upper()}",
            f"",
            f"Timeframe Breakdown:",
        ]
        
        # Sort signals by timeframe weight (descending)
        sorted_signals = sorted(
            analysis.signals,
            key=lambda s: self.timeframe_weights.get(s.timeframe, 0),
            reverse=True
        )
        
        for signal in sorted_signals:
            weight = self.timeframe_weights.get(signal.timeframe, 0.2)
            lines.append(
                f"  [{signal.timeframe.upper():>3}] Score: {signal.score:>3}/100 | "
                f"Signal: {signal.signal.upper():<4} | "
                f"Class: {signal.classification or 'NONE':<7} | "
                f"Weight: {weight*100:.0f}%"
            )
        
        if analysis.details.get('daily_veto_applied'):
            lines.append("")
            lines.append("⚠️  DAILY VETO APPLIED - Daily trend against signal")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
