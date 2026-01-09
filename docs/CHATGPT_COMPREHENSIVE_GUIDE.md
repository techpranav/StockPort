# Stockport v4 - Comprehensive Guide for AI Assistants

This document provides a complete overview of the Stockport v4 system for AI assistants (like ChatGPT) to understand the entire codebase, architecture, features, and implementation details.

## Table of Contents

1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Backend Components](#backend-components)
5. [Frontend Components](#frontend-components)
6. [UI Navigation & Layout](#ui-navigation--layout)
7. [Data Flow](#data-flow)
8. [API Structure](#api-structure)
9. [Key Features](#key-features)
10. [File Structure](#file-structure)
11. [Configuration](#configuration)
12. [Development Workflow](#development-workflow)

---

## System Overview

**Stockport v4** is a fully automated, always-on stock analysis and trading system designed for personal use. It functions as a "trading brain" that continuously scans the market, evaluates opportunities, manages capital and risk, and can execute trades automatically.

### Core Philosophy

- **Always-on Backend**: System runs continuously, independent of UI
- **Event-driven Architecture**: Components communicate via Redis pub/sub
- **Capital-aware Decisions**: Every decision considers available capital and risk limits
- **Multi-strategy Evaluation**: Opportunities evaluated across multiple strategies
- **Learning System**: Tracks performance and improves strategy selection over time
- **Safety First**: Multiple layers of risk management and kill-switch mechanisms

### System Modes

1. **Manual Mode**: System analyzes but requires manual approval for trades
2. **Semi-Auto Mode**: System generates signals, user approves before execution
3. **Full-Auto Mode**: System analyzes, decides, and executes automatically (with safety checks)

---

## Technology Stack

### Backend

- **Python 3.8+**: Core programming language
- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server for FastAPI
- **Redis**: Event bus and pub/sub messaging
- **SQLite/PostgreSQL**: Persistent storage (SQLite default, PostgreSQL optional)
- **Celery**: Distributed task queue for background processing
- **Pydantic**: Data validation and settings management

### Frontend

- **Streamlit**: Web UI framework
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing

### Data & Analysis

- **yfinance**: Yahoo Finance data provider
- **jugaad-data**: NSE data provider
- **nsepython**: NSE Python library
- **smartapi**: Angel One SmartAPI integration
- **pandas, numpy, scipy**: Data analysis and technical indicators

### Infrastructure

- **Redis**: Event bus, caching, pub/sub
- **PostgreSQL**: Production database (optional)
- **SQLite**: Development database (default)

### Documentation

- **MkDocs**: Documentation framework
- **Material Theme**: MkDocs theme

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (v4)                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Multi-page Navigation                            │  │
│  │  - Dashboard, Scanner, Strategies, Portfolio,    │  │
│  │    Execution, Settings                            │  │
│  └──────────────────┬────────────────────────────────┘  │
│                     │ HTTP/REST                         │
└─────────────────────┼───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Backend REST API (FastAPI)                 │
│              http://localhost:8001                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Endpoints:                                        │  │
│  │  - /status, /capital/overview, /opportunities     │  │
│  │  - /signals, /strategies/performance              │  │
│  │  - /market/state, /data/health                    │  │
│  │  - /positions, /orders                           │  │
│  │  - /settings/*                                    │  │
│  └──────────────────┬────────────────────────────────┘  │
│                     │                                    │
└─────────────────────┼───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│           System Integrator (Orchestrator)              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Coordinates all system components                │  │
│  └──────────────────┬────────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────┼────────────────────────────────┐  │
│  │                  │                                  │  │
│  ▼                  ▼                  ▼               │  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │ Scanner  │  │ Strategy │  │ Decision │             │  │
│  │          │  │ Evaluator│  │ Engine   │             │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │  │
│       │             │              │                   │  │
│       └─────────────┼──────────────┘                   │  │
│                     │                                  │  │
│                     ▼                                  │  │
│              ┌──────────────┐                          │  │
│              │  Execution   │                          │  │
│              │   Engine     │                          │  │
│              └──────────────┘                          │  │
└─────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Supporting Systems                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │ Capital  │  │   Risk   │  │ Portfolio│             │  │
│  │ Manager  │  │  Engine   │  │ Manager  │             │  │
│  └──────────┘  └──────────┘  └──────────┘             │  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  Market  │  │   Data   │  │ Learning │             │  │
│  │  State   │  │ Integrity│  │  System  │             │  │
│  └──────────┘  └──────────┘  └──────────┘             │  │
└─────────────────────────────────────────────────────────┘
```

### Component Communication

- **Event Bus (Redis)**: Pub/sub messaging between components
- **REST API**: HTTP interface for UI and external systems
- **WebSocket**: Real-time updates (planned)
- **State Manager**: Persistent state storage
- **Audit Logger**: Comprehensive audit trail

---

## Backend Components

### Core Components

#### 1. Trading Engine (`backend/core/engine.py`)
- Main orchestrator
- Coordinates scanners, evaluators, decision engine, execution
- Manages system state (running/stopped, mode)
- Entry point for system operations

#### 2. Event Bus (`backend/core/event_bus.py`)
- Redis-based pub/sub messaging
- Channels: `opportunities`, `signals`, `decisions`, `executions`, `market_state`
- Enables decoupled component communication

#### 3. State Manager (`backend/core/state_manager.py`)
- Persists system state (SQLite/PostgreSQL)
- Tracks: running status, mode, positions, capital
- Enables state recovery after crashes

#### 4. Decision Engine (`backend/core/decision_engine.py`)
- Integrates capital, risk, portfolio, market state
- Makes trading decisions (APPROVE/REJECT/MODIFY)
- Considers: capital availability, risk limits, portfolio fit, market regime
- Generates reasoning for each decision

### Data Integrity Layer

#### 1. Truth Layer (`backend/data/integrity/truth_layer.py`)
- Single source of truth for market prices
- Reconciles prices from multiple providers
- Handles corporate actions

#### 2. Health Monitor (`backend/data/integrity/health_monitor.py`)
- Monitors data quality (GREEN/YELLOW/RED)
- Tracks provider health
- Alerts on data issues

#### 3. Data Validator (`backend/data/integrity/data_validator.py`)
- Validates incoming market data
- Checks for anomalies (spikes, gaps, bad ticks)
- Ensures data quality before use

### Market State Engine

#### Market State Engine (`backend/market_state/state_engine.py`)
- Detects market regime (trending_up, trending_down, choppy, volatile)
- Monitors volatility (VIX, ATR)
- Tracks market breadth (advance/decline)
- Assesses liquidity
- Publishes state updates via event bus

### Strategy System

#### 1. Strategy Registry (`backend/strategies/registry.py`)
- Manages active/inactive strategies
- Loads strategies from YAML files
- Tracks strategy metadata

#### 2. Strategy Evaluator (`backend/strategies/evaluator.py`)
- Evaluates opportunities against all active strategies
- Filters by market regime applicability
- Generates signals with scores and confidence

#### 3. Strategy Base Class (`backend/strategies/base_strategy.py`)
- Abstract base for all strategies
- Defines: entry rules, exit rules, stop loss, position sizing
- Regime awareness

### Capital & Risk Management

#### 1. Capital Manager (`backend/capital/capital_manager.py`)
- Tracks: total, allocated, reserved, available capital
- Manages capital allocation/deallocation
- Real-time capital state

#### 2. Position Sizer (`backend/capital/position_sizer.py`)
- Risk-based position sizing
- Calculates shares based on risk amount
- Considers stop loss and available capital

#### 3. Risk Engine (`backend/risk/risk_engine.py`)
- Enforces risk limits (per-trade, daily, sector)
- Checks correlation
- Monitors drawdown
- Kill-switch mechanism

### Scanners

#### Market Scanner (`backend/scanners/market_scanner.py`)
- Scans stock universe in parallel
- Applies pre-filters (liquidity, volatility, volume)
- Emits opportunities
- Rate-limited via Celery workers

### Execution

#### 1. Execution Engine (`backend/execution/execution_engine.py`)
- Executes trading decisions
- Safety checks before execution
- Order lifecycle management
- Broker-agnostic interface

#### 2. Order Manager (`backend/execution/order_manager.py`)
- Tracks order status
- Manages order history
- Handles fills and partial fills

#### 3. Brokers
- **Paper Broker** (`backend/execution/brokers/paper_broker.py`): Paper trading
- **Shadow Broker** (`backend/shadow/shadow_broker.py`): Shadow trading
- **Real Brokers**: Abstract interface for real brokers

### Learning System

#### Performance Tracker (`backend/learning/performance_tracker.py`)
- Tracks strategy performance metrics
- Calculates: win rate, profit factor, Sharpe ratio, drawdown
- Stores historical performance

#### Attribution Engine (`backend/learning/attribution_engine.py`)
- Explains why strategies succeed/fail
- Analyzes indicator contributions
- Classifies failures

### Governance & Resilience

#### 1. Audit Logger (`backend/governance/audit_logger.py`)
- Comprehensive audit trail
- Logs: opportunities, signals, decisions, executions
- SQLite/PostgreSQL storage
- Queryable by event type, date, symbol

#### 2. Heartbeat Monitor (`backend/resilience/heartbeat_monitor.py`)
- Monitors service health
- Auto-restart on failures
- Health status reporting

#### 3. State Recovery (`backend/resilience/state_recovery.py`)
- Recovers state after crashes
- Restores positions, capital, orders
- Ensures continuity

---

## Frontend Components

### UI Architecture

```
app.py (Entry Point)
  └── ui/app_v4.py (Main App)
      ├── Sidebar Navigation
      └── Page Router
          ├── Dashboard (ui/dashboard.py)
          ├── Scanner View (ui/scanner_view.py)
          ├── Strategies Panel (ui/strategies_panel.py)
          ├── Portfolio View (ui/portfolio_view.py)
          ├── Execution View (ui/execution_view.py)
          └── Settings Panel (ui/settings_panel.py)
```

### Data Service Layer

```
UI Components
  └── UIDataService (ui/services/ui_data_service.py)
      └── APIClient (ui/services/api_client.py)
          └── REST API (backend/api/rest_api.py)
```

### Component Details

#### 1. Dashboard (`ui/dashboard.py`)
**Purpose**: Main control room view

**Sections**:
- System Status: Running/stopped, mode indicator
- Capital Overview: Total, available, allocated, reserved, daily P&L
- Risk Metrics: Current exposure, daily loss, drawdown
- Active Opportunities: Top opportunities with scores
- Recent Signals: Latest signals with decisions
- Open Positions: Current positions with P&L
- Performance Chart: Portfolio value over time
- Market State: Regime, volatility, breadth, liquidity
- Data Health: Overall status (GREEN/YELLOW/RED)

**Data Sources**:
- `/status` - System status
- `/capital/overview` - Capital breakdown
- `/opportunities?limit=5` - Top opportunities
- `/signals?limit=10` - Recent signals
- `/positions` - Open positions
- `/market/state` - Market state
- `/data/health` - Data health

#### 2. Scanner View (`ui/scanner_view.py`)
**Purpose**: View market scanning results

**Features**:
- Opportunity stream with real-time updates
- Filters: sector, score, volume, market cap
- Opportunity details: indicators, explanation, invalidation conditions
- Pre-filter statistics

**Data Sources**:
- `/opportunities?limit=50` - Recent opportunities

#### 3. Strategies Panel (`ui/strategies_panel.py`)
**Purpose**: Manage and monitor strategies

**Features**:
- Strategy list with status (active/paused)
- Performance metrics: win rate, profit factor, Sharpe ratio
- Strategy controls: activate/pause
- Performance charts
- Shadow trading comparison
- Backtesting lab

**Data Sources**:
- `/strategies/performance` - Strategy performance metrics

#### 4. Portfolio View (`ui/portfolio_view.py`)
**Purpose**: View portfolio and positions

**Features**:
- Capital breakdown (total, allocated, available, reserved)
- Position list with P&L
- Sector allocation (pie chart)
- Risk metrics
- Correlation matrix
- Export functionality

**Data Sources**:
- `/capital/overview` - Capital breakdown
- `/positions` - Open positions

#### 5. Execution View (`ui/execution_view.py`)
**Purpose**: Monitor order execution

**Features**:
- Pending orders
- Order history
- Execution log
- Fill statistics
- Order details

**Data Sources**:
- `/orders?status=pending` - Pending orders
- `/orders` - All orders

#### 6. Settings Panel (`ui/settings_panel.py`)
**Purpose**: Configure system settings

**Features**:
- Category-based organization
- Real-time updates (no restart required)
- Input validation
- Reset to defaults
- Export/Import settings

**Data Sources**:
- `/settings` - All settings
- `/settings/definitions` - Setting definitions
- `PUT /settings/{key}` - Update setting
- `POST /settings/reset/{key}` - Reset setting

---

## UI Navigation & Layout

### Navigation Structure

```
Sidebar (Always Visible)
├── 📈 Stockport v4 (Title)
├── ─────────────────────
├── Navigation Menu (Radio Buttons)
│   ├── 📊 Dashboard
│   ├── 🔍 Market Scanner
│   ├── ⚙️ Strategies
│   ├── 💼 Portfolio
│   ├── ⚡ Execution
│   └── ⚙️ Settings
├── ─────────────────────
└── System Status
    ├── Status Indicator (🟢 Running / 🔴 Stopped)
    └── Mode (manual/semi_auto/full_auto)
```

### Page Layouts

#### Dashboard Layout
```
┌─────────────────────────────────────────────────┐
│  System Status (Top Bar)                        │
├─────────────────────────────────────────────────┤
│  Capital Overview (4 columns)                   │
│  [Total] [Available] [Allocated] [Daily P&L]   │
├─────────────────────────────────────────────────┤
│  Risk Metrics (3 columns)                       │
│  [Exposure] [Daily Loss] [Drawdown]            │
├─────────────────────────────────────────────────┤
│  Active Opportunities (Table)                   │
│  Symbol | Score | Strategy | Price              │
├─────────────────────────────────────────────────┤
│  Recent Signals (Table)                         │
│  Time | Symbol | Strategy | Decision           │
├─────────────────────────────────────────────────┤
│  Open Positions (Table)                         │
│  Symbol | Qty | Entry | Current | P&L          │
├─────────────────────────────────────────────────┤
│  Performance Chart (Plotly)                     │
│  [Line chart: Portfolio value over time]       │
├─────────────────────────────────────────────────┤
│  Market State (3 columns)                       │
│  [Regime] [Volatility] [Breadth]               │
├─────────────────────────────────────────────────┤
│  Data Health (Status Badge)                     │
│  [GREEN/YELLOW/RED]                            │
└─────────────────────────────────────────────────┘
```

#### Scanner View Layout
```
┌─────────────────────────────────────────────────┐
│  Scanner Status                                 │
│  [Running/Stopped] [Last Scan Time]            │
├─────────────────────────────────────────────────┤
│  Filters (Sidebar or Top)                      │
│  [Sector] [Min Score] [Min Volume] [Market Cap]│
├─────────────────────────────────────────────────┤
│  Opportunity Stream                             │
│  ┌───────────────────────────────────────────┐ │
│  │ AAPL - Score: 85 - $150.25               │ │
│  │ [Expandable Details]                     │ │
│  │  - Indicators                            │ │
│  │  - Explanation                           │ │
│  │  - Invalidation Conditions              │ │
│  └───────────────────────────────────────────┘ │
│  [More opportunities...]                       │
└─────────────────────────────────────────────────┘
```

### Tab Navigation

**No traditional tabs** - Uses Streamlit's sidebar radio buttons for navigation. Each "page" is a separate Python module that renders when selected.

**Navigation Flow**:
1. User selects page from sidebar radio buttons
2. `app_v4.py` routes to corresponding page module
3. Page module renders its content
4. All pages share the same sidebar (persistent navigation)

---

## Data Flow

### Opportunity Discovery Flow

```
Market Scanner
  └── Scans symbols in parallel
      └── Applies pre-filters
          └── Creates Opportunity objects
              └── Publishes to "opportunities" channel (Event Bus)
                  └── Strategy Evaluator subscribes
                      └── Evaluates against all strategies
                          └── Generates Signals
                              └── Publishes to "signals" channel
                                  └── Decision Engine subscribes
                                      └── Makes decision (APPROVE/REJECT)
                                          └── Publishes to "decisions" channel
                                              └── Execution Engine subscribes
                                                  └── Executes if APPROVED
```

### UI Data Flow

```
User Action (UI)
  └── UI Component calls UIDataService
      └── UIDataService calls APIClient
          └── APIClient makes HTTP request to REST API
              └── REST API queries SystemIntegrator components
                  └── Returns JSON response
                      └── APIClient parses response
                          └── UIDataService formats data
                              └── UI Component displays data
```

### Settings Update Flow

```
User updates setting in UI
  └── Settings Panel calls APIClient.update_setting()
      └── PUT /settings/{key} request
          └── REST API updates SettingsManager
              └── SettingsManager validates and saves
                  └── Publishes change event (WebSocket/Event Bus)
                      └── UI receives update
                          └── Settings Panel refreshes
```

---

## API Structure

### REST API Endpoints

#### System
- `GET /status` - System status (running/stopped, mode)
- `POST /command` - Execute command (start, stop, set_mode)

#### Capital & Portfolio
- `GET /capital/overview` - Capital breakdown
- `GET /positions` - Open positions
- `GET /orders` - Orders (with optional status filter)

#### Market Data
- `GET /opportunities?limit=50` - Recent opportunities
- `GET /signals?limit=50` - Recent signals
- `GET /market/state` - Current market state
- `GET /data/health` - Data health status

#### Strategies
- `GET /strategies/performance?strategy_id=xxx` - Strategy performance

#### Settings
- `GET /settings` - All settings
- `GET /settings/{key}` - Get specific setting
- `PUT /settings/{key}` - Update setting
- `GET /settings/definitions` - Setting definitions
- `POST /settings/reset/{key}` - Reset setting to default
- `POST /settings/reset-all` - Reset all settings

### Response Formats

All endpoints return JSON:

```json
// Capital Overview
{
  "total": 100000.0,
  "available": 75000.0,
  "allocated": 20000.0,
  "reserved": 5000.0
}

// Opportunities
{
  "opportunities": [
    {
      "symbol": "AAPL",
      "timestamp": "2024-01-01T10:30:00Z",
      "price": 150.25,
      "volume": 1500000,
      "score": 85,
      "sector": "Technology",
      "source": "market_scanner",
      "indicators": {...}
    }
  ]
}

// Signals
{
  "signals": [
    {
      "signal_id": "sig_123",
      "symbol": "AAPL",
      "strategy_id": "trend_following_v1",
      "timestamp": "2024-01-01T10:30:00Z",
      "score": 85,
      "confidence": 0.9,
      "entry_price": 150.25,
      "stop_loss": 142.50,
      "take_profit": 165.00,
      "decision": "APPROVE"
    }
  ]
}
```

---

## Key Features

### 1. Continuous Market Scanning
- Scans entire stock universe in parallel
- Pre-filters for liquidity, volatility, volume
- Emits only qualified opportunities
- Rate-limited via Celery workers

### 2. Multi-Strategy Evaluation
- Each opportunity evaluated against all active strategies
- Strategies filtered by market regime
- Signals include score, confidence, entry/exit prices

### 3. Capital-Aware Decision Making
- Every decision considers available capital
- Risk-based position sizing
- Enforces per-trade, daily, sector limits

### 4. Portfolio-Level Intelligence
- Tracks sector exposure
- Monitors correlation
- Evaluates portfolio fit

### 5. Learning & Attribution
- Tracks strategy performance
- Explains why strategies succeed/fail
- Adjusts strategy weights over time

### 6. Shadow Trading
- Test strategies without risking capital
- Compare shadow vs live performance
- Isolated execution environment

### 7. Explainability
- Decision explanations
- Confidence scoring
- Uncertainty quantification

### 8. Safety & Governance
- Kill-switch mechanism
- Daily loss caps
- Comprehensive audit trail
- State recovery after crashes

---

## File Structure

```
stockport/
├── app.py                          # Main entry point (launches Streamlit)
├── start_backend.py                # Backend startup script
├── requirements.txt                # Python dependencies
├── mkdocs.yml                      # Developer documentation config
├── mkdocs-user.yml                 # User documentation config
│
├── backend/                        # Backend code
│   ├── api/                        # REST API and WebSocket
│   │   ├── rest_api.py            # REST API endpoints
│   │   ├── websocket_server.py    # WebSocket server
│   │   └── __main__.py            # API entry point
│   │
│   ├── core/                       # Core components
│   │   ├── engine.py              # Trading engine
│   │   ├── event_bus.py           # Event bus (Redis)
│   │   ├── state_manager.py       # State persistence
│   │   └── decision_engine.py     # Decision engine
│   │
│   ├── data/                       # Data integrity
│   │   ├── integrity/             # Data validation, health
│   │   └── providers/              # Data providers
│   │
│   ├── scanners/                   # Market scanners
│   │   ├── base_scanner.py
│   │   └── market_scanner.py
│   │
│   ├── strategies/                 # Strategy system
│   │   ├── registry.py
│   │   ├── evaluator.py
│   │   └── base_strategy.py
│   │
│   ├── capital/                    # Capital management
│   │   ├── capital_manager.py
│   │   └── position_sizer.py
│   │
│   ├── risk/                       # Risk management
│   │   └── risk_engine.py
│   │
│   ├── execution/                  # Execution
│   │   ├── execution_engine.py
│   │   ├── order_manager.py
│   │   └── brokers/               # Broker implementations
│   │
│   ├── market_state/               # Market state engine
│   │   └── state_engine.py
│   │
│   ├── portfolio/                  # Portfolio management
│   │   └── portfolio_manager.py
│   │
│   ├── learning/                   # Learning system
│   │   ├── performance_tracker.py
│   │   └── attribution_engine.py
│   │
│   ├── governance/                 # Audit and compliance
│   │   └── audit_logger.py
│   │
│   ├── resilience/                 # Operational resilience
│   │   ├── heartbeat_monitor.py
│   │   ├── state_recovery.py
│   │   └── safe_shutdown.py
│   │
│   ├── settings/                   # Settings system
│   │   ├── settings_manager.py
│   │   └── settings_adapter.py
│   │
│   └── integration/                # System integration
│       └── system_integrator.py
│
├── ui/                             # Frontend code
│   ├── app_v4.py                  # Main Streamlit app
│   ├── dashboard.py               # Dashboard page
│   ├── scanner_view.py            # Scanner page
│   ├── strategies_panel.py        # Strategies page
│   ├── portfolio_view.py         # Portfolio page
│   ├── execution_view.py         # Execution page
│   ├── settings_panel.py         # Settings page
│   │
│   └── services/                  # UI services
│       ├── api_client.py         # REST API client
│       └── ui_data_service.py    # Data service layer
│
├── models/                         # Data models
│   ├── opportunity.py
│   ├── strategy_signal.py
│   └── trading_decision.py
│
├── config/                         # Configuration
│   ├── app_config.py             # App configuration
│   └── constants/                # Constants
│
├── utils/                          # Utilities
│   └── debug_utils.py            # Logging
│
├── docs/                           # Documentation
│   ├── user/                     # User documentation
│   └── [various docs]           # Developer docs
│
└── tests/                          # Tests
    ├── unit/                     # Unit tests
    ├── integration/              # Integration tests
    └── conftest.py              # Test fixtures
```

---

## Configuration

### Environment Variables

- `STOCKPORT_API_URL`: Backend API URL (default: `http://localhost:8001`)
- `STOCKPORT_API_HOST`: API host (default: `0.0.0.0`)
- `STOCKPORT_API_PORT`: API port (default: `8001`)
- `REDIS_HOST`: Redis host (default: `localhost`)
- `REDIS_PORT`: Redis port (default: `6379`)
- `DATABASE_TYPE`: Database type (`sqlite` or `postgresql`)

### Settings System

All system settings are managed via `SettingsManager`:
- 25+ configurable settings
- Real-time updates (no restart required)
- Categories: Data, Risk, Performance, Trading, etc.
- Accessible via REST API and UI

---

## Development Workflow

### Starting the System

1. **Start Backend**:
   ```bash
   python -m backend.api.rest_api
   # or
   python start_backend.py
   ```

2. **Start UI**:
   ```bash
   streamlit run app.py
   ```

### Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest tests/ --cov=backend --cov=ui
```

### Documentation

```bash
# Serve developer docs
mkdocs serve

# Serve user docs
mkdocs serve -f mkdocs-user.yml

# Build docs
mkdocs build
mkdocs build -f mkdocs-user.yml
```

---

## Key Design Patterns

1. **Service Layer Pattern**: Business logic in services
2. **Factory Pattern**: Provider creation
3. **Strategy Pattern**: Pluggable strategies
4. **Observer Pattern**: Event bus pub/sub
5. **Facade Pattern**: SystemIntegrator orchestrates components
6. **Repository Pattern**: Data access abstraction

---

## Important Notes for AI Assistants

1. **Always check backend availability** before making API calls in UI
2. **Use UIDataService** for all data fetching (don't call APIClient directly)
3. **Settings are real-time** - changes apply immediately
4. **Event-driven architecture** - components communicate via events
5. **State is persistent** - system recovers state after crashes
6. **Safety first** - multiple risk checks before execution
7. **Audit everything** - all decisions logged for compliance

---

This document should provide sufficient context for AI assistants to understand and work with the Stockport v4 codebase. For specific implementation details, refer to the code comments and inline documentation.

