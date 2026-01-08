"""
Audit Logger

Comprehensive audit trail for all system decisions.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import json
import sqlite3
from pathlib import Path

from utils.debug_utils import DebugUtils
from config.app_config import DATA_DIR


@dataclass
class AuditLog:
    """Audit log entry."""
    timestamp: datetime
    event_type: str
    event_data: Dict[str, Any]
    user_id: Optional[str]
    decision_id: str
    explanation: str


class AuditLogger:
    """
    Comprehensive audit logger.
    
    Logs:
    - All trading decisions
    - All order executions
    - All capital allocations
    - All risk limit checks
    - All strategy evaluations
    - All kill-switch activations
    - All user overrides
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize audit logger.
        
        Args:
            db_path: Path to audit database
        """
        if db_path is None:
            db_path = DATA_DIR / "audit_log.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        DebugUtils.info(f"AuditLogger initialized with database at {self.db_path}")
    
    def _init_database(self):
        """Initialize audit database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                user_id TEXT,
                decision_id TEXT,
                explanation TEXT
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_type ON audit_logs(event_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_decision_id ON audit_logs(decision_id)
        """)
        
        conn.commit()
        conn.close()
    
    def log(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        decision_id: Optional[str] = None,
        user_id: Optional[str] = None,
        explanation: Optional[str] = None
    ):
        """
        Log an event.
        
        Args:
            event_type: Type of event
            event_data: Event data dictionary
            decision_id: Decision identifier (optional)
            user_id: User identifier (optional)
            explanation: Human-readable explanation (optional)
        """
        timestamp = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_logs (
                timestamp, event_type, event_data, user_id, decision_id, explanation
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            timestamp.isoformat(),
            event_type,
            json.dumps(event_data),
            user_id,
            decision_id,
            explanation
        ))
        
        conn.commit()
        conn.close()
        
        DebugUtils.debug(f"Audit log: {event_type} - {decision_id or 'N/A'}")
    
    def get_logs(
        self,
        event_type: Optional[str] = None,
        decision_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs.
        
        Args:
            event_type: Filter by event type (optional)
            decision_id: Filter by decision ID (optional)
            limit: Maximum number of logs to return
            
        Returns:
            List of AuditLog objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if decision_id:
            query += " AND decision_id = ?"
            params.append(decision_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append(AuditLog(
                timestamp=datetime.fromisoformat(row[1]),
                event_type=row[2],
                event_data=json.loads(row[3]),
                user_id=row[4],
                decision_id=row[5],
                explanation=row[6]
            ))
        
        return logs

