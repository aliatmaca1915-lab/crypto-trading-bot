"""
Simple Test Suite for Core Components
Run with: python -m pytest tests/test_core.py -v
"""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import ConfigManager
from src.core.scoring import ScoringEngine
from src.indicators.technical import TechnicalIndicators
from src.indicators.market_intelligence import MarketIntelligence
from src.indicators.advanced_signals import AdvancedSignals
from src.risk.position_sizing import PositionSizer
from src.risk.risk_manager import RiskManager


class TestConfiguration:
    """Test configuration management"""
    
    def test_config_loading(self):
        """Test that configuration loads successfully"""
        config = ConfigManager()
        assert config is not None
        assert config.get('mode') in ['paper', 'real']
        assert config.get_leverage() == 10
        assert config.get_minimum_score() >= 60
    
    def test_paper_trading_default(self):
        """Test that paper trading is default mode"""
        config = ConfigManager()
        assert config.is_paper_trading() == True


class TestTechnicalIndicators:
    """Test technical indicators"""
    
    def setup_method(self):
        """Setup test data"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=500, freq='1h')
        prices = 45000 + np.cumsum(np.random.randn(500) * 100)
        
        self.df = pd.DataFrame({
            'open': prices,
            'high': prices + np.random.rand(500) * 50,
            'low': prices - np.random.rand(500) * 50,
            'close': prices + np.random.randn(500) * 20,
            'volume': np.random.rand(500) * 1000
        }, index=dates)
        
        self.indicators = TechnicalIndicators()
    
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        rsi = self.indicators.calculate_rsi(self.df['close'])
        assert rsi is not None
        assert len(rsi) == len(self.df)
        # RSI should be between 0 and 100
        assert rsi.dropna().min() >= 0
        assert rsi.dropna().max() <= 100
    
    def test_macd_calculation(self):
        """Test MACD calculation"""
        macd, signal, histogram = self.indicators.calculate_macd(self.df['close'])
        assert macd is not None
        assert signal is not None
        assert histogram is not None
        assert len(macd) == len(self.df)
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        upper, middle, lower = self.indicators.calculate_bollinger_bands(self.df['close'])
        assert upper is not None
        assert middle is not None
        assert lower is not None
        # Upper should be greater than middle, middle greater than lower
        assert (upper.dropna() >= middle.dropna()).all()
        assert (middle.dropna() >= lower.dropna()).all()
    
    def test_technical_scoring(self):
        """Test technical scoring"""
        scores = self.indicators.calculate_all_technical_scores(self.df)
        assert 'rsi' in scores
        assert 'macd' in scores
        assert 'bollinger_bands' in scores
        assert 'ema_sma' in scores
        assert 'stochastic' in scores
        assert 'atr' in scores
        
        # Check total score
        total, max_score = self.indicators.get_total_technical_score(scores)
        assert 0 <= total <= max_score
        assert max_score == 45  # Total technical indicators max score


class TestScoringEngine:
    """Test scoring engine"""
    
    def setup_method(self):
        """Setup test data"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=500, freq='1h')
        prices = 45000 + np.cumsum(np.random.randn(500) * 100)
        
        self.df = pd.DataFrame({
            'open': prices,
            'high': prices + np.random.rand(500) * 50,
            'low': prices - np.random.rand(500) * 50,
            'close': prices + np.random.randn(500) * 20,
            'volume': np.random.rand(500) * 1000
        }, index=dates)
        
        self.scoring_engine = ScoringEngine()
    
    def test_score_calculation(self):
        """Test complete score calculation"""
        score = self.scoring_engine.calculate_score(self.df, "BTC/USDT")
        
        assert score is not None
        assert 0 <= score.total_score <= 100
        assert 0 <= score.technical_score <= 45
        assert 0 <= score.market_intelligence_score <= 30
        assert 0 <= score.advanced_signals_score <= 25
        assert score.classification in [None, "SILVER", "GOLD", "DIAMOND"]
    
    def test_classification(self):
        """Test score classification"""
        # Test different score ranges
        assert self.scoring_engine._classify_score(50) is None  # Below threshold
        assert self.scoring_engine._classify_score(65) == "SILVER"
        assert self.scoring_engine._classify_score(85) == "GOLD"
        assert self.scoring_engine._classify_score(95) == "DIAMOND"
    
    def test_tradeable_threshold(self):
        """Test tradeable threshold"""
        score_low = type('obj', (object,), {'total_score': 50})()
        score_high = type('obj', (object,), {'total_score': 70})()
        
        assert self.scoring_engine.is_tradeable(score_low) == False
        assert self.scoring_engine.is_tradeable(score_high) == True


class TestPositionSizing:
    """Test position sizing"""
    
    def setup_method(self):
        """Setup position sizer"""
        self.position_sizer = PositionSizer()
        self.capital = 10000
        self.price = 45000
    
    def test_silver_position(self):
        """Test SILVER classification position sizing"""
        position = self.position_sizer.calculate_position_size(
            "SILVER", self.capital, self.price
        )
        
        assert position.classification == "SILVER"
        assert position.leverage == 10
        assert position.base_percentage == 0.10
        assert position.effective_position == 1.0
        # Position value should be 10% of capital × 10x
        expected_value = self.capital * 0.10 * 10
        assert abs(position.position_value - expected_value) < 1
    
    def test_gold_position(self):
        """Test GOLD classification position sizing"""
        position = self.position_sizer.calculate_position_size(
            "GOLD", self.capital, self.price
        )
        
        assert position.classification == "GOLD"
        assert position.leverage == 10
        assert position.base_percentage == 0.15
        assert position.effective_position == 1.5
    
    def test_diamond_position(self):
        """Test DIAMOND classification position sizing"""
        position = self.position_sizer.calculate_position_size(
            "DIAMOND", self.capital, self.price
        )
        
        assert position.classification == "DIAMOND"
        assert position.leverage == 10
        assert position.base_percentage == 0.20
        assert position.effective_position == 2.0
    
    def test_stop_loss_calculation(self):
        """Test stop-loss price calculation"""
        entry_price = 45000
        stop_loss_pct = 0.025  # 2.5%
        
        stop_loss = self.position_sizer.calculate_stop_loss_price(
            entry_price, stop_loss_pct, 'long'
        )
        
        expected = entry_price * (1 - stop_loss_pct)
        assert abs(stop_loss - expected) < 1
    
    def test_liquidation_price(self):
        """Test liquidation price calculation"""
        entry_price = 45000
        leverage = 10
        
        liq_price = self.position_sizer.calculate_liquidation_price(
            entry_price, leverage, 'long'
        )
        
        # Liquidation should be below entry for long position
        assert liq_price < entry_price
        # Should be approximately 10% below (1/leverage)
        expected_distance = entry_price * (1 / leverage)
        assert abs((entry_price - liq_price) - expected_distance) < entry_price * 0.02


class TestRiskManagement:
    """Test risk management"""
    
    def setup_method(self):
        """Setup risk manager"""
        self.risk_manager = RiskManager()
    
    def test_position_limits(self):
        """Test position limit checks"""
        symbol = "BTC/USDT"
        position_value = 4000  # 4% of capital
        capital = 100000
        existing_positions = []
        
        # Should pass with reasonable position size (4% < 5% limit)
        result = self.risk_manager.check_position_limits(
            symbol, position_value, capital, existing_positions
        )
        assert result.passed == True
        
        # Should fail with oversized position (10% > 5% limit)
        result = self.risk_manager.check_position_limits(
            symbol, 10000, capital, existing_positions
        )
        assert result.passed == False
    
    def test_loss_limits(self):
        """Test loss limit checks"""
        current_capital = 9000
        initial_capital = 10000
        
        # Should pass with small loss (10%)
        result = self.risk_manager.check_loss_limits(
            current_capital, initial_capital, 'daily'
        )
        assert result.passed == False  # Exceeds 5% daily limit
        
        # Should pass with acceptable loss
        result = self.risk_manager.check_loss_limits(
            9600, initial_capital, 'daily'
        )
        assert result.passed == True  # 4% loss is acceptable
    
    def test_liquidation_buffer(self):
        """Test liquidation buffer check"""
        entry_price = 45000
        current_price = 45000  # At entry
        
        result = self.risk_manager.check_liquidation_buffer(
            entry_price, current_price, leverage=10
        )
        
        # Should pass at entry price
        assert result.passed == True
        assert result.details['buffer'] > 0.03  # More than 3% buffer


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
