"""
Database Initialization Script

Initializes the database with schema (SQLite by default, PostgreSQL optional).
"""

from pathlib import Path
import sys
import io
import sqlite3

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.debug_utils import DebugUtils
from database.connection import DatabaseConnection
from config.app_config import DATA_DIR


def init_database(use_postgresql: bool = False):
    """
    Initialize the database with schema.
    
    Args:
        use_postgresql: If True, use PostgreSQL; otherwise use SQLite (default)
        
    Returns:
        True if successful, False otherwise
    """
    db_type = "PostgreSQL" if use_postgresql else "SQLite"
    print(f"Initializing {db_type} database...")
    
    try:
        if use_postgresql:
            # Use PostgreSQL
            try:
                from config.app_config import (
                    POSTGRES_HOST,
                    POSTGRES_PORT,
                    POSTGRES_DB,
                    POSTGRES_USER,
                    POSTGRES_PASSWORD
                )
                DatabaseConnection.use_postgresql(
                    host=POSTGRES_HOST,
                    port=POSTGRES_PORT,
                    database=POSTGRES_DB,
                    user=POSTGRES_USER,
                    password=POSTGRES_PASSWORD
                )
                schema_file = Path(__file__).parent / "schema.sql"
            except ImportError:
                DebugUtils.error("PostgreSQL driver not available. Install psycopg2-binary")
                return False
        else:
            # Use SQLite (default for personal use)
            DatabaseConnection.use_sqlite()
            schema_file = Path(__file__).parent / "schema_sqlite.sql"
        
        if not schema_file.exists():
            DebugUtils.error(f"Schema file not found: {schema_file}")
            return False
        
        # Read and execute schema
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema statements
        with DatabaseConnection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            
            # Separate CREATE TABLE and CREATE INDEX statements
            table_statements = []
            index_statements = []
            
            for statement in statements:
                if not statement or statement.startswith('--'):
                    continue
                statement_upper = statement.upper().strip()
                if statement_upper.startswith('CREATE TABLE'):
                    table_statements.append(statement)
                elif statement_upper.startswith('CREATE INDEX'):
                    index_statements.append(statement)
                else:
                    # Other statements (like ALTER, etc.)
                    table_statements.append(statement)
            
            # Execute table statements first
            for statement in table_statements:
                try:
                    cursor.execute(statement)
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'already exists' in error_msg or 'duplicate' in error_msg:
                        DebugUtils.debug(f"Table already exists, skipping: {statement[:50]}...")
                        if use_postgresql:
                            conn.rollback()
                            conn.autocommit = True
                        continue
                    else:
                        if use_postgresql:
                            conn.rollback()
                        DebugUtils.log_error(e, f"Error creating table: {statement[:100]}")
                        raise
            
            # Execute index statements after tables
            for statement in index_statements:
                try:
                    cursor.execute(statement)
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'already exists' in error_msg or 'duplicate' in error_msg or 'no such table' in error_msg:
                        DebugUtils.debug(f"Index already exists or table missing, skipping: {statement[:50]}...")
                        if use_postgresql:
                            conn.rollback()
                            conn.autocommit = True
                        continue
                    else:
                        if use_postgresql:
                            conn.rollback()
                        DebugUtils.log_error(e, f"Error creating index: {statement[:100]}")
                        raise
            
            if not use_postgresql:
                conn.commit()  # SQLite needs explicit commit
            cursor.close()
        
        print(f"[SUCCESS] {db_type} database schema initialized successfully!")
        DebugUtils.info(f"Database schema initialized successfully ({'PostgreSQL' if use_postgresql else 'SQLite'})")
        
        return True
        
    except Exception as e:
        DebugUtils.log_error(e, "Error initializing database")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Stockport v4 database")
    parser.add_argument(
        "--postgresql",
        action="store_true",
        help="Use PostgreSQL instead of SQLite (default: SQLite)"
    )
    
    args = parser.parse_args()
    success = init_database(use_postgresql=args.postgresql)
    sys.exit(0 if success else 1)

