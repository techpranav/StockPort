# Stockport v4 - Automated Quantitative Trading Platform

A fully automated, always-on quantitative trading platform designed for personal hedge-fund-style trading. Stockport v4 transforms from an analysis tool into a complete trading system with real-time market scanning, strategy evaluation, capital management, risk controls, and automated execution.

## 🎯 Overview

Stockport v4 is a production-ready, enterprise-grade quantitative trading platform that:

- **Continuously scans** the entire stock universe in parallel
- **Detects high-quality** trading opportunities using multiple strategies
- **Manages capital and risk** intelligently with real-time tracking
- **Executes trades** automatically with strict safety controls
- **Learns from performance** and improves strategy selection over time
- **Provides explainability** for all trading decisions
- **Maintains complete audit trails** for compliance and analysis

## ✨ Key Features

### 🏗️ Core Architecture

#### Always-On Backend
- **Daemon-based system** that runs continuously, independent of UI
- **Event-driven architecture** using Redis pub/sub for scalability
- **State persistence** with SQLite (default) and PostgreSQL support
- **Distributed task processing** with Celery workers
- **Auto-recovery** from crashes with state restoration

#### Data Integrity Layer
- **Multi-layer validation** - Validates all incoming market data
- **Anomaly detection** - Detects price spikes, missing candles, bad ticks
- **Corporate actions handling** - Adjusts for splits, dividends
- **Price reconciliation** - Reconciles provider vs broker prices
- **Health monitoring** - GREEN/YELLOW/RED status for all data sources
- **Truth layer** - Single source of truth for market prices

#### Market State Engine
- **Regime detection** - Identifies trending, choppy, volatile markets
- **Volatility analysis** - Uses VIX and ATR for volatility state
- **Breadth analysis** - Advance/decline ratio for market breadth
- **Liquidity detection** - Monitors overall market liquidity
- **State publishing** - Real-time market state updates via Redis

### 📊 Strategy System

#### Pluggable Strategies
- **YAML-based definitions** - Easy strategy creation and modification
- **Strategy registry** - Manages active and inactive strategies
- **Multiple strategy types**:
  - Trend following
  - Momentum trading
  - Mean reversion
  - Breakout strategies
  - Options strategies (extensible)
- **Regime-aware** - Strategies adapt to market conditions
- **Backtestable** - All strategies can be backtested

#### Strategy Evaluation
- **Parallel evaluation** - Evaluates opportunities against all active strategies
- **Scoring system** - Multi-factor weighted scoring
- **Confidence levels** - Calculates confidence for each signal
- **Entry/exit rules** - Explicit entry and exit conditions
- **Stop loss logic** - Strategy-specific stop loss rules

### 💰 Capital & Risk Management

#### Capital Management
- **Real-time tracking** - Tracks total, allocated, reserved, and available capital
- **Dynamic allocation** - Allocates capital based on risk and opportunity
- **Position sizing** - Risk-based position sizing with multiple methods:
  - Risk-based (default)
  - Fixed amount
  - Volatility-based
- **Settings-driven** - All capital parameters configurable via settings

#### Risk Management
- **Per-trade limits** - Maximum risk per trade (default: 2% of capital)
- **Daily loss limits** - Maximum daily loss (default: 5% of capital)
- **Sector exposure limits** - Maximum exposure per sector (default: 25%)
- **Correlation checking** - Prevents overexposure to correlated positions
- **Kill-switch** - Emergency stop mechanism
- **Drawdown protection** - Automatic position reduction during drawdowns

### 🔍 Market Scanning

#### Continuous Scanning
- **Parallel processing** - Scans multiple symbols simultaneously
- **Pre-filters** - Filters by liquidity, price, market cap before analysis
- **Rate limiting** - Celery workers with configurable rate limits
- **Data integrity** - Only processes validated data
- **Opportunity scoring** - Pre-filters opportunities by quality

#### Scanner Types
- **Market scanner** - General market opportunity scanner
- **Sector scanner** - Sector-specific scanning (extensible)
- **Event-driven scanner** - News and event-based opportunities (extensible)
- **Options scanner** - Options-specific opportunities (extensible)

### 🎯 Decision Engine

#### Intelligent Decision Making
- **Multi-factor analysis** - Integrates capital, risk, portfolio, and market state
- **Timing awareness** - Rejects stale signals and opportunities
- **Portfolio fit** - Evaluates how new positions fit existing portfolio
- **Risk-reward analysis** - Calculates risk-reward ratios
- **Decision types**: APPROVE, REJECT, MODIFY

#### Decision Factors
- Capital availability
- Risk limits compliance
- Portfolio diversification
- Market regime alignment
- Signal freshness
- Data quality

### ⚡ Execution Engine

#### Order Management
- **Broker-agnostic** - Abstract interface for multiple brokers
- **Order lifecycle** - Tracks orders from creation to fill
- **Safety checks** - Pre-execution validation
- **Slippage handling** - Accounts for execution slippage
- **Fill tracking** - Monitors order fills and partial fills

#### Execution Modes
- **Paper trading** - Test strategies without real money
- **Assisted trading** - Manual approval required
- **Fully automated** - Automatic execution (with safety controls)

### 📈 Portfolio Intelligence

#### Portfolio Management
- **Real-time tracking** - Tracks all open positions
- **Exposure analysis** - Sector, factor, and correlation exposure
- **Diversification scoring** - Ensures portfolio diversification
- **Opportunity ranking** - Ranks opportunities by portfolio fit
- **Rebalancing** - Suggests portfolio rebalancing (extensible)

### ⏱️ Timing Awareness

#### Signal Freshness
- **Signal expiry** - Strategy-specific expiry times
- **Stale detection** - Detects stale opportunities and signals
- **Latency tracking** - Tracks latency across trading pipeline
- **Time-based rejection** - Rejects signals that are too old

### 🧠 Learning & Attribution

#### Performance Tracking
- **Strategy performance** - Tracks win rate, profit factor, Sharpe ratio
- **Trade attribution** - Attributes trades to entry/exit reasons
- **Indicator contribution** - Analyzes which indicators contributed to signals
- **Failure classification** - Classifies trade failures for learning
- **Decay detection** - Detects when strategies are underperforming

#### Learning System
- **Performance metrics**:
  - Win rate
  - Profit factor
  - Sharpe ratio
  - Sortino ratio
  - Calmar ratio
  - Max drawdown
  - Annualized return
- **Strategy weighting** - Adjusts strategy weights based on performance
- **Auto-disable** - Automatically disables poor-performing strategies

### 👻 Shadow Trading

#### Parallel Testing
- **Shadow engine** - Executes strategies in parallel without risking capital
- **Isolation layer** - Prevents shadow strategies from executing live trades
- **Comparison engine** - Compares shadow vs live performance
- **Activation recommendations** - Suggests when to activate shadow strategies

### 🔍 Explainability

#### Decision Explanations
- **Human-readable explanations** - Explains why trades were made
- **Confidence scoring** - Calculates confidence for each decision
- **Uncertainty quantification** - Quantifies uncertainty in decisions
- **Invalidation conditions** - Lists what could invalidate a trade

### 🛡️ Governance & Resilience

#### Audit & Compliance
- **Comprehensive audit trail** - Logs all decisions and executions
- **Event logging** - Logs opportunity discovery, signal generation, decisions, executions
- **Audit database** - Persistent storage of all audit logs
- **Query interface** - Query audit logs by event type, date, symbol

#### Operational Resilience
- **Heartbeat monitoring** - Monitors service health
- **Auto-restart** - Automatically restarts failed services
- **State recovery** - Recovers state after crashes
- **Duplicate prevention** - Idempotency keys prevent duplicate orders
- **Safe shutdown** - Graceful shutdown with state saving

### ⚙️ Settings System

#### Enterprise Configuration
- **25+ configurable settings** - All thresholds, timings, amounts configurable
- **Real-time updates** - Settings changes apply immediately (no restart)
- **Category organization** - Settings organized by category:
  - Capital settings
  - Risk settings
  - Trading settings
  - Data settings
  - Timing settings
  - Performance settings
- **Validation** - Type and range validation for all settings
- **Default values** - Sensible defaults for all settings

### 🌐 API Infrastructure

#### REST API
- **System status** - Get system status and health
- **Commands** - Execute system commands (start, stop, pause)
- **Positions** - Get current positions
- **Orders** - Get order history and status
- **Settings** - Get and update settings
- **Performance** - Get strategy performance metrics

#### WebSocket Server
- **Real-time updates** - Push updates to connected clients
- **Event streaming** - Streams opportunities, signals, decisions, executions
- **Settings updates** - Real-time settings change notifications
- **Market state** - Real-time market state updates

### 🖥️ UI Components

#### Control Room Dashboard
- **System status** - Real-time system status and health
- **Capital overview** - Total, allocated, reserved, available capital
- **Risk metrics** - Current exposure, daily loss, drawdown
- **Active opportunities** - Real-time opportunity stream
- **Recent signals** - Latest trading signals
- **Open positions** - Current positions with P&L
- **Performance chart** - Portfolio value over time
- **Market state** - Regime, volatility, breadth, liquidity
- **Data health** - GREEN/YELLOW/RED status indicators

#### Scanner View
- **Opportunity stream** - Real-time opportunity feed
- **Filters** - Sector, score, volume, market cap filters
- **Opportunity details** - Detailed opportunity information
- **Explanation display** - Why this opportunity, what could invalidate it
- **Pre-filter statistics** - Scanner performance metrics

#### Strategies Panel
- **Strategy list** - All strategies with status and performance
- **Strategy controls** - Activate, pause, disable strategies
- **Performance metrics** - Win rate, profit factor, Sharpe ratio
- **Performance charts** - Win rate and profit factor over time
- **Backtesting lab** - Backtest strategies on historical data
- **Shadow comparison** - Compare shadow vs live performance

#### Portfolio View
- **Capital breakdown** - Detailed capital allocation
- **Position list** - All open positions with details
- **Sector allocation** - Pie chart of sector exposure
- **Risk metrics** - Portfolio-level risk metrics
- **Correlation matrix** - Position correlation analysis
- **Export** - Export portfolio reports

#### Execution View
- **Pending orders** - Orders awaiting execution
- **Order history** - Historical order execution
- **Execution log** - Real-time execution events
- **Fill statistics** - Slippage, fill rate, fill time

#### Settings Panel
- **Category-based organization** - Settings grouped by category
- **Real-time updates** - Changes apply immediately
- **Input validation** - Type and range validation
- **Reset to defaults** - Reset individual or all settings
- **Export/Import** - Export and import settings

## 🏛️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Stockport v4 System                       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────┐    ┌─────────▼─────────┐   ┌──────▼──────┐
│   UI Layer   │    │   API Gateway      │   │  Workers    │
│  (Streamlit) │    │  (FastAPI)         │   │  (Celery)   │
│              │    │  - REST API        │   │  - Scanner  │
│  - Dashboard │    │  - WebSocket       │   │  - Evaluator│
│  - Scanner   │    │  - Real-time       │   │  - Executor │
│  - Strategies│    │    Updates         │   │             │
│  - Portfolio │    │                    │   │             │
│  - Execution │    │                    │   │             │
└───────┬──────┘    └─────────┬─────────┘   └──────┬──────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Trading Engine   │
                    │  (Orchestrator)   │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────┐    ┌─────────▼─────────┐   ┌──────▼──────┐
│   Scanner    │    │   Strategy        │   │  Decision   │
│   System     │    │   Evaluator       │   │  Engine     │
│              │    │                   │   │             │
│  - Market    │    │  - Registry       │   │  - Capital  │
│  - Sector    │    │  - Loader         │   │  - Risk     │
│  - Event     │    │  - Evaluator      │   │  - Portfolio│
│              │    │  - Strategies     │   │  - Timing   │
└───────┬──────┘    └─────────┬─────────┘   └──────┬──────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Execution Engine │
                    │                   │
                    │  - Order Manager  │
                    │  - Safety Checks  │
                    │  - Broker Adapter │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────┐    ┌─────────▼─────────┐   ┌──────▼──────┐
│   Learning   │    │   Governance      │   │   Data      │
│   System     │    │   & Resilience    │   │   Integrity │
│              │    │                   │   │             │
│  - Perf.     │    │  - Audit Logger   │   │  - Validator│
│  - Decay     │    │  - Heartbeat      │   │  - Anomaly  │
│  - Attribution│   │  - Recovery      │   │  - Health   │
│              │    │  - Duplicate      │   │  - Truth    │
│              │    │    Prevention     │   │    Layer    │
└──────────────┘    └───────────────────┘   └─────────────┘
```

### Data Flow

```
Market Data
    │
    ▼
Data Integrity Layer (Validation, Anomaly Detection, Health Monitoring)
    │
    ▼
Truth Layer (Single Source of Truth)
    │
    ▼
Market Scanner (Parallel Scanning)
    │
    ▼
Opportunities
    │
    ▼
Strategy Evaluator (Evaluate against all active strategies)
    │
    ▼
Strategy Signals
    │
    ▼
Decision Engine (Capital + Risk + Portfolio + Timing)
    │
    ▼
Trading Decisions (APPROVE/REJECT/MODIFY)
    │
    ▼
Execution Engine (Safety Checks + Order Management)
    │
    ▼
Broker (Paper/Live)
    │
    ▼
Order Execution
    │
    ▼
Performance Tracker (Record Trade)
    │
    ▼
Learning System (Update Strategy Weights)
```

### Component Architecture

#### Backend Structure
```
backend/
├── core/                    # Core orchestration
│   ├── engine.py           # Main trading engine
│   ├── event_bus.py        # Redis pub/sub messaging
│   ├── state_manager.py     # State persistence
│   └── decision_engine.py  # Decision making
├── data/
│   └── integrity/          # Data integrity layer
│       ├── data_validator.py
│       ├── anomaly_detector.py
│       ├── health_monitor.py
│       └── truth_layer.py
├── market_state/           # Market state engine
│   ├── state_engine.py
│   ├── regime_detector.py
│   ├── volatility_detector.py
│   └── breadth_detector.py
├── strategies/             # Strategy system
│   ├── registry.py
│   ├── loader.py
│   ├── base_strategy.py
│   └── evaluator.py
├── portfolio/              # Portfolio management
│   ├── portfolio_manager.py
│   ├── exposure_tracker.py
│   └── diversification_engine.py
├── capital/                # Capital management
│   ├── capital_manager.py
│   └── position_sizer.py
├── risk/                   # Risk management
│   ├── risk_engine.py
│   ├── limits.py
│   └── kill_switch.py
├── execution/              # Execution engine
│   ├── execution_engine.py
│   ├── order_manager.py
│   └── brokers/
├── timing/                 # Timing awareness
│   ├── signal_expiry.py
│   └── stale_detector.py
├── learning/               # Learning system
│   ├── performance_tracker.py
│   └── decay_detector.py
├── attribution/            # Trade attribution
│   ├── attribution_engine.py
│   └── failure_classifier.py
├── shadow/                 # Shadow trading
│   ├── shadow_engine.py
│   └── comparison_engine.py
├── explainability/         # Explainability
│   ├── explainer_engine.py
│   └── decision_explainer.py
├── governance/             # Governance
│   └── audit_logger.py
├── resilience/             # Operational resilience
│   ├── state_recovery.py
│   └── duplicate_prevention.py
├── api/                    # API layer
│   ├── rest_api.py
│   └── websocket_server.py
├── workers/                # Celery workers
│   └── scanner_worker.py
└── settings/               # Settings system
    ├── settings_manager.py
    └── settings_adapter.py
```

## 🧪 Testing

### Test Infrastructure

- **Unit Tests** - Test individual components in isolation
- **Integration Tests** - Test end-to-end flows
- **Coverage Reporting** - 70% minimum coverage threshold
- **CI/CD Integration** - Automated testing on push/PR
- **Test Fixtures** - Comprehensive shared fixtures

### Test Suites

#### Unit Tests
- Data integrity layer
- Market state engine
- Capital manager
- Risk engine
- Position sizer

#### Integration Tests
- End-to-end flow (scanner → execution)
- Disaster recovery
- Duplicate prevention
- Audit logging

### Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest tests/ --cov=backend --cov=ui --cov=models --cov-report=html

# Using Makefile
make test              # All tests
make test-unit         # Unit tests
make test-integration  # Integration tests
make test-coverage     # With coverage
```

## 📁 Project Structure

```
stockport/
├── backend/                 # Backend trading system
│   ├── core/               # Core orchestration
│   ├── data/               # Data integrity
│   ├── market_state/       # Market state engine
│   ├── strategies/         # Strategy system
│   ├── portfolio/          # Portfolio management
│   ├── capital/            # Capital management
│   ├── risk/               # Risk management
│   ├── execution/          # Execution engine
│   ├── timing/             # Timing awareness
│   ├── learning/           # Learning system
│   ├── attribution/        # Trade attribution
│   ├── shadow/             # Shadow trading
│   ├── explainability/     # Explainability
│   ├── governance/         # Governance
│   ├── resilience/         # Operational resilience
│   ├── api/                # API layer
│   ├── workers/            # Celery workers
│   └── settings/           # Settings system
├── ui/                     # User interface
│   ├── dashboard.py        # Main dashboard
│   ├── scanner_view.py     # Scanner view
│   ├── strategies_panel.py # Strategies panel
│   ├── portfolio_view.py   # Portfolio view
│   ├── execution_view.py   # Execution view
│   ├── settings_panel.py   # Settings panel
│   └── services/           # UI services
├── models/                 # Data models
│   ├── opportunity.py
│   ├── strategy_signal.py
│   └── trading_decision.py
├── config/                 # Configuration
│   ├── app_config.py
│   └── constants/
├── database/               # Database setup
│   ├── init_db.py
│   └── connection.py
├── tests/                  # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/                   # Documentation
├── pytest.ini             # Pytest configuration
├── Makefile               # Test commands
└── requirements.txt       # Dependencies
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Redis (for event bus and Celery)
- PostgreSQL (optional, SQLite default)
- Git

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/stockport.git
cd stockport
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up database:**
```bash
# SQLite (default)
python database/init_db.py

# PostgreSQL (optional)
python database/setup_postgresql.py
```

5. **Configure Redis:**
```bash
# Update config/app_config.py with Redis connection details
# Default: localhost:6379
```

6. **Start Redis:**
```bash
# Linux/Mac
redis-server

# Windows
# Install Redis from https://redis.io/download
```

## 🎮 Usage

### Starting the System

1. **Start the backend:**
```bash
python -m backend.core.engine
```

2. **Start Celery workers:**
```bash
celery -A backend.workers.scanner_worker worker --loglevel=info
```

3. **Start the API server:**
```bash
uvicorn backend.api.rest_api:app --reload
```

4. **Start the UI:**
```bash
streamlit run app.py
```

### Accessing the System

- **UI**: http://localhost:8501
- **REST API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

## ⚙️ Configuration

### Settings System

All system parameters are configurable via the Settings UI or REST API:

- **Capital Settings**: Initial capital, cash reserve
- **Risk Settings**: Per-trade risk, daily loss limits, sector exposure
- **Trading Settings**: Default risk per trade, max position size
- **Data Settings**: Min volume, min price, min market cap
- **Timing Settings**: Signal expiry times, latency budgets
- **Performance Settings**: Decay detection thresholds

### Environment Variables

```bash
# Database
DATABASE_TYPE=sqlite  # or postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=admin
DATABASE_NAME=stockport

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## 📊 Performance Metrics

The system tracks comprehensive performance metrics:

- **Win Rate** - Percentage of winning trades
- **Profit Factor** - Gross profit / Gross loss
- **Sharpe Ratio** - Risk-adjusted returns
- **Sortino Ratio** - Downside risk-adjusted returns
- **Calmar Ratio** - Return / Max drawdown
- **Max Drawdown** - Maximum peak-to-trough decline
- **Annualized Return** - Annualized return rate

## 🔒 Safety Features

- **Kill-switch** - Emergency stop mechanism
- **Daily loss limits** - Automatic trading halt on daily loss
- **Position limits** - Maximum position size per trade
- **Sector limits** - Maximum exposure per sector
- **Correlation limits** - Prevents overexposure to correlated positions
- **Stale signal rejection** - Rejects outdated signals
- **Data quality checks** - Only trades on validated data
- **Audit trail** - Complete logging of all decisions

## 📚 Documentation

- **Architecture**: See `docs/STOCKPORT_V4_COMPLETE.md`
- **API Documentation**: http://localhost:8000/docs
- **Test Documentation**: See `tests/README.md`
- **Settings Documentation**: See `docs/SETTINGS_SYSTEM.md`

## 🧪 Testing

See `tests/README.md` for comprehensive testing documentation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Status

**Production Ready** ✅

- All 91 todos completed (100%)
- Comprehensive test coverage
- Full audit trail
- Complete documentation
- CI/CD integration

## 🙏 Acknowledgments

Built with:
- Python 3.8+
- Streamlit (UI)
- FastAPI (API)
- Celery (Task Queue)
- Redis (Event Bus)
- PostgreSQL/SQLite (Database)
- Pandas, NumPy (Data Processing)
- Plotly (Visualization)
