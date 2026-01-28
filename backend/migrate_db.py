#!/usr/bin/env python3
"""
Database Migration Script for S-Panel

This script adds new columns to existing tables without losing data.
Run this script when upgrading S-Panel to add new features.

Usage:
    python migrate_db.py
"""

import sqlite3
import sys
from pathlib import Path

DATABASE_FILE = "spanel.db"


def get_existing_columns(cursor, table_name: str) -> set:
    """Get the set of existing column names for a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def add_column_if_not_exists(cursor, table_name: str, column_name: str, column_def: str) -> bool:
    """Add a column to a table if it doesn't already exist."""
    existing_columns = get_existing_columns(cursor, table_name)

    if column_name in existing_columns:
        print(f"  ✓ Column '{column_name}' already exists in '{table_name}'")
        return False

    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
        print(f"  ✓ Added column '{column_name}' to '{table_name}'")
        return True
    except sqlite3.OperationalError as e:
        print(f"  ✗ Error adding column '{column_name}': {e}")
        return False


def migrate_website_table(cursor):
    """Add is_static column to website table."""
    print("\n[Website Table Migration]")

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='website'")
    if not cursor.fetchone():
        print("  ⚠ Table 'website' does not exist, skipping...")
        return

    # Add is_static column (defaults to False for existing sites)
    add_column_if_not_exists(cursor, "website", "is_static", "BOOLEAN DEFAULT 0 NOT NULL")


def run_migrations():
    """Run all database migrations."""
    db_path = Path(DATABASE_FILE)

    if not db_path.exists():
        print(f"Database file '{DATABASE_FILE}' not found.")
        print("If this is a fresh install, the database will be created automatically when S-Panel starts.")
        sys.exit(0)

    print(f"S-Panel Database Migration")
    print(f"{'=' * 40}")
    print(f"Database: {db_path.absolute()}")

    # Create a backup before migration
    backup_path = db_path.with_suffix(".db.backup")
    try:
        import shutil

        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Run migrations
        migrate_website_table(cursor)

        # Commit changes
        conn.commit()
        print(f"\n{'=' * 40}")
        print("Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        print("Database has been rolled back. Check the backup file if needed.")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migrations()
