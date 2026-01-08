-- Stockport v4 Database Schema (SQLite)
-- SQLite-compatible schema for personal use

-- Positions table
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price REAL NOT NULL,
    current_price REAL,
    entry_date TIMESTAMP NOT NULL,
    strategy_id TEXT,
    signal_id TEXT,
    sector TEXT,
    value REAL,
    pnl REAL,
    pnl_percent REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_positions_strategy_id ON positions(strategy_id);
CREATE INDEX IF NOT EXISTS idx_positions_entry_date ON positions(entry_date);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE NOT NULL,
    decision_id TEXT,
    signal_id TEXT,
    strategy_id TEXT,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,  -- 'buy' or 'sell'
    quantity INTEGER NOT NULL,
    order_type TEXT NOT NULL,  -- 'market', 'limit', 'stop'
    limit_price REAL,
    stop_price REAL,
    fill_price REAL,
    filled_quantity INTEGER,
    status TEXT NOT NULL,  -- 'pending', 'submitted', 'filled', 'cancelled', 'rejected'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP,
    filled_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    risk_justification TEXT,  -- JSON stored as TEXT
    idempotency_key TEXT UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_idempotency_key ON orders(idempotency_key);

-- Trades table (closed positions)
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    strategy_id TEXT,
    signal_id TEXT,
    entry_price REAL NOT NULL,
    exit_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    entry_date TIMESTAMP NOT NULL,
    exit_date TIMESTAMP NOT NULL,
    pnl REAL NOT NULL,
    pnl_percent REAL NOT NULL,
    holding_period_days INTEGER,
    exit_reason TEXT,
    entry_regime TEXT,
    exit_regime TEXT,
    attribution TEXT,  -- JSON stored as TEXT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trades_trade_id ON trades(trade_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_strategy_id ON trades(strategy_id);
CREATE INDEX IF NOT EXISTS idx_trades_entry_date ON trades(entry_date);
CREATE INDEX IF NOT EXISTS idx_trades_exit_date ON trades(exit_date);

-- Strategy performance table
CREATE TABLE IF NOT EXISTS strategy_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id TEXT NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    total_trades INTEGER NOT NULL,
    winning_trades INTEGER NOT NULL,
    losing_trades INTEGER NOT NULL,
    win_rate REAL NOT NULL,
    profit_factor REAL NOT NULL,
    total_return REAL NOT NULL,
    sharpe_ratio REAL,
    max_drawdown REAL,
    average_win REAL,
    average_loss REAL,
    average_holding_period INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_strategy_performance_strategy_id ON strategy_performance(strategy_id);
CREATE INDEX IF NOT EXISTS idx_strategy_performance_period_start ON strategy_performance(period_start);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    event_type TEXT NOT NULL,
    event_data TEXT NOT NULL,  -- JSON stored as TEXT
    user_id TEXT,
    decision_id TEXT,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_decision_id ON audit_logs(decision_id);

-- Opportunities table (scanned opportunities)
CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price REAL NOT NULL,
    volume REAL NOT NULL,
    market_cap REAL,
    sector TEXT,
    indicators TEXT,  -- JSON stored as TEXT
    pre_filter_score REAL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_opportunities_symbol ON opportunities(symbol);
CREATE INDEX IF NOT EXISTS idx_opportunities_timestamp ON opportunities(timestamp);
CREATE INDEX IF NOT EXISTS idx_opportunities_source ON opportunities(source);

-- Strategy signals table
CREATE TABLE IF NOT EXISTS strategy_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id TEXT UNIQUE NOT NULL,
    strategy_id TEXT NOT NULL,
    opportunity_id INTEGER,
    score REAL NOT NULL,
    confidence REAL NOT NULL,
    entry_price REAL NOT NULL,
    stop_loss REAL,
    take_profit REAL,
    conditions TEXT,  -- JSON stored as TEXT
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_strategy_signals_signal_id ON strategy_signals(signal_id);
CREATE INDEX IF NOT EXISTS idx_strategy_signals_strategy_id ON strategy_signals(strategy_id);
CREATE INDEX IF NOT EXISTS idx_strategy_signals_timestamp ON strategy_signals(timestamp);

-- Trading decisions table
CREATE TABLE IF NOT EXISTS trading_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT UNIQUE NOT NULL,
    decision TEXT NOT NULL,  -- 'APPROVE', 'REJECT', 'MODIFY'
    symbol TEXT NOT NULL,
    strategy_id TEXT NOT NULL,
    signal_id TEXT NOT NULL,
    risk_amount REAL NOT NULL,
    risk_percent REAL NOT NULL,
    reward_amount REAL NOT NULL,
    risk_reward_ratio REAL NOT NULL,
    position_size TEXT NOT NULL,  -- JSON stored as TEXT
    reasoning TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trading_decisions_decision_id ON trading_decisions(decision_id);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_symbol ON trading_decisions(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_decision ON trading_decisions(decision);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_timestamp ON trading_decisions(timestamp);

-- Market state table
CREATE TABLE IF NOT EXISTS market_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    regime TEXT NOT NULL,
    volatility_state TEXT NOT NULL,
    breadth_state TEXT NOT NULL,
    liquidity_state TEXT NOT NULL,
    vix_level REAL,
    market_direction TEXT,
    confidence REAL,
    indicators TEXT,  -- JSON stored as TEXT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_market_state_timestamp ON market_state(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_state_regime ON market_state(regime);

-- Data health table
CREATE TABLE IF NOT EXISTS data_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status TEXT NOT NULL,  -- 'GREEN', 'YELLOW', 'RED'
    validation_failure_rate REAL,
    reconciliation_failure_rate REAL,
    anomaly_frequency REAL,
    data_freshness_seconds REAL,
    issues TEXT,  -- JSON stored as TEXT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_data_health_symbol ON data_health(symbol);
CREATE INDEX IF NOT EXISTS idx_data_health_timestamp ON data_health(timestamp);
CREATE INDEX IF NOT EXISTS idx_data_health_status ON data_health(status);

