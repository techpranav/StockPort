"""
State Manager for System State Persistence

Manages persistent state storage and recovery.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import sqlite3
from pathlib import Path

from utils.debug_utils import DebugUtils
from config.app_config import DATA_DIR


class StateManager:
    """
    Manages system state persistence.
    
    Provides:
    - Save system state
    - Load system state
    - State recovery after crashes
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize state manager.
        
        Args:
            db_path: Path to state database file
        """
        if db_path is None:
            db_path = DATA_DIR / "trading_state.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        DebugUtils.info(f"StateManager initialized with database at {self.db_path}")
    
    def _init_database(self):
        """Initialize the state database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # System state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # State snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_data TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_system_state(self, state: Dict[str, Any]):
        """
        Save system state.
        
        Args:
            state: State dictionary to save
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        for key, value in state.items():
            cursor.execute("""
                INSERT OR REPLACE INTO system_state (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json.dumps(value), timestamp))
        
        conn.commit()
        conn.close()
        
        DebugUtils.debug(f"Saved system state: {list(state.keys())}")
    
    def load_system_state(self) -> Dict[str, Any]:
        """
        Load system state.
        
        Returns:
            Dictionary with system state
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT key, value FROM system_state")
        rows = cursor.fetchall()
        
        conn.close()
        
        state = {}
        for key, value_json in rows:
            try:
                state[key] = json.loads(value_json)
            except json.JSONDecodeError:
                DebugUtils.warning(f"Failed to decode state value for key: {key}")
        
        return state
    
    def save_snapshot(self, snapshot_data: Dict[str, Any]):
        """
        Save a state snapshot.
        
        Args:
            snapshot_data: Snapshot data dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO state_snapshots (snapshot_data, created_at)
            VALUES (?, ?)
        """, (json.dumps(snapshot_data), timestamp))
        
        conn.commit()
        conn.close()
        
        DebugUtils.debug("Saved state snapshot")
    
    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest state snapshot.
        
        Returns:
            Latest snapshot data or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT snapshot_data FROM state_snapshots
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                return json.loads(row[0])
            except json.JSONDecodeError:
                DebugUtils.warning("Failed to decode snapshot data")
                return None
        
        return None

