"""
DCF (Discounted Cash Flow) Valuation Model

Calculates fair value using discounted cash flow analysis.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException


class DCFValuation:
    """
    Discounted Cash Flow valuation model.
    
    Features:
    - Free cash flow projection
    - Terminal value estimation
    - Sensitivity analysis
    - Fair value calculation
    - Margin of safety calculation
    """
    
    def __init__(self):
        """Initialize DCF valuation calculator."""
        pass
    
    def calculate_dcf(
        self,
        free_cash_flows: List[float],
        growth_rate: float,
        terminal_growth_rate: float,
        discount_rate: float,
        terminal_multiple: Optional[float] = None,
        shares_outstanding: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate DCF valuation.
        
        Args:
            free_cash_flows: Historical free cash flows (last 3-5 years)
            growth_rate: Projected growth rate (e.g., 0.10 for 10%)
            terminal_growth_rate: Terminal growth rate (e.g., 0.03 for 3%)
            discount_rate: Discount rate (WACC, e.g., 0.10 for 10%)
            terminal_multiple: Terminal multiple (optional, alternative to terminal growth)
            shares_outstanding: Number of shares outstanding
            
        Returns:
            Dictionary with DCF valuation results
        """
        try:
            if not free_cash_flows or len(free_cash_flows) < 1:
                raise DataProcessingException("Need at least 1 year of free cash flow data")
            
            # Use most recent FCF as base
            base_fcf = free_cash_flows[-1] if free_cash_flows else 0
            
            if base_fcf <= 0:
                raise DataProcessingException("Base free cash flow must be positive")
            
            # Project FCF for next 5-10 years
            projection_years = 10
            projected_fcf = []
            
            for year in range(1, projection_years + 1):
                fcf = base_fcf * ((1 + growth_rate) ** year)
                projected_fcf.append(fcf)
            
            # Calculate present value of projected FCF
            pv_projected_fcf = []
            for i, fcf in enumerate(projected_fcf):
                year = i + 1
                pv = fcf / ((1 + discount_rate) ** year)
                pv_projected_fcf.append(pv)
            
            total_pv_projected = sum(pv_projected_fcf)
            
            # Calculate terminal value
            if terminal_multiple:
                # Use multiple method
                terminal_fcf = projected_fcf[-1]
                terminal_value = terminal_fcf * terminal_multiple
            else:
                # Use perpetuity growth method
                terminal_fcf = projected_fcf[-1] * (1 + terminal_growth_rate)
                terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
            
            # Present value of terminal value
            pv_terminal = terminal_value / ((1 + discount_rate) ** projection_years)
            
            # Enterprise value
            enterprise_value = total_pv_projected + pv_terminal
            
            # Equity value (assuming no debt for simplicity, can be enhanced)
            equity_value = enterprise_value
            
            # Fair value per share
            fair_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
            
            return {
                'enterprise_value': float(enterprise_value),
                'equity_value': float(equity_value),
                'fair_value_per_share': float(fair_value_per_share),
                'projected_fcf': [float(f) for f in projected_fcf],
                'pv_projected_fcf': [float(pv) for pv in pv_projected_fcf],
                'terminal_value': float(terminal_value),
                'pv_terminal_value': float(pv_terminal),
                'total_pv': float(enterprise_value),
                'assumptions': {
                    'growth_rate': growth_rate,
                    'terminal_growth_rate': terminal_growth_rate,
                    'discount_rate': discount_rate,
                    'projection_years': projection_years
                }
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating DCF valuation")
            raise DataProcessingException(f"DCF calculation failed: {str(e)}") from e
    
    def calculate_sensitivity_analysis(
        self,
        base_fair_value: float,
        growth_rate_range: List[float],
        discount_rate_range: List[float]
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on DCF assumptions.
        
        Args:
            base_fair_value: Base fair value
            growth_rate_range: Range of growth rates to test
            discount_rate_range: Range of discount rates to test
            
        Returns:
            Sensitivity analysis matrix
        """
        sensitivity_matrix = []
        
        for growth_rate in growth_rate_range:
            row = []
            for discount_rate in discount_rate_range:
                # Simplified sensitivity (would need full DCF recalculation)
                # This is a placeholder - full implementation would recalculate DCF
                adjustment_factor = (1 + growth_rate) / (1 + discount_rate)
                adjusted_value = base_fair_value * adjustment_factor
                row.append(float(adjusted_value))
            sensitivity_matrix.append(row)
        
        return {
            'growth_rates': growth_rate_range,
            'discount_rates': discount_rate_range,
            'sensitivity_matrix': sensitivity_matrix,
            'base_fair_value': base_fair_value
        }
    
    def calculate_margin_of_safety(
        self,
        fair_value: float,
        current_price: float
    ) -> Dict[str, Any]:
        """
        Calculate margin of safety.
        
        Args:
            fair_value: Calculated fair value
            current_price: Current stock price
            
        Returns:
            Margin of safety metrics
        """
        if fair_value <= 0:
            return {
                'margin_of_safety_pct': 0.0,
                'overvalued_pct': 0.0,
                'recommendation': 'N/A'
            }
        
        if current_price <= 0:
            return {
                'margin_of_safety_pct': 0.0,
                'overvalued_pct': 0.0,
                'recommendation': 'N/A'
            }
        
        # Margin of safety (how much below fair value)
        if current_price < fair_value:
            margin_of_safety = ((fair_value - current_price) / fair_value) * 100
            overvalued_pct = 0.0
            recommendation = 'UNDERVALUED'
        else:
            margin_of_safety = 0.0
            overvalued_pct = ((current_price - fair_value) / fair_value) * 100
            recommendation = 'OVERVALUED'
        
        return {
            'fair_value': float(fair_value),
            'current_price': float(current_price),
            'margin_of_safety_pct': float(margin_of_safety),
            'overvalued_pct': float(overvalued_pct),
            'recommendation': recommendation
        }

