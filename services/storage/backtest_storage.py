"""
Backtest Storage

Storage system for backtest history.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

from models.backtest_result import BacktestResult
from utils.debug_utils import DebugUtils
from utils.file_utils import ensure_directory_exists
from config.app_config import DATA_DIR


class BacktestStorage:
    """
    Manages storage and retrieval of backtest results.
    
    Features:
    - Save backtest results
    - Retrieve backtest history
    - Compare backtests
    - Delete backtests
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize backtest storage.
        
        Args:
            storage_dir: Directory for storing backtests (default: DATA_DIR/backtests)
        """
        self.storage_dir = storage_dir or os.path.join(DATA_DIR, 'backtests')
        ensure_directory_exists(self.storage_dir)
        DebugUtils.info(f"Initialized BacktestStorage at {self.storage_dir}")
    
    def save_backtest(self, result: BacktestResult) -> bool:
        """
        Save backtest result to storage.
        
        Args:
            result: BacktestResult to save
            
        Returns:
            True if saved successfully
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{result.id}.json")
            
            with open(file_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
            
            DebugUtils.info(f"Saved backtest {result.id}")
            return True
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error saving backtest {result.id}")
            return False
    
    def load_backtest(self, backtest_id: str) -> Optional[BacktestResult]:
        """
        Load backtest result by ID.
        
        Args:
            backtest_id: Backtest ID
            
        Returns:
            BacktestResult or None if not found
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{backtest_id}.json")
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Reconstruct BacktestResult (simplified - would need proper deserialization)
            # For now, return dict
            return data
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error loading backtest {backtest_id}")
            return None
    
    def list_backtests(
        self,
        strategy_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all backtests with optional filtering.
        
        Args:
            strategy_name: Filter by strategy name
            limit: Maximum number of results
            
        Returns:
            List of backtest metadata
        """
        backtests = []
        
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    backtest_id = filename[:-5]  # Remove .json
                    result = self.load_backtest(backtest_id)
                    
                    if result:
                        if not strategy_name or result.get('strategy_name') == strategy_name:
                            backtests.append({
                                'id': result.get('id'),
                                'strategy_name': result.get('strategy_name'),
                                'symbols': result.get('symbols', []),
                                'start_date': result.get('start_date'),
                                'end_date': result.get('end_date'),
                                'total_return_pct': result.get('total_return_pct', 0),
                                'win_rate': result.get('win_rate', 0),
                                'created_at': result.get('created_at')
                            })
            
            # Sort by created_at descending
            backtests.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return backtests[:limit]
            
        except Exception as e:
            DebugUtils.log_error(e, "Error listing backtests")
            return []
    
    def delete_backtest(self, backtest_id: str) -> bool:
        """
        Delete backtest result.
        
        Args:
            backtest_id: Backtest ID
            
        Returns:
            True if deleted successfully
        """
        try:
            file_path = os.path.join(self.storage_dir, f"{backtest_id}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                DebugUtils.info(f"Deleted backtest {backtest_id}")
                return True
            
            return False
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error deleting backtest {backtest_id}")
            return False
    
    def compare_backtests(self, backtest_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple backtests.
        
        Args:
            backtest_ids: List of backtest IDs to compare
            
        Returns:
            Comparison dictionary
        """
        results = []
        
        for backtest_id in backtest_ids:
            result = self.load_backtest(backtest_id)
            if result:
                results.append(result)
        
        if not results:
            return {}
        
        comparison = {
            'count': len(results),
            'strategies': [r.get('strategy_name') for r in results],
            'avg_return_pct': sum(r.get('total_return_pct', 0) for r in results) / len(results),
            'avg_win_rate': sum(r.get('win_rate', 0) for r in results) / len(results),
            'best_return': max(r.get('total_return_pct', 0) for r in results),
            'worst_return': min(r.get('total_return_pct', 0) for r in results),
            'results': results
        }
        
        return comparison

