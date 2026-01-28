import sqlite3
import os

DB_FILE = "spanel.db"

def migrate():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute("PRAGMA table_info(website)")
    columns = [info[1] for info in cursor.fetchall()]

    if "is_static" not in columns:
        print("Adding is_static column to website table...")
        try:
            # SQLite doesn't support adding column with default value for NOT NULL constraints easily
            # without a default. Boolean in SQLModel is Integer in SQLite (0/1).
            # Default to 0 (False)
            cursor.execute("ALTER TABLE website ADD COLUMN is_static BOOLEAN DEFAULT 0")
            conn.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed: {e}")
    else:
        print("Column is_static already exists.")

    conn.close()

if __name__ == "__main__":
    migrate()
