---
name: Stockport v4 Architecture & Refactor Plan
overview: "Complete architectural redesign of Stockport from analysis tool to fully automated quantitative trading platform. Includes system architecture, module refactor plan, strategy system, continuous scanning, capital/risk management, execution engine, learning system, UI redesign, safety/governance, and phased rollout plan. Extended with institutional-grade capabilities: data integrity, market state engine, portfolio intelligence, attribution, timing awareness, shadow trading, explainability, and operational resilience."
todos:
  - id: foundation-1
    content: Create new backend/ directory structure with core modules (engine.py, event_bus.py, state_manager.py)
    status: completed
  - id: foundation-2
    content: Set up Redis and PostgreSQL infrastructure with connection pooling
    status: completed
  - id: foundation-3
    content: Implement event bus (backend/core/event_bus.py) for pub/sub messaging
    status: completed
    dependencies:
      - foundation-2
  - id: foundation-4
    content: Implement state manager (backend/core/state_manager.py) for system state persistence
    status: completed
    dependencies:
      - foundation-2
  - id: foundation-5
    content: Create base models (models/opportunity.py, models/strategy_signal.py, models/trading_decision.py)
    status: completed
  - id: foundation-6
    content: Set up database schema with migrations for positions, orders, performance, audit logs
    status: completed
    dependencies:
      - foundation-2
  - id: foundation-7
    content: Create paper broker (backend/execution/brokers/paper_broker.py) for testing
    status: completed
    dependencies:
      - foundation-5
  - id: data-integrity-1
    content: Implement data validator (backend/data/integrity/data_validator.py) with validation rules
    status: completed
    dependencies:
      - foundation-1
  - id: data-integrity-2
    content: Implement anomaly detector (backend/data/integrity/anomaly_detector.py) for spikes, gaps, bad ticks
    status: completed
    dependencies:
      - data-integrity-1
  - id: data-integrity-3
    content: Implement corporate actions handler (backend/data/integrity/corporate_actions.py) for splits, dividends
    status: completed
    dependencies:
      - data-integrity-1
  - id: data-integrity-4
    content: Implement price reconciler (backend/data/integrity/price_reconciler.py) to reconcile provider vs broker prices
    status: completed
    dependencies:
      - data-integrity-1
      - foundation-7
  - id: data-integrity-5
    content: Implement data health monitor (backend/data/integrity/health_monitor.py) with GREEN/YELLOW/RED status
    status: completed
    dependencies:
      - data-integrity-1
      - data-integrity-2
  - id: data-integrity-6
    content: Implement truth layer (backend/data/integrity/truth_layer.py) as single source of truth for prices
    status: completed
    dependencies:
      - data-integrity-4
      - data-integrity-5
  - id: scanner-1
    content: Implement base scanner (backend/scanners/base_scanner.py) abstract class
    status: completed
    dependencies:
      - foundation-1
      - data-integrity-6
  - id: scanner-2
    content: Implement market scanner (backend/scanners/market_scanner.py) with parallel workers
    status: completed
    dependencies:
      - scanner-1
  - id: scanner-3
    content: Set up Celery workers for scanner tasks with rate limiting
    status: pending
    dependencies:
      - scanner-2
      - foundation-2
  - id: market-state-1
    content: Implement market state engine (backend/market_state/state_engine.py) with state data model
    status: completed
    dependencies:
      - foundation-1
  - id: market-state-2
    content: Implement regime detector (backend/market_state/regime_detector.py) for trending/choppy/volatile regimes
    status: completed
    dependencies:
      - market-state-1
  - id: market-state-3
    content: Implement volatility detector (backend/market_state/volatility_detector.py) using VIX and ATR
    status: completed
    dependencies:
      - market-state-1
  - id: market-state-4
    content: Implement breadth detector (backend/market_state/breadth_detector.py) for advance/decline analysis
    status: completed
    dependencies:
      - market-state-1
  - id: market-state-5
    content: Implement state publisher (backend/market_state/state_publisher.py) with Redis pub/sub
    status: completed
    dependencies:
      - market-state-2
      - market-state-3
      - market-state-4
      - foundation-2
  - id: strategy-1
    content: Create strategy registry (backend/strategies/registry.py) for strategy management
    status: completed
    dependencies:
      - foundation-1
  - id: strategy-2
    content: Implement strategy loader (backend/strategies/loader.py) to load YAML strategy definitions
    status: completed
    dependencies:
      - strategy-1
  - id: strategy-3
    content: Create base strategy class (backend/strategies/base_strategy.py) with abstract methods
    status: completed
    dependencies:
      - strategy-1
  - id: strategy-4
    content: Implement example strategies (trend_following.py, momentum.py) as reference implementations
    status: completed
    dependencies:
      - strategy-3
  - id: strategy-5
    content: Implement strategy evaluator (backend/strategies/evaluator.py) to evaluate opportunities against strategies
    status: completed
    dependencies:
      - strategy-3
      - market-state-5
  - id: portfolio-1
    content: Implement portfolio manager (backend/portfolio/portfolio_manager.py) for portfolio state tracking
    status: completed
    dependencies:
      - foundation-1
  - id: portfolio-2
    content: Implement exposure tracker (backend/portfolio/exposure_tracker.py) for sector, factor, correlation exposure
    status: completed
    dependencies:
      - portfolio-1
  - id: portfolio-3
    content: Implement diversification engine (backend/portfolio/diversification_engine.py) with guardrails
    status: completed
    dependencies:
      - portfolio-2
  - id: portfolio-4
    content: Implement opportunity ranker (backend/portfolio/opportunity_ranker.py) to rank by portfolio fit
    status: completed
    dependencies:
      - portfolio-3
  - id: capital-1
    content: Implement capital manager (backend/capital/capital_manager.py) for real-time capital tracking
    status: completed
    dependencies:
      - foundation-1
  - id: capital-2
    content: Implement position sizer (backend/capital/position_sizer.py) with risk-based sizing
    status: completed
    dependencies:
      - capital-1
  - id: risk-1
    content: Implement risk engine (backend/risk/risk_engine.py) for risk limit enforcement
    status: completed
    dependencies:
      - foundation-1
      - capital-1
  - id: risk-2
    content: Implement risk limits (backend/risk/limits.py) for per-trade, daily, sector limits
    status: completed
    dependencies:
      - risk-1
  - id: risk-3
    content: Implement correlation checker (backend/risk/correlation.py) for position correlation analysis
    status: completed
    dependencies:
      - risk-1
      - portfolio-2
  - id: risk-4
    content: Implement kill-switch (backend/risk/kill_switch.py) with emergency stop logic
    status: completed
    dependencies:
      - risk-1
  - id: decision-1
    content: Implement decision engine (backend/core/decision_engine.py) integrating capital, risk, portfolio
    status: completed
    dependencies:
      - capital-2
      - risk-2
      - portfolio-4
      - market-state-5
  - id: execution-1
    content: Implement execution engine (backend/execution/execution_engine.py) for order management
    status: completed
    dependencies:
      - foundation-1
      - decision-1
  - id: execution-2
    content: Implement order manager (backend/execution/order_manager.py) for order lifecycle
    status: completed
    dependencies:
      - execution-1
  - id: execution-3
    content: Implement safety checks (backend/execution/safety_checks.py) for pre-execution validation
    status: completed
    dependencies:
      - execution-1
      - risk-2
  - id: timing-1
    content: Implement signal expiry (backend/timing/signal_expiry.py) with strategy-specific expiry times
    status: completed
    dependencies:
      - strategy-5
  - id: timing-2
    content: Implement latency tracker (backend/timing/latency_tracker.py) with latency budgets per strategy
    status: completed
    dependencies:
      - timing-1
  - id: timing-3
    content: Implement stale detector (backend/timing/stale_detector.py) to detect stale opportunities
    status: completed
    dependencies:
      - timing-1
  - id: learning-1
    content: Implement performance tracker (backend/learning/performance_tracker.py) for strategy performance
    status: completed
    dependencies:
      - foundation-1
      - execution-2
  - id: learning-2
    content: Implement decay detector (backend/learning/decay_detector.py) for strategy decay detection
    status: completed
    dependencies:
      - learning-1
  - id: attribution-1
    content: Implement attribution engine (backend/attribution/attribution_engine.py) for trade attribution
    status: completed
    dependencies:
      - learning-1
  - id: attribution-2
    content: Implement trade attributor (backend/attribution/trade_attributor.py) for entry/exit attribution
    status: completed
    dependencies:
      - attribution-1
  - id: attribution-3
    content: Implement indicator contributor (backend/attribution/indicator_contributor.py) for indicator analysis
    status: completed
    dependencies:
      - attribution-1
  - id: attribution-4
    content: Implement failure classifier (backend/attribution/failure_classifier.py) for failure categorization
    status: completed
    dependencies:
      - attribution-2
  - id: shadow-1
    content: Implement shadow engine (backend/shadow/shadow_engine.py) for shadow trading
    status: completed
    dependencies:
      - strategy-5
      - execution-1
  - id: shadow-2
    content: Implement shadow broker (backend/shadow/shadow_broker.py) for paper trading execution
    status: completed
    dependencies:
      - shadow-1
      - foundation-7
  - id: shadow-3
    content: Implement isolation layer (backend/shadow/isolation_layer.py) to prevent shadow leakage
    status: completed
    dependencies:
      - shadow-1
  - id: shadow-4
    content: Implement comparison engine (backend/shadow/comparison_engine.py) for shadow vs live comparison
    status: completed
    dependencies:
      - shadow-2
      - learning-1
  - id: explainability-1
    content: Implement explainer engine (backend/explainability/explainer_engine.py) for decision explanations
    status: completed
    dependencies:
      - decision-1
  - id: explainability-2
    content: Implement decision explainer (backend/explainability/decision_explainer.py) for human-readable explanations
    status: completed
    dependencies:
      - explainability-1
  - id: explainability-3
    content: Implement confidence calculator (backend/explainability/confidence_calculator.py) for confidence scores
    status: completed
    dependencies:
      - explainability-1
  - id: explainability-4
    content: Implement uncertainty quantifier (backend/explainability/uncertainty_quantifier.py) for uncertainty analysis
    status: completed
    dependencies:
      - explainability-1
  - id: governance-1
    content: Implement audit logger (backend/governance/audit_logger.py) for comprehensive audit trail
    status: completed
    dependencies:
      - foundation-1
  - id: governance-2
    content: Integrate audit logging into all decision points (scanner, evaluator, decision, execution)
    status: completed
    dependencies:
      - governance-1
      - scanner-2
      - strategy-5
      - decision-1
      - execution-1
  - id: resilience-1
    content: Implement heartbeat monitor (backend/resilience/heartbeat_monitor.py) for service health
    status: completed
    dependencies:
      - foundation-1
  - id: resilience-2
    content: Implement service manager (backend/resilience/service_manager.py) for auto-restart
    status: completed
    dependencies:
      - resilience-1
  - id: resilience-3
    content: Implement state recovery (backend/resilience/state_recovery.py) for crash recovery
    status: completed
    dependencies:
      - foundation-4
      - execution-2
  - id: resilience-4
    content: Implement duplicate prevention (backend/resilience/duplicate_prevention.py) with idempotency keys
    status: completed
    dependencies:
      - execution-2
  - id: resilience-5
    content: Implement safe shutdown (backend/resilience/safe_shutdown.py) for graceful shutdown handling
    status: completed
    dependencies:
      - resilience-3
  - id: api-1
    content: Implement WebSocket server (backend/api/websocket_server.py) for real-time UI updates
    status: completed
    dependencies:
      - foundation-2
      - foundation-3
  - id: api-2
    content: Implement REST API (backend/api/rest_api.py) for commands and queries
    status: completed
    dependencies:
      - foundation-1
  - id: ui-1
    content: Create main dashboard (ui/dashboard.py) with system status and key metrics
    status: completed
    dependencies:
      - api-1
  - id: ui-2
    content: Create scanner view (ui/scanner_view.py) with opportunity stream and filters
    status: completed
    dependencies:
      - api-1
  - id: ui-3
    content: Create strategies panel (ui/strategies_panel.py) for strategy management
    status: completed
    dependencies:
      - api-1
  - id: ui-4
    content: Create portfolio view (ui/portfolio_view.py) with capital and positions
    status: completed
    dependencies:
      - api-1
  - id: ui-5
    content: Create execution view (ui/execution_view.py) for order monitoring
    status: completed
    dependencies:
      - api-1
  - id: ui-6
    content: Add data health indicators to UI (GREEN/YELLOW/RED status badges)
    status: completed
    dependencies:
      - ui-1
      - data-integrity-5
  - id: ui-7
    content: Add market state visualization to dashboard (regime, volatility, breadth)
    status: completed
    dependencies:
      - ui-1
      - market-state-5
  - id: ui-8
    content: Add explanation display to signals (why this trade, what could invalidate)
    status: completed
    dependencies:
      - ui-2
      - explainability-2
  - id: ui-9
    content: Add shadow trading comparison view to strategies panel
    status: completed
    dependencies:
      - ui-3
      - shadow-4
  - id: integration-1
    content: Integrate data integrity layer with scanners (block invalid data)
    status: completed
    dependencies:
      - scanner-2
      - data-integrity-6
  - id: integration-2
    content: Integrate market state with strategy evaluator (regime filtering)
    status: completed
    dependencies:
      - strategy-5
      - market-state-5
  - id: integration-3
    content: Integrate portfolio intelligence with decision engine (portfolio fit checks)
    status: completed
    dependencies:
      - decision-1
      - portfolio-4
  - id: integration-4
    content: Integrate timing awareness with execution engine (reject stale signals)
    status: completed
    dependencies:
      - execution-1
      - timing-3
  - id: integration-5
    content: Integrate attribution with learning system (feedback loop)
    status: completed
    dependencies:
      - learning-1
      - attribution-4
  - id: testing-1
    content: Write unit tests for data integrity layer
    status: completed
    dependencies:
      - data-integrity-6
  - id: testing-2
    content: Write unit tests for market state engine
    status: completed
    dependencies:
      - market-state-5
  - id: testing-3
    content: Write integration tests for end-to-end flow (scanner → execution)
    status: completed
    dependencies:
      - execution-2
      - integration-1
      - integration-2
      - integration-3
      - integration-4
  - id: testing-4
    content: Test disaster recovery procedures (crash recovery, state restoration)
    status: completed
    dependencies:
      - resilience-3
      - resilience-5
  - id: testing-5
    content: Test duplicate order prevention with idempotency
    status: completed
    dependencies:
      - resilience-4
---

# Stockport v4: Quantitative Trading Platform Architecture

## Executive Summary

Transform Stockport from a stock analysis tool into a **fully automated, always-on quantitative trading platform** - a "trading brain" that continuously scans markets, evaluates opportunities, manages capital and risk, and executes trades with strict safety controls.**Core Philosophy**: Backend-first, event-driven, strategy-based, capital-aware, and safety-first.---

## PART 1: SYSTEM ARCHITECTURE

### High-Level Architecture

```javascript
┌─────────────────────────────────────────────────────────────────┐
│                        UI Layer (Streamlit)                      │
│  - Dashboard (read-only, subscribes to backend state)           │
│  - Control Panel (sends commands, never triggers analysis)       │
│  - Monitoring & Overrides                                        │
└───────────────────────┬─────────────────────────────────────────┘
                        │ WebSocket / REST API
                        │ (State subscription, commands)
┌───────────────────────▼─────────────────────────────────────────┐
│                    API Gateway / Message Bus                     │
│  - WebSocket server for real-time updates                        │
│  - REST API for commands                                         │
│  - Event routing                                                 │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│   Scanner    │ │  Strategy   │ │  Execution  │
│   Workers    │ │  Evaluator  │ │   Engine    │
└───────┬──────┘ └──────┬──────┘ └──────┬──────┘
        │               │               │
        └───────┬───────┼───────────────┘
                │       │
        ┌───────▼───────▼───────┐
        │   Decision Engine     │
        │  (Capital + Risk)      │
        └───────┬───────────────┘
                │
┌───────────────┼───────────────┐
│               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│   Learning   │ │   Audit &   │ │   Broker    │
│   System     │ │  Governance │ │  Adapters   │
└──────────────┘ └─────────────┘ └─────────────┘
```

### Component Responsibilities

#### 1. **Market Scanner Workers** (Always-On)

- **Purpose**: Continuously scan stock universe during market hours
- **Responsibilities**:
- Fetch market data in parallel
- Apply pre-filters (liquidity, volatility, volume)
- Emit qualified opportunities to queue
- Market regime detection
- **Output**: Stream of `Opportunity` events

#### 2. **Strategy Registry & Evaluator**

- **Purpose**: Manage and evaluate trading strategies
- **Responsibilities**:
- Load strategies from registry
- Evaluate opportunities against active strategies
- Score and rank opportunities
- Strategy performance tracking
- **Output**: `StrategySignal` with confidence scores

#### 3. **Decision Engine** (Capital & Risk)

- **Purpose**: Capital-aware decision making
- **Responsibilities**:
- Track available capital in real-time
- Enforce risk limits (per-trade, daily, sector)
- Position sizing calculations
- Correlation checks
- Kill-switch enforcement
- **Output**: `TradingDecision` (APPROVE/REJECT/MODIFY)

#### 4. **Execution Engine**

- **Purpose**: Broker-agnostic trade execution
- **Responsibilities**:
- Convert decisions to orders
- Execute via broker adapters
- Handle slippage and costs
- Retry logic and failure handling
- Order status tracking
- **Output**: `ExecutionResult` with audit trail

#### 5. **Learning System**

- **Purpose**: Continuous improvement from performance
- **Responsibilities**:
- Track strategy performance over time
- Detect strategy decay
- Adjust strategy weights
- Parameter optimization
- Regime-aware strategy selection
- **Output**: Strategy performance reports, weight adjustments

#### 6. **Audit & Governance**

- **Purpose**: Safety, compliance, and explainability
- **Responsibilities**:
- Log all decisions and executions
- Explainable decision trees
- Compliance checks
- Alert on anomalies
- **Output**: Audit logs, compliance reports

#### 7. **UI Layer** (Control Room)

- **Purpose**: Monitoring and manual overrides
- **Responsibilities**:
- Display real-time system state
- Show opportunities and signals
- Manual override controls
- Risk dashboard
- Strategy management UI
- **Key Principle**: **Never triggers analysis directly** - only subscribes to backend state

### Data Flow: Market → Decision → Execution

```javascript
Market Data
    ↓
[Scanner Workers] → Opportunity Events → [Redis Queue]
    ↓
[Strategy Evaluator] → Strategy Signals → [Redis Queue]
    ↓
[Decision Engine] → Trading Decision → [Redis Queue]
    ↓
[Execution Engine] → Order → [Broker Adapter] → Market
    ↓
[Execution Result] → [Learning System] → [Performance DB]
    ↓
[UI Dashboard] ← [WebSocket Updates]
```

### Infrastructure Stack

**Core Services:**

- **Redis**: Message queue, state cache, pub/sub for events
- **PostgreSQL**: Persistent storage (positions, orders, performance, audit logs)
- **Celery**: Distributed task queue for scanner workers
- **WebSocket Server**: Real-time UI updates (FastAPI/Flask-SocketIO)

**Data Flow:**

- Scanner workers → Redis Queue → Strategy Evaluator
- Strategy Evaluator → Redis Queue → Decision Engine
- Decision Engine → Redis Queue → Execution Engine
- Execution Engine → PostgreSQL (audit) + Redis (state)

**Deployment:**

- Backend: Docker containers (scanner, evaluator, executor, API)
- UI: Streamlit (can be separate container or same host)
- Database: PostgreSQL (persistent) + Redis (ephemeral state)

### Boundaries: Manual vs Semi-Auto vs Auto

**Manual Mode:**

- UI shows opportunities
- User manually approves each trade
- Execution engine executes approved orders
- All risk checks still apply

**Semi-Auto Mode:**

- System generates signals
- User sets daily capital limit
- System auto-executes up to limit
- User can override/reject

**Full Auto Mode:**

- System generates, evaluates, and executes
- Daily loss limits enforced
- Kill-switch available
- User receives alerts only

---

## PART 2: MODULE-BY-MODULE REFACTOR PLAN

### New Top-Level Structure

```javascript
stockport_v4/
├── backend/
│   ├── core/
│   │   ├── engine.py              # Main orchestrator
│   │   ├── event_bus.py            # Event routing
│   │   └── state_manager.py        # System state management
│   │
│   ├── scanners/
│   │   ├── base_scanner.py         # Abstract scanner
│   │   ├── market_scanner.py       # Main market scanner
│   │   ├── sector_scanner.py       # Sector-specific
│   │   ├── liquidity_scanner.py   # Liquidity filters
│   │   └── event_scanner.py        # Event-driven (earnings, etc.)
│   │
│   ├── strategies/
│   │   ├── registry.py             # Strategy registry
│   │   ├── base_strategy.py        # Abstract strategy
│   │   ├── evaluator.py            # Strategy evaluation engine
│   │   ├── loader.py               # Load from YAML/JSON
│   │   └── strategies/             # Strategy implementations
│   │       ├── trend_following.py
│   │       ├── mean_reversion.py
│   │       ├── momentum.py
│   │       ├── breakout.py
│   │       └── options.py
│   │
│   ├── capital/
│   │   ├── capital_manager.py      # Capital tracking
│   │   ├── position_sizer.py      # Position sizing logic
│   │   ├── allocation.py           # Capital allocation
│   │   └── constraints.py           # Capital constraints
│   │
│   ├── risk/
│   │   ├── risk_engine.py          # Main risk engine
│   │   ├── limits.py                # Risk limits (per-trade, daily, sector)
│   │   ├── correlation.py           # Correlation analysis
│   │   ├── drawdown.py              # Drawdown protection
│   │   └── kill_switch.py           # Emergency stops
│   │
│   ├── execution/
│   │   ├── execution_engine.py      # Main execution engine
│   │   ├── order_manager.py         # Order lifecycle
│   │   ├── brokers/                 # Broker adapters
│   │   │   ├── base_broker.py       # Abstract broker
│   │   │   ├── paper_broker.py      # Paper trading
│   │   │   ├── alpaca_broker.py     # Alpaca adapter
│   │   │   ├── ibkr_broker.py       # Interactive Brokers
│   │   │   └── zerodha_broker.py    # Zerodha Kite
│   │   ├── safety_checks.py         # Pre-execution checks
│   │   └── slippage.py              # Slippage handling
│   │
│   ├── learning/
│   │   ├── performance_tracker.py   # Track strategy performance
│   │   ├── strategy_optimizer.py    # Parameter optimization
│   │   ├── regime_detector.py       # Market regime detection
│   │   ├── weight_adjuster.py       # Strategy weight adjustment
│   │   └── decay_detector.py        # Strategy decay detection
│   │
│   ├── governance/
│   │   ├── audit_logger.py          # Audit trail
│   │   ├── explainer.py             # Decision explainability
│   │   ├── compliance.py            # Compliance checks
│   │   └── alerts.py                # Anomaly alerts
│   │
│   ├── data/
│   │   ├── providers/               # Existing data providers (reuse)
│   │   ├── cache.py                 # Data caching
│   │   └── market_data.py           # Market data interface
│   │
│   ├── api/
│   │   ├── websocket_server.py      # WebSocket for UI
│   │   ├── rest_api.py              # REST API
│   │   └── commands.py              # Command handlers
│   │
│   └── workers/
│       ├── scanner_worker.py        # Celery worker for scanning
│       ├── evaluator_worker.py      # Strategy evaluation worker
│       └── executor_worker.py       # Execution worker
│
├── ui/
│   ├── dashboard.py                 # Main dashboard
│   ├── scanner_view.py              # Scanner monitoring
│   ├── strategies_panel.py          # Strategy management
│   ├── portfolio_view.py            # Capital & positions
│   ├── execution_view.py            # Order execution
│   ├── backtest_lab.py              # Backtesting UI
│   ├── alerts_view.py               # Alerts & insights
│   ├── controls.py                  # System controls
│   └── reports.py                   # Reports & history
│
├── models/
│   ├── opportunity.py                # Opportunity model
│   ├── strategy_signal.py           # Strategy signal model
│   ├── trading_decision.py          # Decision model
│   ├── order.py                      # Order model
│   ├── position.py                   # Position model
│   └── performance.py               # Performance metrics
│
├── config/
│   ├── trading_config.py             # Trading configuration
│   ├── risk_config.py                # Risk parameters
│   └── strategies/                   # Strategy definitions (YAML)
│
└── database/
    ├── migrations/                   # DB migrations
    └── schema.sql                    # Database schema
```

### Module Reuse vs Rewrite

**REUSE (with modifications):**

- `services/data_providers/` → Move to `backend/data/providers/`
- `services/analyzers/indicators/` → Extract indicator calculations, use in strategies
- `services/analyzers/patterns/` → Use in strategy pattern matching
- `services/backtesting/backtest_engine.py` → Enhance for strategy backtesting
- `models/signals.py` → Extend for `StrategySignal` and `TradingDecision`
- `utils/debug_utils.py` → Keep as-is
- `config/app_config.py` → Extend with trading config

**REWRITE:**

- `core/stock_analyzer.py` → Replace with `backend/core/engine.py` (orchestrator)
- `core/parallel_analyzer.py` → Replace with Celery workers
- `core/enhanced_analyzer.py` → Logic moves to strategy evaluator
- `services/analyzers/signals/entry_detector.py` → Rewrite as strategy-based
- `ui/pages/main_page.py` → Complete UI redesign

**DEPRECATE:**

- `ui/components/analysis.py` → Replaced by dashboard
- Direct UI-triggered analysis flows → All analysis moves to backend
- Report generation as primary feature → Becomes secondary (audit/reports)

### Execution Order: Phase 1 → Phase 4

**Phase 1: Foundation (Weeks 1-2)**

1. Create new `backend/` structure
2. Set up Redis + PostgreSQL
3. Implement event bus (`backend/core/event_bus.py`)
4. Implement state manager (`backend/core/state_manager.py`)
5. Create base models (`models/opportunity.py`, `models/strategy_signal.py`)
6. Set up database schema
7. Create paper broker (`backend/execution/brokers/paper_broker.py`)

**Phase 2: Scanning & Strategies (Weeks 3-4)**

1. Implement base scanner (`backend/scanners/base_scanner.py`)
2. Implement market scanner (`backend/scanners/market_scanner.py`)
3. Create strategy registry (`backend/strategies/registry.py`)
4. Implement strategy loader (`backend/strategies/loader.py`)
5. Create 2-3 example strategies (trend, momentum)
6. Implement strategy evaluator (`backend/strategies/evaluator.py`)
7. Set up Celery workers for scanning

**Phase 3: Capital & Risk (Weeks 5-6)**

1. Implement capital manager (`backend/capital/capital_manager.py`)
2. Implement position sizer (`backend/capital/position_sizer.py`)
3. Implement risk engine (`backend/risk/risk_engine.py`)
4. Implement risk limits (`backend/risk/limits.py`)
5. Implement kill-switch (`backend/risk/kill_switch.py`)
6. Integrate with decision engine

**Phase 4: Execution & Learning (Weeks 7-8)**

1. Implement execution engine (`backend/execution/execution_engine.py`)
2. Implement order manager (`backend/execution/order_manager.py`)
3. Connect paper broker
4. Implement learning system (`backend/learning/performance_tracker.py`)
5. Implement audit logger (`backend/governance/audit_logger.py`)
6. Create WebSocket API (`backend/api/websocket_server.py`)

**Phase 5: UI Redesign (Weeks 9-10)**

1. Create dashboard (`ui/dashboard.py`)
2. Create scanner view (`ui/scanner_view.py`)
3. Create strategies panel (`ui/strategies_panel.py`)
4. Create portfolio view (`ui/portfolio_view.py`)
5. Connect UI to WebSocket API
6. Test end-to-end flow

**Phase 6: Testing & Hardening (Weeks 11-12)**

1. Paper trading testing
2. Strategy backtesting
3. Risk limit testing
4. Kill-switch testing
5. Performance optimization
6. Documentation

---

## PART 3: STRATEGY SYSTEM & DSL

### Strategy Definition Language (YAML)

```yaml
# Example: Trend Following Strategy
strategy:
  name: "trend_following_v1"
  type: "trend_following"
  version: "1.0.0"
  author: "system"
  status: "active"  # active, paused, disabled
  
  description: "Follows strong trends with momentum confirmation"
  
  # Market Regime Applicability
  market_regimes:
    - "trending_up"
    - "trending_down"
    exclude_regimes:
      - "choppy"
      - "high_volatility"
  
  # Entry Rules
  entry:
    conditions:
      - type: "indicator"
        name: "sma_20"
        operator: "above"
        value: "sma_50"
        weight: 0.3
      
      - type: "indicator"
        name: "rsi"
        operator: "between"
        value: [40, 70]
        weight: 0.2
      
      - type: "indicator"
        name: "macd"
        operator: "cross_above"
        value: "signal_line"
        weight: 0.3
      
      - type: "pattern"
        name: "bullish_engulfing"
        weight: 0.2
    
    min_confirmations: 3
    min_score: 70
    
    # Entry Price Logic
    entry_price:
      type: "market"  # market, limit, stop
      limit_offset: 0.001  # 0.1% for limit orders
  
  # Exit Rules
  exit:
    profit_target:
      type: "atr_multiple"
      multiplier: 3.0
      min_risk_reward: 2.0
    
    stop_loss:
      type: "atr_multiple"
      multiplier: 2.0
      max_loss_percent: 0.05  # 5% max
    
    trailing_stop:
      enabled: true
      type: "atr_multiple"
      multiplier: 1.5
    
    time_based:
      max_holding_days: 20
      exit_on_friday: false
  
  # Position Sizing
  position_sizing:
    method: "risk_based"  # risk_based, fixed_amount, kelly
    risk_per_trade: 0.02  # 2% of capital
    max_position_size: 0.10  # 10% of capital max
    min_position_size: 0.01  # 1% minimum
  
  # Risk Constraints
  risk:
    max_correlation: 0.7  # Don't take if correlation > 0.7
    max_sector_exposure: 0.25  # 25% max per sector
    max_daily_trades: 5
    max_daily_loss: 0.05  # 5% daily loss limit
  
  # Performance Tracking
  performance:
    min_win_rate: 0.45
    min_profit_factor: 1.2
    min_sharpe: 0.5
    lookback_days: 90
    auto_disable_on_decay: true
    decay_threshold: -0.15  # -15% performance drop
```

### Strategy Lifecycle

1. **Create**: Define strategy in YAML, save to `config/strategies/`
2. **Validate**: Strategy loader validates syntax and logic
3. **Backtest**: Run backtest on historical data
4. **Review**: Review backtest results (win rate, Sharpe, drawdown)
5. **Activate**: Set status to "active" (or "paper_only" for testing)
6. **Monitor**: System tracks live performance
7. **Optimize**: Adjust parameters based on performance
8. **Disable**: Auto-disable on decay or manual disable

### Strategy Performance Metrics

**Tracked Metrics:**

- Win rate (winning trades / total trades)
- Profit factor (gross profit / gross loss)
- Average win / average loss
- Sharpe ratio
- Maximum drawdown
- Average holding period
- Total return
- Risk-adjusted return

**Decay Detection:**

- Rolling 30-day performance vs 90-day baseline
- Win rate decline > 10%
- Profit factor < 1.0 for 30 days
- Drawdown > 20%

### Strategy Types

1. **Trend Following**: Follows established trends
2. **Mean Reversion**: Trades against extremes
3. **Momentum**: Captures strong price movements
4. **Breakout**: Trades breakouts from ranges
5. **Options Strategies**: Covered calls, spreads, etc.

---

## PART 4: CONTINUOUS MARKET SCANNING

### Scanner Architecture

**Scanner Workers** (Celery tasks):

- Run continuously during market hours
- Parallel execution (10-50 workers)
- Rate-limited per data provider
- Emit `Opportunity` events to Redis queue

**Scanner Dimensions:**

1. **Sector/Domain**: Scan by GICS sectors
2. **Market Cap**: Large cap, mid cap, small cap
3. **Liquidity**: Minimum daily volume (e.g., $1M+)
4. **Volatility**: ATR-based volatility filters
5. **Relative Strength**: RSI, price vs moving averages
6. **Money Flow**: OBV, CMF, volume trends
7. **Options OI**: Unusual options activity (if available)
8. **Event-Driven**: Earnings, news, FDA approvals

### Noise Reduction

**Pre-Filters (Before Strategy Evaluation):**

- Minimum volume: $500K daily (configurable)
- Minimum price: $5 (avoid penny stocks)
- Maximum spread: 0.5% bid-ask spread
- Minimum market cap: $100M (configurable)
- Exclude delisted, halted stocks

**Post-Filters (After Strategy Evaluation):**

- Minimum strategy score: 70/100
- Minimum confidence: 0.6
- Maximum correlation: 0.7 with existing positions
- Sector exposure limits

### Scanning Frequency

**Market Hours:**

- **Pre-market (4:00 AM - 9:30 AM ET)**: Once at 8:00 AM
- **Regular hours (9:30 AM - 4:00 PM ET)**: Every 5 minutes
- **After-hours (4:00 PM - 8:00 PM ET)**: Every 15 minutes

**Scan Types:**

- **Full scan**: All stocks (runs every 30 minutes)
- **Focused scan**: Watchlist + recent opportunities (every 5 minutes)
- **Event scan**: Earnings, news events (real-time)

### Result Flow

```javascript
Scanner → Opportunity Event → Redis Queue → Strategy Evaluator
                                    ↓
                            [Pre-filters applied]
                                    ↓
                            [Strategy evaluation]
                                    ↓
                            StrategySignal → Redis Queue → Decision Engine
```

**Opportunity Event Structure:**

```python
@dataclass
class Opportunity:
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    market_cap: float
    sector: str
    indicators: Dict[str, float]
    pre_filter_score: float  # Pre-filter quality score
    source: str  # Which scanner found it
```

---

## PART 5: CAPITAL & RISK MANAGEMENT (CRITICAL)

### Capital Manager

**Responsibilities:**

- Track available capital in real-time
- Track allocated capital (open positions)
- Track reserved capital (pending orders)
- Calculate free capital = total - allocated - reserved

**Capital Tracking:**

```python
class CapitalManager:
    def get_available_capital(self) -> float:
        """Get free capital available for new positions."""
        total = self.get_total_capital()
        allocated = sum(pos.value for pos in self.open_positions)
        reserved = sum(order.notional for order in self.pending_orders)
        return total - allocated - reserved
    
    def allocate_capital(self, amount: float, order_id: str):
        """Reserve capital for pending order."""
        # Implementation
    
    def release_capital(self, order_id: str):
        """Release reserved capital on order fill/cancel."""
        # Implementation
```

### Risk Rules

**Per-Trade Risk:**

- Maximum risk per trade: 2% of capital (configurable)
- Minimum risk-reward ratio: 1.5:1 (configurable)
- Maximum position size: 10% of capital (configurable)

**Daily Risk:**

- Maximum daily loss: 5% of capital (configurable)
- Maximum daily trades: 10 (configurable)
- Stop trading if daily loss limit hit

**Portfolio Risk:**

- Maximum sector exposure: 25% per sector
- Maximum correlation: 0.7 between positions
- Maximum total exposure: 80% of capital (20% cash reserve)

**Drawdown Protection:**

- If portfolio drawdown > 10%: Reduce position sizes by 50%
- If portfolio drawdown > 20%: Stop new trades
- If portfolio drawdown > 30%: Liquidate all positions (kill-switch)

### Position Sizing Model

**Risk-Based Sizing:**

```python
def calculate_position_size(
    entry_price: float,
    stop_loss: float,
    available_capital: float,
    risk_per_trade: float = 0.02
) -> Dict[str, float]:
    """
    Calculate position size based on risk.
    
    Returns:
        - shares: Number of shares
        - notional: Dollar amount
        - risk_amount: Dollar amount at risk
    """
    risk_per_share = abs(entry_price - stop_loss)
    if risk_per_share == 0:
        return {'shares': 0, 'notional': 0, 'risk_amount': 0}
    
    risk_amount = available_capital * risk_per_trade
    shares = int(risk_amount / risk_per_share)
    notional = shares * entry_price
    
    # Apply max position size limit (10% of capital)
    max_notional = available_capital * 0.10
    if notional > max_notional:
        shares = int(max_notional / entry_price)
        notional = shares * entry_price
        risk_amount = shares * risk_per_share
    
    return {
        'shares': shares,
        'notional': notional,
        'risk_amount': risk_amount
    }
```

**Alternative Methods:**

- **Fixed Amount**: Fixed dollar amount per trade
- **Kelly Criterion**: Optimal bet sizing (advanced)
- **Volatility-Based**: Adjust size based on ATR

### Drawdown Protection Mechanisms

1. **Position Size Reduction**: Reduce sizes by 50% after 10% drawdown
2. **Trade Freeze**: Stop new trades after 20% drawdown
3. **Liquidation**: Liquidate all positions after 30% drawdown (kill-switch)
4. **Recovery Mode**: Gradual position size increase as drawdown recovers

---

## PART 6: EXECUTION ENGINE

### Broker-Agnostic Interface

```python
class BaseBroker(ABC):
    """Abstract broker interface."""
    
    @abstractmethod
    def place_order(self, order: Order) -> OrderResult:
        """Place order and return result."""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel order."""
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Position:
        """Get current position for symbol."""
        pass
    
    @abstractmethod
    def get_account_info(self) -> AccountInfo:
        """Get account balance, buying power, etc."""
        pass
```

### Execution Modes

**Paper Trading:**

- Simulates execution with realistic slippage
- Tracks P&L as if real
- No real money at risk
- Use for testing strategies

**Assisted Trading:**

- System generates orders
- User approves before execution
- User can modify order (price, size)
- Execution via broker API

**Fully Automated:**

- System generates and executes
- All safety checks enforced
- Kill-switch available
- Audit trail required

### Execution Safety Checks

**Pre-Execution Checks:**

1. Available capital sufficient
2. Risk limits not exceeded
3. Position size within limits
4. Correlation check passed
5. Sector exposure limit not exceeded
6. Daily loss limit not hit
7. Kill-switch not active
8. Market hours (if applicable)

**Order Structure:**

```python
@dataclass
class Order:
    symbol: str
    side: str  # "buy" or "sell"
    quantity: int
    order_type: str  # "market", "limit", "stop"
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    strategy_id: str
    signal_id: str
    risk_justification: Dict[str, Any]
    timestamp: datetime
```

### Failure Handling

**Retry Logic:**

- Network errors: Retry 3 times with exponential backoff
- Rate limit errors: Wait and retry
- Insufficient funds: Reject order (don't retry)
- Invalid symbol: Reject order (don't retry)

**Slippage Handling:**

- Estimate slippage based on volume and volatility
- Adjust fill price in paper trading
- Track actual vs expected slippage in real trading

**Order Status Tracking:**

- Pending → Submitted → Filled/Partially Filled/Cancelled/Rejected
- Update position on fill
- Update capital on fill

---

## PART 7: LEARNING & AUTO-IMPROVEMENT

### Performance Tracking

**Data Model:**

```python
@dataclass
class StrategyPerformance:
    strategy_id: str
    period_start: datetime
    period_end: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    average_win: float
    average_loss: float
    average_holding_period: int  # days
```

**Tracking Frequency:**

- Real-time: Update on each trade close
- Daily: Aggregate daily performance
- Weekly: Weekly performance report
- Monthly: Monthly performance review

### Strategy Decay Detection

**Decay Indicators:**

1. **Win Rate Decline**: 30-day win rate < 90-day win rate - 10%
2. **Profit Factor Drop**: 30-day profit factor < 1.0
3. **Sharpe Decline**: 30-day Sharpe < 0.3
4. **Drawdown Increase**: Current drawdown > 20%

**Auto-Disable Logic:**

```python
def detect_strategy_decay(strategy_id: str) -> bool:
    """Detect if strategy is decaying."""
    recent = get_performance(strategy_id, days=30)
    baseline = get_performance(strategy_id, days=90)
    
    if recent.win_rate < baseline.win_rate - 0.10:
        return True  # Decay detected
    
    if recent.profit_factor < 1.0:
        return True
    
    if recent.sharpe_ratio < 0.3:
        return True
    
    return False
```

### Strategy Weight Adjustment

**Weight Calculation:**

- Base weight: 1.0 for all strategies
- Performance multiplier: Based on Sharpe ratio
- Decay penalty: Reduce weight if decay detected
- Final weight = base × performance_mult × (1 - decay_penalty)

**Weight Application:**

- Higher weight strategies get more capital allocation
- Lower weight strategies get less capital
- Disabled strategies get 0 weight

### Parameter Optimization

**Optimization Process:**

1. Identify underperforming strategies
2. Extract strategy parameters
3. Run backtest with parameter variations
4. Select best parameters (highest Sharpe)
5. Update strategy definition
6. Test in paper trading before activation

**Safety Constraints:**

- Never optimize on < 30 days of data
- Never change > 20% of parameters at once
- Always backtest before activating
- Paper trade for 1 week before real money

### Regime-Aware Strategy Selection

**Market Regime Detection:**

- Trending: Strong directional movement
- Choppy: Sideways, no clear direction
- High Volatility: VIX > 20
- Low Volatility: VIX < 15

**Regime-Based Strategy Activation:**

- Enable strategies that match current regime
- Disable strategies that don't match
- Adjust position sizes based on volatility

---

## PART 8: UI/UX REDESIGN (CONTROL ROOM)

### Design Principles

1. **Dashboard-First**: Main screen shows system state at a glance
2. **Signal-First**: Opportunities and signals are primary content
3. **Capital Always Visible**: Capital, risk, P&L always on screen
4. **Explainability**: Every decision has explanation
5. **Manual Override**: Override controls on every screen

### Screen 1: Main Dashboard

**Purpose**: System pulse and key metrics**Key Widgets:**

- **System Status**: Running/Stopped, Mode (Auto/Semi/Manual)
- **Capital Overview**: Total, Available, Allocated, Daily P&L
- **Risk Metrics**: Current exposure, daily loss, drawdown
- **Active Opportunities**: Top 5 opportunities by score
- **Recent Signals**: Last 10 strategy signals
- **Open Positions**: Current positions with P&L
- **Performance Chart**: Portfolio value over time

**User Actions:**

- Toggle system on/off
- Switch mode (Auto/Semi/Manual)
- View opportunity details
- Override/reject signal
- View position details

### Screen 2: Market Scanner

**Purpose**: Monitor scanner activity and opportunities**Key Widgets:**

- **Scanner Status**: Active scanners, scan frequency
- **Opportunity Stream**: Real-time stream of opportunities
- **Filters**: Filter by sector, market cap, score
- **Opportunity Details**: Click to see full analysis
- **Pre-filter Stats**: Volume, liquidity, volatility stats

**User Actions:**

- Pause/resume scanners
- Adjust scan frequency
- Add symbol to watchlist
- View opportunity analysis

### Screen 3: Strategies Control Panel

**Purpose**: Manage strategies**Key Widgets:**

- **Strategy List**: All strategies with status (active/paused/disabled)
- **Strategy Performance**: Win rate, Sharpe, P&L per strategy
- **Strategy Details**: Click to see strategy definition
- **Strategy Controls**: Enable/disable, adjust weights
- **Backtest Results**: Historical performance

**User Actions:**

- Enable/disable strategies
- Adjust strategy weights
- View/edit strategy definition
- Run backtest
- View performance charts

### Screen 4: Portfolio & Capital

**Purpose**: Capital and position management**Key Widgets:**

- **Capital Breakdown**: Total, allocated, available, reserved
- **Position List**: All open positions with P&L
- **Sector Allocation**: Pie chart of sector exposure
- **Risk Metrics**: Per-trade risk, daily risk, portfolio risk
- **Correlation Matrix**: Position correlations

**User Actions:**

- Close position
- Adjust position size
- View position details
- Export portfolio report

### Screen 5: Positions & Execution

**Purpose**: Monitor order execution**Key Widgets:**

- **Pending Orders**: Orders awaiting execution
- **Order History**: Recent orders with status
- **Execution Log**: Real-time execution events
- **Fill Details**: Slippage, fill price, timing

**User Actions:**

- Cancel pending order
- Modify order
- View order details
- Retry failed order

### Screen 6: Backtesting Lab

**Purpose**: Test strategies on historical data**Key Widgets:**

- **Strategy Selector**: Choose strategy to backtest
- **Date Range**: Select historical period
- **Backtest Results**: Performance metrics
- **Trade List**: All trades in backtest
- **Performance Chart**: Equity curve

**User Actions:**

- Run backtest
- Compare strategies
- Export backtest report
- Optimize parameters

### Screen 7: Alerts & Insights

**Purpose**: System alerts and insights**Key Widgets:**

- **Alert List**: All active alerts
- **Insights**: AI-generated insights (if enabled)
- **Performance Alerts**: Strategy decay, drawdown warnings
- **Risk Alerts**: Limit breaches, correlation warnings

**User Actions:**

- Acknowledge alert
- View alert details
- Configure alert thresholds

### Screen 8: System & Risk Controls

**Purpose**: System configuration and safety**Key Widgets:**

- **Risk Limits**: Configure all risk limits
- **Kill Switch**: Emergency stop button
- **Daily Limits**: Daily loss, trade limits
- **System Settings**: Mode, capital, etc.
- **Audit Log**: Recent system decisions

**User Actions:**

- Adjust risk limits
- Activate kill-switch
- Change system mode
- View audit log

### Screen 9: Reports & History

**Purpose**: Historical performance and reports**Key Widgets:**

- **Performance Report**: Daily/weekly/monthly
- **Trade History**: All historical trades
- **Strategy Performance**: Per-strategy reports
- **Risk Report**: Risk metrics over time

**User Actions:**

- Generate report
- Export to PDF/Excel
- Filter by date/strategy
- Compare periods

---

## PART 9: SAFETY, GOVERNANCE & COMPLIANCE

### Kill Switch

**Activation Triggers:**

- Manual: User clicks kill-switch button
- Automatic: Portfolio drawdown > 30%
- Automatic: Daily loss > 10%
- Automatic: System error detected

**Kill-Switch Actions:**

1. Cancel all pending orders
2. Stop accepting new signals
3. Optionally: Liquidate all positions (configurable)
4. Send alert to user
5. Log kill-switch activation

### Daily Loss Cap

**Enforcement:**

- Track daily P&L in real-time
- If daily loss > limit: Stop new trades
- If daily loss > 2× limit: Liquidate all positions
- Reset at market close

### Market Crash Detector

**Detection:**

- Market-wide decline > 5% in 1 hour
- VIX spike > 50
- High correlation spike (> 0.9) across positions

**Actions:**

- Reduce position sizes
- Stop new trades
- Alert user
- Optionally: Liquidate positions

### Strategy Approval Workflow

**New Strategy:**

1. Define strategy in YAML
2. Validate syntax
3. Backtest on historical data
4. Review backtest results
5. User approval required
6. Paper trade for 1 week
7. User approval for real money

**Strategy Changes:**

- Parameter changes require re-approval
- Status changes (active/disabled) require approval
- Weight adjustments are automatic (within limits)

### Audit Logs

**Logged Events:**

- All trading decisions (APPROVE/REJECT/MODIFY)
- All order executions
- All capital allocations
- All risk limit checks
- All strategy evaluations
- All kill-switch activations
- All user overrides

**Log Structure:**

```python
@dataclass
class AuditLog:
    timestamp: datetime
    event_type: str
    event_data: Dict[str, Any]
    user_id: Optional[str]
    decision_id: str
    explanation: str
```

### Explainable Decisions

**Decision Explanation:**

- Why opportunity was selected/rejected
- Which strategies matched
- Risk calculations
- Capital allocation reasoning
- Override reasons (if applicable)

**Example Explanation:**

```javascript
Opportunity: AAPL
Strategy: trend_following_v1 (score: 85)
Risk: $200 (2% of $10K capital)
Position: 10 shares @ $150
Reasoning: Strong uptrend (SMA20 > SMA50), RSI 65 (not overbought), MACD bullish crossover, bullish engulfing pattern detected. Risk-reward 2.5:1. Sector exposure: 15% (within 25% limit).
```

---

## PART 10: ROLLOUT PLAN

### Phase 1: Analysis-Only (Weeks 1-4)

**Goal**: Build scanning and strategy evaluation without execution**Deliverables:**

- Market scanner running continuously
- Strategy registry and evaluator
- UI dashboard showing opportunities
- No execution (analysis only)

**Success Criteria:**

- Scanner finds 50+ opportunities per day
- Strategies evaluate opportunities correctly
- UI shows real-time opportunities
- System runs 24/7 without crashes

### Phase 2: Paper Trading (Weeks 5-8)

**Goal**: Add execution engine with paper trading**Deliverables:**

- Paper broker implementation
- Execution engine
- Capital and risk management
- Order tracking

**Success Criteria:**

- Paper trades execute correctly
- Risk limits enforced
- Capital tracking accurate
- P&L calculated correctly

### Phase 3: Assisted Trading (Weeks 9-12)

**Goal**: Real broker integration with user approval**Deliverables:**

- Broker adapter (start with one: Alpaca or Zerodha)
- User approval workflow
- Real capital tracking
- Small capital allocation ($1K-$5K)

**Success Criteria:**

- Real orders execute via broker
- User can approve/reject trades
- Capital and risk limits work
- No execution errors

### Phase 4: Limited Automation (Weeks 13-16)

**Goal**: Semi-automated trading with strict limits**Deliverables:**

- Semi-auto mode
- Daily capital limits
- Learning system (basic)
- Performance tracking

**Success Criteria:**

- System auto-executes up to daily limit
- Learning system tracks performance
- Strategy weights adjust
- User can override

### Phase 5: Full Automation (Weeks 17-20)

**Goal**: Fully automated with continuous learning**Deliverables:**

- Full auto mode
- Strategy decay detection
- Auto-disable poor strategies
- Regime-aware strategy selection

**Success Criteria:**

- System runs fully automated
- Strategies auto-disable on decay
- Performance improves over time
- No manual intervention needed (except monitoring)

---

## Implementation Priorities

**Critical Path:**

1. Event bus and state management
2. Scanner workers
3. Strategy system
4. Capital and risk management
5. Paper broker
6. Execution engine
7. UI dashboard
8. Learning system

**Can Defer:**

- Advanced learning (ML/RL)
- Multiple broker adapters (start with one)
- Options strategies (add later)
- Advanced regime detection (start simple)

---

## Risk Mitigation

**Technical Risks:**

- System crashes: Implement health checks and auto-restart
- Data provider failures: Multiple providers with fallback
- Broker API failures: Retry logic and error handling
- Database corruption: Regular backups

**Trading Risks:**

- Over-trading: Daily trade limits
- Large losses: Daily loss limits and kill-switch
- Strategy decay: Auto-disable mechanisms
- Market crashes: Crash detection and position reduction

**Operational Risks:**

- User error: Approval workflows and overrides
- System bugs: Extensive testing and paper trading
- Data quality: Validation and error handling

---

## Success Metrics

**Technical Metrics:**

- System uptime: > 99.5%
- Scanner latency: < 5 seconds per scan
- Strategy evaluation: < 1 second per opportunity
- Execution latency: < 2 seconds

**Trading Metrics:**

- Win rate: > 50%
- Profit factor: > 1.5
- Sharpe ratio: > 1.0
- Maximum drawdown: < 15%

**User Experience:**

- Dashboard load time: < 2 seconds
- Real-time updates: < 1 second latency
- Override response time: < 500ms

---

## PART 11: MARKET DATA INTEGRITY & TRUTH LAYER

### Purpose

Prevent silent failures from bad data. Bad data corrupts all downstream decisions. This layer validates, reconciles, and monitors data quality, with the power to halt trading if data integrity is compromised.

### Architecture

**New Module Structure:**

```
backend/
├── data/
│   ├── integrity/
│   │   ├── data_validator.py          # Core validation engine
│   │   ├── anomaly_detector.py        # Detect spikes, gaps, bad ticks
│   │   ├── corporate_actions.py       # Handle splits, dividends, bonuses
│   │   ├── price_reconciler.py        # Reconcile data providers vs broker
│   │   ├── health_monitor.py          # Data health scoring and alerts
│   │   └── truth_layer.py             # Single source of truth for prices
│   │
│   └── providers/                     # Existing providers (unchanged)
```

### Data Validator

**Responsibilities:**

- Validate incoming market data before it enters the system
- Check for required fields (OHLCV)
- Validate data types and ranges
- Detect missing candles (gaps in time series)
- Detect price spikes (unrealistic moves > 10% in 1 minute)
- Detect volume anomalies (volume = 0 on trading day)

**Validation Rules:**

```python
class DataValidator:
    def validate_candle(self, candle: Dict) -> ValidationResult:
        """Validate a single candle."""
        checks = [
            self._check_required_fields(candle),
            self._check_price_ranges(candle),
            self._check_ohlc_logic(candle),  # High >= Low, etc.
            self._check_volume(candle),
            self._check_timestamp(candle)
        ]
        return ValidationResult(checks)
    
    def validate_series(self, series: pd.DataFrame) -> ValidationResult:
        """Validate entire time series."""
        checks = [
            self._check_missing_candles(series),
            self._check_price_spikes(series),
            self._check_volume_anomalies(series),
            self._check_corporate_actions(series)
        ]
        return ValidationResult(checks)
```

**Blocking Behavior:**

- If validation fails: Mark data as INVALID
- Invalid data is NOT passed to scanners
- Scanners skip symbols with invalid data
- Health monitor tracks validation failure rate

### Anomaly Detector

**Detected Anomalies:**

1. **Price Spikes:**

      - Price change > 10% in 1 minute (configurable)
      - Price change > 20% in 1 day
      - Price outside 3-sigma range (statistical outlier)

2. **Missing Candles:**

      - Expected candle missing (e.g., market hours but no data)
      - Gap in time series > 5 minutes during trading hours
      - Missing pre-market/after-hours data (if expected)

3. **Bad Ticks:**

      - Bid > Ask (impossible)
      - Volume < 0
      - Price = 0 or negative
      - Timestamp in future or too old

**Anomaly Handling:**

- **Minor Anomaly**: Log warning, continue with data
- **Major Anomaly**: Mark data as SUSPECT, require reconciliation
- **Critical Anomaly**: Mark data as INVALID, block trading for symbol

### Corporate Actions Handler

**Handled Actions:**

- **Stock Splits**: Adjust historical prices proportionally
- **Reverse Splits**: Adjust prices and quantities
- **Dividends**: Track ex-dividend dates (affects price)
- **Bonus Issues**: Adjust quantities
- **Mergers/Acquisitions**: Handle symbol changes

**Implementation:**

```python
class CorporateActionsHandler:
    def apply_split(self, data: pd.DataFrame, split_ratio: float, split_date: datetime):
        """Adjust historical prices for stock split."""
        # Divide prices before split date by split ratio
        # Adjust volumes proportionally
        pass
    
    def detect_corporate_action(self, symbol: str, date: datetime) -> Optional[CorporateAction]:
        """Detect if corporate action occurred on date."""
        # Check against corporate action database
        # Or detect from price/volume anomalies
        pass
```

**Data Provider Integration:**

- Yahoo Finance provides split data
- Alpha Vantage provides corporate actions
- Reconcile between providers
- Apply corrections to historical data

### Price Reconciler

**Purpose:** Ensure data from providers matches broker prices (ground truth)

**Reconciliation Process:**

1. Fetch latest price from data provider
2. Fetch latest price from broker (if position exists)
3. Compare prices
4. If discrepancy > 0.5%: Mark as RECONCILIATION_FAILED
5. If discrepancy > 2%: HALT trading for symbol

**Reconciliation Triggers:**

- Before placing new order
- Periodically for open positions (every 5 minutes)
- On data provider price update
- On broker position update

**Reconciliation Result:**

```python
@dataclass
class ReconciliationResult:
    symbol: str
    provider_price: float
    broker_price: float
    discrepancy: float
    discrepancy_percent: float
    status: str  # MATCH, MINOR_DISCREPANCY, MAJOR_DISCREPANCY, FAILED
    timestamp: datetime
```

### Data Health Monitor

**Health Scoring:**

- **GREEN**: All validations pass, reconciliation matches
- **YELLOW**: Minor anomalies detected, reconciliation minor discrepancy
- **RED**: Major anomalies, reconciliation failed, trading blocked

**Health Metrics:**

- Validation failure rate (last 100 data points)
- Reconciliation failure rate (last 24 hours)
- Anomaly frequency (anomalies per hour)
- Data freshness (time since last update)

**Health-Based Actions:**

- **GREEN**: Normal operation
- **YELLOW**: Log warnings, continue trading
- **RED**: HALT trading, alert user, require manual intervention

**UI Indicators:**

- Dashboard shows data health status (GREEN/YELLOW/RED badge)
- Per-symbol health status in scanner view
- Health history chart (trend over time)
- Alert when health degrades

### Truth Layer

**Purpose:** Single source of truth for market prices

**Implementation:**

```python
class TruthLayer:
    """Single source of truth for market data."""
    
    def get_price(self, symbol: str, timestamp: datetime) -> Optional[float]:
        """Get authoritative price for symbol at timestamp."""
        # 1. Check broker price (if position exists) - highest priority
        # 2. Check reconciled provider price
        # 3. Check cached price (if recent)
        # 4. Return None if no valid price available
        pass
    
    def is_data_valid(self, symbol: str) -> bool:
        """Check if data is valid for trading."""
        health = self.health_monitor.get_health(symbol)
        return health.status == "GREEN" or health.status == "YELLOW"
```

**Integration Points:**

- Scanners check `is_data_valid()` before processing
- Decision engine uses `get_price()` for price checks
- Execution engine reconciles before placing orders

---

## PART 12: EXPLICIT MARKET STATE ENGINE

### Purpose

Market state is not implicit - it's a first-class object that strategies, risk engine, and capital manager consume. This prevents strategies from trading in wrong regimes and allows risk limits to adapt to market conditions.

### Architecture

**New Module Structure:**

```
backend/
├── market_state/
│   ├── state_engine.py                # Main state engine
│   ├── regime_detector.py             # Detect market regimes
│   ├── volatility_detector.py         # Volatility state
│   ├── breadth_detector.py            # Market breadth (advance/decline)
│   ├── liquidity_detector.py          # Liquidity conditions
│   └── state_publisher.py             # Publish state to subscribers
```

### Market State Data Model

```python
@dataclass
class MarketState:
    """Authoritative market state object."""
    timestamp: datetime
    regime: str  # trending_up, trending_down, choppy, high_volatility, low_volatility
    volatility_state: str  # low, normal, high, extreme
    breadth_state: str  # bullish, neutral, bearish
    liquidity_state: str  # high, normal, low
    vix_level: float
    market_direction: str  # up, down, sideways
    confidence: float  # 0-1, how confident in state classification
    indicators: Dict[str, float]  # Supporting indicators
    transitions: List[StateTransition]  # Recent state changes
```

**State Dimensions:**

1. **Regime:**

      - **trending_up**: Strong upward trend (SPY > SMA50, momentum positive)
      - **trending_down**: Strong downward trend (SPY < SMA50, momentum negative)
      - **choppy**: Sideways, no clear direction
      - **high_volatility**: VIX > 25, high ATR
      - **low_volatility**: VIX < 15, low ATR

2. **Volatility State:**

      - **low**: VIX < 15, ATR < 1%
      - **normal**: VIX 15-25, ATR 1-3%
      - **high**: VIX 25-35, ATR 3-5%
      - **extreme**: VIX > 35, ATR > 5%

3. **Breadth State:**

      - **bullish**: Advance/decline ratio > 1.5, new highs > new lows
      - **neutral**: Advance/decline ratio 0.67-1.5
      - **bearish**: Advance/decline ratio < 0.67, new lows > new highs

4. **Liquidity State:**

      - **high**: High volume, tight spreads
      - **normal**: Average volume and spreads
      - **low**: Low volume, wide spreads

### State Detection Logic

**Regime Detection:**

```python
class RegimeDetector:
    def detect_regime(self, market_data: pd.DataFrame) -> str:
        """Detect current market regime."""
        # Calculate SPY trend
        spy_trend = self._calculate_trend(market_data['SPY'])
        
        # Calculate volatility
        vix = self._get_vix()
        atr = self._calculate_atr(market_data)
        
        # Determine regime
        if vix > 25 or atr > 0.05:
            return "high_volatility"
        elif spy_trend > 0.02:  # 2% uptrend
            return "trending_up"
        elif spy_trend < -0.02:  # 2% downtrend
            return "trending_down"
        elif abs(spy_trend) < 0.005:  # Less than 0.5% movement
            return "choppy"
        else:
            return "normal"
```

**Volatility Detection:**

- VIX level (primary indicator)
- ATR of SPY (secondary indicator)
- Recent price swings (tertiary indicator)

**Breadth Detection:**

- Advance/decline ratio (NYSE or NASDAQ)
- New highs vs new lows
- Percentage of stocks above moving averages

**Liquidity Detection:**

- Average daily volume vs 30-day average
- Bid-ask spreads
- Market depth (if available)

### State Publishing

**Update Frequency:**

- Every 5 minutes during market hours
- On significant state change (regime transition)
- On volatility spike (> 20% VIX change)

**Publishing Mechanism:**

- Redis pub/sub: `market_state:current`
- WebSocket broadcast to UI
- Event bus: `MarketStateUpdated` event

**Subscribers:**

- Strategy evaluator (filters strategies by regime)
- Risk engine (adjusts limits based on volatility)
- Capital manager (adjusts position sizes)
- UI dashboard (displays current state)

### Strategy Integration

**Strategy Regime Filtering:**

```python
# In strategy YAML
market_regimes:
 - "trending_up"
 - "trending_down"
exclude_regimes:
 - "choppy"
 - "high_volatility"

# In strategy evaluator
def evaluate_strategy(strategy, opportunity, market_state):
    # Check if strategy is applicable to current regime
    if market_state.regime not in strategy.market_regimes:
        return None  # Strategy not applicable
    
    if market_state.regime in strategy.exclude_regimes:
        return None  # Strategy explicitly excluded
    
    # Continue evaluation...
```

### Risk Engine Integration

**Volatility-Based Risk Adjustment:**

- **Low Volatility**: Normal position sizes
- **Normal Volatility**: Normal position sizes
- **High Volatility**: Reduce position sizes by 25%
- **Extreme Volatility**: Reduce position sizes by 50%, stop new trades

**Regime-Based Risk Adjustment:**

- **Trending Markets**: Normal risk limits
- **Choppy Markets**: Tighter risk limits, shorter holding periods
- **High Volatility**: Reduced position sizes, wider stop losses

### UI Visualization

**Market State Widget:**

- Current regime badge (color-coded)
- Volatility gauge (low/normal/high/extreme)
- Breadth indicator (bullish/neutral/bearish)
- State history chart (regime transitions over time)
- Confidence indicator (how certain is the state)

**State Transitions:**

- Show when regime changed
- Highlight significant transitions
- Alert on volatility spikes

---

## PART 13: PORTFOLIO-LEVEL INTELLIGENCE

### Purpose

Extend decision-making from trade-level to portfolio-level. A good trade in isolation may be bad for the portfolio (correlation, sector concentration, factor exposure).

### Architecture

**New Module Structure:**

```
backend/
├── portfolio/
│   ├── portfolio_manager.py           # Main portfolio orchestrator
│   ├── exposure_tracker.py            # Track sector, factor, correlation exposure
│   ├── diversification_engine.py        # Diversification guardrails
│   ├── rebalancer.py                  # Optional rebalancing logic
│   └── opportunity_ranker.py         # Rank opportunities by portfolio fit
```

### Portfolio State Tracking

**Tracked Exposures:**

1. **Sector Exposure:**

      - Percentage of capital per GICS sector
      - Maximum sector limit (e.g., 25%)
      - Alert when approaching limit

2. **Factor Exposure:**

      - Value, Growth, Momentum, Quality factors
      - Factor loadings per position
      - Portfolio factor exposure

3. **Correlation Exposure:**

      - Pairwise correlations between positions
      - Portfolio correlation matrix
      - Average portfolio correlation

4. **Market Cap Exposure:**

      - Large cap, mid cap, small cap allocation
      - Target allocation vs actual

5. **Geographic Exposure:**

      - US, International, Emerging markets
      - Currency exposure

**Portfolio State Model:**

```python
@dataclass
class PortfolioState:
    timestamp: datetime
    total_capital: float
    allocated_capital: float
    available_capital: float
    sector_exposure: Dict[str, float]  # Sector -> percentage
    factor_exposure: Dict[str, float]  # Factor -> loading
    correlation_matrix: pd.DataFrame
    average_correlation: float
    diversification_score: float  # 0-1, higher is better
    positions: List[Position]
```

### Exposure Optimization

**Optimization Goals:**

- Maximize diversification (minimize correlation)
- Balance sector exposure (avoid concentration)
- Maintain target factor exposure
- Respect risk limits

**Optimization Process:**

1. Calculate current portfolio state
2. Evaluate new opportunity against portfolio
3. Calculate projected portfolio state if trade taken
4. Check if projected state violates limits
5. Reject or modify trade if limits violated

**Example:**

```python
def evaluate_portfolio_fit(opportunity: Opportunity, portfolio_state: PortfolioState) -> PortfolioFit:
    """Evaluate if opportunity fits portfolio."""
    # Calculate projected exposure
    projected_sector_exposure = calculate_projected_exposure(opportunity, portfolio_state)
    
    # Check sector limits
    if projected_sector_exposure[opportunity.sector] > 0.25:
        return PortfolioFit(
            approved=False,
            reason="Sector exposure limit exceeded",
            current_exposure=portfolio_state.sector_exposure[opportunity.sector],
            projected_exposure=projected_sector_exposure[opportunity.sector]
        )
    
    # Check correlation
    correlation = calculate_correlation(opportunity, portfolio_state.positions)
    if correlation > 0.7:
        return PortfolioFit(
            approved=False,
            reason="High correlation with existing positions",
            correlation=correlation
        )
    
    return PortfolioFit(approved=True, diversification_improvement=...)
```

### Diversification Guardrails

**Guardrails:**

1. **Sector Concentration:**

      - Maximum 25% per sector (configurable)
      - Alert at 20%
      - Block new trades at 25%

2. **Correlation Limits:**

      - Maximum 0.7 correlation with any existing position
      - Maximum 0.5 average portfolio correlation
      - Prefer negative correlations

3. **Factor Balancing:**

      - Avoid over-concentration in single factor
      - Maintain balanced factor exposure
      - Rebalance if factor exposure drifts > 10%

4. **Position Count:**

      - Minimum 5 positions (diversification)
      - Maximum 20 positions (manageability)
      - Optimal 10-15 positions

### Opportunity Ranking

**Ranking Factors:**

1. **Strategy Score**: Original strategy evaluation score
2. **Portfolio Fit**: How well it fits portfolio (diversification)
3. **Correlation Penalty**: Penalize high correlations
4. **Sector Balance**: Prefer sectors with low exposure
5. **Factor Balance**: Prefer factors with low exposure

**Ranking Formula:**

```
Final Score = Strategy Score × Portfolio Fit Multiplier
Portfolio Fit Multiplier = 
    (1 - correlation_penalty) × 
    (1 - sector_concentration_penalty) × 
    (1 - factor_concentration_penalty) ×
    diversification_bonus
```

**Example:**

- Opportunity A: Strategy score 85, correlation 0.8 → Final score 68 (reduced)
- Opportunity B: Strategy score 75, correlation 0.2 → Final score 82 (increased)

### Rebalancing Logic (Optional)

**Rebalancing Triggers:**

- Sector exposure drifts > 5% from target
- Factor exposure drifts > 10% from target
- Correlation increases > 0.1
- Monthly rebalancing (optional)

**Rebalancing Process:**

1. Calculate target portfolio state
2. Identify positions to reduce
3. Identify positions to increase
4. Generate rebalancing orders
5. Execute rebalancing (with user approval)

**Safety:**

- Rebalancing requires user approval
- Respects position size limits
- Respects transaction costs
- Only rebalance if benefit > cost

---

## PART 14: STRATEGY ATTRIBUTION & POST-MORTEM ENGINE

### Purpose

Explain WHY strategies succeed or fail. This enables better strategy optimization, builds trust, and improves learning quality.

### Architecture

**New Module Structure:**

```
backend/
├── attribution/
│   ├── attribution_engine.py          # Main attribution engine
│   ├── trade_attributor.py           # Trade-level attribution
│   ├── indicator_contributor.py      # Indicator contribution analysis
│   ├── failure_classifier.py         # Classify failure reasons
│   └── feedback_loop.py               # Feed back to learning system
```

### Trade-Level Attribution

**Attribution Model:**

```python
@dataclass
class TradeAttribution:
    trade_id: str
    strategy_id: str
    symbol: str
    entry_reason: str
    exit_reason: str
    pnl: float
    pnl_percent: float
    
    # Entry Attribution
    entry_indicators: Dict[str, float]  # Indicator values at entry
    entry_indicator_contributions: Dict[str, float]  # How much each indicator contributed
    entry_patterns: List[str]  # Patterns detected at entry
    entry_regime: str  # Market regime at entry
    
    # Exit Attribution
    exit_indicators: Dict[str, float]
    exit_reason_category: str  # profit_target, stop_loss, time_based, manual
    exit_timing: str  # early, on_time, late
    
    # Performance Attribution
    max_favorable_excursion: float  # Best price reached
    max_adverse_excursion: float  # Worst price reached
    entry_quality: float  # 0-1, how good was entry
    exit_quality: float  # 0-1, how good was exit
```

**Attribution Process:**

1. **Entry Attribution:**

      - Which indicators triggered entry
      - Contribution of each indicator to signal score
      - Patterns detected
      - Market regime at entry

2. **Exit Attribution:**

      - Why trade exited (profit target, stop loss, time)
      - Was exit optimal (compare to max favorable excursion)
      - Was exit timely (early, on time, late)

3. **Performance Attribution:**

      - Entry quality: How close to optimal entry
      - Exit quality: How close to optimal exit
      - Holding period quality: Was holding period appropriate

### Indicator Contribution Analysis

**Contribution Calculation:**

```python
def calculate_indicator_contribution(strategy_signal: StrategySignal) -> Dict[str, float]:
    """Calculate how much each indicator contributed to signal."""
    contributions = {}
    total_score = 0
    
    for condition in strategy_signal.conditions:
        indicator_name = condition.indicator
        condition_score = condition.score * condition.weight
        contributions[indicator_name] = condition_score
        total_score += condition_score
    
    # Normalize to percentages
    for indicator in contributions:
        contributions[indicator] = contributions[indicator] / total_score * 100
    
    return contributions
```

**Example Output:**

```
Signal Score: 85
Indicator Contributions:
 - SMA_20: 35% (strong trend)
 - RSI: 25% (momentum confirmation)
 - MACD: 20% (crossover signal)
 - Pattern: 20% (bullish engulfing)
```

### Failure Classification

**Failure Categories:**

1. **Late Entry:**

      - Entry after optimal entry point
      - Missed initial move
      - Entry quality < 0.5

2. **Volatility Spike:**

      - Unexpected volatility increase
      - Stop loss hit due to volatility, not trend reversal
      - ATR increased > 50% during trade

3. **Regime Mismatch:**

      - Strategy traded in wrong regime
      - Market regime changed during trade
      - Strategy not suitable for current regime

4. **False Signal:**

      - Indicators gave false signal
      - Pattern did not play out
      - Signal confidence was low but trade taken

5. **Poor Exit Timing:**

      - Exited too early (left money on table)
      - Exited too late (gave back profits)
      - Exit quality < 0.5

6. **External Event:**

      - News event moved price
      - Earnings surprise
      - Market-wide event

**Classification Process:**

```python
def classify_failure(trade: Trade, attribution: TradeAttribution) -> FailureCategory:
    """Classify why trade failed."""
    if trade.pnl < 0:
        if attribution.entry_quality < 0.5:
            return FailureCategory.LATE_ENTRY
        elif attribution.exit_reason == "stop_loss" and volatility_spike_detected(trade):
            return FailureCategory.VOLATILITY_SPIKE
        elif attribution.entry_regime != attribution.exit_regime:
            return FailureCategory.REGIME_MISMATCH
        elif attribution.entry_indicator_contributions["confidence"] < 0.6:
            return FailureCategory.FALSE_SIGNAL
        else:
            return FailureCategory.UNKNOWN
    else:
        if attribution.exit_quality < 0.5:
            return FailureCategory.POOR_EXIT_TIMING
        else:
            return FailureCategory.SUCCESS
```

### Feedback into Learning System

**Feedback Data:**

- Failure category per trade
- Indicator contribution per trade
- Entry/exit quality per trade
- Regime performance per strategy

**Learning Adjustments:**

1. **Strategy Weight Adjustment:**

      - Reduce weight if failure rate > threshold
      - Increase weight if success rate > threshold
      - Adjust based on failure category

2. **Indicator Weight Adjustment:**

      - Reduce weight of indicators with low contribution
      - Increase weight of indicators with high contribution
      - Disable indicators that consistently fail

3. **Regime Awareness:**

      - Disable strategy in regimes where it fails
      - Enable strategy in regimes where it succeeds
      - Adjust position sizes based on regime performance

4. **Parameter Optimization:**

      - Optimize parameters based on failure patterns
      - Adjust stop loss based on volatility spike frequency
      - Adjust holding period based on exit timing quality

---

## PART 15: TIME & LATENCY AWARENESS

### Purpose

Signals have expiration dates. Stale signals are dangerous. This system ensures signals are fresh and execution is timely.

### Architecture

**New Module Structure:**

```
backend/
├── timing/
│   ├── signal_expiry.py               # Signal expiry logic
│   ├── latency_tracker.py             # Track latency budgets
│   ├── stale_detector.py              # Detect stale opportunities
│   └── timing_constraints.py           # Timing constraints per strategy
```

### Signal Expiry Logic

**Expiry Rules:**

- **Intraday Strategies**: Signals expire after 5 minutes
- **Swing Strategies**: Signals expire after 1 hour
- **Position Strategies**: Signals expire after 4 hours
- **Configurable per strategy**: Each strategy defines expiry time

**Expiry Model:**

```python
@dataclass
class SignalExpiry:
    signal_id: str
    generated_at: datetime
    expires_at: datetime
    strategy_type: str  # intraday, swing, position
    expiry_minutes: int  # Strategy-specific expiry
    is_expired: bool
    age_seconds: float
```

**Expiry Check:**

```python
def is_signal_stale(signal: StrategySignal, current_time: datetime) -> bool:
    """Check if signal is stale."""
    age = (current_time - signal.generated_at).total_seconds()
    expiry_seconds = signal.strategy.expiry_minutes * 60
    
    if age > expiry_seconds:
        return True
    
    # Additional checks
    if signal.opportunity.price_changed > 0.05:  # 5% price change
        return True  # Price moved too much, signal invalid
    
    return False
```

**Expiry Handling:**

- Stale signals are NOT evaluated
- Stale signals are NOT passed to decision engine
- Stale signals are logged for analysis
- UI shows signal age and expiry status

### Latency Budgets

**Latency Budgets per Strategy:**

- **Intraday**: Total latency < 2 seconds (scanner → execution)
- **Swing**: Total latency < 10 seconds
- **Position**: Total latency < 30 seconds

**Latency Tracking:**

```python
@dataclass
class LatencyBudget:
    strategy_type: str
    max_total_latency: float  # seconds
    scanner_latency: float
    evaluation_latency: float
    decision_latency: float
    execution_latency: float
    current_total: float
    is_within_budget: bool
```

**Latency Monitoring:**

- Track latency at each stage
- Alert if latency exceeds budget
- Reject signals if latency too high
- Optimize slow stages

### Stale Opportunity Detection

**Staleness Indicators:**

1. **Price Change**: Opportunity price changed > 5% since generation
2. **Time Elapsed**: More than expiry time elapsed
3. **Volume Change**: Volume dropped > 50% since generation
4. **Indicator Change**: Key indicators changed significantly

**Staleness Check:**

```python
def is_opportunity_stale(opportunity: Opportunity, signal: StrategySignal) -> bool:
    """Check if opportunity is stale."""
    # Check time
    if is_signal_stale(signal, datetime.now()):
        return True
    
    # Check price change
    price_change = abs(opportunity.current_price - signal.entry_price) / signal.entry_price
    if price_change > 0.05:  # 5% change
        return True
    
    # Check volume
    if opportunity.volume < signal.opportunity.volume * 0.5:
        return True
    
    return False
```

**Staleness Handling:**

- Stale opportunities are rejected
- Stale opportunities are logged
- UI shows staleness status
- Alert user if staleness rate > 10%

### Execution Timing

**Timing Constraints:**

- Execute within latency budget
- Reject if signal expired
- Reject if opportunity stale
- Prioritize fresh signals

**Execution Flow:**

```
Signal Generated → Check Expiry → Check Staleness → Check Latency → Execute
                        ↓              ↓                ↓
                    Reject if      Reject if       Reject if
                    expired        stale           too slow
```

---

## PART 16: SHADOW / GHOST TRADING MODE

### Purpose

Test disabled strategies, new parameters, or experiments in parallel with live trading without risking capital.

### Architecture

**New Module Structure:**

```
backend/
├── shadow/
│   ├── shadow_engine.py              # Main shadow trading engine
│   ├── shadow_broker.py              # Shadow broker (paper trading)
│   ├── shadow_tracker.py             # Track shadow positions
│   ├── comparison_engine.py          # Compare shadow vs live
│   └── isolation_layer.py             # Prevent shadow leakage
```

### Shadow Trading Flow

**Shadow Execution:**

1. **Signal Generation**: Same as live (all strategies evaluated)
2. **Shadow Filter**: Filter signals for shadow strategies
3. **Shadow Execution**: Execute via shadow broker (paper trading)
4. **Shadow Tracking**: Track shadow positions separately
5. **Shadow P&L**: Calculate shadow P&L independently

**Shadow Strategies:**

- Disabled strategies (test if they would work)
- New strategies (test before activation)
- Modified strategies (test parameter changes)
- Experimental strategies (test new ideas)

**Shadow Configuration:**

```python
@dataclass
class ShadowConfig:
    strategy_id: str
    shadow_capital: float  # Virtual capital for shadow trading
    start_date: datetime
    end_date: Optional[datetime]  # None = ongoing
    comparison_benchmark: str  # Compare to which live strategy
```

### Shadow Broker

**Implementation:**

- Same interface as real broker
- Paper trading execution
- Realistic slippage simulation
- Realistic fill simulation
- Track shadow positions

**Shadow Position Tracking:**

```python
class ShadowBroker:
    def place_order(self, order: Order) -> OrderResult:
        """Place shadow order (paper trading)."""
        # Simulate execution
        fill_price = self._simulate_fill(order)
        slippage = self._calculate_slippage(order)
        
        # Create shadow position
        shadow_position = ShadowPosition(
            symbol=order.symbol,
            quantity=order.quantity,
            entry_price=fill_price,
            timestamp=datetime.now()
        )
        
        return OrderResult(filled=True, fill_price=fill_price, ...)
```

### Shadow vs Live Comparison

**Comparison Metrics:**

- Win rate comparison
- Profit factor comparison
- Sharpe ratio comparison
- Drawdown comparison
- Trade timing comparison

**Comparison Report:**

```python
@dataclass
class ShadowComparison:
    strategy_id: str
    period_start: datetime
    period_end: datetime
    
    # Live Performance
    live_win_rate: float
    live_profit_factor: float
    live_sharpe: float
    live_drawdown: float
    
    # Shadow Performance
    shadow_win_rate: float
    shadow_profit_factor: float
    shadow_sharpe: float
    shadow_drawdown: float
    
    # Comparison
    win_rate_diff: float
    profit_factor_diff: float
    sharpe_diff: float
    drawdown_diff: float
    
    # Recommendation
    recommendation: str  # activate, keep_shadow, disable
```

### Isolation Layer

**Prevent Shadow Leakage:**

- Shadow strategies NEVER execute real orders
- Shadow capital is separate from live capital
- Shadow positions are separate from live positions
- Shadow decisions don't affect live decisions

**Isolation Checks:**

```python
def is_shadow_strategy(strategy_id: str) -> bool:
    """Check if strategy is shadow-only."""
    strategy = strategy_registry.get(strategy_id)
    return strategy.shadow_only == True

def prevent_shadow_leakage(order: Order):
    """Ensure shadow orders never execute live."""
    if is_shadow_strategy(order.strategy_id):
        if order.broker != "shadow":
            raise IsolationError("Shadow strategy attempted live execution")
```

### UI Comparison Views

**Shadow Dashboard:**

- List of shadow strategies
- Shadow performance vs live performance
- Side-by-side comparison charts
- Recommendation (activate/keep shadow/disable)

**Comparison Charts:**

- Equity curves (shadow vs live)
- Win rate comparison
- Drawdown comparison
- Trade timing comparison

---

## PART 17: HUMAN TRUST & EXPLAINABILITY LAYER

### Purpose

Maintain human trust in automation through explainability, confidence indicators, and clear reasoning.

### Architecture

**New Module Structure:**

```
backend/
├── explainability/
│   ├── explainer_engine.py           # Main explainability engine
│   ├── decision_explainer.py          # Explain trading decisions
│   ├── confidence_calculator.py       # Calculate confidence scores
│   ├── uncertainty_quantifier.py      # Quantify uncertainty
│   └── trust_scorer.py                # Overall trust score
```

### Decision Explainability

**Explanation Model:**

```python
@dataclass
class DecisionExplanation:
    decision_id: str
    decision: str  # APPROVE, REJECT, MODIFY
    symbol: str
    strategy_id: str
    
    # Why This Trade
    entry_reasoning: str  # Human-readable explanation
    indicator_summary: str  # Key indicators and values
    pattern_summary: str  # Patterns detected
    regime_alignment: str  # How it aligns with market regime
    
    # Risk Justification
    risk_amount: float
    risk_percent: float
    risk_reward_ratio: float
    position_size_reasoning: str
    
    # Portfolio Fit
    portfolio_fit: str  # How it fits portfolio
    diversification_impact: str  # Diversification impact
    correlation_impact: str  # Correlation impact
    
    # What Could Invalidate
    invalidation_conditions: List[str]  # Conditions that would invalidate trade
    stop_loss_reason: str  # Why this stop loss
    take_profit_reason: str  # Why this take profit
    
    # Confidence
    confidence_score: float  # 0-1
    confidence_factors: List[str]  # What increases/decreases confidence
    uncertainty_sources: List[str]  # Sources of uncertainty
```

**Explanation Generation:**

```python
def explain_decision(decision: TradingDecision) -> DecisionExplanation:
    """Generate human-readable explanation of decision."""
    explanation = DecisionExplanation(
        decision_id=decision.id,
        decision=decision.decision,
        symbol=decision.symbol,
        strategy_id=decision.strategy_id,
        
        entry_reasoning=f"Strong {decision.strategy_type} signal detected. "
                       f"{decision.indicators['sma_20']} is above {decision.indicators['sma_50']}, "
                       f"indicating uptrend. RSI at {decision.indicators['rsi']} shows momentum without overbought conditions.",
        
        risk_justification=f"Risking ${decision.risk_amount:.2f} ({decision.risk_percent:.1f}% of capital) "
                          f"for potential reward of ${decision.reward_amount:.2f} "
                          f"(risk-reward ratio: {decision.risk_reward_ratio:.2f}:1).",
        
        invalidation_conditions=[
            "Price breaks below stop loss at $X",
            "RSI exceeds 70 (overbought)",
            "Market regime changes to choppy",
            "Correlation with existing positions exceeds 0.7"
        ],
        
        confidence_score=calculate_confidence(decision),
        confidence_factors=[
            "High strategy score (85/100)",
            "Multiple indicator confirmations",
            "Strong pattern detection",
            "Favorable market regime"
        ],
        uncertainty_sources=[
            "Recent volatility increase",
            "Low volume day",
            "Earnings announcement upcoming"
        ]
    )
    
    return explanation
```

### Confidence Scoring

**Confidence Factors:**

1. **Strategy Score**: Higher score = higher confidence
2. **Indicator Confirmations**: More confirmations = higher confidence
3. **Pattern Strength**: Stronger patterns = higher confidence
4. **Regime Alignment**: Better regime match = higher confidence
5. **Data Quality**: Better data quality = higher confidence
6. **Historical Performance**: Better historical performance = higher confidence

**Confidence Calculation:**

```python
def calculate_confidence(decision: TradingDecision) -> float:
    """Calculate confidence score (0-1)."""
    factors = []
    
    # Strategy score factor (0-0.3)
    factors.append(decision.strategy_score / 100 * 0.3)
    
    # Indicator confirmations (0-0.2)
    confirmations = len([c for c in decision.conditions if c.met])
    factors.append(min(confirmations / 5, 1.0) * 0.2)
    
    # Pattern strength (0-0.2)
    if decision.patterns:
        avg_pattern_strength = sum(p.strength for p in decision.patterns) / len(decision.patterns)
        factors.append(avg_pattern_strength / 100 * 0.2)
    
    # Regime alignment (0-0.15)
    regime_match = 1.0 if decision.regime in decision.strategy.regimes else 0.5
    factors.append(regime_match * 0.15)
    
    # Data quality (0-0.15)
    data_quality = decision.data_quality_score  # From data integrity layer
    factors.append(data_quality * 0.15)
    
    return sum(factors)
```

### Uncertainty Quantification

**Uncertainty Sources:**

1. **Data Uncertainty**: Low data quality, missing data
2. **Model Uncertainty**: Strategy performance variance
3. **Market Uncertainty**: High volatility, regime uncertainty
4. **Execution Uncertainty**: Slippage, fill uncertainty

**Uncertainty Model:**

```python
@dataclass
class Uncertainty:
    total_uncertainty: float  # 0-1, higher is more uncertain
    data_uncertainty: float
    model_uncertainty: float
    market_uncertainty: float
    execution_uncertainty: float
    uncertainty_sources: List[str]
```

**Uncertainty Handling:**

- High uncertainty → Lower position sizes
- High uncertainty → Require user approval
- High uncertainty → Wider stop losses
- High uncertainty → Alert user

### Trust Scoring

**Trust Score Components:**

1. **System Reliability**: Uptime, error rate
2. **Decision Quality**: Win rate, profit factor
3. **Explainability**: Quality of explanations
4. **Transparency**: How much user understands
5. **Consistency**: Consistent behavior over time

**Trust Score:**

```python
@dataclass
class TrustScore:
    overall_trust: float  # 0-1
    system_reliability: float
    decision_quality: float
    explainability: float
    transparency: float
    consistency: float
    trust_trend: str  # improving, stable, declining
```

### UI Affordances

**Explanation Display:**

- "Why This Trade" section on every signal
- "What Could Invalidate" section
- Confidence gauge (visual indicator)
- Uncertainty indicators
- Trust score badge

**Override Justifications:**

- When user overrides, require justification
- Log override reason
- Track override performance
- Learn from overrides

**Audit Trail:**

- All explanations logged
- All overrides logged with reasons
- Trust score history
- Explanation quality metrics

---

## PART 18: OPERATIONAL RESILIENCE & DISASTER RECOVERY

### Purpose

System must survive crashes, restarts, network failures, and other operational issues without losing state or creating duplicate orders.

### Architecture

**New Module Structure:**

```
backend/
├── resilience/
│   ├── heartbeat_monitor.py           # Health monitoring
│   ├── service_manager.py              # Auto-restart services
│   ├── state_recovery.py               # Recover state after crash
│   ├── duplicate_prevention.py        # Prevent duplicate orders
│   ├── safe_shutdown.py               # Graceful shutdown handling
│   └── disaster_recovery.py           # Disaster recovery procedures
```

### Heartbeat Monitoring

**Heartbeat System:**

- Each service sends heartbeat every 30 seconds
- Monitor tracks heartbeats
- Alert if heartbeat missing > 90 seconds
- Auto-restart service if heartbeat missing > 2 minutes

**Heartbeat Model:**

```python
@dataclass
class Heartbeat:
    service_id: str
    timestamp: datetime
    status: str  # healthy, degraded, unhealthy
    metrics: Dict[str, Any]  # CPU, memory, queue depth, etc.
```

**Health Checks:**

- Service responding
- Database connected
- Redis connected
- Broker API connected
- Queue depth reasonable
- Error rate acceptable

### Auto-Restart Services

**Restart Logic:**

1. Detect service failure (missing heartbeat)
2. Attempt graceful shutdown
3. Wait 10 seconds
4. Restart service
5. Verify service healthy
6. Alert if restart fails

**Service Manager:**

```python
class ServiceManager:
    def monitor_services(self):
        """Monitor all services."""
        for service in self.services:
            if not service.is_healthy():
                self.restart_service(service)
    
    def restart_service(self, service: Service):
        """Restart failed service."""
        try:
            service.shutdown()
            time.sleep(10)
            service.start()
            if service.is_healthy():
                logger.info(f"Service {service.id} restarted successfully")
            else:
                raise ServiceRestartError(f"Service {service.id} failed to restart")
        except Exception as e:
            logger.error(f"Failed to restart service {service.id}: {e}")
            alert_user(f"Service {service.id} requires manual intervention")
```

### Safe Shutdown Handling

**Shutdown Scenarios:**

1. **Graceful Shutdown**: System shutdown command
2. **Ungraceful Shutdown**: Crash, power loss, kill signal
3. **Mid-Trade Shutdown**: Shutdown during active trade

**Shutdown Process:**

1. **Stop Accepting New Signals**: Stop processing new opportunities
2. **Complete In-Flight Operations**: Wait for current operations to complete
3. **Cancel Pending Orders**: Cancel orders not yet filled (optional)
4. **Save State**: Save all state to database
5. **Close Connections**: Close database, Redis, broker connections
6. **Exit**: Clean exit

**Mid-Trade Handling:**

- If shutdown during trade:
    - Save trade state
    - On restart, recover trade state
    - Continue monitoring trade
    - Execute exit logic when conditions met

### State Recovery

**Recovery After Crash:**

1. **Load Persistent State**: Load from database
2. **Reconstruct In-Memory State**: Rebuild from database
3. **Reconcile Positions**: Reconcile with broker
4. **Resume Operations**: Continue from last known good state

**State to Recover:**

- Open positions
- Pending orders
- Capital state
- Strategy states
- Market state
- Scanner states

**Recovery Process:**

```python
class StateRecovery:
    def recover_after_crash(self):
        """Recover system state after crash."""
        # Load positions
        positions = self.db.load_positions()
        
        # Reconcile with broker
        broker_positions = self.broker.get_all_positions()
        reconciled_positions = self.reconcile_positions(positions, broker_positions)
        
        # Reconstruct capital state
        capital_state = self.reconstruct_capital(reconciled_positions)
        
        # Load pending orders
        pending_orders = self.db.load_pending_orders()
        
        # Verify orders still pending
        for order in pending_orders:
            broker_order = self.broker.get_order(order.id)
            if broker_order.status != "pending":
                # Order filled or cancelled, update state
                self.update_order_status(order.id, broker_order.status)
        
        # Resume operations
        self.resume_operations()
```

### Duplicate Order Prevention

**Prevention Mechanisms:**

1. **Idempotency Keys**: Each order has unique idempotency key
2. **Order Deduplication**: Check if order already exists before placing
3. **State Machine**: Order state machine prevents duplicate transitions
4. **Database Constraints**: Unique constraints on order IDs

**Idempotency:**

```python
def place_order_with_idempotency(order: Order):
    """Place order with idempotency check."""
    idempotency_key = generate_idempotency_key(order)
    
    # Check if order already exists
    existing_order = db.get_order_by_idempotency_key(idempotency_key)
    if existing_order:
        return existing_order  # Return existing order, don't create duplicate
    
    # Place new order
    result = broker.place_order(order)
    
    # Store with idempotency key
    db.save_order(order, idempotency_key)
    
    return result
```

**Recovery Scenarios:**

- **Network Failure**: Retry with same idempotency key
- **Crash Before Confirmation**: On restart, check if order exists
- **Duplicate Request**: Same idempotency key = same order

### Disaster Recovery Procedures

**Disaster Scenarios:**

1. **Database Corruption**: Restore from backup
2. **Data Loss**: Restore from backup, reconcile with broker
3. **Broker API Failure**: Switch to backup broker (if available)
4. **Complete System Failure**: Restore from backup, rebuild state

**Recovery Procedures:**

1. **Backup Strategy**: Daily database backups, hourly state snapshots
2. **Backup Verification**: Test backups regularly
3. **Recovery Testing**: Test recovery procedures monthly
4. **Documentation**: Document all recovery procedures

**Backup Schedule:**

- **Database**: Daily full backup, hourly incremental
- **State Snapshots**: Every 15 minutes
- **Configuration**: On every change
- **Audit Logs**: Daily backup, retain 90 days

**Recovery Time Objectives:**

- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 15 minutes (max data loss)

---

## Updated Module Structure

Add to existing structure:

```
backend/
├── data/
│   └── integrity/                     # NEW: Data integrity layer
│       ├── data_validator.py
│       ├── anomaly_detector.py
│       ├── corporate_actions.py
│       ├── price_reconciler.py
│       ├── health_monitor.py
│       └── truth_layer.py
│
├── market_state/                      # NEW: Market state engine
│   ├── state_engine.py
│   ├── regime_detector.py
│   ├── volatility_detector.py
│   ├── breadth_detector.py
│   ├── liquidity_detector.py
│   └── state_publisher.py
│
├── portfolio/                         # NEW: Portfolio intelligence
│   ├── portfolio_manager.py
│   ├── exposure_tracker.py
│   ├── diversification_engine.py
│   ├── rebalancer.py
│   └── opportunity_ranker.py
│
├── attribution/                       # NEW: Attribution engine
│   ├── attribution_engine.py
│   ├── trade_attributor.py
│   ├── indicator_contributor.py
│   ├── failure_classifier.py
│   └── feedback_loop.py
│
├── timing/                           # NEW: Timing awareness
│   ├── signal_expiry.py
│   ├── latency_tracker.py
│   ├── stale_detector.py
│   └── timing_constraints.py
│
├── shadow/                            # NEW: Shadow trading
│   ├── shadow_engine.py
│   ├── shadow_broker.py
│   ├── shadow_tracker.py
│   ├── comparison_engine.py
│   └── isolation_layer.py
│
├── explainability/                    # NEW: Explainability
│   ├── explainer_engine.py
│   ├── decision_explainer.py
│   ├── confidence_calculator.py
│   ├── uncertainty_quantifier.py
│   └── trust_scorer.py
│
└── resilience/                        # NEW: Resilience
    ├── heartbeat_monitor.py
    ├── service_manager.py
    ├── state_recovery.py
    ├── duplicate_prevention.py
    ├── safe_shutdown.py
    └── disaster_recovery.py
```

---

## Updated Rollout Plan

**Phase 1: Foundation + Data Integrity (Weeks 1-3)**

- Add data integrity layer
- Add market state engine
- Integrate with existing scanners

**Phase 2: Portfolio Intelligence (Weeks 4-5)**

- Add portfolio-level intelligence
- Integrate with decision engine
- Test diversification logic

**Phase 3: Attribution & Timing (Weeks 6-7)**

- Add attribution engine
- Add timing awareness
- Integrate with execution engine

**Phase 4: Shadow Trading & Explainability (Weeks 8-9)**

- Add shadow trading
- Add explainability layer
- Integrate with UI

**Phase 5: Resilience & Hardening (Weeks 10-12)**

- Add resilience mechanisms
- Test disaster recovery
- Performance optimization

---