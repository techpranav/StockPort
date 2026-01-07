"""
Enhanced Stock Analyzer Module

This module integrates all enhanced analysis capabilities including parallel processing,
advanced indicators, pattern recognition, entry detection, and multi-timeframe analysis.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from core.parallel_analyzer import ParallelStockAnalyzer
from core.stock_analyzer import StockAnalyzer
from services.analyzers.indicators.intraday_indicators import IntradayIndicators
from services.analyzers.indicators.volume_indicators import VolumeIndicators
from services.analyzers.indicators.momentum_indicators import MomentumIndicators
from services.analyzers.patterns.pattern_analyzer import PatternAnalyzer
from services.analyzers.timeframe_analyzer import TimeframeAnalyzer
from services.analyzers.signals.entry_detector import EntryDetector
from services.analyzers.risk.risk_calculator import RiskCalculator
from services.data_providers.intraday_fetcher import IntradayFetcher
from services.data_providers.data_preprocessor import DataPreprocessor
from services.stock_service import StockService
from utils.cache_manager import CacheManager
from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException
from services.data_providers.adapters.adapter_factory import AdapterFactory
from config.constants.DataConstants import DEFAULT_PROVIDER
from config.app_config import (
    ENABLE_PARALLEL_PROCESSING,
    ENABLE_INTRADAY_ANALYSIS,
    ENABLE_ENTRY_DETECTION,
    ENABLE_PATTERN_RECOGNITION
)


class EnhancedStockAnalyzer:
    """
    Enhanced stock analyzer with all advanced features.
    
    Integrates:
    - Parallel processing
    - Advanced technical indicators
    - Pattern recognition
    - Multi-timeframe analysis
    - Entry point detection
    - Risk calculations
    """
    
    def __init__(
        self,
        days_back: int = 365,
        enable_parallel: bool = True,
        max_workers: Optional[int] = None
    ):
        """
        Initialize enhanced analyzer.
        
        Args:
            days_back: Days of historical data
            enable_parallel: Enable parallel processing
            max_workers: Maximum parallel workers
        """
        self.days_back = days_back
        self.enable_parallel = enable_parallel and ENABLE_PARALLEL_PROCESSING
        
        # Initialize components
        self.stock_service = StockService(days_back=days_back)
        self.parallel_analyzer = ParallelStockAnalyzer(max_workers=max_workers) if self.enable_parallel else None
        self.intraday_indicators = IntradayIndicators()
        self.volume_indicators = VolumeIndicators()
        self.momentum_indicators = MomentumIndicators()
        self.pattern_analyzer = PatternAnalyzer()
        self.timeframe_analyzer = TimeframeAnalyzer()
        self.entry_detector = EntryDetector()
        self.risk_calculator = RiskCalculator()
        self.data_preprocessor = DataPreprocessor()
        self.cache_manager = CacheManager()
        
        DebugUtils.info(
            f"Initialized EnhancedStockAnalyzer: parallel={self.enable_parallel}, "
            f"days_back={days_back}"
        )
    
    def analyze_stock_comprehensive(
        self,
        symbol: str,
        include_intraday: bool = True,
        include_patterns: bool = True,
        include_entry_signals: bool = True,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a stock.
        
        Args:
            symbol: Stock symbol
            include_intraday: Include intraday analysis
            include_patterns: Include pattern recognition
            include_entry_signals: Include entry point detection
            provider_name: Name of the data provider (default: yahoo_finance)
            
        Returns:
            Comprehensive analysis results
        """
        try:
            DebugUtils.info(f"Starting comprehensive analysis for {symbol}")
            
            # Fetch base data
            stock_data = self.stock_service.fetch_stock_data(symbol)
            history = stock_data.raw_data.get('history', pd.DataFrame())
            
            if history.empty:
                raise DataProcessingException(f"No historical data for {symbol}")
            
            # Preprocess data (will normalize via adapter)
            history = self.data_preprocessor.preprocess_data(history, provider_name=provider_name)
            
            results = {
                'symbol': symbol,
                'base_data': stock_data.to_dict(),
                'indicators': {},
                'patterns': {},
                'entry_signals': None,
                'risk_metrics': None
            }
            
            # Calculate advanced indicators
            if include_intraday and ENABLE_INTRADAY_ANALYSIS:
                results['indicators'].update(self._calculate_all_indicators(history, provider_name))
            
            # Pattern recognition
            if include_patterns and ENABLE_PATTERN_RECOGNITION:
                results['patterns'] = self.pattern_analyzer.analyze_patterns(history, provider_name)
            
            # Entry point detection
            if include_entry_signals and ENABLE_ENTRY_DETECTION:
                entry_signal = self._detect_entry_point(symbol, history, results, provider_name)
                results['entry_signals'] = entry_signal.to_dict() if entry_signal else None
                
                # Risk metrics
                if entry_signal:
                    risk_metrics = self.risk_calculator.calculate_risk_metrics(
                        history,
                        entry_signal.entry_price,
                        results['indicators'],
                        provider_name=provider_name
                    )
                    results['risk_metrics'] = risk_metrics
            
            DebugUtils.info(f"Completed comprehensive analysis for {symbol}")
            return results
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error in comprehensive analysis for {symbol}")
            raise DataProcessingException(f"Comprehensive analysis failed: {str(e)}") from e
    
    def _calculate_all_indicators(
        self,
        data: pd.DataFrame,
        provider_name: str = DEFAULT_PROVIDER
    ) -> Dict[str, Any]:
        """Calculate all technical indicators."""
        indicators = {}
        adapter = AdapterFactory.get_adapter(provider_name)
        
        try:
            # Check if volume column exists using adapter
            has_volume = False
            try:
                adapter.get_column(data, 'VOLUME')
                has_volume = True
            except DataProcessingException:
                pass
            
            # Intraday indicators
            if len(data) >= 14:
                k_percent, d_percent = self.intraday_indicators.calculate_stochastic(data, provider_name=provider_name)
                indicators['stochastic_k'] = k_percent
                indicators['stochastic_d'] = d_percent
            
            if len(data) >= 28:
                adx, plus_di, minus_di = self.intraday_indicators.calculate_adx(data, provider_name=provider_name)
                indicators['adx'] = adx
                indicators['plus_di'] = plus_di
                indicators['minus_di'] = minus_di
            
            if len(data) >= 14:
                indicators['atr'] = self.intraday_indicators.calculate_atr(data, provider_name=provider_name)
                indicators['cci'] = self.intraday_indicators.calculate_cci(data, provider_name=provider_name)
                indicators['williams_r'] = self.intraday_indicators.calculate_williams_r(data, provider_name=provider_name)
            
            if has_volume:
                if len(data) >= 14:
                    indicators['mfi'] = self.intraday_indicators.calculate_mfi(data, provider_name=provider_name)
                    indicators['obv'] = self.intraday_indicators.calculate_obv(data, provider_name=provider_name)
                
                indicators['vwap'] = self.intraday_indicators.calculate_vwap(data, provider_name=provider_name)
            
            # Volume indicators
            if has_volume:
                indicators['cmf'] = self.volume_indicators.calculate_cmf(data, provider_name=provider_name)
                indicators['ad_line'] = self.volume_indicators.calculate_accumulation_distribution(data, provider_name=provider_name)
            
            # Momentum indicators
            if len(data) >= 12:
                indicators['roc'] = self.momentum_indicators.calculate_roc(data, provider_name=provider_name)
                indicators['momentum'] = self.momentum_indicators.calculate_momentum(data, provider_name=provider_name)
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating indicators")
        
        return indicators
    
    def _detect_entry_point(
        self,
        symbol: str,
        data: pd.DataFrame,
        analysis_results: Dict[str, Any],
        provider_name: str = DEFAULT_PROVIDER
    ) -> Optional[Any]:
        """Detect entry point for stock."""
        try:
            indicators = analysis_results.get('indicators', {})
            patterns = analysis_results.get('patterns')
            adapter = AdapterFactory.get_adapter(provider_name)
            
            # Get risk metrics
            current_price = adapter.get_column(data, 'CLOSE').iloc[-1]
            risk_metrics = self.risk_calculator.calculate_risk_metrics(
                data,
                current_price,
                indicators,
                provider_name=provider_name
            )
            
            # Detect entry
            entry_signal = self.entry_detector.detect_entry(
                symbol=symbol,
                data=data,
                indicators=indicators,
                patterns=patterns,
                risk_metrics=risk_metrics,
                provider_name=provider_name
            )
            
            return entry_signal
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error detecting entry point for {symbol}")
            return None
    
    def analyze_batch_parallel(
        self,
        symbols: List[str],
        **analysis_kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze multiple stocks in parallel.
        
        Args:
            symbols: List of stock symbols
            **analysis_kwargs: Additional arguments for analysis
            
        Returns:
            Dictionary mapping symbol to analysis results
        """
        if not self.enable_parallel or not self.parallel_analyzer:
            # Fallback to sequential
            results = {}
            for symbol in symbols:
                try:
                    results[symbol] = self.analyze_stock_comprehensive(symbol, **analysis_kwargs)
                except Exception as e:
                    DebugUtils.log_error(e, f"Error analyzing {symbol}")
                    results[symbol] = {'symbol': symbol, 'status': 'error', 'error': str(e)}
            return results
        
        # Parallel analysis
        def analyze_func(symbol: str) -> Dict[str, Any]:
            return self.analyze_stock_comprehensive(symbol, **analysis_kwargs)
        
        return self.parallel_analyzer.analyze_batch(symbols, analyze_func)

