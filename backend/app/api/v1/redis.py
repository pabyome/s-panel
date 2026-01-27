from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from app.api.deps import CurrentUser
from app.services.redis_manager import RedisManager
from app.schemas.redis import RedisConfigUpdate, RedisKeyDetail

router = APIRouter()


@router.get("/status")
def get_redis_status(current_user: CurrentUser):
    \"\"\"Check Redis service status\"\"\"
    return RedisManager.get_service_status()


@router.post("/service/{action}")
def control_redis_service(action: str, current_user: CurrentUser):
    \"\"\"Start, stop, or restart Redis service\"\"\"
    if action not in ["start", "stop", "restart"]:
        raise HTTPException(status_code=400, detail="Action must be 'start', 'stop', or 'restart'")

    success, message = RedisManager.control_service(action)
    if not success:
        raise HTTPException(status_code=500, detail=message)
    return {"status": "success", "message": message}


@router.get("/config")
def get_config(current_user: CurrentUser):
    config = RedisManager.read_config()
    if "error" in config:
        # Fallback or strict? If no config file, we might just return empty or error.
        # But we want to guide user.
        return {"config": {}, "error": config["error"]}
    return {"config": config}

@router.put("/config")
def update_config(updates: RedisConfigUpdate, current_user: CurrentUser):
    # Filter None values
    data = {k: v for k, v in updates.model_dump().items() if v is not None}

    # Special handling for empty password (disable requirepass)
    # If user sends empty string for requirepass, we might want to comment it out or set empty?
    # Redis typically uses `requirepass foobared`. To disable, you often comment it out.
    # Our simple manager replaces values.

    if RedisManager.save_config(data):
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Failed to save config")

@router.get("/info")
def get_info(current_user: CurrentUser):
    return RedisManager.get_info()

@router.get("/keys")
def get_keys(current_user: CurrentUser, pattern: str = "*", count: int = 100):
    # This just returns list of strings
    return {"keys": RedisManager.scan_keys(pattern, count)}

@router.get("/keys/{key:path}") # :path allows slashes in key name
def get_key_detail(key: str, current_user: CurrentUser):
    # Decode double encoding if necessary?
    # Usually wrapper handles it.
    return RedisManager.get_key_details(key)

@router.delete("/keys/{key:path}")
def delete_key(key: str, current_user: CurrentUser):
    if RedisManager.delete_key(key):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Key not found or could not be deleted")

@router.post("/flush")
def flush_db(current_user: CurrentUser):
    if RedisManager.flush_db():
        return {"status": "flushed"}
    raise HTTPException(status_code=500, detail="Failed to flush DB")
