"""
Add Docker Swarm deployment columns to deploymentconfig table
- deployment_mode: 'supervisor' or 'docker-swarm'
- swarm_replicas: number of replicas for Swarm
- current_port: internal app port
- dockerfile_path: path to Dockerfile
"""

def upgrade(conn):
    """Run the migration - add columns if they don't exist"""
    columns_to_add = [
        ("deployment_mode", "TEXT DEFAULT 'supervisor'"),
        ("swarm_replicas", "INTEGER DEFAULT 2"),
        ("current_port", "INTEGER DEFAULT 3000"),
        ("dockerfile_path", "TEXT DEFAULT 'Dockerfile'"),
    ]

    for column_name, column_def in columns_to_add:
        try:
            conn.execute(f"ALTER TABLE deploymentconfig ADD COLUMN {column_name} {column_def}")
            print(f"      Added column: {column_name}")
        except Exception as e:
            if 'duplicate column' in str(e).lower():
                print(f"      Column {column_name} already exists (skipped)")
            else:
                raise

def downgrade(conn):
    """Rollback - SQLite doesn't easily support DROP COLUMN"""
    pass
