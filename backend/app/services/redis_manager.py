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
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Parse "key value"
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    config[parts[0]] = parts[1]

        return config

    @classmethod
    def save_config(cls, updates: Dict[str, str]) -> bool:
        path = cls.get_config_path()
        if not path:
            return False

        with open(path, 'r') as f:
            lines = f.readlines()

        new_lines = []
        # Track which keys we updated
        updated_keys = set()

        for line in lines:
            stripped = line.strip()
            # Check if this line is a config directive we want to change
            # We must be careful not to uncomment commented lines unless requested,
            # but usually we just modify active lines or append.
            # Simplified approach: If line starts with key, replace it.

            # TODO: robust parsing. For now, simple line match.
            replaced = False
            if stripped and not stripped.startswith('#'):
                parts = stripped.split(maxsplit=1)
                if len(parts) >= 1:
                    key = parts[0]
                    if key in updates:
                        new_lines.append(f"{key} {updates[key]}\n")
                        updated_keys.add(key)
                        replaced = True

            if not replaced:
                new_lines.append(line)

        # Append new keys if they weren't found
        for key, value in updates.items():
            if key not in updated_keys:
                new_lines.append(f"\n{key} {value}\n")

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
