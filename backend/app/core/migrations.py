import sqlite3
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

DB_FILE = "spanel.db" # This matches the default in database.py usually, or we can parse the URL

def get_db_path():
    # Parse from connection string or use default
    # DATABASE_URL: str = "sqlite:///spanel.db"
    # Simplistic parsing for SQLite
    url = "sqlite:///spanel.db" # Hardcoded default from database.py for now if not in settings
    if hasattr(settings, "DATABASE_URL"):
        url = settings.DATABASE_URL

    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "")
    return "spanel.db"

def run_migrations():
    db_path = get_db_path()

    # If using absolute path or relative, ensure we find it.
    # In docker or prod, CWD might vary, but usually it's root of app.
    if not os.path.exists(db_path):
        # If DB doesn't exist, SQLModel create_db_and_tables will handle it.
        return

    logger.info("Checking for pending database migrations...")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- Migration 001: Add missing DeploymentConfig columns ---
        cursor.execute("PRAGMA table_info(deploymentconfig)")
        columns = [col[1] for col in cursor.fetchall()]

        if "id" in columns: # Table exists
            if "last_commit" not in columns:
                logger.info("Migrating: Adding last_commit to deploymentconfig")
                cursor.execute("ALTER TABLE deploymentconfig ADD COLUMN last_commit VARCHAR")

            if "last_logs" not in columns:
                logger.info("Migrating: Adding last_logs to deploymentconfig")
                cursor.execute("ALTER TABLE deploymentconfig ADD COLUMN last_logs VARCHAR")

            if "deploy_count" not in columns:
                logger.info("Migrating: Adding deploy_count to deploymentconfig")
                cursor.execute("ALTER TABLE deploymentconfig ADD COLUMN deploy_count INTEGER DEFAULT 0 NOT NULL")

        conn.commit()
        conn.close()
        logger.info("Database migrations completed.")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
