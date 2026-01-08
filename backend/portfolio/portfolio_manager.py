"""
Portfolio Manager

Manages portfolio state and evaluates portfolio fit.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from utils.debug_utils import DebugUtils
from models.opportunity import Opportunity
from backend.portfolio.exposure_tracker import ExposureTracker
from backend.portfolio.diversification_engine import DiversificationEngine


@dataclass
class PortfolioState:
    """Portfolio state representation."""
    timestamp: datetime
    total_capital: float
    allocated_capital: float
    available_capital: float
    sector_exposure: Dict[str, float]
    factor_exposure: Dict[str, float]
    average_correlation: float
    diversification_score: float
    positions: List[Dict[str, Any]]


class PortfolioManager:
    """
    Manages portfolio state and evaluates portfolio fit.
    
    Responsibilities:
    - Track portfolio state
    - Evaluate portfolio fit for new opportunities
    - Manage diversification
    """
    
    def __init__(
        self,
        exposure_tracker: Optional[ExposureTracker] = None,
        diversification_engine: Optional[DiversificationEngine] = None
    ):
        """
        Initialize portfolio manager.
        
        Args:
            exposure_tracker: Exposure tracker instance
            diversification_engine: Diversification engine instance
        """
        self.exposure_tracker = exposure_tracker or ExposureTracker()
        self.diversification_engine = diversification_engine or DiversificationEngine()
    
    def get_portfolio_state(
        self,
        positions: List[Dict[str, Any]],
        total_capital: float
    ) -> PortfolioState:
        """
        Get current portfolio state.
        
        Args:
            positions: List of positions
            total_capital: Total capital
            
        Returns:
            PortfolioState
        """
        allocated_capital = sum(pos.get('value', 0) for pos in positions)
        available_capital = total_capital - allocated_capital
        
        # Get exposures
        sector_exposure = self.exposure_tracker.get_sector_exposure(positions, total_capital)
        factor_exposure = self.exposure_tracker.get_factor_exposure(positions)
        
        # Get correlation
        average_correlation = self.exposure_tracker.get_average_correlation(positions)
        
        # Get diversification score
        diversification_score = self.diversification_engine.calculate_score(
            positions, sector_exposure, average_correlation
        )
        
        return PortfolioState(
            timestamp=datetime.now(),
            total_capital=total_capital,
            allocated_capital=allocated_capital,
            available_capital=available_capital,
            sector_exposure=sector_exposure,
            factor_exposure=factor_exposure,
            average_correlation=average_correlation,
            diversification_score=diversification_score,
            positions=positions
        )
    
    def evaluate_fit(
        self,
        opportunity: Opportunity,
        existing_positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate if opportunity fits portfolio.
        
        Args:
            opportunity: Opportunity to evaluate
            existing_positions: Existing positions
            
        Returns:
            Dictionary with approval status and reasoning
        """
        # Check diversification
        diversification_check = self.diversification_engine.check_diversification(
            opportunity, existing_positions
        )
        
        if not diversification_check['approved']:
            return diversification_check
        
        # Check sector exposure
        sector_check = self.exposure_tracker.check_sector_exposure(
            opportunity.sector, existing_positions
        )
        
        if not sector_check['approved']:
            return sector_check
        
        return {
            'approved': True,
            'reason': 'Portfolio fit check passed',
            'diversification_improvement': diversification_check.get('improvement', 0)
        }

