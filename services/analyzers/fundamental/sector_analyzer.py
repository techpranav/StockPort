"""
Sector Comparison Analyzer

Compares stocks against sector averages and peers.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from utils.debug_utils import DebugUtils
from exceptions.stock_data_exceptions import DataProcessingException


class SectorAnalyzer:
    """
    Sector comparison analyzer.
    
    Features:
    - Compare stock metrics to sector averages
    - Relative strength vs. sector
    - Sector rotation analysis
    - Peer comparison
    """
    
    def __init__(self):
        """Initialize sector analyzer."""
        # Sector averages (would typically come from database or API)
        self.sector_averages: Dict[str, Dict[str, float]] = {}
    
    def compare_to_sector(
        self,
        stock_metrics: Dict[str, float],
        sector: str,
        sector_averages: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Compare stock metrics to sector averages.
        
        Args:
            stock_metrics: Dictionary of stock financial metrics
            sector: Sector name
            sector_averages: Sector average metrics (optional, will use defaults if not provided)
            
        Returns:
            Comparison results
        """
        try:
            if sector_averages is None:
                sector_averages = self._get_default_sector_averages(sector)
            
            if not sector_averages:
                return {
                    'sector': sector,
                    'comparisons': {},
                    'relative_strength': 0.0
                }
            
            comparisons = {}
            relative_scores = []
            
            # Compare key metrics
            metrics_to_compare = [
                'pe_ratio', 'pb_ratio', 'roe', 'roa', 'debt_to_equity',
                'current_ratio', 'profit_margin', 'revenue_growth'
            ]
            
            for metric in metrics_to_compare:
                stock_value = stock_metrics.get(metric)
                sector_avg = sector_averages.get(metric)
                
                if stock_value is not None and sector_avg is not None and sector_avg != 0:
                    # Calculate relative performance
                    relative_performance = ((stock_value - sector_avg) / abs(sector_avg)) * 100
                    
                    # Score: positive if better, negative if worse
                    # For ratios like P/E, lower is better, so invert
                    if metric in ['pe_ratio', 'pb_ratio', 'debt_to_equity']:
                        relative_performance = -relative_performance
                    
                    comparisons[metric] = {
                        'stock_value': float(stock_value),
                        'sector_average': float(sector_avg),
                        'relative_performance_pct': float(relative_performance),
                        'better_than_sector': relative_performance > 0
                    }
                    
                    relative_scores.append(relative_performance)
            
            # Calculate overall relative strength
            relative_strength = sum(relative_scores) / len(relative_scores) if relative_scores else 0.0
            
            return {
                'sector': sector,
                'comparisons': comparisons,
                'relative_strength': float(relative_strength),
                'better_than_sector': relative_strength > 0
            }
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error comparing stock to sector {sector}")
            return {
                'sector': sector,
                'comparisons': {},
                'relative_strength': 0.0
            }
    
    def calculate_relative_strength(
        self,
        stock_returns: List[float],
        sector_returns: List[float]
    ) -> Dict[str, float]:
        """
        Calculate relative strength vs. sector.
        
        Args:
            stock_returns: List of stock returns
            sector_returns: List of sector returns
            
        Returns:
            Relative strength metrics
        """
        try:
            if not stock_returns or not sector_returns:
                return {
                    'relative_strength': 0.0,
                    'outperformance_pct': 0.0
                }
            
            stock_total_return = sum(stock_returns)
            sector_total_return = sum(sector_returns)
            
            outperformance = stock_total_return - sector_total_return
            outperformance_pct = (outperformance / abs(sector_total_return) * 100) if sector_total_return != 0 else 0.0
            
            return {
                'relative_strength': float(outperformance),
                'outperformance_pct': float(outperformance_pct),
                'stock_return': float(stock_total_return),
                'sector_return': float(sector_total_return)
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating relative strength")
            return {
                'relative_strength': 0.0,
                'outperformance_pct': 0.0
            }
    
    def compare_peers(
        self,
        stock_metrics: Dict[str, float],
        peer_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare stock to peer group.
        
        Args:
            stock_metrics: Stock metrics
            peer_metrics: List of peer metrics (each with 'symbol' and metrics)
            
        Returns:
            Peer comparison results
        """
        try:
            if not peer_metrics:
                return {
                    'peers': [],
                    'rankings': {}
                }
            
            # Calculate peer averages
            peer_averages = {}
            metric_keys = stock_metrics.keys()
            
            for metric in metric_keys:
                peer_values = [
                    peer.get('metrics', {}).get(metric)
                    for peer in peer_metrics
                    if peer.get('metrics', {}).get(metric) is not None
                ]
                
                if peer_values:
                    peer_averages[metric] = np.mean(peer_values)
            
            # Compare to peers
            comparisons = {}
            for metric, stock_value in stock_metrics.items():
                peer_avg = peer_averages.get(metric)
                
                if stock_value is not None and peer_avg is not None and peer_avg != 0:
                    relative = ((stock_value - peer_avg) / abs(peer_avg)) * 100
                    comparisons[metric] = {
                        'stock_value': float(stock_value),
                        'peer_average': float(peer_avg),
                        'relative_pct': float(relative)
                    }
            
            # Rank among peers
            rankings = {}
            for metric in metric_keys:
                stock_value = stock_metrics.get(metric)
                if stock_value is not None:
                    peer_values = [
                        (peer.get('symbol', ''), peer.get('metrics', {}).get(metric))
                        for peer in peer_metrics
                        if peer.get('metrics', {}).get(metric) is not None
                    ]
                    
                    # Add stock to list for ranking
                    all_values = [(stock_metrics.get('symbol', 'STOCK'), stock_value)] + peer_values
                    
                    # Sort (higher is better for most metrics, except P/E, P/B, debt ratios)
                    if metric in ['pe_ratio', 'pb_ratio', 'debt_to_equity']:
                        all_values.sort(key=lambda x: x[1] if x[1] is not None else float('inf'))
                    else:
                        all_values.sort(key=lambda x: x[1] if x[1] is not None else float('-inf'), reverse=True)
                    
                    # Find rank
                    rank = next((i + 1 for i, (sym, _) in enumerate(all_values) if sym == stock_metrics.get('symbol', 'STOCK')), len(all_values))
                    total = len(all_values)
                    
                    rankings[metric] = {
                        'rank': rank,
                        'total': total,
                        'percentile': ((total - rank) / total * 100) if total > 0 else 0.0
                    }
            
            return {
                'peers': peer_metrics,
                'peer_averages': peer_averages,
                'comparisons': comparisons,
                'rankings': rankings
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error comparing to peers")
            return {
                'peers': [],
                'rankings': {}
            }
    
    def _get_default_sector_averages(self, sector: str) -> Dict[str, float]:
        """
        Get default sector averages (placeholder - would come from database).
        
        Args:
            sector: Sector name
            
        Returns:
            Dictionary of sector average metrics
        """
        # Placeholder values - in production, these would come from a database or API
        defaults = {
            'technology': {
                'pe_ratio': 25.0,
                'pb_ratio': 5.0,
                'roe': 15.0,
                'roa': 10.0,
                'debt_to_equity': 0.5,
                'current_ratio': 2.0,
                'profit_margin': 20.0,
                'revenue_growth': 15.0
            },
            'finance': {
                'pe_ratio': 15.0,
                'pb_ratio': 1.5,
                'roe': 12.0,
                'roa': 1.0,
                'debt_to_equity': 2.0,
                'current_ratio': 1.0,
                'profit_margin': 25.0,
                'revenue_growth': 8.0
            }
        }
        
        return defaults.get(sector.lower(), {})

