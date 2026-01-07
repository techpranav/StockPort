"""
Export Configuration Model

Defines configuration for data export with criteria fields.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ExportFormat(Enum):
    """Supported export formats."""
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"
    WORD = "word"


class DataType(Enum):
    """Types of data to export."""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SIGNALS = "signals"
    PATTERNS = "patterns"
    RISK_METRICS = "risk_metrics"
    ALL = "all"


@dataclass
class ExportCriteria:
    """Criteria for data export."""
    stock_symbols: List[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    data_types: List[DataType] = field(default_factory=lambda: [DataType.ALL])
    export_format: ExportFormat = ExportFormat.EXCEL
    include_indicators: List[str] = field(default_factory=list)  # Specific indicators to include
    exclude_indicators: List[str] = field(default_factory=list)  # Specific indicators to exclude
    custom_filters: Dict[str, Any] = field(default_factory=dict)  # Custom filter criteria
    template_name: Optional[str] = None  # Custom report template


@dataclass
class ExportPreset:
    """Saved export preset configuration."""
    name: str
    criteria: ExportCriteria
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    use_count: int = 0

