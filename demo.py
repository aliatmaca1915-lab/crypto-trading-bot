"""
Quick Demo Script
Demonstrates the bot's scoring and analysis capabilities without executing trades
"""
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config import get_config
from src.core.logger import get_logger
from src.core.scoring import ScoringEngine
from src.data.provider import DataProvider
from src.strategies.multi_timeframe import MultiTimeframeAnalyzer


def main():
    """Run a quick demo of the bot's analysis"""
    print("=" * 80)
    print("CRYPTOCURRENCY TRADING BOT - DEMO MODE")
    print("=" * 80)
    print()
    
    # Load configuration
    config = get_config()
    logger = get_logger("Demo")
    
    logger.info("Initializing demo...")
    
    # Initialize components
    data_provider = DataProvider(config)
    scoring_engine = ScoringEngine(config)
    mtf_analyzer = MultiTimeframeAnalyzer(config)
    
    # Demo symbol
    symbol = "BTC/USDT"
    
    logger.info(f"Analyzing {symbol}...")
    
    # Fetch multi-timeframe data
    timeframes = ['5m', '15m', '1h', '4h', '1d']
    mtf_data = data_provider.fetch_multi_timeframe_data(symbol, timeframes, limit=500)
    
    # Fetch order book
    order_book = data_provider.fetch_order_book(symbol)
    
    # Analyze primary timeframe (1h)
    if '1h' in mtf_data and len(mtf_data['1h']) >= 200:
        logger.info("\n" + "="*80)
        logger.info("SINGLE TIMEFRAME ANALYSIS (1h)")
        logger.info("="*80)
        
        score = scoring_engine.calculate_score(mtf_data['1h'], symbol, order_book)
        print("\n" + scoring_engine.format_score_summary(score))
        
        if scoring_engine.is_tradeable(score):
            logger.info(f"\n✅ TRADEABLE - Score: {score.total_score}/100, Classification: {score.classification}")
        else:
            logger.info(f"\n❌ NOT TRADEABLE - Score: {score.total_score}/100 (Below 60 threshold)")
    
    # Multi-timeframe analysis
    logger.info("\n" + "="*80)
    logger.info("MULTI-TIMEFRAME ANALYSIS")
    logger.info("="*80)
    
    mtf_analysis = mtf_analyzer.analyze_timeframes(symbol, mtf_data, order_book)
    print("\n" + mtf_analyzer.format_analysis_summary(mtf_analysis))
    
    if mtf_analysis.final_signal == 'buy':
        logger.info(f"\n✅ BUY SIGNAL - {mtf_analysis.alignment_count}/{len(mtf_analysis.signals)} timeframes aligned")
    else:
        logger.info(f"\n❌ HOLD - Only {mtf_analysis.alignment_count}/{len(mtf_analysis.signals)} timeframes aligned (need {mtf_analysis.required_alignment})")
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print()
    print("This demo analyzed the market using simulated data.")
    print("To run the actual bot in paper trading mode, execute: python src/main.py")
    print()


if __name__ == "__main__":
    main()
