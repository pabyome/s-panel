import redis
import os
import re
from typing import Dict, Any, List, Optional

class RedisManager:
    # Default locations to search for redis.conf
    CONFIG_PATHS = [
        "/etc/redis/redis.conf",
        "/usr/local/etc/redis.conf",
        "/opt/homebrew/etc/redis.conf" # Mac
    ]

    _client: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls, host='localhost', port=6379, password=None, db=0) -> redis.Redis:
        # For now, we assume local redis.
        # In future, we might read connection details from the config we parse.
        # But to parse config, we don't need a client.
        # To get stats/data, we do.
        if not cls._client:
            # Try to connect with defaults.
            # If the user has a password in config, we might need to be told it
            # or try to extract it from config file first?
            # Let's try passwordless first, or allow passing it.
            cls._client = redis.Redis(host=host, port=port, password=password, db=db, decode_responses=True)
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
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
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
    def save_config(cls, updates: Dict[str, str]) -> bool:
        path = cls.get_config_path()
        if not path:
            return False

        try:
            with open(path, 'r') as f:
                lines = f.readlines()
        except Exception:
            return False

        new_lines = []
        updated_keys = set()

        # Regex to match keys for replacement (simpler than full parse)
        key_pattern = re.compile(r'^\s*([^\s#]+)\s+')

        for line in lines:
            match = key_pattern.match(line)
            replaced = False

            if match and not line.strip().startswith('#'):
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
            with open(path, 'w') as f:
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

    @classmethod
    def get_dbs_keys(cls) -> Dict[str, int]:
        # Info 'keyspace' gives usage
        info = cls.get_info()
        # info["db0"] = {'keys': 1, ...}
        return {k: v['keys'] for k, v in info.items() if k.startswith('db')}

    @classmethod
    def scan_keys(cls, pattern="*", count=100) -> List[str]:
        client = cls.get_client()
        # scan iterator
        return [k for k in client.scan_iter(match=pattern, count=count)]

    @classmethod
    def get_key_details(cls, key: str) -> Dict[str, Any]:
        client = cls.get_client()
        type_ = client.type(key)
        ttl = client.ttl(key)
        val = None
        if type_ == 'string':
            val = client.get(key)
        elif type_ == 'list':
            val = client.lrange(key, 0, -1)
        elif type_ == 'set':
            val = list(client.smembers(key))
        elif type_ == 'hash':
            val = client.hgetall(key)
        elif type_ == 'zset':
             val = client.zrange(key, 0, -1, withscores=True)

        return {"key": key, "type": type_, "ttl": ttl, "value": val}

    @classmethod
    def delete_key(cls, key: str) -> bool:
        client = cls.get_client()
        return client.delete(key) > 0

    @classmethod
    def flush_db(cls) -> bool:
        client = cls.get_client()
        return client.flushdb()
