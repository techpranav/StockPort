"""
Pytest Configuration and Fixtures

Shared fixtures and configuration for all tests.
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.capital.capital_manager import CapitalManager
from backend.capital.position_sizer import PositionSizer
from backend.risk.risk_engine import RiskEngine
from backend.portfolio.portfolio_manager import PortfolioManager
from backend.market_state.state_engine import MarketStateEngine
from backend.strategies.registry import StrategyRegistry
from backend.execution.brokers.paper_broker import PaperBroker
from backend.execution.order_manager import OrderManager
from backend.learning.performance_tracker import PerformanceTracker
from backend.data.integrity.truth_layer import TruthLayer
from backend.data.integrity.health_monitor import HealthMonitor
from backend.data.integrity.price_reconciler import PriceReconciler
from backend.governance.audit_logger import AuditLogger
from backend.scanners.market_scanner import MarketScanner
from backend.strategies.evaluator import StrategyEvaluator
from backend.core.decision_engine import DecisionEngine
from backend.execution.execution_engine import ExecutionEngine


@pytest.fixture(scope="session")
def project_root_path():
    """Return project root path."""
    return Path(__file__).parent.parent


@pytest.fixture
def capital_manager():
    """Create capital manager instance."""
    return CapitalManager(initial_capital=100000.0)


@pytest.fixture
def position_sizer():
    """Create position sizer instance."""
    return PositionSizer()


@pytest.fixture
def risk_engine(capital_manager):
    """Create risk engine instance."""
    return RiskEngine(capital_manager)


@pytest.fixture
def portfolio_manager():
    """Create portfolio manager instance."""
    return PortfolioManager()


@pytest.fixture
def market_state_engine():
    """Create market state engine instance."""
    return MarketStateEngine()


@pytest.fixture
def strategy_registry():
    """Create strategy registry instance."""
    return StrategyRegistry()


@pytest.fixture
def paper_broker():
    """Create paper broker instance."""
    return PaperBroker(initial_capital=100000.0)


@pytest.fixture
def order_manager():
    """Create order manager instance."""
    return OrderManager()


@pytest.fixture
def performance_tracker():
    """Create performance tracker instance."""
    return PerformanceTracker()


@pytest.fixture
def health_monitor():
    """Create health monitor instance."""
    return HealthMonitor()


@pytest.fixture
def price_reconciler(paper_broker):
    """Create price reconciler instance."""
    return PriceReconciler(paper_broker)


@pytest.fixture
def truth_layer(health_monitor, price_reconciler):
    """Create truth layer instance."""
    return TruthLayer(health_monitor, price_reconciler)


@pytest.fixture
def audit_logger(tmp_path):
    """Create audit logger instance with temporary database."""
    return AuditLogger(db_path=tmp_path / "audit.db")


@pytest.fixture
def market_scanner(truth_layer, audit_logger):
    """Create market scanner instance."""
    return MarketScanner(truth_layer=truth_layer, audit_logger=audit_logger)


@pytest.fixture
def strategy_evaluator(strategy_registry, market_state_engine, audit_logger):
    """Create strategy evaluator instance."""
    return StrategyEvaluator(
        strategy_registry=strategy_registry,
        market_state_engine=market_state_engine,
        audit_logger=audit_logger
    )


@pytest.fixture
def decision_engine(
    capital_manager,
    position_sizer,
    risk_engine,
    portfolio_manager,
    market_state_engine,
    audit_logger
):
    """Create decision engine instance."""
    return DecisionEngine(
        capital_manager=capital_manager,
        position_sizer=position_sizer,
        risk_engine=risk_engine,
        portfolio_manager=portfolio_manager,
        market_state_engine=market_state_engine,
        audit_logger=audit_logger
    )


@pytest.fixture
def execution_engine(paper_broker, order_manager, performance_tracker, audit_logger):
    """Create execution engine instance."""
    return ExecutionEngine(
        broker=paper_broker,
        order_manager=order_manager,
        performance_tracker=performance_tracker,
        audit_logger=audit_logger
    )


@pytest.fixture
def complete_system(
    market_scanner,
    strategy_evaluator,
    decision_engine,
    execution_engine,
    capital_manager,
    paper_broker,
    performance_tracker
):
    """Create complete system with all components."""
    return {
        'scanner': market_scanner,
        'evaluator': strategy_evaluator,
        'decision_engine': decision_engine,
        'execution_engine': execution_engine,
        'capital_manager': capital_manager,
        'broker': paper_broker,
        'performance_tracker': performance_tracker
    }


@pytest.fixture
def sample_opportunity():
    """Create sample opportunity for testing."""
    from models.opportunity import Opportunity
    
    return Opportunity(
        symbol="AAPL",
        price=150.0,
        volume=1000000,
        timestamp=datetime.now(),
        sector="Technology",
        market_cap=2500000000000.0,
        indicators={
            'sma_20': 148.0,
            'sma_50': 145.0,
            'rsi': 65.0,
            'macd': 0.5
        }
    )


@pytest.fixture
def sample_signal(sample_opportunity):
    """Create sample strategy signal for testing."""
    from models.strategy_signal import StrategySignal
    
    return StrategySignal(
        signal_id="test_signal_1",
        strategy_id="trend_following_v1",
        opportunity=sample_opportunity,
        score=75.0,
        entry_price=150.0,
        stop_loss=145.0,
        take_profit=160.0,
        confidence=0.8,
        timestamp=datetime.now()
    )


@pytest.fixture(autouse=True)
def reset_state():
    """Reset state before each test."""
    # This runs before each test
    yield
    # Cleanup after each test (if needed)
