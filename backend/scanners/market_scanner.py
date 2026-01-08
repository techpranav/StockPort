"""
Market Scanner

Main market scanner that scans the stock universe.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.debug_utils import DebugUtils
from models.opportunity import Opportunity
from backend.scanners.base_scanner import BaseScanner
from backend.data.integrity.truth_layer import TruthLayer
from services.data_providers.stock_data_provider import StockDataProvider
from services.stock_data_factory import StockDataFactory
from backend.governance.audit_logger import AuditLogger


class MarketScanner(BaseScanner):
    """
    Main market scanner.
    
    Scans stock universe in parallel and emits opportunities.
    """
    
    def __init__(
        self,
        truth_layer: Optional[TruthLayer] = None,
        data_provider: Optional[StockDataProvider] = None,
        max_workers: int = 10,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize market scanner.
        
        Args:
            truth_layer: Truth layer instance
            data_provider: Data provider instance
            max_workers: Maximum parallel workers
            audit_logger: Audit logger instance (optional)
        """
        from backend.settings import get_settings
        self.settings = get_settings()
        
        super().__init__(truth_layer)
        self.data_provider = data_provider or StockDataFactory.get_provider("yahoo_finance")
        self.max_workers = max_workers
        self.audit_logger = audit_logger
        
        # Subscribe to settings changes
        self.settings.subscribe('data.min_volume', self._on_min_volume_changed)
        self.settings.subscribe('data.min_price', self._on_min_price_changed)
        self.settings.subscribe('data.min_market_cap', self._on_min_market_cap_changed)
        
        # Pre-filters (from settings)
        self._min_volume = None
        self._min_price = None
        self._min_market_cap = None
        self._update_from_settings()
    
    def _update_from_settings(self):
        """Update filters from settings."""
        self._min_volume = self.settings.get_min_volume()
        self._min_price = self.settings.get_min_price()
        self._min_market_cap = self.settings.get_min_market_cap()
    
    def _on_min_volume_changed(self, key: str, old_value: float, new_value: float):
        """Handle min volume change."""
        self._min_volume = new_value
        DebugUtils.info(f"MarketScanner: Min volume updated to ${new_value:,.0f}")
    
    def _on_min_price_changed(self, key: str, old_value: float, new_value: float):
        """Handle min price change."""
        self._min_price = new_value
        DebugUtils.info(f"MarketScanner: Min price updated to ${new_value:.2f}")
    
    def _on_min_market_cap_changed(self, key: str, old_value: float, new_value: float):
        """Handle min market cap change."""
        self._min_market_cap = new_value
        DebugUtils.info(f"MarketScanner: Min market cap updated to ${new_value:,.0f}")
    
    @property
    def min_volume(self) -> float:
        """Get current min volume."""
        if self._min_volume is None:
            self._min_volume = self.settings.get_min_volume()
        return self._min_volume
    
    @property
    def min_price(self) -> float:
        """Get current min price."""
        if self._min_price is None:
            self._min_price = self.settings.get_min_price()
        return self._min_price
    
    @property
    def min_market_cap(self) -> float:
        """Get current min market cap."""
        if self._min_market_cap is None:
            self._min_market_cap = self.settings.get_min_market_cap()
        return self._min_market_cap
    
    def scan(self, symbols: Optional[List[str]] = None) -> List[Opportunity]:
        """
        Scan for opportunities.
        
        Args:
            symbols: List of symbols to scan (None = scan all)
            
        Returns:
            List of opportunities
        """
        if symbols is None:
            # Would load from universe file or database
            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # Example
        
        opportunities = []
        
        # Scan in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self._scan_symbol, symbol): symbol
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    opportunity = future.result()
                    if opportunity:
                        opportunities.append(opportunity)
                except Exception as e:
                    DebugUtils.log_error(e, f"Error scanning {symbol}")
        
        DebugUtils.info(f"Market scanner found {len(opportunities)} opportunities")
        
        return opportunities
    
    def _scan_symbol(self, symbol: str) -> Optional[Opportunity]:
        """
        Scan a single symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Opportunity or None
        """
        # Check data validity
        if not self.is_data_valid(symbol):
            return None
        
        try:
            # Fetch data
            stock_data = self.data_provider.fetch_stock_data(symbol)
            if not stock_data or stock_data.history.empty:
                return None
            
            # Get latest data
            latest = stock_data.history.iloc[-1]
            current_price = latest['Close']
            volume = latest['Volume']
            
            # Apply pre-filters
            if not self._passes_pre_filters(symbol, current_price, volume, stock_data):
                return None
            
            # Calculate indicators (simplified)
            indicators = self._calculate_indicators(stock_data.history)
            
            # Calculate pre-filter score
            pre_filter_score = self._calculate_pre_filter_score(
                symbol, current_price, volume, indicators
            )
            
            # Create opportunity
            opportunity = Opportunity(
                symbol=symbol,
                timestamp=datetime.now(),
                price=current_price,
                volume=volume,
                market_cap=stock_data.company_info.market_cap if stock_data.company_info else 0,
                sector=stock_data.company_info.sector if stock_data.company_info else "Unknown",
                indicators=indicators,
                pre_filter_score=pre_filter_score,
                source="market_scanner"
            )
            
            # Audit log opportunity discovery
            if self.audit_logger:
                self.audit_logger.log(
                    event_type="OPPORTUNITY_DISCOVERED",
                    event_data={
                        'symbol': symbol,
                        'price': current_price,
                        'volume': volume,
                        'pre_filter_score': pre_filter_score,
                        'indicators': indicators
                    },
                    decision_id=f"opp_{symbol}_{datetime.now().isoformat()}",
                    explanation=f"Opportunity discovered for {symbol} with score {pre_filter_score:.1f}"
                )
            
            return opportunity
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error scanning symbol {symbol}")
            return None
    
    def _passes_pre_filters(
        self,
        symbol: str,
        price: float,
        volume: float,
        stock_data: Any
    ) -> bool:
        """Check if symbol passes pre-filters."""
        # Price filter
        if price < self.min_price:
            return False
        
        # Volume filter
        if volume < self.min_volume:
            return False
        
        # Market cap filter
        market_cap = stock_data.company_info.market_cap if stock_data.company_info else 0
        if market_cap < self.min_market_cap:
            return False
        
        return True
    
    def _calculate_indicators(self, data: Any) -> Dict[str, float]:
        """Calculate indicators (simplified)."""
        if data.empty:
            return {}
        
        latest = data.iloc[-1]
        
        # Simplified indicator calculation
        # In production, would use actual indicator calculations
        return {
            'sma_20': latest.get('Close', 0) * 1.01,  # Simplified
            'sma_50': latest.get('Close', 0) * 0.99,
            'rsi': 55.0,
            'macd': 0.5,
            'macd_signal': 0.3,
            'atr': latest.get('Close', 0) * 0.02
        }
    
    def _calculate_pre_filter_score(
        self,
        symbol: str,
        price: float,
        volume: float,
        indicators: Dict[str, float]
    ) -> float:
        """Calculate pre-filter quality score."""
        score = 50.0  # Base score
        
        # Volume score
        if volume > 1000000:  # > $1M
            score += 20
        elif volume > 500000:  # > $500K
            score += 10
        
        # Price score (higher price = more stable)
        if price > 50:
            score += 10
        elif price > 20:
            score += 5
        
        return min(score, 100.0)

