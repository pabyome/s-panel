import sqlite3
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

DB_FILE = "spanel.db"

def get_db_path():
    url = "sqlite:///spanel.db" # Default
    if hasattr(settings, "DATABASE_URL"):
        url = settings.DATABASE_URL

    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "")
    return "spanel.db"

def add_column_safe(cursor, table, col_def):
    """Helper to safely add a column to a table."""
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
        logger.info(f"Migrating: Added column {col_def} to {table}")
    except sqlite3.OperationalError as e:
        # SQLite error messages for duplicate columns can vary or be specific
        if "duplicate column name" in str(e).lower():
            logger.info(f"Migration check: Column '{col_def.split()[0]}' already exists in {table}")
        else:
            # Some versions might fail differently, but generally this means it exists or table is locked
            logger.warning(f"Migration warning for {table} column {col_def}: {e}")

def run_migrations():
    db_path = get_db_path()

    if not os.path.exists(db_path):
        # Database doesn't exist yet, SQLModel will create it with correct schema
        return

    logger.info("Checking for pending database migrations...")

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- Migration 001: DeploymentConfig Columns ---
        cursor.execute("PRAGMA table_info(deploymentconfig)")
        columns = [col[1] for col in cursor.fetchall()]

        if "id" in columns: # Table exists
            if "last_commit" not in columns:
                add_column_safe(cursor, "deploymentconfig", "last_commit VARCHAR")

            if "last_logs" not in columns:
                add_column_safe(cursor, "deploymentconfig", "last_logs VARCHAR")

            if "deploy_count" not in columns:
                add_column_safe(cursor, "deploymentconfig", "deploy_count INTEGER DEFAULT 0 NOT NULL")

            if "run_as_user" not in columns:
                add_column_safe(cursor, "deploymentconfig", "run_as_user VARCHAR DEFAULT 'root'")

        # --- Migration 002: Website Columns ---
        cursor.execute("PRAGMA table_info(website)")
        website_columns = [col[1] for col in cursor.fetchall()]

        if "id" in website_columns: # Table exists
            if "created_at" not in website_columns:
                add_column_safe(cursor, "website", "created_at DATETIME DEFAULT CURRENT_TIMESTAMP")

            if "owner_id" not in website_columns:
                # Adding basic INTEGER column.
                # SQLite ALTER TABLE support for REFERENCES is limited/complex. simple integer is safer for migration.
                add_column_safe(cursor, "website", "owner_id INTEGER")

        conn.commit()
        logger.info("Database migrations completed.")

    except Exception as e:
        logger.error(f"Migration failed checking: {e}")
    finally:
        if conn:
            conn.close()
