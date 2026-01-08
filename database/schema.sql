-- Stockport v4 Database Schema
-- PostgreSQL database schema for persistent storage

-- Positions table
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(15, 4) NOT NULL,
    current_price DECIMAL(15, 4),
    entry_date TIMESTAMP NOT NULL,
    strategy_id VARCHAR(100),
    signal_id VARCHAR(100),
    sector VARCHAR(100),
    value DECIMAL(15, 2),
    pnl DECIMAL(15, 2),
    pnl_percent DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_symbol ON positions(symbol);
CREATE INDEX idx_positions_strategy_id ON positions(strategy_id);
CREATE INDEX idx_positions_entry_date ON positions(entry_date);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    decision_id VARCHAR(100),
    signal_id VARCHAR(100),
    strategy_id VARCHAR(100),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,  -- 'buy' or 'sell'
    quantity INTEGER NOT NULL,
    order_type VARCHAR(20) NOT NULL,  -- 'market', 'limit', 'stop'
    limit_price DECIMAL(15, 4),
    stop_price DECIMAL(15, 4),
    fill_price DECIMAL(15, 4),
    filled_quantity INTEGER,
    status VARCHAR(20) NOT NULL,  -- 'pending', 'submitted', 'filled', 'cancelled', 'rejected'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP,
    filled_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    risk_justification JSONB,
    idempotency_key VARCHAR(255) UNIQUE
);

CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_symbol ON orders(symbol);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_idempotency_key ON orders(idempotency_key);

-- Trades table (closed positions)
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(100) UNIQUE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    strategy_id VARCHAR(100),
    signal_id VARCHAR(100),
    entry_price DECIMAL(15, 4) NOT NULL,
    exit_price DECIMAL(15, 4) NOT NULL,
    quantity INTEGER NOT NULL,
    entry_date TIMESTAMP NOT NULL,
    exit_date TIMESTAMP NOT NULL,
    pnl DECIMAL(15, 2) NOT NULL,
    pnl_percent DECIMAL(10, 4) NOT NULL,
    holding_period_days INTEGER,
    exit_reason VARCHAR(100),
    entry_regime VARCHAR(50),
    exit_regime VARCHAR(50),
    attribution JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trades_trade_id ON trades(trade_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_strategy_id ON trades(strategy_id);
CREATE INDEX idx_trades_entry_date ON trades(entry_date);
CREATE INDEX idx_trades_exit_date ON trades(exit_date);

-- Strategy performance table
CREATE TABLE IF NOT EXISTS strategy_performance (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR(100) NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    total_trades INTEGER NOT NULL,
    winning_trades INTEGER NOT NULL,
    losing_trades INTEGER NOT NULL,
    win_rate DECIMAL(5, 4) NOT NULL,
    profit_factor DECIMAL(10, 4) NOT NULL,
    total_return DECIMAL(15, 2) NOT NULL,
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    average_win DECIMAL(15, 2),
    average_loss DECIMAL(15, 2),
    average_holding_period INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_strategy_performance_strategy_id ON strategy_performance(strategy_id);
CREATE INDEX idx_strategy_performance_period_start ON strategy_performance(period_start);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    user_id VARCHAR(100),
    decision_id VARCHAR(100),
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_decision_id ON audit_logs(decision_id);

-- Opportunities table (scanned opportunities)
CREATE TABLE IF NOT EXISTS opportunities (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(15, 4) NOT NULL,
    volume DECIMAL(20, 2) NOT NULL,
    market_cap DECIMAL(20, 2),
    sector VARCHAR(100),
    indicators JSONB,
    pre_filter_score DECIMAL(5, 2),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_opportunities_symbol ON opportunities(symbol);
CREATE INDEX idx_opportunities_timestamp ON opportunities(timestamp);
CREATE INDEX idx_opportunities_source ON opportunities(source);

-- Strategy signals table
CREATE TABLE IF NOT EXISTS strategy_signals (
    id SERIAL PRIMARY KEY,
    signal_id VARCHAR(100) UNIQUE NOT NULL,
    strategy_id VARCHAR(100) NOT NULL,
    opportunity_id INTEGER REFERENCES opportunities(id),
    score DECIMAL(5, 2) NOT NULL,
    confidence DECIMAL(5, 4) NOT NULL,
    entry_price DECIMAL(15, 4) NOT NULL,
    stop_loss DECIMAL(15, 4),
    take_profit DECIMAL(15, 4),
    conditions JSONB,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_strategy_signals_signal_id ON strategy_signals(signal_id);
CREATE INDEX idx_strategy_signals_strategy_id ON strategy_signals(strategy_id);
CREATE INDEX idx_strategy_signals_timestamp ON strategy_signals(timestamp);

-- Trading decisions table
CREATE TABLE IF NOT EXISTS trading_decisions (
    id SERIAL PRIMARY KEY,
    decision_id VARCHAR(100) UNIQUE NOT NULL,
    decision VARCHAR(20) NOT NULL,  -- 'APPROVE', 'REJECT', 'MODIFY'
    symbol VARCHAR(20) NOT NULL,
    strategy_id VARCHAR(100) NOT NULL,
    signal_id VARCHAR(100) NOT NULL,
    risk_amount DECIMAL(15, 2) NOT NULL,
    risk_percent DECIMAL(10, 4) NOT NULL,
    reward_amount DECIMAL(15, 2) NOT NULL,
    risk_reward_ratio DECIMAL(10, 4) NOT NULL,
    position_size JSONB NOT NULL,
    reasoning TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trading_decisions_decision_id ON trading_decisions(decision_id);
CREATE INDEX idx_trading_decisions_symbol ON trading_decisions(symbol);
CREATE INDEX idx_trading_decisions_decision ON trading_decisions(decision);
CREATE INDEX idx_trading_decisions_timestamp ON trading_decisions(timestamp);

-- Market state table
CREATE TABLE IF NOT EXISTS market_state (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    regime VARCHAR(50) NOT NULL,
    volatility_state VARCHAR(50) NOT NULL,
    breadth_state VARCHAR(50) NOT NULL,
    liquidity_state VARCHAR(50) NOT NULL,
    vix_level DECIMAL(10, 4),
    market_direction VARCHAR(20),
    confidence DECIMAL(5, 4),
    indicators JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_market_state_timestamp ON market_state(timestamp);
CREATE INDEX idx_market_state_regime ON market_state(regime);

-- Data health table
CREATE TABLE IF NOT EXISTS data_health (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'GREEN', 'YELLOW', 'RED'
    validation_failure_rate DECIMAL(5, 4),
    reconciliation_failure_rate DECIMAL(5, 4),
    anomaly_frequency DECIMAL(10, 2),
    data_freshness_seconds DECIMAL(10, 2),
    issues JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_health_symbol ON data_health(symbol);
CREATE INDEX idx_data_health_timestamp ON data_health(timestamp);
CREATE INDEX idx_data_health_status ON data_health(status);

