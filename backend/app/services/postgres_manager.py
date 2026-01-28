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
            cmd.extend(["-t", "-A", "-F|"])  # Tuples only, Unaligned, Pipe separated (safer than comma)
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
            parts = line.split("|")
            if len(parts) >= 3:
                dbs.append({"name": parts[0].strip(), "owner": parts[1].strip(), "size": parts[2].strip()})
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
        # Use pg_roles which is more reliable than pg_user
        sql = "SELECT rolname, rolsuper, rolcreatedb, rolcreaterole FROM pg_catalog.pg_roles WHERE rolcanlogin = true ORDER BY rolname;"
        success, output = PostgresManager._run_psql(sql, as_csv=True)
        if not success:
            return []

        users = []
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) >= 4:
                users.append(
                    {
                        "name": parts[0].strip(),
                        "superuser": parts[1].strip() == "t",
                        "createdb": parts[2].strip() == "t",
                        "createrole": parts[3].strip() == "t",
                    }
                )
        return users

    @staticmethod
    def create_user(name: str, password: str, superuser: bool = False, createdb: bool = False) -> Tuple[bool, str]:
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Invalid username"

        # Check if user already exists
        check_sql = f"SELECT 1 FROM pg_roles WHERE rolname = '{name}';"
        exists, output = PostgresManager._run_psql(check_sql)
        if exists and output.strip() == "1":
            # User exists, update password and attributes instead
            flags = []
            if superuser:
                flags.append("SUPERUSER")
            else:
                flags.append("NOSUPERUSER")
            if createdb:
                flags.append("CREATEDB")
            else:
                flags.append("NOCREATEDB")
            flag_str = " ".join(flags)
            sql = f"ALTER ROLE {name} WITH PASSWORD '{password}' {flag_str};"
            success, msg = PostgresManager._run_psql(sql)
            if success:
                return True, "User updated (already existed)"
            return False, msg

        # Construct SQL for new user
        flags = ["LOGIN"]  # Ensure user can login
        if superuser:
            flags.append("SUPERUSER")
        if createdb:
            flags.append("CREATEDB")
        flag_str = " ".join(flags)

        sql = f"CREATE ROLE {name} WITH {flag_str} PASSWORD '{password}';"
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

    # Popular PostgreSQL extensions with their package requirements
    EXTENSION_INFO = {
        "postgis": {
            "package": "postgresql-{ver}-postgis-3",
            "description": "Geographic Information Systems (GIS) support",
            "category": "GIS",
        },
        "postgis_topology": {
            "package": "postgresql-{ver}-postgis-3",
            "description": "PostGIS topology support",
            "category": "GIS",
        },
        "pg_trgm": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "Trigram matching for similarity searches",
            "category": "Search",
        },
        "uuid-ossp": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "UUID generation functions",
            "category": "Utilities",
        },
        "hstore": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "Key-value store within a single value",
            "category": "Data Types",
        },
        "pgcrypto": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "Cryptographic functions",
            "category": "Security",
        },
        "citext": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "Case-insensitive character string type",
            "category": "Data Types",
        },
        "ltree": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "Hierarchical tree-like data type",
            "category": "Data Types",
        },
        "pg_stat_statements": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "Track execution statistics of SQL statements",
            "category": "Monitoring",
        },
        "tablefunc": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "Functions for crosstab and other table manipulations",
            "category": "Utilities",
        },
        "unaccent": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "Remove accents from text",
            "category": "Search",
        },
        "fuzzystrmatch": {
            "package": "postgresql-{ver}",  # Built-in contrib
            "description": "Fuzzy string matching (soundex, levenshtein)",
            "category": "Search",
        },
        "timescaledb": {
            "package": "timescaledb-2-postgresql-{ver}",
            "description": "Time-series database extension",
            "category": "Time Series",
            "repo": "https://packagecloud.io/timescale/timescaledb",
        },
        "pg_cron": {
            "package": "postgresql-{ver}-cron",
            "description": "Job scheduler for PostgreSQL",
            "category": "Utilities",
        },
        "vector": {
            "package": "postgresql-{ver}-pgvector",
            "description": "Vector similarity search (AI/ML embeddings)",
            "category": "AI/ML",
        },
        "plpgsql": {
            "package": "postgresql-{ver}",  # Built-in
            "description": "PL/pgSQL procedural language (built-in)",
            "category": "Languages",
        },
    }

    @staticmethod
    def list_extensions(db_name: str) -> List[Dict[str, str]]:
        # List installed extensions
        sql = "SELECT extname, extversion FROM pg_extension;"
        success, output = PostgresManager._run_psql(sql, db=db_name, as_csv=True)
        if not success:
            return []

        exts = []
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) >= 2:
                exts.append({"name": parts[0].strip(), "version": parts[1].strip()})
        return exts

    @staticmethod
    def list_available_extensions() -> List[Dict[str, Any]]:
        """List all extensions available to be installed (from pg_available_extensions)."""
        sql = "SELECT name, default_version, comment FROM pg_available_extensions ORDER BY name;"
        success, output = PostgresManager._run_psql(sql, as_csv=True)
        if not success:
            return []

        exts = []
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) >= 2:
                ext_name = parts[0].strip()
                info = PostgresManager.EXTENSION_INFO.get(ext_name, {})
                exts.append(
                    {
                        "name": ext_name,
                        "version": parts[1].strip() if len(parts) > 1 else "",
                        "description": parts[2].strip() if len(parts) > 2 else info.get("description", ""),
                        "category": info.get("category", "Other"),
                        "available": True,
                    }
                )
        return exts

    @staticmethod
    def get_extension_info(ext_name: str) -> Dict[str, Any]:
        """Get detailed info about an extension including installation instructions."""
        pg_version = PostgresManager.get_version()
        major_ver = pg_version.split(".")[0] if pg_version else "14"

        # Check if extension is available in PostgreSQL
        sql = f"SELECT name, default_version, comment FROM pg_available_extensions WHERE name = '{ext_name}';"
        success, output = PostgresManager._run_psql(sql, as_csv=True)

        is_available = success and output.strip()

        info = PostgresManager.EXTENSION_INFO.get(ext_name, {})
        package = info.get("package", "").replace("{ver}", major_ver)

        result = {
            "name": ext_name,
            "available": is_available,
            "description": info.get("description", "No description available"),
            "category": info.get("category", "Other"),
            "package": package,
            "install_instructions": None,
        }

        if not is_available:
            # Generate installation instructions
            if package:
                instructions = f"# Install the required package:\nsudo apt-get update\nsudo apt-get install -y {package}\n\n# Then restart PostgreSQL:\nsudo systemctl restart postgresql"
                if info.get("repo"):
                    instructions = f"# First add the repository:\n# See: {info['repo']}\n\n" + instructions
                result["install_instructions"] = instructions
            else:
                result["install_instructions"] = (
                    f"# Extension '{ext_name}' may require manual installation.\n# Check PostgreSQL documentation or extension website."
                )

        return result

    @staticmethod
    def get_popular_extensions() -> List[Dict[str, Any]]:
        """Get list of popular extensions with availability status."""
        pg_version = PostgresManager.get_version()
        major_ver = pg_version.split(".")[0] if pg_version else "14"

        # Get list of available extensions
        available = set()
        sql = "SELECT name FROM pg_available_extensions;"
        success, output = PostgresManager._run_psql(sql, as_csv=True)
        if success:
            for line in output.splitlines():
                if line.strip():
                    available.add(line.strip())

        results = []
        for ext_name, info in PostgresManager.EXTENSION_INFO.items():
            package = info.get("package", "").replace("{ver}", major_ver)
            results.append(
                {
                    "name": ext_name,
                    "description": info.get("description", ""),
                    "category": info.get("category", "Other"),
                    "available": ext_name in available,
                    "package": package,
                }
            )

        return sorted(results, key=lambda x: (not x["available"], x["category"], x["name"]))

    @staticmethod
    def install_extension_package(ext_name: str) -> Tuple[bool, str]:
        """Install the system package required for an extension."""
        pg_version = PostgresManager.get_version()
        major_ver = pg_version.split(".")[0] if pg_version else "14"

        info = PostgresManager.EXTENSION_INFO.get(ext_name)
        if not info:
            return False, f"Unknown extension: {ext_name}. Manual installation may be required."

        package = info.get("package", "").replace("{ver}", major_ver)
        if not package:
            return False, f"No package information available for {ext_name}"

        # Update apt
        PostgresManager._run_command(["apt-get", "update"])

        # Install package
        success, output = PostgresManager._run_command(["apt-get", "install", "-y", package])
        if not success:
            return False, f"Failed to install package {package}: {output}"

        # Restart PostgreSQL to load new extension
        PostgresManager._run_command(["systemctl", "restart", "postgresql"])

        return True, f"Package {package} installed successfully. PostgreSQL restarted."

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
