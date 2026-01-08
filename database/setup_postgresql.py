"""
PostgreSQL Setup Script

Automatically sets up PostgreSQL database, user, and permissions.
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.debug_utils import DebugUtils
from config.app_config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD
)


def setup_postgresql():
    """
    Automatically set up PostgreSQL database.
    
    Creates:
    - Database if it doesn't exist
    - User if it doesn't exist
    - Grants necessary permissions
    """
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        DebugUtils.error("PostgreSQL driver (psycopg2-binary) not installed.")
        DebugUtils.info("Install it with: pip install psycopg2-binary")
        return False
    
    print("Setting up PostgreSQL database...")
    DebugUtils.info("Setting up PostgreSQL database...")
    
    try:
        # Connect to PostgreSQL server (using default postgres database)
        # Try connecting as postgres user first (common default)
        conn = None
        connected_user = None
        connected_password = None
        
        # Try common default users
        default_users = [
            ("postgres", POSTGRES_PASSWORD),
            ("postgres", "admin"),  # Your password
            (POSTGRES_USER, POSTGRES_PASSWORD),
        ]
        
        for user, password in default_users:
            try:
                print(f"Attempting to connect as user: {user}...")
                DebugUtils.info(f"Attempting to connect as user: {user}")
                conn = psycopg2.connect(
                    host=POSTGRES_HOST,
                    port=POSTGRES_PORT,
                    database="postgres",  # Connect to default database
                    user=user,
                    password=password
                )
                connected_user = user
                connected_password = password
                print(f"✓ Connected to PostgreSQL as {user}")
                DebugUtils.info(f"Connected to PostgreSQL as {user}")
                break
            except psycopg2.OperationalError as e:
                print(f"  Failed to connect as {user}")
                DebugUtils.debug(f"Failed to connect as {user}: {e}")
                continue
        
        if conn is None:
            print("❌ Could not connect to PostgreSQL server.")
            print(f"   Please ensure PostgreSQL is running at {POSTGRES_HOST}:{POSTGRES_PORT}")
            DebugUtils.error("Could not connect to PostgreSQL server.")
            DebugUtils.info(f"Please ensure PostgreSQL is running and accessible at {POSTGRES_HOST}:{POSTGRES_PORT}")
            DebugUtils.info("You may need to provide correct credentials in .env file")
            return False
        
        conn.autocommit = True  # Required for creating database
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (POSTGRES_DB,)
        )
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print(f"Creating database: {POSTGRES_DB}...")
            DebugUtils.info(f"Creating database: {POSTGRES_DB}")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(POSTGRES_DB)
                )
            )
            print(f"✓ Database '{POSTGRES_DB}' created successfully")
            DebugUtils.info(f"Database '{POSTGRES_DB}' created successfully")
        else:
            print(f"✓ Database '{POSTGRES_DB}' already exists")
            DebugUtils.info(f"Database '{POSTGRES_DB}' already exists")
        
        # Check if user exists
        cursor.execute(
            "SELECT 1 FROM pg_user WHERE usename = %s",
            (POSTGRES_USER,)
        )
        user_exists = cursor.fetchone()
        
        if not user_exists:
            print(f"Creating user: {POSTGRES_USER}...")
            DebugUtils.info(f"Creating user: {POSTGRES_USER}")
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(POSTGRES_USER)
                ),
                (POSTGRES_PASSWORD,)
            )
            print(f"✓ User '{POSTGRES_USER}' created successfully")
            DebugUtils.info(f"User '{POSTGRES_USER}' created successfully")
        else:
            print(f"✓ User '{POSTGRES_USER}' already exists")
            DebugUtils.info(f"User '{POSTGRES_USER}' already exists")
            # Update password if user exists
            try:
                cursor.execute(
                    sql.SQL("ALTER USER {} WITH PASSWORD %s").format(
                        sql.Identifier(POSTGRES_USER)
                    ),
                    (POSTGRES_PASSWORD,)
                )
                print(f"✓ Password updated for user '{POSTGRES_USER}'")
                DebugUtils.info(f"Password updated for user '{POSTGRES_USER}'")
            except Exception as e:
                print(f"  Note: Could not update password (may require superuser)")
                DebugUtils.debug(f"Could not update password (may require superuser): {e}")
        
        # Grant privileges
        print(f"Granting privileges to user '{POSTGRES_USER}' on database '{POSTGRES_DB}'...")
        DebugUtils.info(f"Granting privileges to user '{POSTGRES_USER}' on database '{POSTGRES_DB}'")
        try:
            # Grant database privileges
            cursor.execute(
                sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                    sql.Identifier(POSTGRES_DB),
                    sql.Identifier(POSTGRES_USER)
                )
            )
            
            # Connect to the target database to grant schema privileges
            cursor.close()
            conn.close()
            
            # Reconnect to the new database
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB,
                user=connected_user,  # Use the user we connected with
                password=connected_password
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Grant schema privileges
            cursor.execute(
                sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(
                    sql.Identifier(POSTGRES_USER)
                )
            )
            
            # Grant default privileges for future tables
            cursor.execute(
                sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}").format(
                    sql.Identifier(POSTGRES_USER)
                )
            )
            
            print("✓ Privileges granted successfully")
            DebugUtils.info("Privileges granted successfully")
            
        except Exception as e:
            print(f"⚠ Warning: Could not grant all privileges (may require superuser)")
            print(f"  Database and user created, but some privileges may need manual setup")
            DebugUtils.warning(f"Could not grant all privileges (may require superuser): {e}")
            DebugUtils.info("Database and user created, but some privileges may need manual setup")
        
        cursor.close()
        conn.close()
        
        print()
        print("✅ PostgreSQL setup completed successfully!")
        print(f"   Database: {POSTGRES_DB}")
        print(f"   User: {POSTGRES_USER}")
        print(f"   Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
        DebugUtils.info("PostgreSQL setup completed successfully!")
        DebugUtils.info(f"Database: {POSTGRES_DB}")
        DebugUtils.info(f"User: {POSTGRES_USER}")
        DebugUtils.info(f"Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
        
        return True
        
    except psycopg2.OperationalError as e:
        DebugUtils.error(f"PostgreSQL connection error: {e}")
        DebugUtils.info("Please ensure PostgreSQL is running and accessible")
        return False
    except psycopg2.Error as e:
        DebugUtils.log_error(e, "PostgreSQL error during setup")
        return False
    except Exception as e:
        DebugUtils.log_error(e, "Unexpected error during PostgreSQL setup")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL Setup Script")
    print("=" * 60)
    print()
    
    success = setup_postgresql()
    
    print()
    if success:
        print("✅ PostgreSQL setup complete!")
        print()
        print("You can now use PostgreSQL by setting DATABASE_TYPE=postgresql in .env")
        print("Otherwise, the system will use SQLite by default (no setup needed)")
        DebugUtils.info("\n✅ PostgreSQL setup complete!")
        DebugUtils.info("You can now use PostgreSQL by setting DATABASE_TYPE=postgresql in .env")
    else:
        print("❌ PostgreSQL setup failed")
        print("The system will use SQLite by default (which requires no setup)")
        DebugUtils.error("\n❌ PostgreSQL setup failed")
        DebugUtils.info("The system will use SQLite by default (which requires no setup)")
    
    print()
    sys.exit(0 if success else 1)

