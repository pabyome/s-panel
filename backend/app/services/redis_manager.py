import redis
import os
import re
import subprocess
from typing import Dict, Any, List, Optional, Tuple, Iterator
from app.core.config import settings


class RedisManager:
    # Default locations to search for redis.conf
    CONFIG_PATHS = ["/etc/redis/redis.conf", "/usr/local/etc/redis.conf", "/opt/homebrew/etc/redis.conf"]  # Mac

    _client: Optional[redis.Redis] = None

    @classmethod
    def get_service_status(cls) -> Dict[str, Any]:
        """Check if Redis service is running"""
        try:
            # Try systemctl first (Linux)
            result = subprocess.run(
                ["systemctl", "is-active", "redis-server"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                running = result.stdout.strip() == "active"
            else:
                # Try redis-server service name variant
                result = subprocess.run(
                    ["systemctl", "is-active", "redis"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                running = result.stdout.strip() == "active"

            # Get version
            version = None
            try:
                ver_result = subprocess.run(
                    ["redis-server", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if ver_result.returncode == 0:
                    # Output: "Redis server v=7.0.0 sha=..."
                    match = re.search(r"v=(\d+\.\d+\.\d+)", ver_result.stdout)
                    if match:
                        version = match.group(1)
            except:
                pass

            return {"running": running, "version": version, "error": None}
        except FileNotFoundError:
            return {"running": False, "version": None, "error": "systemctl not found"}
        except Exception as e:
            return {"running": False, "version": None, "error": str(e)}

    @classmethod
    def control_service(cls, action: str) -> Tuple[bool, str]:
        """Start, stop, or restart Redis service"""
        service_names = ["redis-server", "redis"]

        for service in service_names:
            try:
                result = subprocess.run(
                    ["systemctl", action, service], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if result.returncode == 0:
                    return True, f"Redis service {action}ed successfully"
            except:
                continue

        return False, f"Failed to {action} Redis service"

    @classmethod
    def get_client(
        cls,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        db: Optional[int] = None,
    ) -> redis.Redis:
        # Resolve config defaults
        host = host or settings.REDIS_HOST
        port = port or settings.REDIS_PORT
        username = username or settings.REDIS_USER
        password = password or settings.REDIS_PASS
        if db is None:
            db = settings.REDIS_DB

        # Auto-discovery fallback for password if not provided
        if not password:
             discovered = cls.auto_discover_credentials()
             if discovered.get("password"):
                 password = discovered["password"]
                 # If we discovered a password, and no user is set, we might default to 'default'
                 # But 'default' is implied by Redis if no user is passed, so we can leave username as None or "default"
                 if not username and discovered.get("username"):
                     username = discovered["username"]

        # Check if we have a client and if it matches the requested DB
        if cls._client:
            connection_kwargs = cls._client.connection_pool.connection_kwargs
            # We could check more params, but typically DB is the main switcher
            current_db = connection_kwargs.get('db')
            current_host = connection_kwargs.get('host')
            current_port = connection_kwargs.get('port')

            # Simple check if connection params changed (re-connection needed)
            if (current_db != db or
                current_host != host or
                current_port != port):
                 cls._client.close()
                 cls._client = None
            else:
                 return cls._client

        # Create new
        cls._client = redis.Redis(
            host=host,
            port=port,
            username=username,
            password=password,
            db=db,
            decode_responses=True
        )
        return cls._client

    @classmethod
    def get_config_path(cls) -> Optional[str]:
        # Allow env override
        if os.getenv("REDIS_CONF_PATH"):
            return os.getenv("REDIS_CONF_PATH")

        for path in cls.CONFIG_PATHS:
            if os.path.exists(path):
                return path
        return None

    @classmethod
    def read_config(cls) -> Dict[str, str]:
        path = cls.get_config_path()
        if not path:
            return {"error": "Config file not found"}

        config = {}
        # Regex for "key value" where value can be quoted or not
        # Basic Redis config: keyword argument...
        # We assume 1 argument for simplicity map (key -> value)
        # Matches: key value (simple), key "value with spaces", key 'value'
        # Ignores comments starting with #

        # Pattern:
        # ^\s*          Start of line, optional whitespace
        # ([^\s#]+)     Key: non-whitespace, non-comment char
        # \s+           Whitespace separator
        # (             Value Group
        #   "(?:[^"\\]|\\.)*"  Double quoted string
        #   |
        #   '(?:[^'\\]|\\.)*'  Single quoted string
        #   |
        #   [^#\r\n]+          Unquoted value (until comment or EOL)
        # )
        pattern = re.compile(r'^\s*([^\s#]+)\s+(?:"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'|([^#\r\n]+))')

        try:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    match = pattern.match(line)
                    if match:
                        key = match.group(1)
                        # Value could be in group 2 (double quote), 3 (single quote), or 4 (unquoted)
                        if match.group(2) is not None:
                            val = match.group(2)
                        elif match.group(3) is not None:
                            val = match.group(3)
                        else:
                            val = match.group(4).strip()

                        config[key] = val
        except Exception as e:
            return {"error": f"Failed to parse config: {str(e)}"}

        return config

    @classmethod
    def auto_discover_credentials(cls) -> Dict[str, str]:
        """Attempt to read credentials from redis.conf"""
        try:
            config = cls.read_config()
            if "error" in config:
                return {}

            creds = {}
            if "requirepass" in config:
                creds["password"] = config["requirepass"]
                # If requirepass is set, it's usually for the default user or global
                creds["username"] = "default"

            # Parsing ACL "user" lines is complex and they might be in a separate aclfile
            # but we can try basic 'user default ... >password' if it exists in main conf
            # Realistically, most simple setups just use requirepass.

            return creds
        except:
            return {}

    @classmethod
    def save_config(cls, updates: Dict[str, str]) -> bool:
        path = cls.get_config_path()
        if not path:
            return False

        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except Exception:
            return False

        new_lines = []
        updated_keys = set()

        # Regex to match keys for replacement (simpler than full parse)
        key_pattern = re.compile(r"^\s*([^\s#]+)\s+")

        for line in lines:
            match = key_pattern.match(line)
            replaced = False

            if match and not line.strip().startswith("#"):
                key = match.group(1)
                if key in updates:
                    # Replace the entire line with new key value
                    # We check if value needs quoting? For simplicity, we just write it.
                    # Should verify if value has spaces.
                    val = str(updates[key])
                    if " " in val and not (val.startswith('"') or val.startswith("'")):
                        val = f'"{val}"'

                    new_lines.append(f"{key} {val}\n")
                    updated_keys.add(key)
                    replaced = True

            if not replaced:
                new_lines.append(line)

        # Append new keys
        if updates and len(updated_keys) < len(updates):
            new_lines.append("\n# Added by s-panel\n")
            for key, val in updates.items():
                if key not in updated_keys:
                    s_val = str(val)
                    if " " in s_val and not (s_val.startswith('"') or s_val.startswith("'")):
                        s_val = f'"{s_val}"'
                    new_lines.append(f"{key} {s_val}\n")

        try:
            with open(path, "w") as f:
                f.writelines(new_lines)
            return True
        except Exception as e:
            print(f"Error saving redis config: {e}")
            return False

    # Data Operations

    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        client = cls.get_client()
        try:
            return client.info()
        except redis.ConnectionError:
            return {"error": "Could not connect to Redis"}
        except redis.AuthenticationError:
            return {"error": "Authentication failed"}

    @classmethod
    def check_connection(cls) -> Dict[str, Any]:
        """Explicit check for connection status."""
        client = cls.get_client()
        try:
            client.ping()
            return {"status": "connected"}
        except redis.AuthenticationError:
            return {"status": "auth_required", "detail": "Authentication failed"}
        except redis.ConnectionError as e:
            return {"status": "failed", "detail": str(e)}
        except Exception as e:
            return {"status": "failed", "detail": str(e)}

    @classmethod
    def update_credentials(cls, host: str, port: int, password: str, username: str = None) -> bool:
        """Update .env file with new credentials"""
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

        try:
            # Read existing
            lines = []
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    lines = f.readlines()

            updates = {
                "REDIS_HOST": host,
                "REDIS_PORT": port,
                "REDIS_PASS": password,
            }
            if username:
                updates["REDIS_USER"] = username

            new_lines = []
            # Updated existing keys
            updated_keys = set()

            for line in lines:
                key_match = re.match(r"^([A-Z_]+)=", line)
                if key_match:
                    key = key_match.group(1)
                    if key in updates:
                        # Replace
                        val = updates[key]
                        new_lines.append(f"{key}={val}\n")
                        updated_keys.add(key)
                        continue
                new_lines.append(line)

            # Append missing
            if len(new_lines) > 0 and not new_lines[-1].endswith("\n"):
                 new_lines.append("\n")

            for key, val in updates.items():
                if key not in updated_keys:
                    new_lines.append(f"{key}={val}\n")

            with open(env_path, "w") as f:
                f.writelines(new_lines)

            # Also update runtime settings if we can, or rely on reload.
            # Ideally we reload settings. But simple variable update might work for immediate use.
            settings.REDIS_HOST = str(host)
            settings.REDIS_PORT = int(port)
            settings.REDIS_PASS = str(password)
            settings.REDIS_USER = str(username) if username else None

            # Reset client to force reconnect with new creds
            if cls._client:
                cls._client.close()
                cls._client = None

            return True
        except Exception as e:
            print(f"Failed to update .env: {e}")
            return False

    @classmethod
    def get_dbs_keys(cls) -> Dict[str, int]:
        # Info 'keyspace' gives usage
        info = cls.get_info()
        # info["db0"] = {'keys': 1, ...}
        return {k: v["keys"] for k, v in info.items() if k.startswith("db")}

    @classmethod
    def scan_keys(cls, pattern="*", count=100, db: Optional[int] = None) -> Iterator[str]:
        client = cls.get_client(db=db)
        # scan iterator
        return client.scan_iter(match=pattern, count=count)

    @classmethod
    def get_key_details(cls, key: str, db: Optional[int] = None) -> Dict[str, Any]:
        client = cls.get_client(db=db)
        type_ = client.type(key)
        ttl = client.ttl(key)
        val = None
        if type_ == "string":
            val = client.get(key)
        elif type_ == "list":
            val = client.lrange(key, 0, -1)
        elif type_ == "set":
            val = list(client.smembers(key))
        elif type_ == "hash":
            val = client.hgetall(key)
        elif type_ == "zset":
            val = client.zrange(key, 0, -1, withscores=True)

        return {"key": key, "type": type_, "ttl": ttl, "value": val}

    @classmethod
    def delete_key(cls, key: str, db: Optional[int] = None) -> bool:
        client = cls.get_client(db=db)
        return client.delete(key) > 0

    @classmethod
    def flush_db(cls, db: Optional[int] = None) -> bool:
        client = cls.get_client(db=db)
        return client.flushdb()

    # ACL Operations

    @classmethod
    def get_acl_users(cls) -> List[str]:
        """Return list of ACL usernames."""
        client = cls.get_client()
        try:
            # Redis 6+
            return client.execute_command("ACL", "USERS")
        except redis.ResponseError:
            # Fallback or older redis
            return []

    @classmethod
    def get_acl_user_details(cls, username: str) -> Dict[str, Any]:
        """Return details for a specific user."""
        client = cls.get_client()
        try:
            # ACL GETUSER username
            info = client.execute_command("ACL", "GETUSER", username)
            # info is a list/dict depending on python redis version but usually list of key-values or dict
            # In decode_responses=True, likely dict or pairwise list
            # We can normalize it. Redis-py often parses it well.
            if isinstance(info, list):
                 # Convert list [key, val, key, val] to dict if needed, but normally it's dict in newer redis-py
                 # If list of strings:
                 it = iter(info)
                 return dict(zip(it, it))
            return info
        except redis.ResponseError:
            return {}

    @classmethod
    def set_acl_user(cls, username: str, rules: str) -> bool:
        """Create or update a user with full ACL rule string."""
        client = cls.get_client()
        try:
            # ACL SETUSER username rule1 rule2 ...
            # We assume 'rules' is a space-separated string of rules like "on >pass +@all"
            # We split by space for args
            # "reset" rule is useful to clear old state if updating
            cmd = ["ACL", "SETUSER", username] + rules.split()
            result = client.execute_command(*cmd)
            return result == "OK"
        except redis.ResponseError as e:
            print(f"ACL SETUSER failed: {e}")
            return False

    @classmethod
    def delete_acl_user(cls, username: str) -> bool:
        client = cls.get_client()
        try:
            # ACL DELUSER username
            result = client.execute_command("ACL", "DELUSER", username)
            return result >= 1 # Returns number of deleted users
        except redis.ResponseError:
            return False
