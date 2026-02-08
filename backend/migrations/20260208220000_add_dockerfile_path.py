"""
Add dockerfile_path column to deploymentconfig table
This allows specifying a custom Dockerfile location for Docker Swarm deployments
"""

def upgrade(conn):
    """Run the migration"""
    conn.execute("""
        ALTER TABLE deploymentconfig
        ADD COLUMN dockerfile_path TEXT DEFAULT 'Dockerfile'
    """)

def downgrade(conn):
    """Rollback the migration (SQLite doesn't support DROP COLUMN easily)"""
    pass
