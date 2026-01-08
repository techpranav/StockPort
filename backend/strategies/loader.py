"""
Strategy Loader

Loads strategies from YAML/JSON definitions.
"""

from typing import Dict, Any, List
from pathlib import Path
import yaml
import json

from utils.debug_utils import DebugUtils
from backend.strategies.base_strategy import BaseStrategy
from backend.strategies.strategies.trend_following import TrendFollowingStrategy
from backend.strategies.strategies.momentum import MomentumStrategy


class StrategyLoader:
    """
    Loads strategies from configuration files.
    
    Supports:
    - YAML format
    - JSON format
    """
    
    def __init__(self, strategies_dir: Path):
        """
        Initialize strategy loader.
        
        Args:
            strategies_dir: Directory containing strategy definitions
        """
        self.strategies_dir = Path(strategies_dir)
        self.strategies_dir.mkdir(parents=True, exist_ok=True)
    
    def load_strategy(self, file_path: Path) -> BaseStrategy:
        """
        Load a strategy from file.
        
        Args:
            file_path: Path to strategy definition file
            
        Returns:
            Strategy instance
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Strategy file not found: {file_path}")
        
        # Load file
        if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
            with open(file_path, 'r') as f:
                strategy_def = yaml.safe_load(f)
        elif file_path.suffix == '.json':
            with open(file_path, 'r') as f:
                strategy_def = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Validate strategy definition
        self._validate_strategy_def(strategy_def)
        
        # Create strategy instance based on type
        strategy_type = strategy_def['strategy']['type']
        strategy_id = strategy_def['strategy']['name']
        name = strategy_def['strategy'].get('description', strategy_id)
        status = strategy_def['strategy'].get('status', 'active')
        
        if strategy_type == 'trend_following':
            strategy = TrendFollowingStrategy(strategy_id, name, strategy_def)
        elif strategy_type == 'momentum':
            strategy = MomentumStrategy(strategy_id, name, strategy_def)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        # Set market regimes
        strategy.market_regimes = strategy_def['strategy'].get('market_regimes', [])
        strategy.exclude_regimes = strategy_def['strategy'].get('exclude_regimes', [])
        
        DebugUtils.info(f"Loaded strategy: {strategy_id} from {file_path}")
        
        return strategy
    
    def load_all(self) -> List[BaseStrategy]:
        """
        Load all strategies from strategies directory.
        
        Returns:
            List of strategy instances
        """
        strategies = []
        
        # Find all YAML and JSON files
        for file_path in self.strategies_dir.glob('*.yaml'):
            try:
                strategy = self.load_strategy(file_path)
                strategies.append(strategy)
            except Exception as e:
                DebugUtils.log_error(e, f"Error loading strategy from {file_path}")
        
        for file_path in self.strategies_dir.glob('*.yml'):
            try:
                strategy = self.load_strategy(file_path)
                strategies.append(strategy)
            except Exception as e:
                DebugUtils.log_error(e, f"Error loading strategy from {file_path}")
        
        for file_path in self.strategies_dir.glob('*.json'):
            try:
                strategy = self.load_strategy(file_path)
                strategies.append(strategy)
            except Exception as e:
                DebugUtils.log_error(e, f"Error loading strategy from {file_path}")
        
        return strategies
    
    def _validate_strategy_def(self, strategy_def: Dict[str, Any]):
        """
        Validate strategy definition.
        
        Args:
            strategy_def: Strategy definition dictionary
            
        Raises:
            ValueError: If definition is invalid
        """
        if 'strategy' not in strategy_def:
            raise ValueError("Missing 'strategy' key in definition")
        
        strategy = strategy_def['strategy']
        
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in strategy:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate entry conditions
        if 'entry' not in strategy:
            raise ValueError("Missing 'entry' section")
        
        if 'conditions' not in strategy['entry']:
            raise ValueError("Missing 'entry.conditions'")

