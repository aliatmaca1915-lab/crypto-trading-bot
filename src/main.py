"""
Main Trading Bot Engine
Orchestrates all components for automated cryptocurrency trading
"""
import time
import signal
import sys
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import get_config
from src.core.logger import get_logger
from src.core.database import get_database
from src.core.scoring import ScoringEngine
from src.data.provider import DataProvider
from src.risk.position_sizing import PositionSizer
from src.risk.risk_manager import RiskManager
from src.execution.executor import OrderExecutor
from src.analytics.performance import PerformanceAnalyzer
from src.alerts.notifier import AlertSystem
from src.strategies.multi_timeframe import MultiTimeframeAnalyzer
from src.ml_models.ensemble import MLModels


class TradingBot:
    """Main cryptocurrency trading bot"""
    
    def __init__(self):
        """Initialize trading bot"""
        print("=" * 80)
        print("CRYPTOCURRENCY TRADING BOT - PHASE 2")
        print("Advanced Edition with 10x Fixed Leverage")
        print("=" * 80)
        print()
        
        # Load configuration
        self.config = get_config()
        print(f"✓ Configuration loaded: {self.config}")
        
        # Initialize logger
        self.logger = get_logger("TradingBot", self.config)
        self.logger.info("Trading Bot initializing...")
        
        # Initialize database
        self.db = get_database()
        self.logger.info("✓ Database initialized")
        
        # Initialize components
        self.scoring_engine = ScoringEngine(self.config)
        self.data_provider = DataProvider(self.config)
        self.position_sizer = PositionSizer(self.config)
        self.risk_manager = RiskManager(self.config)
        self.executor = OrderExecutor(self.config, self.data_provider)
        self.performance_analyzer = PerformanceAnalyzer(self.config)
        self.alert_system = AlertSystem(self.config)
        self.mtf_analyzer = MultiTimeframeAnalyzer(self.config)
        self.ml_models = MLModels(self.config)
        
        self.logger.info("✓ All components initialized")
        
        # Bot state
        self.running = False
        self.initial_capital = self.config.get_initial_capital()
        self.current_capital = self.initial_capital
        self.daily_start_capital = self.initial_capital
        self.weekly_start_capital = self.initial_capital
        self.capital_history = [self.initial_capital]
        
        # Track last update times
        self.last_day = datetime.now().date()
        self.last_week = datetime.now().isocalendar()[1]
        
        # Cryptocurrencies to trade
        self.symbols = self.config.get_cryptocurrencies()
        self.logger.info(f"✓ Tracking {len(self.symbols)} cryptocurrencies: {', '.join(self.symbols)}")
        
        # Mode
        self.mode = self.config.get('mode', 'paper')
        mode_display = "PAPER TRADING (SAFE)" if self.mode == 'paper' else "⚠️  REAL TRADING ⚠️"
        self.logger.info(f"✓ Mode: {mode_display}")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print()
        print("=" * 80)
        print("Bot initialization complete. Ready to start trading.")
        print("=" * 80)
        print()
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        self.logger.warning("Shutdown signal received. Stopping bot...")
        self.running = False
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("=" * 80)
        self.logger.info("STARTING TRADING BOT")
        self.logger.info("=" * 80)
        
        self.running = True
        
        # Main trading loop
        while self.running:
            try:
                # Check if new day/week for reset
                self._check_period_reset()
                
                # Analyze each cryptocurrency
                for symbol in self.symbols:
                    self._analyze_and_trade(symbol)
                
                # Update capital history
                self.capital_history.append(self.current_capital)
                
                # Check positions
                self._monitor_positions()
                
                # Sleep before next iteration
                sleep_time = self.config.get('update.data_refresh_interval', 5)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                self.logger.warning("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.exception(f"Error in main loop: {e}")
                time.sleep(10)  # Wait before retrying
        
        self._shutdown()
    
    def _analyze_and_trade(self, symbol: str):
        """
        Analyze symbol and execute trade if conditions are met
        
        Args:
            symbol: Trading pair to analyze
        """
        try:
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"Analyzing {symbol}")
            self.logger.info(f"{'='*80}")
            
            # Fetch multi-timeframe data
            timeframes = self.config.get_timeframes()
            mtf_data = self.data_provider.fetch_multi_timeframe_data(symbol, timeframes)
            
            if not mtf_data or len(mtf_data) == 0:
                self.logger.warning(f"No data available for {symbol}")
                return
            
            # Fetch order book
            order_book = self.data_provider.fetch_order_book(symbol)
            
            # Multi-timeframe analysis
            mtf_analysis = self.mtf_analyzer.analyze_timeframes(
                symbol, mtf_data, order_book
            )
            
            # Log multi-timeframe analysis
            self.logger.info(self.mtf_analyzer.format_analysis_summary(mtf_analysis))
            
            # Check if signal is buy and timeframes are aligned
            if mtf_analysis.final_signal != 'buy' or not mtf_analysis.aligned:
                self.logger.info(f"Signal: HOLD - Timeframes not aligned or score below threshold")
                return
            
            # Get primary timeframe score (1h)
            primary_tf = '1h'
            if primary_tf not in mtf_data:
                self.logger.warning(f"Primary timeframe {primary_tf} not available")
                return
            
            primary_score = self.scoring_engine.calculate_score(
                mtf_data[primary_tf], symbol, order_book
            )
            
            # Log detailed score
            self.logger.info(self.scoring_engine.format_score_summary(primary_score))
            
            # ML prediction
            technical_scores = self.scoring_engine.technical.calculate_all_technical_scores(mtf_data[primary_tf])
            ml_prediction = self.ml_models.predict(mtf_data[primary_tf], technical_scores)
            
            self.logger.info(f"\nML Prediction: {ml_prediction.signal.upper()} (Confidence: {ml_prediction.confidence:.1f}%)")
            
            # Check if should trade
            if not self.scoring_engine.is_tradeable(primary_score):
                self.logger.info("Score below minimum threshold (60). Skipping trade.")
                return
            
            # Get existing positions
            existing_positions = self.executor.get_open_positions()
            
            # Get current price
            current_price = self.data_provider.get_current_price(symbol)
            
            # Calculate position size
            position_size = self.position_sizer.calculate_position_size(
                primary_score.classification,
                self.current_capital,
                current_price,
                atr=None  # Would calculate from data in production
            )
            
            # Adjust position size by ML confidence
            adjusted_quantity = self.ml_models.adjust_position_by_confidence(
                position_size.quantity,
                ml_prediction.confidence
            )
            
            if adjusted_quantity == 0:
                self.logger.info("ML confidence too low. Skipping trade.")
                return
            
            # Risk checks
            risk_check = self.risk_manager.comprehensive_risk_check(
                symbol=symbol,
                position_value=adjusted_quantity * current_price,
                current_capital=self.current_capital,
                initial_capital=self.daily_start_capital,
                existing_positions=existing_positions,
                entry_price=current_price,
                current_price=current_price
            )
            
            if not risk_check.passed:
                self.logger.warning(f"Risk check failed: {risk_check.reason}")
                self.alert_system.send_risk_alert({
                    'type': 'Risk Check Failed',
                    'severity': 'high',
                    'details': risk_check.reason,
                    'current_capital': self.current_capital,
                    'max_drawdown': 0
                })
                return
            
            # Calculate stop-loss and take-profit
            stop_loss_price = self.position_sizer.calculate_stop_loss_price(
                current_price,
                position_size.stop_loss_pct
            )
            take_profit_price = self.position_sizer.calculate_take_profit_price(
                current_price,
                position_size.take_profit_pct
            )
            
            # Execute trade
            self.logger.info(f"\n🚀 EXECUTING BUY ORDER")
            self.logger.info(f"Classification: {primary_score.classification}")
            self.logger.info(f"Quantity: {adjusted_quantity:.6f}")
            self.logger.info(f"Entry Price: ${current_price:.2f}")
            self.logger.info(f"Position Value: ${adjusted_quantity * current_price:,.2f}")
            self.logger.info(f"Stop Loss: ${stop_loss_price:.2f}")
            self.logger.info(f"Take Profit: ${take_profit_price:.2f}")
            
            order = self.executor.execute_market_order(
                symbol=symbol,
                side='buy',
                quantity=adjusted_quantity,
                leverage=10,
                stop_loss=stop_loss_price,
                take_profit=take_profit_price
            )
            
            if order.status == 'filled':
                self.logger.info("✅ Order filled successfully!")
                
                # Save trade to database
                trade_data = {
                    'symbol': symbol,
                    'side': 'buy',
                    'entry_price': order.filled_price,
                    'quantity': order.filled_quantity,
                    'leverage': 10,
                    'position_size': order.filled_quantity * order.filled_price,
                    'classification': primary_score.classification,
                    'score': primary_score.total_score,
                    'stop_loss': stop_loss_price,
                    'take_profit': take_profit_price,
                    'mode': self.mode,
                    'notes': f"MTF Analysis: {mtf_analysis.alignment_count}/{len(mtf_analysis.signals)} aligned"
                }
                self.db.save_trade(trade_data)
                
                # Send alert
                self.alert_system.send_trade_alert(trade_data)
            else:
                self.logger.error(f"❌ Order failed: {order.notes}")
            
        except Exception as e:
            self.logger.exception(f"Error analyzing {symbol}: {e}")
    
    def _monitor_positions(self):
        """Monitor open positions for stop-loss/take-profit"""
        # This is simplified - in production, implement full position monitoring
        pass
    
    def _check_period_reset(self):
        """Check if need to reset daily/weekly tracking"""
        current_date = datetime.now().date()
        current_week = datetime.now().isocalendar()[1]
        
        # Reset daily
        if current_date != self.last_day:
            self._generate_daily_report()
            self.daily_start_capital = self.current_capital
            self.last_day = current_date
        
        # Reset weekly
        if current_week != self.last_week:
            self.weekly_start_capital = self.current_capital
            self.last_week = current_week
    
    def _generate_daily_report(self):
        """Generate and send daily report"""
        trades = self.db.get_open_trades(self.mode)
        
        summary = self.performance_analyzer.generate_daily_report(
            trades,
            self.current_capital,
            self.daily_start_capital
        )
        summary['mode'] = self.mode
        
        self.logger.info("\n" + "="*80)
        self.logger.info("DAILY REPORT")
        self.logger.info("="*80)
        for key, value in summary.items():
            self.logger.info(f"{key}: {value}")
        self.logger.info("="*80)
        
        self.alert_system.send_daily_summary(summary)
    
    def _shutdown(self):
        """Graceful shutdown"""
        self.logger.info("\n" + "="*80)
        self.logger.info("SHUTTING DOWN TRADING BOT")
        self.logger.info("="*80)
        
        # Generate final report
        self.logger.info("Generating final performance report...")
        
        # Close all positions if in paper mode
        if self.mode == 'paper':
            self.logger.info("Closing all paper trading positions...")
        
        self.logger.info("Bot shutdown complete.")
        self.logger.info("="*80)


def main():
    """Main entry point"""
    bot = TradingBot()
    bot.start()


if __name__ == "__main__":
    main()
