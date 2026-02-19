"""
Cryptocurrency Trading Bot - Main Orchestration
Enterprise-grade trading bot with 5500+ lines of code
"""
import time
import signal
import sys
from datetime import datetime
from typing import Dict
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Import all modules
from config import Config
from database import DatabaseManager
from data_fetcher import DataFetcher
from websocket_handler import MarketDataCollector
from technical_analysis import TechnicalAnalyzer
from ai_engine import AIEngine
from market_intelligence import MarketIntelligence
from risk_management import RiskManager
from scoring_system import ScoringSystem
from trading_engine import TradingEngine
from portfolio_manager import PortfolioManager
from alert_system import AlertSystem
from backtester import Backtester
from logger import log


class CryptoTradingBot:
    """
    Main trading bot orchestrator
    
    Features:
    - Real-time monitoring of 10 cryptocurrencies
    - Advanced technical indicators (RSI, MACD, BB, EMA, SMA, ATR, Stochastic)
    - AI/ML predictions (LSTM, Pattern Recognition)
    - Intelligent scoring system (20-100 points)
    - Classification system (SILVER/GOLD/DIAMOND)
    - Risk management (Stop-loss, Take-profit, Position sizing)
    - Market sentiment analysis
    - Portfolio management
    - Paper trading mode (default)
    - Real-time alerts
    - Comprehensive analytics
    """
    
    def __init__(self):
        """Initialize the trading bot"""
        log.info("="*80)
        log.info("🚀 Cryptocurrency Trading Bot - Initializing...")
        log.info("="*80)
        
        # Initialize all components
        self.config = Config
        self.db = DatabaseManager()
        self.data_fetcher = DataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        self.ai_engine = AIEngine()
        self.market_intelligence = MarketIntelligence()
        self.risk_manager = RiskManager()
        self.scoring_system = ScoringSystem()
        self.trading_engine = TradingEngine(self.db)
        self.portfolio_manager = PortfolioManager(self.db)
        self.alert_system = AlertSystem(self.db)
        
        # WebSocket data collector
        self.ws_collector = MarketDataCollector(self.db)
        
        # State
        self.is_running = False
        self.last_analysis_time = {}
        self.analysis_interval = 300  # 5 minutes
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        log.info(f"Trading Mode: {'PAPER TRADING (Simulated)' if Config.PAPER_TRADING else 'REAL TRADING'}")
        log.info(f"Tracking {len(Config.CRYPTOCURRENCIES)} cryptocurrencies")
        log.info(f"Minimum Score Threshold: {Config.MIN_SCORE_THRESHOLD} points")
        log.info("="*80)
    
    def start(self):
        """Start the trading bot"""
        log.info("Starting trading bot...")
        
        # Start WebSocket data collection
        self.ws_collector.start()
        time.sleep(2)  # Allow WebSocket to connect
        
        self.is_running = True
        
        # Display startup banner
        self._display_banner()
        
        # Main trading loop
        try:
            self._trading_loop()
        except KeyboardInterrupt:
            log.info("Received interrupt signal")
        except Exception as e:
            log.error(f"Fatal error in trading loop: {e}")
            self.alert_system.alert_system_error(str(e))
        finally:
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        log.info("Stopping trading bot...")
        self.is_running = False
        
        # Stop WebSocket
        self.ws_collector.stop()
        
        # Save final portfolio snapshot
        portfolio_value = self.trading_engine.get_portfolio_value()
        self.portfolio_manager.save_portfolio_snapshot(
            portfolio_value=portfolio_value,
            cash_balance=self.trading_engine.paper_balance if self.trading_engine.paper_trading else 0,
            invested_value=0,
            unrealized_pnl=0,
            realized_pnl=portfolio_value - Config.INITIAL_CAPITAL
        )
        
        log.info("Trading bot stopped")
        log.info("="*80)
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        log.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)
    
    def _trading_loop(self):
        """Main trading loop"""
        iteration = 0
        
        while self.is_running:
            iteration += 1
            current_time = datetime.utcnow()
            
            try:
                # Display status every 10 iterations
                if iteration % 10 == 0:
                    self._display_status()
                
                # Analyze each cryptocurrency
                for symbol in self.config.CRYPTOCURRENCIES:
                    # Check if enough time has passed since last analysis
                    last_time = self.last_analysis_time.get(symbol, datetime.min)
                    time_diff = (current_time - last_time).total_seconds()
                    
                    if time_diff < self.analysis_interval:
                        continue
                    
                    # Analyze and potentially trade
                    self._analyze_and_trade(symbol)
                    self.last_analysis_time[symbol] = current_time
                
                # Check existing positions
                current_prices = self.ws_collector.ws_handler.get_all_prices()
                if current_prices:
                    self._check_positions(current_prices)
                
                # Update market sentiment (every 30 minutes)
                if iteration % 60 == 0:
                    self._update_market_sentiment()
                
                # Save portfolio snapshot (every hour)
                if iteration % 120 == 0:
                    self._save_portfolio_snapshot()
                
                # Sleep before next iteration
                time.sleep(30)  # 30 seconds
            
            except Exception as e:
                log.error(f"Error in trading loop iteration {iteration}: {e}")
                time.sleep(60)
    
    def _analyze_and_trade(self, symbol: str):
        """Analyze a symbol and execute trade if signal is strong"""
        try:
            # Get current price
            current_price = self.ws_collector.get_current_price(symbol)
            
            if current_price == 0:
                log.warning(f"No price data available for {symbol}")
                return
            
            # Fetch historical data
            df = self.data_fetcher.fetch_historical_klines(symbol, '1h', limit=500)
            
            if df.empty:
                log.warning(f"No historical data for {symbol}")
                return
            
            # Calculate comprehensive score
            score_result = self.scoring_system.calculate_comprehensive_score(
                symbol=symbol,
                df=df,
                current_price=current_price
            )
            
            log.info(f"{symbol}: Score={score_result['total_score']} | Classification={score_result['classification']} | Signal={score_result['signal']}")
            
            # Check if tradeable
            if not score_result['is_tradeable']:
                return
            
            # Alert on high scores
            if score_result['total_score'] >= 85:
                self.alert_system.alert_high_score_signal(
                    symbol,
                    score_result['total_score'],
                    score_result['classification'],
                    score_result['signal']
                )
            
            # Execute trade if signal is BUY and we don't have a position
            if score_result['signal'] == 'BUY':
                position = self.db.get_position(symbol)
                if position:
                    log.info(f"{symbol}: Already have open position, skipping")
                    return
                
                # Get portfolio value
                portfolio_value = self.trading_engine.get_portfolio_value()
                
                # Get indicators
                latest = df.iloc[-1]
                indicators = {
                    'rsi': latest.get('rsi', 50),
                    'macd': latest.get('macd', 0),
                    'macd_signal': latest.get('macd_signal', 0),
                    'bb_upper': latest.get('bb_upper', current_price),
                    'bb_lower': latest.get('bb_lower', current_price),
                    'ema_short': latest.get('ema_short', current_price),
                    'ema_long': latest.get('ema_long', current_price),
                    'atr': latest.get('atr', current_price * 0.02),
                    'volume_24h': latest.get('volume', 0)
                }
                
                # Calculate volatility
                returns = df['close'].pct_change().dropna()
                volatility = returns.std() if len(returns) > 0 else 0.02
                
                # Execute trade
                trade_result = self.trading_engine.execute_trade(
                    symbol=symbol,
                    signal='BUY',
                    score=score_result['total_score'],
                    price=current_price,
                    indicators=indicators,
                    portfolio_value=portfolio_value,
                    volatility=volatility
                )
                
                if trade_result['success']:
                    log.info(f"✅ Trade executed: {trade_result}")
                    self.alert_system.alert_trade_executed(trade_result)
                else:
                    log.warning(f"❌ Trade failed: {trade_result.get('error', 'Unknown error')}")
        
        except Exception as e:
            log.error(f"Error analyzing {symbol}: {e}")
    
    def _check_positions(self, current_prices: Dict[str, float]):
        """Check positions for stop-loss or take-profit"""
        try:
            actions = self.trading_engine.check_positions(current_prices)
            
            for action in actions:
                symbol = action['symbol']
                price = action['current_price']
                reason = action['reason']
                
                log.info(f"Closing position {symbol} due to {reason}")
                
                result = self.trading_engine.close_position(symbol, price, reason)
                
                if result['success']:
                    pnl = result.get('pnl', 0)
                    
                    if reason == 'STOP_LOSS':
                        self.alert_system.alert_stop_loss(
                            symbol,
                            action['position'].entry_price,
                            price,
                            pnl
                        )
                    elif reason == 'TAKE_PROFIT':
                        self.alert_system.alert_take_profit(
                            symbol,
                            action['position'].entry_price,
                            price,
                            pnl
                        )
        
        except Exception as e:
            log.error(f"Error checking positions: {e}")
    
    def _update_market_sentiment(self):
        """Update market sentiment data"""
        try:
            sentiment = self.market_intelligence.get_market_intelligence_summary()
            
            # Save to database
            self.db.save_sentiment({
                'fear_greed_index': sentiment['fear_greed_index']['value'],
                'fear_greed_classification': sentiment['fear_greed_index']['classification'],
                'overall_sentiment': sentiment['overall_sentiment']['overall_sentiment'],
                'timestamp': datetime.utcnow()
            })
            
            # Alert on extreme sentiment
            self.alert_system.alert_market_sentiment(sentiment['fear_greed_index'])
            
            log.info(f"Market Sentiment: F&G={sentiment['fear_greed_index']['value']} ({sentiment['fear_greed_index']['classification']})")
        
        except Exception as e:
            log.error(f"Error updating market sentiment: {e}")
    
    def _save_portfolio_snapshot(self):
        """Save portfolio snapshot"""
        try:
            portfolio_value = self.trading_engine.get_portfolio_value()
            positions = self.db.get_all_positions()
            
            cash_balance = self.trading_engine.paper_balance if self.trading_engine.paper_trading else 0
            invested_value = sum(p.total_value for p in positions)
            unrealized_pnl = sum(p.unrealized_pnl or 0 for p in positions)
            realized_pnl = portfolio_value - Config.INITIAL_CAPITAL - unrealized_pnl
            
            self.portfolio_manager.save_portfolio_snapshot(
                portfolio_value=portfolio_value,
                cash_balance=cash_balance,
                invested_value=invested_value,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl
            )
            
            log.info(f"Portfolio snapshot saved: ${portfolio_value:.2f}")
        
        except Exception as e:
            log.error(f"Error saving portfolio snapshot: {e}")
    
    def _display_banner(self):
        """Display startup banner"""
        banner = f"""
{Fore.CYAN}{'='*80}
{Fore.GREEN}       🚀 CRYPTOCURRENCY TRADING BOT - ENTERPRISE EDITION 🚀
{Fore.CYAN}{'='*80}
{Fore.YELLOW}
       Mode: {'PAPER TRADING (Simulated - No Real Money)' if Config.PAPER_TRADING else 'REAL TRADING (Live Money)'}
       Cryptocurrencies: {len(Config.CRYPTOCURRENCIES)} tracked
       Minimum Score: {Config.MIN_SCORE_THRESHOLD} points
       Initial Capital: ${Config.INITIAL_CAPITAL:,.2f}
       
       Classification System:
       🥈 SILVER (60-80):  10% position size
       🥇 GOLD (81-89):    15% position size
       💎 DIAMOND (90-100): 25% position size
{Fore.CYAN}{'='*80}{Style.RESET_ALL}
        """
        print(banner)
    
    def _display_status(self):
        """Display current status"""
        try:
            # Get account summary
            account = self.trading_engine.get_account_summary()
            positions = self.portfolio_manager.get_position_summary()
            
            # Display header
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.GREEN}📊 STATUS UPDATE - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            
            # Display portfolio
            print(f"\n{Fore.YELLOW}Portfolio:{Style.RESET_ALL}")
            print(f"  Value: ${account['portfolio_value']:,.2f}")
            print(f"  PnL: ${account['total_pnl']:,.2f} ({account['total_pnl_percent']:+.2f}%)")
            print(f"  Positions: {account['open_positions']}")
            print(f"  Total Trades: {account['trade_statistics']['total_trades']}")
            print(f"  Win Rate: {account['trade_statistics']['win_rate']:.1f}%")
            
            # Display positions
            if positions:
                print(f"\n{Fore.YELLOW}Open Positions:{Style.RESET_ALL}")
                table_data = [
                    [
                        p['symbol'],
                        f"{p['quantity']:.6f}",
                        f"${p['entry_price']:.2f}",
                        f"${p['current_price']:.2f}",
                        f"{p['allocation']:.1f}%",
                        f"${p['unrealized_pnl']:+.2f}",
                        f"{p['unrealized_pnl_percent']:+.2f}%"
                    ]
                    for p in positions
                ]
                headers = ['Symbol', 'Qty', 'Entry', 'Current', 'Alloc%', 'PnL', 'PnL%']
                print(tabulate(table_data, headers=headers, tablefmt='simple'))
            
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        except Exception as e:
            log.error(f"Error displaying status: {e}")
    
    def run_backtest(self, symbol: str = 'BTCUSDT', days: int = 90):
        """Run backtest on historical data"""
        log.info(f"Running backtest for {symbol}...")
        
        backtester = Backtester()
        results = backtester.run_backtest(symbol, '1h', days)
        
        if results['success']:
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.GREEN}📈 BACKTEST RESULTS - {symbol}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            print(f"\nInitial Capital: ${results['initial_capital']:,.2f}")
            print(f"Final Value: ${results['final_value']:,.2f}")
            print(f"Total Return: {results['total_return']:+.2f}%")
            print(f"\nTrades: {results['total_trades']}")
            print(f"Win Rate: {results['win_rate']:.1f}%")
            print(f"Profit Factor: {results['profit_factor']:.2f}")
            print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
            print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cryptocurrency Trading Bot')
    parser.add_argument('--mode', choices=['trade', 'backtest'], default='trade',
                      help='Run mode: trade (live/paper) or backtest')
    parser.add_argument('--symbol', default='BTCUSDT',
                      help='Symbol for backtesting')
    parser.add_argument('--days', type=int, default=90,
                      help='Days for backtesting')
    
    args = parser.parse_args()
    
    bot = CryptoTradingBot()
    
    if args.mode == 'backtest':
        bot.run_backtest(args.symbol, args.days)
    else:
        bot.start()


if __name__ == '__main__':
    main()
