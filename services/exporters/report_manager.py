import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from config.constants import *
from config.constants.Messages import (
    SUCCESS_REPORT_DELETED,
    MSG_NO_REPORTS_AVAILABLE
)
from utils.debug_utils import DebugUtils

class ReportManager:
    """Manages report storage, cleanup, and retrieval."""
    
    def __init__(self, reports_dir: str = None):
        """Initialize the report manager."""
        self.reports_dir = Path(reports_dir) if reports_dir else Path(REPORTS_DIR)
        self.reports_dir.mkdir(exist_ok=True)
        self.metadata_file = self.reports_dir / "reports_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load report metadata from JSON file."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            return {"reports": []}
        except Exception as e:
            DebugUtils.log_error(e, "Error loading report metadata")
            return {"reports": []}
    
    def _save_metadata(self):
        """Save report metadata to JSON file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            DebugUtils.log_error(e, "Error saving report metadata")
    
    def register_report(self, symbol: str, report_type: str, file_path: str, 
                       analysis_date: datetime = None, days_back: int = 30) -> str:
        """Register a new report in the metadata."""
        try:
            if analysis_date is None:
                analysis_date = datetime.now()
            
            report_id = f"{symbol}_{report_type}_{analysis_date.strftime('%Y%m%d_%H%M%S')}"
            
            report_entry = {
                "id": report_id,
                "symbol": symbol,
                "report_type": report_type,  # 'excel' or 'word'
                "file_path": str(file_path),
                "file_name": Path(file_path).name,
                "analysis_date": analysis_date.isoformat(),
                "days_back": days_back,
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "created_at": datetime.now().isoformat()
            }
            
            self.metadata["reports"].append(report_entry)
            self._save_metadata()
            
            DebugUtils.info(f"Registered report: {report_id}")
            return report_id
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error registering report for {symbol}")
            return ""
    
    def get_reports(self, symbol: str = None, report_type: str = None, 
                   days_limit: int = None) -> List[Dict[str, Any]]:
        """Get reports filtered by criteria."""
        try:
            reports = self.metadata.get("reports", [])
            
            # Filter by symbol
            if symbol:
                reports = [r for r in reports if r.get("symbol", "").upper() == symbol.upper()]
            
            # Filter by report type
            if report_type:
                reports = [r for r in reports if r.get("report_type") == report_type]
            
            # Filter by date limit
            if days_limit:
                cutoff_date = datetime.now() - timedelta(days=days_limit)
                reports = [r for r in reports if datetime.fromisoformat(r.get("analysis_date", "")) >= cutoff_date]
            
            # Filter out reports where files don't exist
            valid_reports = []
            for report in reports:
                if os.path.exists(report.get("file_path", "")):
                    valid_reports.append(report)
                else:
                    DebugUtils.warning(f"Report file not found: {report.get('file_path')}")
            
            # Sort by analysis date (newest first)
            valid_reports.sort(key=lambda x: x.get("analysis_date", ""), reverse=True)
            
            # Transform field names for UI compatibility
            transformed_reports = []
            for report in valid_reports:
                transformed_report = report.copy()
                # Transform field names to match UI expectations
                transformed_report['created_date'] = datetime.fromisoformat(report.get('created_at', ''))
                transformed_report['size'] = report.get('file_size', 0)
                transformed_report['path'] = report.get('file_path', '')
                transformed_reports.append(transformed_report)
            
            return transformed_reports
            
        except Exception as e:
            DebugUtils.log_error(e, "Error retrieving reports")
            return []
    
    def cleanup_old_reports(self, days: int) -> int:
        """Clean up reports older than specified days."""
        try:
            if days <= 0:
                DebugUtils.info("Report cleanup disabled (days <= 0)")
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=days)
            reports_to_remove = []
            files_removed = 0
            
            for report in self.metadata.get("reports", []):
                try:
                    analysis_date = datetime.fromisoformat(report.get("analysis_date", ""))
                    if analysis_date < cutoff_date:
                        # Remove the file
                        file_path = report.get("file_path", "")
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            files_removed += 1
                            DebugUtils.info(f"Removed old report: {file_path}")
                        
                        reports_to_remove.append(report)
                        
                except Exception as e:
                    DebugUtils.log_error(e, f"Error processing report: {report.get('id')}")
            
            # Remove from metadata
            for report in reports_to_remove:
                self.metadata["reports"].remove(report)
            
            self._save_metadata()
            
            DebugUtils.info(f"Cleanup complete: Removed {files_removed} old reports (older than {days} days)")
            return files_removed
            
        except Exception as e:
            DebugUtils.log_error(e, "Error during report cleanup")
            return 0
    
    def get_report_stats(self) -> Dict[str, Any]:
        """Get statistics about stored reports."""
        try:
            reports = self.metadata.get("reports", [])
            total_reports = len(reports)
            
            # Count by type
            excel_reports = len([r for r in reports if r.get("report_type") == REPORT_TYPE_EXCEL])
            word_reports = len([r for r in reports if r.get("report_type") == REPORT_TYPE_WORD])
            
            # Count by symbol
            symbols = {}
            for report in reports:
                symbol = report.get("symbol", "Unknown")
                symbols[symbol] = symbols.get(symbol, 0) + 1
            
            # Calculate total size
            total_size = sum(r.get("file_size", 0) for r in reports)
            
            # Recent reports (last 7 days)
            recent_cutoff = datetime.now() - timedelta(days=7)
            recent_reports = len([r for r in reports 
                                if datetime.fromisoformat(r.get("analysis_date", "")) >= recent_cutoff])
            
            return {
                "total_reports": total_reports,
                "excel_reports": excel_reports,
                "word_reports": word_reports,
                "unique_symbols": len(symbols),
                "symbols_breakdown": symbols,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "recent_reports_7days": recent_reports,
                "oldest_report": min([r.get("analysis_date") for r in reports]) if reports else None,
                "newest_report": max([r.get("analysis_date") for r in reports]) if reports else None
            }
            
        except Exception as e:
            DebugUtils.log_error(e, "Error calculating report stats")
            return {}
    
    def delete_report(self, report_id: str) -> bool:
        """Delete a specific report by ID."""
        try:
            reports = self.metadata.get("reports", [])
            for i, report in enumerate(reports):
                if report.get("id") == report_id:
                    # Remove the file
                    file_path = report.get("file_path", "")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    # Remove from metadata
                    del self.metadata["reports"][i]
                    self._save_metadata()
                    
                    DebugUtils.info(f"Deleted report: {report_id}")
                    return True
            
            DebugUtils.warning(f"Report not found: {report_id}")
            return False
            
        except Exception as e:
            DebugUtils.log_error(e, f"Error deleting report: {report_id}")
            return False
    
    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report by ID."""
        try:
            reports = self.metadata.get("reports", [])
            for report in reports:
                if report.get("id") == report_id:
                    return report
            return None
        except Exception as e:
            DebugUtils.log_error(e, f"Error retrieving report: {report_id}")
            return None 