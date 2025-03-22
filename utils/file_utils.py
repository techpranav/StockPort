import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta

class FileUtils:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_output_directory(self) -> Path:
        """Get the output directory path."""
        return self.output_dir

    def read_stock_symbols(self, filename: str) -> List[str]:
        """Read stock symbols from a file."""
        file_path = self.input_dir / filename
        if not file_path.exists():
            return []

        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def append_to_file(self, filename: str, content: str) -> None:
        """Append content to a file."""
        file_path = self.output_dir / filename
        with open(file_path, 'a') as f:
            f.write(f"{content}\n")

    def save_json(self, data: dict, filename: str) -> None:
        """Save data as JSON file."""
        file_path = self.output_dir / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_json(self, filename: str) -> Optional[dict]:
        """Load data from JSON file."""
        file_path = self.output_dir / filename
        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            return json.load(f)

    def get_report_filename(self, symbol: str, extension: str = ".docx") -> Path:
        """Generate a report filename for a stock symbol."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{symbol}_Analysis_Report_{timestamp}{extension}"

    def cleanup_old_reports(self, days: int = 7) -> None:
        """Remove report files older than specified days."""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for file in self.output_dir.glob("*_Analysis_Report_*"):
            if file.stat().st_mtime < cutoff_date:
                file.unlink()

    def get_file_size(self, filepath: Path) -> int:
        """Get file size in bytes."""
        return filepath.stat().st_size if filepath.exists() else 0

    def save_filtered_data(self, symbol: str, data: Dict[str, Any], output_dir: Path) -> None:
        """Save filtered data to JSON file."""
        output_file = output_dir / f"{symbol}_filtered_data.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4, default=str)

    def load_filtered_data(self, symbol: str, output_dir: Path) -> Dict[str, Any]:
        """Load filtered data from JSON file."""
        input_file = output_dir / f"{symbol}_filtered_data.json"
        if not input_file.exists():
            return {}
        
        with open(input_file, 'r') as f:
            return json.load(f)

    def cleanup_old_files(self, directory: Path, pattern: str, days: int) -> None:
        """Clean up files older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        for file_path in directory.glob(pattern):
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                file_path.unlink()

    def ensure_directory(self, directory: Path) -> None:
        """Ensure directory exists."""
        directory.mkdir(parents=True, exist_ok=True) 