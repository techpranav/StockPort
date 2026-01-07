"""
Risk Calculator Module

This module calculates risk metrics including ATR-based stop-loss,
risk-reward ratios, position sizing, and maximum drawdown.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER


class RiskCalculator:
    """
    Risk calculator for position management.
    
    Features:
    - ATR-based stop-loss calculation
    - Risk-reward ratio analysis
    - Position sizing recommendations
    - Maximum drawdown calculation
    - Portfolio risk metrics
    """
    
    def __init__(
        self,
        risk_per_trade: float = 0.02,  # 2% risk per trade
        risk_reward_ratio: float = 1.5  # Minimum 1.5:1
    ):
        """
        Initialize risk calculator.
        
        Args:
            risk_per_trade: Percentage of capital to risk per trade (default: 2%)
            risk_reward_ratio: Minimum risk-reward ratio (default: 1.5:1)
        """
        self.risk_per_trade = risk_per_trade
        self.risk_reward_ratio = risk_reward_ratio
    
    def calculate_risk_metrics(
        self,
        data: pd.DataFrame,
        entry_price: float,
        indicators: Dict[str, Any],
        account_size: Optional[float] = None,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk metrics.
        
        Args:
            data: DataFrame with OHLCV data (will be normalized)
            entry_price: Proposed entry price
            indicators: Dictionary of technical indicators
            account_size: Optional account size for position sizing
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Dictionary with risk metrics
        """
        try:
            # Normalize data using adapter
            adapter = AdapterFactory.get_adapter(provider_name)
            normalized_data = adapter.normalize_dataframe(data)
            
            if normalized_data.empty:
                raise DataProcessingException("Data cannot be empty for risk calculation")
            
            current_price = adapter.get_column(normalized_data, 'CLOSE').iloc[-1]
            
            # Calculate stop-loss using ATR
            stop_loss = self._calculate_atr_stop_loss(
                entry_price,
                normalized_data,
                indicators,
                adapter
            )
            
            # Calculate take-profit
            take_profit = self._calculate_take_profit(
                entry_price,
                stop_loss
            )
            
            # Risk-reward ratio
            risk_amount = abs(entry_price - stop_loss)
            reward_amount = abs(take_profit - entry_price)
            risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
            
            # Position sizing
            position_size = None
            if account_size:
                position_size = self._calculate_position_size(
                    account_size,
                    entry_price,
                    stop_loss
                )
            
            # Maximum drawdown
            max_drawdown = self._calculate_max_drawdown(normalized_data, adapter)
            
            # Volatility
            volatility = self._calculate_volatility(normalized_data, adapter)
            
            return {
                'stop_loss': round(stop_loss, 2),
                'take_profit': round(take_profit, 2),
                'risk_amount': round(risk_amount, 2),
                'reward_amount': round(reward_amount, 2),
                'risk_reward_ratio': round(risk_reward_ratio, 2),
                'position_size': position_size,
                'max_drawdown': round(max_drawdown, 2),
                'volatility': round(volatility, 2),
                'risk_per_trade': self.risk_per_trade
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating risk metrics")
            raise DataProcessingException(f"Risk calculation failed: {str(e)}") from e
    
    def _calculate_atr_stop_loss(
        self,
        entry_price: float,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        adapter
    ) -> float:
        """Calculate ATR-based stop-loss."""
        # Use ATR if available
        if 'atr' in indicators:
            atr = indicators['atr']
            if isinstance(atr, pd.Series):
                atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else entry_price * 0.02
            
            # Stop-loss: 2 ATR below entry (for long positions)
            stop_loss = entry_price - (atr * 2)
        else:
            # Fallback: 2% stop-loss
            stop_loss = entry_price * 0.98
        
        # Ensure stop-loss is reasonable (not more than 10% away)
        min_stop_loss = entry_price * 0.90
        return max(stop_loss, min_stop_loss)
    
    def _calculate_take_profit(
        self,
        entry_price: float,
        stop_loss: float
    ) -> float:
        """Calculate take-profit based on risk-reward ratio."""
        risk_amount = abs(entry_price - stop_loss)
        reward_amount = risk_amount * self.risk_reward_ratio
        take_profit = entry_price + reward_amount
        
        return take_profit
    
    def _calculate_position_size(
        self,
        account_size: float,
        entry_price: float,
        stop_loss: float
    ) -> Dict[str, float]:
        """
        Calculate recommended position size.
        
        Returns:
            Dictionary with:
            - shares: Number of shares
            - dollar_amount: Dollar amount to invest
            - percentage: Percentage of account
        """
        risk_amount_per_share = abs(entry_price - stop_loss)
        
        if risk_amount_per_share == 0:
            return {
                'shares': 0,
                'dollar_amount': 0,
                'percentage': 0
            }
        
        # Risk amount for this trade
        risk_dollar_amount = account_size * self.risk_per_trade
        
        # Number of shares based on risk
        shares = int(risk_dollar_amount / risk_amount_per_share)
        
        # Dollar amount to invest
        dollar_amount = shares * entry_price
        
        # Percentage of account
        percentage = (dollar_amount / account_size) * 100
        
        return {
            'shares': shares,
            'dollar_amount': dollar_amount,
            'percentage': percentage
        }
    
    def _calculate_max_drawdown(
        self,
        data: pd.DataFrame,
        adapter
    ) -> float:
        """Calculate maximum drawdown."""
        if data.empty:
            return 0.0
        
        try:
            close = adapter.get_column(data, 'CLOSE')
        except DataProcessingException:
            return 0.0
        
        # Calculate running maximum
        running_max = close.expanding().max()
        
        # Calculate drawdown
        drawdown = (close - running_max) / running_max
        
        # Maximum drawdown
        max_drawdown = abs(drawdown.min()) * 100  # As percentage
        
        return max_drawdown
    
    def _calculate_volatility(
        self,
        data: pd.DataFrame,
        adapter,
        period: int = 20
    ) -> float:
        """Calculate volatility (standard deviation of returns)."""
        if data.empty or len(data) < period:
            return 0.0
        
        try:
            close = adapter.get_column(data, 'CLOSE')
        except DataProcessingException:
            return 0.0
        returns = close.pct_change().dropna()
        
        if len(returns) < period:
            volatility = returns.std() * 100
        else:
            volatility = returns.tail(period).std() * 100
        
        return volatility

