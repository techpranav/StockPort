"""
Database Connection Manager

Manages database connections (SQLite for personal use, PostgreSQL optional).
"""

from typing import Optional
import sqlite3
from pathlib import Path
from contextlib import contextmanager

from utils.debug_utils import DebugUtils
from config.app_config import DATA_DIR

# Try to import PostgreSQL (optional)
try:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    DebugUtils.info("PostgreSQL not available, using SQLite")


class DatabaseConnection:
    """
    Manages database connections.
    
    Supports:
    - SQLite (default, for personal use)
    - PostgreSQL (optional, for production)
    """
    
    _connection_pool = None
    _db_type: Optional[str] = None  # "sqlite" or "postgresql"
    _db_path: Optional[Path] = None
    
    @classmethod
    def use_sqlite(cls, db_path: Optional[Path] = None):
        """
        Use SQLite database (default for personal use).
        
        Args:
            db_path: Path to SQLite database file
        """
        cls._db_type = "sqlite"
        if db_path is None:
            db_path = DATA_DIR / "stockport.db"
        cls._db_path = Path(db_path)
        cls._db_path.parent.mkdir(parents=True, exist_ok=True)
        DebugUtils.info(f"Using SQLite database: {cls._db_path}")
    
    @classmethod
    def use_postgresql(
        cls,
        host: str = "localhost",
        port: int = 5432,
        database: str = "stockport",
        user: str = "stockport",
        password: str = "admin",
        min_connections: int = 1,
        max_connections: int = 10
    ):
        """
        Use PostgreSQL database (optional).
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: Database name
            user: Database user
            password: Database password
            min_connections: Minimum connections in pool
            max_connections: Maximum connections in pool
        """
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("PostgreSQL driver not available. Install psycopg2-binary")
        
        cls._db_type = "postgresql"
        try:
            cls._connection_pool = pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            DebugUtils.info(f"Using PostgreSQL database: {database}@{host}:{port}")
        except Exception as e:
            DebugUtils.log_error(e, "Failed to initialize PostgreSQL connection pool")
            raise
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Get a database connection.
        
        Yields:
            Database connection
        """
        if cls._db_type is None:
            cls.use_sqlite()  # Default to SQLite
        
        if cls._db_type == "sqlite":
            if cls._db_path is None:
                cls.use_sqlite()  # Initialize with default path
            conn = sqlite3.connect(cls._db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            try:
                yield conn
            finally:
                conn.close()
        else:  # PostgreSQL
            if cls._connection_pool is None:
                raise RuntimeError("PostgreSQL connection pool not initialized. Call use_postgresql() first.")
            conn = None
            try:
                conn = cls._connection_pool.getconn()
                yield conn
            finally:
                if conn:
                    cls._connection_pool.putconn(conn)
    
    @classmethod
    def execute_query(
        cls,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = True
    ):
        """
        Execute a database query.
        
        Args:
            query: SQL query (SQLite or PostgreSQL compatible)
            params: Query parameters
            fetch: Whether to fetch results
            
        Returns:
            Query results if fetch=True, None otherwise
        """
        # Initialize database type if not set
        if cls._db_type is None:
            cls.use_sqlite()  # Default to SQLite
        
        # Convert PostgreSQL syntax to SQLite if needed
        if cls._db_type == "sqlite":
            query = cls._convert_postgres_to_sqlite(query)
        
        with cls.get_connection() as conn:
            if cls._db_type == "postgresql":
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()
            
            try:
                cursor.execute(query, params)
                if fetch:
                    rows = cursor.fetchall()
                    # Convert to list of dicts for SQLite
                    if cls._db_type == "sqlite":
                        return [dict(row) for row in rows]
                    return rows
                else:
                    conn.commit()
                    return cursor.rowcount
            except Exception as e:
                if cls._db_type == "postgresql":
                    conn.rollback()
                DebugUtils.log_error(e, f"Error executing query: {query[:100]}")
                raise
            finally:
                cursor.close()
    
    @classmethod
    def _convert_postgres_to_sqlite(cls, query: str) -> str:
        """
        Convert PostgreSQL-specific syntax to SQLite.
        
        Args:
            query: PostgreSQL query
            
        Returns:
            SQLite-compatible query
        """
        # Replace PostgreSQL-specific types and syntax
        query = query.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        query = query.replace("DECIMAL(15, 4)", "REAL")
        query = query.replace("DECIMAL(15, 2)", "REAL")
        query = query.replace("DECIMAL(10, 4)", "REAL")
        query = query.replace("DECIMAL(5, 4)", "REAL")
        query = query.replace("DECIMAL(5, 2)", "REAL")
        query = query.replace("VARCHAR(100)", "TEXT")
        query = query.replace("VARCHAR(50)", "TEXT")
        query = query.replace("VARCHAR(20)", "TEXT")
        query = query.replace("VARCHAR(10)", "TEXT")
        query = query.replace("JSONB", "TEXT")  # Store as JSON string
        query = query.replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        # Remove PostgreSQL-specific constraints that SQLite doesn't support
        query = query.replace("REFERENCES opportunities(id)", "")
        return query
    
    @classmethod
    def close_pool(cls):
        """Close the connection pool (PostgreSQL only)."""
        if cls._db_type == "postgresql" and cls._connection_pool:
            cls._connection_pool.closeall()
            DebugUtils.info("Database connection pool closed")
