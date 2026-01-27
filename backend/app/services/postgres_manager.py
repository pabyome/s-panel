import subprocess
import os
import shutil
from typing import List, Dict, Any, Tuple, Optional
import re


class PostgresManager:
    """
    Manages PostgreSQL service and database operations via subprocess.
    Assumes running as root (sudo access) to switch to postgres user.
    """

    @staticmethod
    def _run_command(command: List[str], check=False) -> Tuple[bool, str]:
        try:
            result = subprocess.run(command, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, result.stderr.strip()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _run_psql(sql: str, db: str = "postgres", as_csv=False) -> Tuple[bool, str]:
        """Runs a SQL command as the postgres system user."""
        cmd = ["sudo", "-u", "postgres", "psql", "-d", db]

        if as_csv:
            cmd.extend(["-t", "-A", "-F,"])  # Tuples only, Unaligned, Comma separated
        else:
            cmd.extend(["-t", "-A"])  # Tuples only

        cmd.extend(["-c", sql])
        return PostgresManager._run_command(cmd)

    # --- Service Management ---

    @staticmethod
    def is_installed() -> bool:
        return shutil.which("psql") is not None

    @staticmethod
    def get_version() -> str:
        success, output = PostgresManager._run_command(["psql", "--version"])
        if success:
            return output.split(" ")[-1]
        return "Unknown"

    @staticmethod
    def get_service_status() -> Dict[str, Any]:
        """Returns complex status object."""
        installed = PostgresManager.is_installed()
        status = {
            "installed": installed,
            "running": False,
            "version": None,
            "uptime": None,
            "data_dir": None,
            "remote_access": False,
        }

        if not installed:
            return status

        # Check systemd status
        success, output = PostgresManager._run_command(["systemctl", "is-active", "postgresql"])
        status["running"] = output == "active"
        status["version"] = PostgresManager.get_version()

        if status["running"]:
            # Get Data Dir
            s, d = PostgresManager._run_psql("SHOW data_directory;")
            if s:
                status["data_dir"] = d

            # Check Remote Access (listen_addresses)
            s, remote = PostgresManager._run_psql("SHOW listen_addresses;")
            status["remote_access"] = remote.strip() == "*"

        return status

    @staticmethod
    def install_service() -> Tuple[bool, str]:
        # Update apt and install
        cmd = ["apt-get", "update"]
        PostgresManager._run_command(cmd)

        cmd = ["apt-get", "install", "-y", "postgresql", "postgresql-contrib"]
        success, out = PostgresManager._run_command(cmd)

        if success:
            # Enable service
            PostgresManager._run_command(["systemctl", "enable", "postgresql"])
            PostgresManager._run_command(["systemctl", "start", "postgresql"])
            return True, "Installed successfully"
        return False, out

    @staticmethod
    def uninstall_service() -> Tuple[bool, str]:
        cmd = ["apt-get", "remove", "--purge", "-y", "postgresql", "postgresql-*"]
        return PostgresManager._run_command(cmd)

    @staticmethod
    def control_service(action: str) -> Tuple[bool, str]:
        if action not in ["start", "stop", "restart", "reload"]:
            return False, "Invalid action"
        return PostgresManager._run_command(["systemctl", action, "postgresql"])

    # --- Database Operations ---

    @staticmethod
    def list_databases() -> List[Dict[str, str]]:
        # List DBs with Owner and Size
        sql = "SELECT d.datname, pg_catalog.pg_get_userbyid(d.datdba), pg_size_pretty(pg_database_size(d.datname)) FROM pg_catalog.pg_database d ORDER BY 1;"
        success, output = PostgresManager._run_psql(sql, as_csv=True)
        if not success:
            return []

        dbs = []
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.split(",")
            if len(parts) >= 3:
                dbs.append({"name": parts[0], "owner": parts[1], "size": parts[2]})
        return dbs

    @staticmethod
    def create_database(name: str, owner: str = "postgres") -> Tuple[bool, str]:
        # Validate name to prevent injection
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Invalid database name"

        # Use createdb command wrapper
        cmd = ["sudo", "-u", "postgres", "createdb", "-O", owner, name]
        return PostgresManager._run_command(cmd)

    @staticmethod
    def delete_database(name: str) -> Tuple[bool, str]:
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Invalid database name"
        cmd = ["sudo", "-u", "postgres", "dropdb", name]
        return PostgresManager._run_command(cmd)

    # --- User Operations ---

    @staticmethod
    def list_users() -> List[Dict[str, Any]]:
        sql = "SELECT usename, usesuper, usecreatedb, usecreaterole, usebypassrls FROM pg_catalog.pg_user;"
        success, output = PostgresManager._run_psql(sql, as_csv=True)
        if not success:
            return []

        users = []
        for line in output.splitlines():
            parts = line.split(",")
            if len(parts) >= 5:
                users.append(
                    {
                        "name": parts[0],
                        "superuser": parts[1] == "t",
                        "createdb": parts[2] == "t",
                        "createrole": parts[3] == "t",
                    }
                )
        return users

    @staticmethod
    def create_user(name: str, password: str, superuser: bool = False, createdb: bool = False) -> Tuple[bool, str]:
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Invalid username"

        # Construct SQL
        flags = []
        if superuser:
            flags.append("SUPERUSER")
        if createdb:
            flags.append("CREATEDB")
        flag_str = " ".join(flags)

        sql = f"CREATE USER {name} WITH PASSWORD '{password}' {flag_str};"
        return PostgresManager._run_psql(sql)

    @staticmethod
    def delete_user(name: str) -> Tuple[bool, str]:
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Invalid username"
        sql = f"DROP USER {name};"
        return PostgresManager._run_psql(sql)

    @staticmethod
    def change_password(name: str, password: str) -> Tuple[bool, str]:
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Invalid username"
        sql = f"ALTER USER {name} WITH PASSWORD '{password}';"
        return PostgresManager._run_psql(sql)

    @staticmethod
    def grant_access(db: str, user: str, schema: str = "public") -> Tuple[bool, str]:
        # Grant all on database + schema usage
        sqls = [
            f"GRANT ALL PRIVILEGES ON DATABASE {db} TO {user};",
            f"GRANT ALL ON SCHEMA {schema} TO {user};",  # Note: Needs to be run IN the db
        ]

        # Run DB grant globally
        s1, m1 = PostgresManager._run_psql(sqls[0])
        if not s1:
            return False, m1

        # Run Schema grant inside DB (requires passing -d dbname)
        # Note: running simple -c on specific db
        s2, m2 = PostgresManager._run_psql(sqls[1], db=db)
        return s2, m2

    # --- Extensions ---

    @staticmethod
    def list_extensions(db_name: str) -> List[Dict[str, str]]:
        # List installed extensions
        sql = "SELECT extname, extversion FROM pg_extension;"
        success, output = PostgresManager._run_psql(sql, db=db_name, as_csv=True)
        if not success:
            return []

        exts = []
        for line in output.splitlines():
            parts = line.split(",")
            if len(parts) >= 2:
                exts.append({"name": parts[0], "version": parts[1]})
        return exts

    @staticmethod
    def manage_extension(db_name: str, ext_name: str, action: str) -> Tuple[bool, str]:
        # action: create or drop
        sql = (
            f"{action.upper()} EXTENSION IF NOT EXISTS {ext_name}"
            if action == "create"
            else f"DROP EXTENSION IF EXISTS {ext_name}"
        )
        return PostgresManager._run_psql(sql, db=db_name)

    # --- Security & Remote Access ---

    @staticmethod
    def toggle_remote_access(enable: bool) -> Tuple[bool, str]:
        # 1. Find config files
        s, data_dir = PostgresManager._run_psql("SHOW data_directory;")
        if not s:
            return False, "Could not find data directory"

        # Usually configs are in /etc/postgresql/X/main or data_dir
        # Debian/Ubuntu uses /etc/postgresql/...
        # Let's try to locate postgresql.conf

        # Determine version first
        ver = PostgresManager.get_version()
        if "." in ver:
            ver = ver.split(".")[0]  # 14.5 -> 14

        conf_dir = f"/etc/postgresql/{ver}/main"
        if not os.path.isdir(conf_dir):
            # Fallback to data_dir
            conf_dir = data_dir

        pg_conf = os.path.join(conf_dir, "postgresql.conf")
        pg_hba = os.path.join(conf_dir, "pg_hba.conf")

        if not os.path.exists(pg_conf):
            return False, f"Config not found at {pg_conf}"

        # 2. Update postgresql.conf (listen_addresses)
        try:
            with open(pg_conf, "r") as f:
                lines = f.readlines()

            new_lines = []
            found_listen = False
            target_listen = "listen_addresses = '*'" if enable else "listen_addresses = 'localhost'"

            for line in lines:
                if line.strip().startswith("listen_addresses"):
                    new_lines.append(f"{target_listen} # Managed by s-panel\n")
                    found_listen = True
                else:
                    new_lines.append(line)

            if not found_listen:
                new_lines.append(f"{target_listen} # Managed by s-panel\n")

            with open(pg_conf, "w") as f:
                f.writelines(new_lines)
        except Exception as e:
            return False, f"Error editing conf: {e}"

        # 3. Update pg_hba.conf (host all all 0.0.0.0/0 md5)
        try:
            with open(pg_hba, "r") as f:
                lines = f.readlines()

            # Remove existing s-panel managed lines
            clean_lines = [l for l in lines if "# Managed by s-panel" not in l]

            if enable:
                # Add allow rule
                # host    all             all             0.0.0.0/0               md5
                clean_lines.append(
                    "host    all             all             0.0.0.0/0               md5 # Managed by s-panel\n"
                )
                clean_lines.append(
                    "host    all             all             ::/0                    md5 # Managed by s-panel\n"
                )

            with open(pg_hba, "w") as f:
                f.writelines(clean_lines)

        except Exception as e:
            return False, f"Error editing pg_hba: {e}"

        # 4. Configure Firewall
        # Using ufw management (assumed system command)
        if enable:
            PostgresManager._run_command(["ufw", "allow", "5432/tcp"])
        else:
            PostgresManager._run_command(["ufw", "delete", "allow", "5432/tcp"])

        # 5. Restart Postgres
        PostgresManager.control_service("restart")

        return True, "Remote access updated"

    # --- Maintenance ---

    @staticmethod
    def vacuum_database(db_name: str) -> Tuple[bool, str]:
        """Run VACUUM ANALYZE on a specific database."""
        if not re.match(r"^[a-zA-Z0-9_]+$", db_name):
            return False, "Invalid database name"
        sql = "VACUUM ANALYZE;"
        return PostgresManager._run_psql(sql, db=db_name)

    @staticmethod
    def vacuum_all() -> Tuple[bool, str]:
        """Run vacuumdb on all databases."""
        cmd = ["sudo", "-u", "postgres", "vacuumdb", "--all", "--analyze"]
        return PostgresManager._run_command(cmd)

    # --- Backup Operations ---

    @staticmethod
    def backup_database(db_name: str, format: str = "plain") -> Tuple[bool, str]:
        """Create a backup of a specific database using pg_dump."""
        if not re.match(r"^[a-zA-Z0-9_]+$", db_name):
            return False, "Invalid database name"

        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "/var/backups/postgresql"

        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)

        if format == "custom":
            backup_file = os.path.join(backup_dir, f"{db_name}_{timestamp}.dump")
            cmd = ["sudo", "-u", "postgres", "pg_dump", "-Fc", "-f", backup_file, db_name]
        else:
            backup_file = os.path.join(backup_dir, f"{db_name}_{timestamp}.sql")
            cmd = ["sudo", "-u", "postgres", "pg_dump", "-f", backup_file, db_name]

        success, msg = PostgresManager._run_command(cmd)
        if success:
            return True, f"Backup created: {backup_file}"
        return False, msg

    @staticmethod
    def backup_all(format: str = "plain") -> Tuple[bool, str]:
        """Create a full backup of all databases using pg_dumpall."""
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "/var/backups/postgresql"

        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = os.path.join(backup_dir, f"all_databases_{timestamp}.sql")
        cmd = ["sudo", "-u", "postgres", "pg_dumpall", "-f", backup_file]

        success, msg = PostgresManager._run_command(cmd)
        if success:
            return True, f"Full backup created: {backup_file}"
        return False, msg

    @staticmethod
    def list_backups() -> List[Dict[str, Any]]:
        """List available backup files."""
        backup_dir = "/var/backups/postgresql"
        if not os.path.isdir(backup_dir):
            return []

        backups = []
        try:
            for f in os.listdir(backup_dir):
                path = os.path.join(backup_dir, f)
                if os.path.isfile(path):
                    stat = os.stat(path)
                    backups.append({"filename": f, "size": stat.st_size, "created": stat.st_mtime})
            backups.sort(key=lambda x: x["created"], reverse=True)
        except Exception:
            pass
        return backups

    # --- Update Check ---

    @staticmethod
    def check_update() -> Dict[str, Any]:
        """Check if a PostgreSQL update is available via apt."""
        result = {"current_version": PostgresManager.get_version(), "available_version": None}

        # Update apt cache
        PostgresManager._run_command(["apt-get", "update", "-qq"])

        # Check for upgradeable postgresql packages
        cmd = ["apt", "list", "--upgradeable"]
        success, output = PostgresManager._run_command(cmd)

        if success:
            for line in output.splitlines():
                if "postgresql" in line.lower() and "postgresql-" not in line.lower():
                    # Parse version from line like: postgresql/focal-security 14.8-0ubuntu0.22.04.1 amd64 [upgradable from: 14.7-0ubuntu0.22.04.1]
                    parts = line.split()
                    if len(parts) >= 2:
                        result["available_version"] = parts[1].split("-")[0] if "-" in parts[1] else parts[1]
                        break

        return result
