from pydantic import BaseModel
from typing import Optional, Dict, Any, Union, List


class RedisConfigUpdate(BaseModel):
    bind: Optional[str] = None
    port: Optional[Union[int, str]] = None
    timeout: Optional[Union[int, str]] = None
    maxclients: Optional[Union[int, str]] = None
    databases: Optional[Union[int, str]] = None
    requirepass: Optional[str] = None
    maxmemory: Optional[str] = None


class RedisKeyDetail(BaseModel):
    key: str
    type: str
    ttl: int
    value: Any


class RedisUserRules(BaseModel):
    enabled: bool = True
    commands: List[str] = ["+@all"] # Default: all commands
    keys: List[str] = ["~*"] # Default: all keys
    channels: List[str] = ["&*"] # Default: all channels
    # passwords: handled separately in set


class RedisUser(BaseModel):
    username: str
    password: Optional[str] = None # None means no change or no password
    enabled: bool = True
    rules: str = "+@all ~* &* +@connection" # Raw ACL string or simplified? Let's use raw for flexibility or simple for UI.
    # To keep it simple for now, we'll accept a raw 'rules' string which is standard ACL format.
    # UI can construct it. Example: "on >password +@all ~*"

class RedisUserCreate(BaseModel):
    username: str
    password: str
    enabled: bool = True
    # Simplified permissions for UI
    is_admin: bool = False # If true, +@all ~* &*
    # Custom rules string if not admin
    custom_rules: Optional[str] = None


class RedisACLUser(BaseModel):
    username: str
    enabled: bool
    flags: List[str]
    passwords: List[str]
    commands: str
    keys: str
    channels: str


class RedisCredentialsUpdate(BaseModel):
    host: str = "127.0.0.1"
    port: int = 6379
    username: Optional[str] = None
    password: Optional[str] = None
