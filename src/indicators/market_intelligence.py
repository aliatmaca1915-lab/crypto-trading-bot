"""
Market Intelligence Systems
Provides scoring for market sentiment, on-chain metrics, funding rates, and liquidation levels
"""
import requests
import numpy as np
import pandas as pd
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class MarketIntelligenceScore:
    """Score for market intelligence component"""
    score: float
    max_score: float
    details: dict


class MarketIntelligence:
    """Market intelligence analysis and scoring"""
    
    def __init__(self, config=None):
        """Initialize market intelligence"""
        self.config = config
        self.fear_greed_cache = None
        self.fear_greed_timestamp = None
    
    def get_fear_greed_index(self) -> Optional[int]:
        """
        Fetch Fear & Greed Index from Alternative.me API
        Returns value between 0-100
        """
        # Use cache if recent (< 1 hour old)
        if self.fear_greed_cache is not None and self.fear_greed_timestamp is not None:
            if datetime.now() - self.fear_greed_timestamp < timedelta(hours=1):
                return self.fear_greed_cache
        
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and 'data' in data and len(data['data']) > 0:
                value = int(data['data'][0]['value'])
                self.fear_greed_cache = value
                self.fear_greed_timestamp = datetime.now()
                return value
        except Exception as e:
            # If API fails, return neutral value
            return 50
        
        return 50
    
    def score_fear_greed_index(self, index_value: Optional[int] = None) -> MarketIntelligenceScore:
        """
        Score Fear & Greed Index (0-10 points)
        - Extreme Fear (0-25): 10 points (buy opportunity)
        - Fear (25-45): 7 points
        - Neutral (45-55): 4 points
        - Greed (55-75): 2 points
        - Extreme Greed (75-100): 0 points (avoid)
        """
        max_score = 10
        
        if index_value is None:
            index_value = self.get_fear_greed_index()
        
        if index_value is None:
            # Default neutral score if data unavailable
            return MarketIntelligenceScore(
                score=4,
                max_score=max_score,
                details={'index_value': None, 'sentiment': 'unknown'}
            )
        
        if index_value <= 25:
            score = 10
            sentiment = "extreme_fear"
        elif index_value <= 45:
            score = 7
            sentiment = "fear"
        elif index_value <= 55:
            score = 4
            sentiment = "neutral"
        elif index_value <= 75:
            score = 2
            sentiment = "greed"
        else:
            score = 0
            sentiment = "extreme_greed"
        
        return MarketIntelligenceScore(
            score=score,
            max_score=max_score,
            details={
                'index_value': index_value,
                'sentiment': sentiment
            }
        )
    
    def analyze_on_chain_metrics(self, symbol: str) -> MarketIntelligenceScore:
        """
        Score On-Chain Metrics (0-8 points)
        Simulated analysis of:
        - Exchange inflow/outflow
        - Holder distribution
        - Whale activity
        - New address creation
        
        Note: In production, integrate with Glassnode, CryptoQuant, or similar APIs
        """
        max_score = 8
        
        # Simulated on-chain analysis
        # In production, fetch real data from on-chain analytics providers
        
        # For now, return a neutral-to-positive score based on market conditions
        # This should be replaced with actual on-chain data
        
        score = 4  # Neutral default
        
        return MarketIntelligenceScore(
            score=score,
            max_score=max_score,
            details={
                'symbol': symbol,
                'exchange_flow': 'neutral',
                'whale_activity': 'low',
                'holder_distribution': 'stable',
                'note': 'Simulated on-chain data - integrate real API in production'
            }
        )
    
    def analyze_funding_rates(self, symbol: str, exchange: str = 'binance') -> MarketIntelligenceScore:
        """
        Score Funding Rates (0-6 points)
        - Highly negative funding (shorts paying longs): 6 points
        - Negative funding: 4 points
        - Neutral: 2 points
        - Positive funding: 0 points
        
        Note: In production, fetch real funding rate data from exchange APIs
        """
        max_score = 6
        
        # Simulated funding rate analysis
        # In production, fetch from exchange APIs
        
        # Default neutral score
        score = 2
        funding_rate = 0.0001  # Simulated neutral funding rate
        
        return MarketIntelligenceScore(
            score=score,
            max_score=max_score,
            details={
                'symbol': symbol,
                'funding_rate': funding_rate,
                'long_short_ratio': 1.0,
                'sentiment': 'neutral',
                'note': 'Simulated funding rate - integrate real API in production'
            }
        )
    
    def analyze_liquidation_levels(self, symbol: str, current_price: float) -> MarketIntelligenceScore:
        """
        Score Liquidation Levels (0-6 points)
        - Large liquidation cluster below (support): 6 points
        - Moderate liquidation support: 4 points
        - Neutral: 2 points
        - Liquidation cluster above (resistance): 0 points
        
        Note: In production, fetch from Coinglass or similar liquidation data providers
        """
        max_score = 6
        
        # Simulated liquidation analysis
        # In production, fetch real liquidation data
        
        score = 3  # Neutral default
        
        return MarketIntelligenceScore(
            score=score,
            max_score=max_score,
            details={
                'symbol': symbol,
                'current_price': current_price,
                'liquidation_support': 'moderate',
                'liquidation_resistance': 'moderate',
                'note': 'Simulated liquidation data - integrate real API in production'
            }
        )
    
    def calculate_all_market_intelligence_scores(self, symbol: str, current_price: float) -> Dict[str, MarketIntelligenceScore]:
        """
        Calculate all market intelligence scores
        
        Returns:
            Dictionary of market intelligence scores
        """
        scores = {}
        
        scores['fear_greed'] = self.score_fear_greed_index()
        scores['on_chain'] = self.analyze_on_chain_metrics(symbol)
        scores['funding_rates'] = self.analyze_funding_rates(symbol)
        scores['liquidation_levels'] = self.analyze_liquidation_levels(symbol, current_price)
        
        return scores
    
    def get_total_market_intelligence_score(self, scores: Dict[str, MarketIntelligenceScore]) -> tuple:
        """
        Calculate total market intelligence score
        
        Returns:
            (total_score, max_possible_score)
        """
        total_score = sum(s.score for s in scores.values())
        max_score = sum(s.max_score for s in scores.values())
        return total_score, max_score
