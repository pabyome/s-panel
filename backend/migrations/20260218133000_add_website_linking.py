
import sqlite3

def upgrade(conn):
    cursor = conn.cursor()

    # 1. Add website_domain and website_ssl to deploymentconfig
    try:
        cursor.execute("ALTER TABLE deploymentconfig ADD COLUMN website_domain VARCHAR")
    except sqlite3.OperationalError:
        pass # Already exists

    try:
        cursor.execute("ALTER TABLE deploymentconfig ADD COLUMN website_ssl BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        # SQLite doesn't have true booleans, uses 0/1.
        # But if column exists error is thrown.
        pass

    # 2. Ensure owner_id is in website table (if website table exists)
    # Check if website table exists first
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='website'")
    if cursor.fetchone():
        try:
            cursor.execute("ALTER TABLE website ADD COLUMN owner_id INTEGER REFERENCES user(id)")
        except sqlite3.OperationalError:
            pass

    conn.commit()
