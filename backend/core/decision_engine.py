"""
Decision Engine

Integrates capital, risk, and portfolio to make trading decisions.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from utils.debug_utils import DebugUtils
from models.opportunity import Opportunity
from models.strategy_signal import StrategySignal
from models.trading_decision import TradingDecision
from backend.capital.capital_manager import CapitalManager
from backend.capital.position_sizer import PositionSizer
from backend.risk.risk_engine import RiskEngine
from backend.portfolio.portfolio_manager import PortfolioManager
from backend.market_state.state_engine import MarketStateEngine
from backend.timing.signal_expiry import SignalExpiryManager
from backend.timing.stale_detector import StaleDetector
from backend.governance.audit_logger import AuditLogger


class DecisionEngine:
    """
    Decision engine that integrates capital, risk, and portfolio.
    
    Makes trading decisions (APPROVE/REJECT/MODIFY) based on:
    - Capital availability
    - Risk limits
    - Portfolio fit
    - Market state
    """
    
    def __init__(
        self,
        capital_manager: CapitalManager,
        position_sizer: PositionSizer,
        risk_engine: RiskEngine,
        portfolio_manager: Optional[PortfolioManager] = None,
        market_state_engine: Optional[MarketStateEngine] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize decision engine.
        
        Args:
            capital_manager: Capital manager instance
            position_sizer: Position sizer instance
            risk_engine: Risk engine instance
            portfolio_manager: Portfolio manager instance (optional)
            market_state_engine: Market state engine instance (optional)
            audit_logger: Audit logger instance (optional)
        """
        self.capital_manager = capital_manager
        self.position_sizer = position_sizer
        self.risk_engine = risk_engine
        self.portfolio_manager = portfolio_manager
        self.market_state_engine = market_state_engine
        self.expiry_manager = SignalExpiryManager()
        self.stale_detector = StaleDetector()
        self.audit_logger = audit_logger
    
    def make_decision(
        self,
        signal: StrategySignal,
        existing_positions: List[Dict[str, Any]]
    ) -> TradingDecision:
        """
        Make trading decision for a signal.
        
        Args:
            signal: Strategy signal
            existing_positions: List of existing positions
            
        Returns:
            TradingDecision
        """
        opportunity = signal.opportunity
        symbol = opportunity.symbol
        
        # Check if signal is stale (timing awareness)
        if self.expiry_manager.is_signal_stale(signal):
            expiry_info = self.expiry_manager.get_expiry_info(signal)
            return TradingDecision(
                decision_id=str(uuid.uuid4()),
                decision="REJECT",
                symbol=symbol,
                strategy_id=signal.strategy_id,
                signal=signal,
                risk_amount=0.0,
                risk_percent=0.0,
                reward_amount=0.0,
                risk_reward_ratio=0.0,
                position_size={'shares': 0, 'notional': 0, 'risk_amount': 0},
                reasoning=f"Signal expired (age: {expiry_info.age_seconds:.1f}s, expiry: {expiry_info.expiry_minutes}min)",
                timestamp=datetime.now()
            )
        
        # Check if opportunity is stale
        if self.stale_detector.is_opportunity_stale(opportunity, signal):
            return TradingDecision(
                decision_id=str(uuid.uuid4()),
                decision="REJECT",
                symbol=symbol,
                strategy_id=signal.strategy_id,
                signal=signal,
                risk_amount=0.0,
                risk_percent=0.0,
                reward_amount=0.0,
                risk_reward_ratio=0.0,
                position_size={'shares': 0, 'notional': 0, 'risk_amount': 0},
                reasoning="Opportunity is stale (price or volume changed significantly)",
                timestamp=datetime.now()
            )
        
        # Get available capital
        available_capital = self.capital_manager.get_available_capital()
        total_capital = self.capital_manager.get_total_capital()
        
        # Calculate position size
        position_size = self.position_sizer.calculate_position_size(
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss or signal.entry_price * 0.95,
            available_capital=available_capital
        )
        
        # Calculate risk metrics
        risk_amount = position_size['risk_amount']
        risk_percent = (risk_amount / total_capital) * 100 if total_capital > 0 else 0
        reward_amount = (signal.take_profit - signal.entry_price) * position_size['shares'] if signal.take_profit else 0
        risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
        
        # Check risk limits
        risk_check = self.risk_engine.check_risk(
            symbol=symbol,
            risk_amount=risk_amount,
            position_size=position_size,
            existing_positions=existing_positions,
            sector=opportunity.sector
        )
        
        # Check portfolio fit (if portfolio manager available)
        portfolio_fit = {'approved': True, 'reason': 'Portfolio check passed'}
        if self.portfolio_manager:
            portfolio_fit = self.portfolio_manager.evaluate_fit(opportunity, existing_positions)
        
        # Make decision
        if not risk_check['approved']:
            decision = "REJECT"
            reasoning = f"Risk check failed: {risk_check.get('reason', 'Unknown')}"
        elif not portfolio_fit['approved']:
            decision = "REJECT"
            reasoning = f"Portfolio fit check failed: {portfolio_fit.get('reason', 'Unknown')}"
        elif position_size['shares'] == 0:
            decision = "REJECT"
            reasoning = "Position size is zero (insufficient capital or invalid stop loss)"
        elif risk_reward_ratio < 1.5:
            decision = "REJECT"
            reasoning = f"Risk-reward ratio too low: {risk_reward_ratio:.2f}:1 (minimum 1.5:1)"
        else:
            decision = "APPROVE"
            reasoning = (
                f"Strong {signal.strategy_id} signal (score: {signal.score:.1f}). "
                f"Risk: ${risk_amount:.2f} ({risk_percent:.1f}% of capital). "
                f"Risk-reward: {risk_reward_ratio:.2f}:1. "
                f"Sector exposure: {opportunity.sector}."
            )
        
        decision_id = str(uuid.uuid4())
        
        decision_obj = TradingDecision(
            decision_id=decision_id,
            decision=decision,
            symbol=symbol,
            strategy_id=signal.strategy_id,
            signal=signal,
            risk_amount=risk_amount,
            risk_percent=risk_percent,
            reward_amount=reward_amount,
            risk_reward_ratio=risk_reward_ratio,
            position_size=position_size,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
        
        # Audit log decision
        if self.audit_logger:
            self.audit_logger.log(
                event_type="TRADING_DECISION",
                event_data={
                    'symbol': symbol,
                    'decision': decision,
                    'strategy_id': signal.strategy_id,
                    'risk_amount': risk_amount,
                    'risk_percent': risk_percent,
                    'risk_reward_ratio': risk_reward_ratio,
                    'position_size': position_size
                },
                decision_id=decision_obj.decision_id,
                explanation=reasoning
            )
        
        return decision_obj

