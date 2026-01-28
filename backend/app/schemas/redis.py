from pydantic import BaseModel
from typing import Optional, Dict, Any, Union


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
