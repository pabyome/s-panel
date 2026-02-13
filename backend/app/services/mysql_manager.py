import os
import re
import shutil
import subprocess
from typing import Any


class MysqlManager:
    """
    Manages MySQL service and database operations via subprocess.
    Assumes running as root (sudo access) to run mysql commands.
    """

    @staticmethod
    def _run_command(command: list[str], check=False) -> tuple[bool, str]:
        try:
            result = subprocess.run(command, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, result.stderr.strip()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _escape_literal(s: str) -> str:
        """Escape a string literal for SQL (replaces ' with '')."""
        if s is None:
            return ""
        # In standard SQL, single quote is escaped by another single quote
        return s.replace("'", "''")

    @staticmethod
    def _escape_identifier(s: str) -> str:
        """Escape an identifier for MySQL (replaces ` with `` and wraps in ``)."""
        if s is None:
            return '``'
        escaped = s.replace('`', '``')
        return f'`{escaped}`'

    @staticmethod
    def _run_mysql(sql: str, as_tuples=False) -> tuple[bool, str]:
        """Runs a SQL command via mysql CLI."""
        # Use sudo mysql to connect via socket as root
        cmd = ["sudo", "mysql"]

        if as_tuples:
            cmd.extend(["-N", "-B"]) # No headers, Batch mode (tab separated)
        else:
            cmd.extend(["-N"]) # No headers

        cmd.extend(["-e", sql])
        return MysqlManager._run_command(cmd)

    # --- Service Management ---

    @staticmethod
    def is_installed() -> bool:
        return shutil.which("mysql") is not None

    @staticmethod
    def get_version() -> str:
        success, output = MysqlManager._run_command(["mysql", "--version"])
        if success:
            # Output format: mysql  Ver 8.0.36-0ubuntu0.22.04.1 for Linux on x86_64 ((Ubuntu))
            match = re.search(r"Ver\s+([0-9.]+)", output)
            if match:
                return match.group(1)
            return output
        return "Unknown"

    @staticmethod
    def get_service_status() -> dict[str, Any]:
        """Returns complex status object."""
        installed = MysqlManager.is_installed()
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
        # Service name might be mysql or mariadb depending on distro
        service_name = "mysql"
        success, output = MysqlManager._run_command(["systemctl", "is-active", service_name])
        status["running"] = output == "active"
        status["version"] = MysqlManager.get_version()

        if status["running"]:
            # Get Data Dir
            s, d = MysqlManager._run_mysql("SELECT @@datadir;")
            if s:
                status["data_dir"] = d

            # Check Remote Access (bind-address)
            # Typically 0.0.0.0 means remote access allowed
            # We can check via config or netstat, but config is safer here if we manage it
            # Or query variable
            s, bind_addr = MysqlManager._run_mysql("SELECT @@bind_address;")
            status["remote_access"] = bind_addr.strip() == "0.0.0.0" or bind_addr.strip() == "*"

        return status

    @staticmethod
    def install_service() -> tuple[bool, str]:
        # Update apt and install
        cmd = ["apt-get", "update"]
        MysqlManager._run_command(cmd)

        cmd = ["apt-get", "install", "-y", "mysql-server"]
        success, out = MysqlManager._run_command(cmd)

        if success:
            # Enable service
            MysqlManager._run_command(["systemctl", "enable", "mysql"])
            MysqlManager._run_command(["systemctl", "start", "mysql"])
            return True, "Installed successfully"
        return False, out

    @staticmethod
    def uninstall_service() -> tuple[bool, str]:
        cmd = ["apt-get", "remove", "--purge", "-y", "mysql-server", "mysql-*"]
        return MysqlManager._run_command(cmd)

    @staticmethod
    def control_service(action: str) -> tuple[bool, str]:
        if action not in ["start", "stop", "restart", "reload"]:
            return False, "Invalid action"
        return MysqlManager._run_command(["systemctl", action, "mysql"])

    # --- Database Operations ---

    @staticmethod
    def list_databases() -> list[dict[str, str]]:
        # List DBs with Size
        # Information Schema query for size
        sql = """
        SELECT table_schema,
               ROUND(SUM(data_length + index_length) / 1024 / 1024, 2)
        FROM information_schema.tables
        GROUP BY table_schema;
        """
        success, output = MysqlManager._run_mysql(sql, as_tuples=True)
        sizes = {}
        if success:
            for line in output.splitlines():
                parts = line.split("\t")
                if len(parts) >= 2:
                    sizes[parts[0]] = parts[1]

        # List all DBs to catch empty ones too
        s, dbs_out = MysqlManager._run_mysql("SHOW DATABASES;", as_tuples=True)
        if not s:
            return []

        dbs = []
        exclude = {'information_schema', 'mysql', 'performance_schema', 'sys'}
        for line in dbs_out.splitlines():
            name = line.strip()
            if name in exclude:
                continue

            size_mb = sizes.get(name, "0.00")
            dbs.append({
                "name": name,
                "owner": "mysql", # MySQL doesn't track owner per DB in the same way
                "size": f"{size_mb} MB"
            })
        return dbs

    @staticmethod
    def create_database(name: str) -> tuple[bool, str]:
        # Validate name to prevent injection
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Invalid database name"

        safe_name = MysqlManager._escape_identifier(name)
        sql = f"CREATE DATABASE {safe_name};"
        return MysqlManager._run_mysql(sql)

    @staticmethod
    def delete_database(name: str) -> tuple[bool, str]:
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Invalid database name"

        safe_name = MysqlManager._escape_identifier(name)
        sql = f"DROP DATABASE {safe_name};"
        return MysqlManager._run_mysql(sql)

    # --- User Operations ---

    @staticmethod
    def list_users() -> list[dict[str, Any]]:
        sql = "SELECT User, Host, Super_priv FROM mysql.user WHERE User NOT IN ('mysql.sys', 'debian-sys-maint', 'root');"
        success, output = MysqlManager._run_mysql(sql, as_tuples=True)
        if not success:
            return []

        users = []
        for line in output.splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                name = parts[0]
                host = parts[1]
                # Combine user@host as unique identifier for UI if needed,
                # but simplistic approach is to just list user
                users.append(
                    {
                        "name": f"{name}@{host}",
                        "superuser": parts[2] == "Y",
                        "createdb": True, # MySQL users generally can if granted
                    }
                )
        return users

    @staticmethod
    def create_user(name: str, password: str, grant_all: bool = False) -> tuple[bool, str]:
        # Validate name
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Invalid username"

        safe_user = name
        safe_pass = MysqlManager._escape_literal(password)

        # Create user for all hosts '%'
        sql_create = f"CREATE USER '{safe_user}'@'%' IDENTIFIED BY '{safe_pass}';"
        s, m = MysqlManager._run_mysql(sql_create)
        if not s:
            return False, m

        if grant_all:
            sql_grant = f"GRANT ALL PRIVILEGES ON *.* TO '{safe_user}'@'%' WITH GRANT OPTION;"
            MysqlManager._run_mysql(sql_grant)

        MysqlManager._run_mysql("FLUSH PRIVILEGES;")
        return True, "User created"

    @staticmethod
    def delete_user(name: str) -> tuple[bool, str]:
        # Expecting name in format user@host
        if "@" not in name:
            return False, "Invalid user format (expected user@host)"

        user, host = name.split("@", 1)
        # simplistic validation

        sql = f"DROP USER '{user}'@'{host}';"
        return MysqlManager._run_mysql(sql)

    @staticmethod
    def change_password(name: str, password: str) -> tuple[bool, str]:
        if "@" not in name:
            return False, "Invalid user format (expected user@host)"

        user, host = name.split("@", 1)
        safe_pass = MysqlManager._escape_literal(password)

        sql = f"ALTER USER '{user}'@'{host}' IDENTIFIED BY '{safe_pass}';"
        return MysqlManager._run_mysql(sql)

    @staticmethod
    def grant_access(db: str, user_host: str) -> tuple[bool, str]:
        if "@" not in user_host:
            return False, "Invalid user format"

        user, host = user_host.split("@", 1)

        safe_db = MysqlManager._escape_identifier(db)
        # If db is *, grant on *.*
        target = f"{safe_db}.*" if db != "*" else "*.*"

        sql = f"GRANT ALL PRIVILEGES ON {target} TO '{user}'@'{host}';"
        s, m = MysqlManager._run_mysql(sql)
        if s:
             MysqlManager._run_mysql("FLUSH PRIVILEGES;")
        return s, m

    # --- Security & Remote Access ---

    @staticmethod
    def toggle_remote_access(enable: bool) -> tuple[bool, str]:
        # Locate my.cnf or mysqld.cnf
        # Common locations: /etc/mysql/mysql.conf.d/mysqld.cnf

        config_file = "/etc/mysql/mysql.conf.d/mysqld.cnf"
        if not os.path.exists(config_file):
            # Try alternate
            config_file = "/etc/mysql/my.cnf"
            if not os.path.exists(config_file):
                return False, "Could not find MySQL configuration file"

        try:
            with open(config_file, "r") as f:
                lines = f.readlines()

            new_lines = []
            found_bind = False
            target_bind = "bind-address = 0.0.0.0" if enable else "bind-address = 127.0.0.1"

            for line in lines:
                if line.strip().startswith("bind-address"):
                    new_lines.append(f"{target_bind} # Managed by s-panel\n")
                    found_bind = True
                else:
                    new_lines.append(line)

            if not found_bind:
                # Add under [mysqld] if possible, otherwise append
                # Simple append might be risky if section not present, but usually [mysqld] is there
                new_lines.append(f"\n[mysqld]\n{target_bind} # Managed by s-panel\n")

            with open(config_file, "w") as f:
                f.writelines(new_lines)

        except Exception as e:
            return False, f"Error editing config: {e}"

        # Firewall
        if enable:
            MysqlManager._run_command(["ufw", "allow", "3306/tcp"])
        else:
            MysqlManager._run_command(["ufw", "delete", "allow", "3306/tcp"])

        # Restart
        return MysqlManager.control_service("restart")

    # --- Backup Operations ---

    @staticmethod
    def backup_database(db_name: str) -> tuple[bool, str]:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "/var/backups/mysql"
        os.makedirs(backup_dir, exist_ok=True)

        if not re.match(r"^[a-zA-Z0-9_]+$", db_name):
             return False, "Invalid database name"

        backup_file = os.path.join(backup_dir, f"{db_name}_{timestamp}.sql")
        # mysqldump needs user/pass usually, but sudo mysqldump might work via socket
        cmd = ["sudo", "mysqldump", db_name]

        try:
            with open(backup_file, "w") as f:
                subprocess.run(cmd, stdout=f, check=True)
            return True, f"Backup created: {backup_file}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def backup_all() -> tuple[bool, str]:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "/var/backups/mysql"
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = os.path.join(backup_dir, f"all_databases_{timestamp}.sql")
        cmd = ["sudo", "mysqldump", "--all-databases"]

        try:
            with open(backup_file, "w") as f:
                subprocess.run(cmd, stdout=f, check=True)
            return True, f"Full backup created: {backup_file}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def list_backups() -> list[dict[str, Any]]:
        backup_dir = "/var/backups/mysql"
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
    def check_update() -> dict[str, Any]:
        """Check if a MySQL update is available via apt."""
        result = {"current_version": MysqlManager.get_version(), "available_version": None}

        # Update apt cache
        MysqlManager._run_command(["apt-get", "update", "-qq"])

        # Check for upgradeable packages
        cmd = ["apt", "list", "--upgradeable"]
        success, output = MysqlManager._run_command(cmd)

        if success:
            for line in output.splitlines():
                if "mysql-server" in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        result["available_version"] = parts[1]
                        break
        return result
