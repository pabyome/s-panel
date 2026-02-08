#!/usr/bin/env python3
"""
Database Migration Runner for s-panel
Runs all pending migrations from the migrations/ directory
Supports Python migration files (.py)
"""
import os
import sys
import sqlite3
import importlib.util
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_FILE = SCRIPT_DIR / "spanel.db"
MIGRATIONS_DIR = SCRIPT_DIR / "migrations"

def get_connection():
    return sqlite3.connect(str(DB_FILE))

def ensure_migrations_table(conn):
    """Create the schema_migrations table if it doesn't exist"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration VARCHAR(255) NOT NULL UNIQUE,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

def get_applied_migrations(conn):
    """Get list of already applied migrations"""
    cursor = conn.execute("SELECT migration FROM schema_migrations")
    return {row[0] for row in cursor.fetchall()}

def load_migration_module(migration_file: Path):
    """Dynamically load a Python migration file"""
    spec = importlib.util.spec_from_file_location(
        migration_file.stem,
        migration_file
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_migration(conn, migration_file: Path):
    """Run a single migration file"""
    migration_name = migration_file.name

    try:
        # Load and execute the migration
        module = load_migration_module(migration_file)

        # Call the upgrade function
        if hasattr(module, 'upgrade'):
            module.upgrade(conn)
            conn.commit()
        else:
            return False, "Migration missing 'upgrade' function"

        # Record the migration
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations (migration) VALUES (?)",
            (migration_name,)
        )
        conn.commit()
        return True, None

    except sqlite3.OperationalError as e:
        # Handle "duplicate column" gracefully
        if 'duplicate column' in str(e).lower():
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations (migration) VALUES (?)",
                (migration_name,)
            )
            conn.commit()
            return True, "Column already exists (skipped)"
        return False, str(e)
    except Exception as e:
        return False, str(e)

def run_migrations():
    """Run all pending migrations"""
    # Check if database exists
    if not DB_FILE.exists():
        print("  ℹ No database found. Will be created on first app run.")
        return 0

    # Ensure migrations directory exists
    MIGRATIONS_DIR.mkdir(exist_ok=True)

    conn = get_connection()
    ensure_migrations_table(conn)

    applied = get_applied_migrations(conn)

    # Get all Python migration files, sorted by name (timestamp order)
    migration_files = sorted(MIGRATIONS_DIR.glob("*.py"))
    # Exclude __init__.py and __pycache__
    migration_files = [f for f in migration_files if not f.name.startswith("__")]

    pending_count = 0
    for migration_file in migration_files:
        migration_name = migration_file.name

        if migration_name in applied:
            continue

        print(f"  ▶ Running migration: {migration_name}")

        success, message = run_migration(conn, migration_file)

        if success:
            if message:
                print(f"    ✓ {message}")
            else:
                print(f"    ✓ Applied")
            pending_count += 1
        else:
            print(f"    ✗ Failed: {message}")
            conn.close()
            sys.exit(1)

    conn.close()

    if pending_count == 0:
        print("  ✓ Database is up to date")
    else:
        print(f"  ✓ Applied {pending_count} migration(s)")

    return pending_count

if __name__ == "__main__":
    run_migrations()
