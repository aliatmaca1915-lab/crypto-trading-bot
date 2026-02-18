# 🚀 Cryptocurrency Trading Bot - PHASE 2
## Advanced Edition with 10x Fixed Leverage

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional, enterprise-grade cryptocurrency trading bot featuring advanced scoring algorithms, ML-powered predictions, and safe leverage management.

## ⚠️ IMPORTANT SAFETY NOTICE

**This bot runs in PAPER TRADING mode by default.** No real money is risked unless you explicitly switch to real trading mode and configure API credentials.

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Advanced Scoring Algorithm](#advanced-scoring-algorithm)
- [Position Sizing & Leverage](#position-sizing--leverage)
- [Risk Management](#risk-management)
- [Performance Metrics](#performance-metrics)
- [Notifications](#notifications)
- [Disclaimer](#disclaimer)

## ✨ Features

### Advanced Scoring System (60-100 Points)
- **Technical Indicators (45 points)**: RSI, MACD, Bollinger Bands, EMA/SMA, Stochastic, ATR
- **Market Intelligence (30 points)**: Fear/Greed Index, On-Chain Metrics, Funding Rates, Liquidation Levels
- **Advanced Signals (25 points)**: Divergence Detection, Order Book Imbalance, Volume Profile

### Classification & Position Sizing
- **🥈 SILVER (60-79 points)**: 10% capital × 10x leverage = 100% effective position
- **🥇 GOLD (80-89 points)**: 15% capital × 10x leverage = 150% effective position
- **💎 DIAMOND (90-100 points)**: 20% capital × 10x leverage = 200% effective position

### Multi-Timeframe Analysis
- Analyzes 5 timeframes: 5m, 15m, 1h, 4h, 1d
- Requires 3+ timeframes to align before trading
- Weighted signal aggregation
- Daily trend veto protection

### ML/AI Ensemble Models
- LSTM for time series prediction
- XGBoost for feature importance
- Random Forest for pattern recognition
- Gradient Boosting for signal strength
- Confidence-based position adjustment

### Advanced Risk Management
- Fixed 10x leverage with liquidation buffer (3-5%)
- Dynamic ATR-based stop-loss
- Multiple take-profit levels (TP1, TP2, TP3)
- Position limits: 5% per coin
- Daily loss limit: 5%
- Weekly loss limit: 10%
- Correlation-based position limits

### Performance Analytics
- Real-time performance tracking
- Sharpe Ratio, Sortino Ratio
- Maximum Drawdown, Profit Factor
- Calmar Ratio, Recovery Factor
- Daily and monthly reports

### Alert System
- Email notifications
- Telegram bot integration
- Discord webhooks
- Trade, risk, and system alerts

## 🏗️ System Architecture

```
crypto-trading-bot/
├── config/
│   └── config.yaml              # Configuration file
├── src/
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── logger.py            # Logging system
│   │   ├── database.py          # Database persistence
│   │   └── scoring.py           # Scoring engine
│   ├── data/
│   │   └── provider.py          # Data fetching from Binance
│   ├── indicators/
│   │   ├── technical.py         # Technical indicators
│   │   ├── market_intelligence.py  # Market intelligence
│   │   └── advanced_signals.py  # Advanced signals
│   ├── ml_models/
│   │   └── ensemble.py          # ML ensemble models
│   ├── risk/
│   │   ├── position_sizing.py   # Position sizing logic
│   │   └── risk_manager.py      # Risk management
│   ├── execution/
│   │   └── executor.py          # Order execution
│   ├── strategies/
│   │   └── multi_timeframe.py   # Multi-timeframe analysis
│   ├── analytics/
│   │   └── performance.py       # Performance analytics
│   ├── alerts/
│   │   └── notifier.py          # Alert system
│   └── main.py                  # Main bot engine
├── data/                        # Database and historical data
├── logs/                        # Log files
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/aliatmaca1915-lab/crypto-trading-bot.git
   cd crypto-trading-bot
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot**
   Edit `config/config.yaml` to customize settings (see Configuration section)

## ⚙️ Configuration

Edit `config/config.yaml`:

### Trading Mode
```yaml
mode: "paper"  # Options: "paper" (safe, default) or "real" (requires API keys)
```

### API Credentials (for real trading only)
```yaml
api:
  binance:
    api_key: "YOUR_BINANCE_API_KEY"
    api_secret: "YOUR_BINANCE_API_SECRET"
    testnet: true  # Use testnet for testing
```

### Capital Settings
```yaml
capital:
  initial_capital: 10000  # Initial capital in USDT
  position_limit_per_coin: 0.05  # 5% of capital per coin
  daily_loss_limit: 0.05  # 5% daily loss limit
  weekly_loss_limit: 0.10  # 10% weekly loss limit
```

### Cryptocurrencies
```yaml
cryptocurrencies:
  - "BTC/USDT"
  - "ETH/USDT"
  - "BNB/USDT"
  - "XRP/USDT"
  - "ADA/USDT"
  - "SOL/USDT"
  - "DOGE/USDT"
  - "DOT/USDT"
  - "LTC/USDT"
```

### Notifications
```yaml
notifications:
  telegram:
    enabled: false
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
  discord:
    enabled: false
    webhook_url: "YOUR_WEBHOOK_URL"
```

## 🚀 Usage

### Start the Bot

**Paper Trading (Default - No Risk)**
```bash
python src/main.py
```

**Real Trading (⚠️ Use with Caution)**
1. Set `mode: "real"` in config.yaml
2. Configure Binance API credentials
3. Start the bot:
   ```bash
   python src/main.py
   ```

### Monitor the Bot

The bot will:
1. ✅ Analyze all configured cryptocurrencies
2. ✅ Calculate scores using advanced algorithms
3. ✅ Check multi-timeframe alignment
4. ✅ Run ML predictions
5. ✅ Execute risk checks
6. ✅ Place trades if all conditions are met
7. ✅ Monitor positions for stop-loss/take-profit
8. ✅ Send notifications for important events
9. ✅ Generate daily performance reports

### Stop the Bot

Press `Ctrl+C` for graceful shutdown

## 📊 Advanced Scoring Algorithm

The bot uses a comprehensive 100-point scoring system:

### Technical Indicators (45 points)
| Indicator | Max Points | Description |
|-----------|------------|-------------|
| RSI | 8 | Relative Strength Index analysis |
| MACD | 8 | Trend and momentum detection |
| Bollinger Bands | 7 | Volatility and squeeze detection |
| EMA/SMA | 8 | Trend strength analysis |
| Stochastic | 7 | Momentum reversal signals |
| ATR | 7 | Volatility assessment |

### Market Intelligence (30 points)
| Component | Max Points | Description |
|-----------|------------|-------------|
| Fear/Greed Index | 10 | Market sentiment |
| On-Chain Metrics | 8 | Whale activity, holder distribution |
| Funding Rates | 6 | Futures market sentiment |
| Liquidation Levels | 6 | Support/resistance zones |

### Advanced Signals (25 points)
| Signal | Max Points | Description |
|--------|------------|-------------|
| Divergence | 8 | Price vs indicator divergence |
| Order Book Imbalance | 8 | Bid/ask pressure analysis |
| Volume Profile | 9 | Volume-based support levels |

**Minimum Threshold**: 60 points required for ANY trade

## 💰 Position Sizing & Leverage

### Fixed 10x Leverage System

| Classification | Score Range | Base % | Leverage | Effective Position | Risk/Trade |
|----------------|-------------|--------|----------|-------------------|------------|
| 🥈 SILVER | 60-79 | 10% | 10x | 100% | 2-3% |
| 🥇 GOLD | 80-89 | 15% | 10x | 150% | 3-4% |
| 💎 DIAMOND | 90-100 | 20% | 10x | 200% | 4-5% |

### Example Calculation
- **Capital**: $10,000
- **Classification**: GOLD (85 points)
- **Base Amount**: $10,000 × 15% = $1,500
- **Leveraged Position**: $1,500 × 10x = $15,000
- **Effective Position**: 150% of capital

## 🛡️ Risk Management

### Liquidation Protection
- Minimum liquidation buffer: 3-5%
- Continuous monitoring
- Automatic position adjustment

### Stop-Loss System
- Dynamic ATR-based calculation
- Support level detection
- Trailing stop option

### Take-Profit Strategy
- **TP1**: 40% of position at 60% of target
- **TP2**: 30% of position at 100% of target
- **TP3**: 30% of position at 150% of target

### Portfolio Limits
- Max 5 concurrent positions
- Max 5% capital per coin
- Correlation-based limits
- Daily loss limit: 5%
- Weekly loss limit: 10%

### Emergency Shutdown
- Triggers at 15% total capital loss
- Automatic position closing
- Alert notifications

## 📈 Performance Metrics

The bot tracks comprehensive performance metrics:

- **Win Rate**: Percentage of winning trades
- **Sharpe Ratio**: Risk-adjusted returns
- **Sortino Ratio**: Downside deviation focus
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Profit Factor**: Gross profit / gross loss
- **Calmar Ratio**: Annual return / max drawdown
- **Recovery Factor**: Net profit / max drawdown

## 🔔 Notifications

Configure alerts for:

### Trade Alerts
- New position opened
- Position closed
- Stop-loss triggered
- Take-profit hit

### Risk Alerts
- High drawdown warning
- Loss limit approached
- Liquidation risk
- Margin call warning

### System Alerts
- Bot started/stopped
- Connection issues
- API errors
- Daily performance summary

## 📁 Database

All trades, signals, and metrics are stored in SQLite database:
- **Trades**: Entry/exit prices, PnL, classification
- **Signals**: Scores, timeframe analysis, decisions
- **Performance**: Daily/weekly/monthly metrics

Database location: `data/trading_bot.db`

## 🔧 Development

### Project Structure
The codebase is modular and well-organized:
- Each component is independent and testable
- Clear separation of concerns
- Extensible architecture for new strategies

### Adding New Indicators
1. Add indicator calculation to `src/indicators/technical.py`
2. Add scoring logic to scoring method
3. Update configuration in `config.yaml`

### Adding New Strategies
1. Create new strategy file in `src/strategies/`
2. Implement strategy logic
3. Integrate with main bot engine

## ⚠️ Disclaimer

**IMPORTANT**: Cryptocurrency trading involves substantial risk of loss. This bot is provided for educational and research purposes only.

- **Not Financial Advice**: This bot does not provide financial advice
- **Use at Your Own Risk**: Trading cryptocurrencies carries high risk
- **No Guarantees**: Past performance does not guarantee future results
- **Test Thoroughly**: Use paper trading mode extensively before real trading
- **Start Small**: Begin with small amounts in real trading
- **Monitor Actively**: Never leave the bot completely unattended in real trading mode

**The authors and contributors are not responsible for any financial losses incurred through the use of this software.**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review configuration examples

## 🙏 Acknowledgments

- Binance API for market data
- Technical indicator libraries
- Open-source cryptocurrency trading community

---

**Made with ❤️ for the crypto trading community**

**Remember**: Always use paper trading mode first, and never trade more than you can afford to lose!
