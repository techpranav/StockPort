import json
import os
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

class FileUtils:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Create directories if they don't exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _json_serializer(self, obj):
        """Custom JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, pd.DataFrame):
            if obj.empty:
                return {}
            # Convert DataFrame to a more manageable format
            try:
                return {
                    'type': 'DataFrame',
                    'data': obj.to_dict('records'),
                    'columns': list(obj.columns),
                    'index': [str(idx) for idx in obj.index]
                }
            except Exception:
                return {'type': 'DataFrame', 'data': {}, 'columns': [], 'index': []}
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return str(obj)
        elif pd.isna(obj):
            return None
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)

    def read_stock_symbols(self, filename: str) -> List[str]:
        """Read stock symbols from a file."""
        filepath = self.input_dir / filename
        if not filepath.exists():
            return []
        
        with open(filepath, 'r') as f:
            symbols = [line.strip().replace('\r', '').replace('\n', '') for line in f.readlines() if line.strip()]
        return symbols

    def save_stock_symbols(self, symbols: List[str], filename: str) -> None:
        """Save stock symbols to a file."""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            for symbol in symbols:
                f.write(f"{symbol}\n")

    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in the input directory."""
        return (self.input_dir / filename).exists()

    def create_backup(self, filepath: Path) -> Path:
        """Create a backup of the given file."""
        backup_path = filepath.with_suffix(filepath.suffix + '.backup')
        if filepath.exists():
            filepath.rename(backup_path)
        return backup_path

    def get_file_size(self, filepath: Path) -> int:
        """Get file size in bytes."""
        return filepath.stat().st_size if filepath.exists() else 0

    def save_filtered_data(self, symbol: str, data: Dict[str, Any], output_dir: Path) -> None:
        """Save filtered data to JSON file with proper DataFrame handling."""
        output_file = output_dir / f"{symbol}_filtered_data.json"
        try:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=4, default=self._json_serializer)
        except Exception as e:
            # If JSON serialization still fails, save a minimal version
            minimal_data = {
                'symbol': data.get('symbol', symbol),
                'info': data.get('info', {}),
                'metrics': data.get('metrics', {}),
                'technical_analysis': data.get('technical_analysis', {}),
                'technical_signals': data.get('technical_signals', {}),
                'error': f"Full data serialization failed: {str(e)}"
            }
            with open(output_file, 'w') as f:
                json.dump(minimal_data, f, indent=4, default=str) 