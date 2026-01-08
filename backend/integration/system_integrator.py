"""
System Integrator

Integrates all system components together.
"""

from typing import Optional, Dict, Any

from utils.debug_utils import DebugUtils
from backend.core.engine import TradingEngine
from backend.core.event_bus import EventBus
from backend.core.state_manager import StateManager
from backend.core.decision_engine import DecisionEngine
from backend.scanners.market_scanner import MarketScanner
from backend.strategies.registry import StrategyRegistry
from backend.strategies.evaluator import StrategyEvaluator
from backend.capital.capital_manager import CapitalManager
from backend.capital.position_sizer import PositionSizer
from backend.risk.risk_engine import RiskEngine
from backend.execution.execution_engine import ExecutionEngine
from backend.execution.brokers.paper_broker import PaperBroker
from backend.market_state.state_engine import MarketStateEngine
from backend.portfolio.portfolio_manager import PortfolioManager
from backend.data.integrity.truth_layer import TruthLayer
from backend.data.integrity.health_monitor import HealthMonitor
from backend.data.integrity.price_reconciler import PriceReconciler
from backend.governance.audit_logger import AuditLogger
from database.connection import DatabaseConnection
from config.app_config import DATABASE_TYPE


class SystemIntegrator:
    """
    Integrates all system components.
    
    Initializes and wires together:
    - Trading engine
    - Scanners
    - Strategy evaluator
    - Decision engine
    - Execution engine
    - Market state engine
    - Data integrity layer
    - Governance layer
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize system integrator.
        
        Args:
            initial_capital: Initial capital amount
        """
        DebugUtils.info("Initializing Stockport v4 system...")
        
        # Initialize database connection
        if DATABASE_TYPE == "postgresql":
            try:
                from config.app_config import (
                    POSTGRES_HOST,
                    POSTGRES_PORT,
                    POSTGRES_DB,
                    POSTGRES_USER,
                    POSTGRES_PASSWORD
                )
                DatabaseConnection.use_postgresql(
                    host=POSTGRES_HOST,
                    port=POSTGRES_PORT,
                    database=POSTGRES_DB,
                    user=POSTGRES_USER,
                    password=POSTGRES_PASSWORD
                )
            except Exception as e:
                DebugUtils.warning(f"Failed to connect to PostgreSQL, falling back to SQLite: {e}")
                DatabaseConnection.use_sqlite()
        else:
            # Default to SQLite for personal use
            DatabaseConnection.use_sqlite()
        
        # Initialize core components
        self.event_bus = EventBus()
        self.state_manager = StateManager()
        self.audit_logger = AuditLogger()
        
        # Initialize data integrity layer
        health_monitor = HealthMonitor()
        price_reconciler = PriceReconciler()
        self.truth_layer = TruthLayer(health_monitor, price_reconciler)
        
        # Initialize market state engine
        self.market_state_engine = MarketStateEngine()
        
        # Initialize capital and risk
        self.capital_manager = CapitalManager(initial_capital)
        self.position_sizer = PositionSizer()
        self.risk_engine = RiskEngine()
        
        # Initialize portfolio
        self.portfolio_manager = PortfolioManager()
        
        # Initialize strategy system
        self.strategy_registry = StrategyRegistry()
        self.strategy_evaluator = StrategyEvaluator(
            self.strategy_registry,
            self.market_state_engine
        )
        
        # Initialize execution
        self.paper_broker = PaperBroker(initial_capital)
        self.execution_engine = ExecutionEngine(self.paper_broker)
        
        # Initialize decision engine
        self.decision_engine = DecisionEngine(
            self.capital_manager,
            self.position_sizer,
            self.risk_engine,
            self.portfolio_manager,
            self.market_state_engine
        )
        
        # Initialize scanner
        self.market_scanner = MarketScanner(truth_layer=self.truth_layer)
        
        # Initialize trading engine
        self.trading_engine = TradingEngine(
            event_bus=self.event_bus,
            state_manager=self.state_manager
        )
        
        DebugUtils.info("Stockport v4 system initialized successfully")
    
    def start(self):
        """Start the trading system."""
        self.trading_engine.start()
        self.market_scanner.start()
        DebugUtils.info("Trading system started")
    
    def stop(self):
        """Stop the trading system."""
        self.market_scanner.stop()
        self.trading_engine.stop()
        DebugUtils.info("Trading system stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get system status.
        
        Returns:
            System status dictionary
        """
        return {
            "trading_engine": self.trading_engine.get_status(),
            "capital": self.capital_manager.get_capital_state(),
            "positions": len(self.paper_broker.positions),
            "strategies": len(self.strategy_registry.get_active())
        }

