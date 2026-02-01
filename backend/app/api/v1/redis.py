from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.api.deps import CurrentUser
from app.services.redis_manager import RedisManager
from app.schemas.redis import RedisConfigUpdate, RedisKeyDetail, RedisUser, RedisCredentialsUpdate

router = APIRouter()


@router.get("/status")
def get_redis_status(current_user: CurrentUser):
    """Check Redis service status"""
    return RedisManager.get_service_status()


@router.get("/connection-status")
def get_connection_status(current_user: CurrentUser):
    """Check explicit connection to Redis (ping)"""
    return RedisManager.check_connection()


@router.post("/credentials")
def update_redis_credentials(creds: RedisCredentialsUpdate, current_user: CurrentUser):
    """Update Redis connection credentials"""
    # Try to connect first?
    # Actually update_credentials just saves. We should verify preferably in manager or UI.
    # The manager updates and reloads.
    if RedisManager.update_credentials(creds.host, creds.port, creds.password, creds.username):
        # Verification check
        check = RedisManager.check_connection()
        return {"status": "success", "connection": check}

    raise HTTPException(status_code=500, detail="Failed to update credentials")


@router.post("/service/{action}")
def control_redis_service(action: str, current_user: CurrentUser):
    """Start, stop, or restart Redis service"""
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
def get_keys(current_user: CurrentUser, pattern: str = "*", count: int = 100, db: Optional[int] = None):
    # This just returns list of strings
    return {"keys": RedisManager.scan_keys(pattern, count, db=db)}


@router.get("/keys/{key:path}")  # :path allows slashes in key name
def get_key_detail(key: str, current_user: CurrentUser, db: Optional[int] = None):
    # Decode double encoding if necessary?
    # Usually wrapper handles it.
    return RedisManager.get_key_details(key, db=db)


@router.delete("/keys/{key:path}")
def delete_key(key: str, current_user: CurrentUser, db: Optional[int] = None):
    if RedisManager.delete_key(key, db=db):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Key not found or could not be deleted")


@router.post("/flush")
def flush_db(current_user: CurrentUser, db: Optional[int] = None):
    if RedisManager.flush_db(db=db):
        return {"status": "flushed"}
    raise HTTPException(status_code=500, detail="Failed to flush DB")

# ACL Endpoints

@router.get("/acl/users")
def get_acl_users(current_user: CurrentUser):
    return {"users": RedisManager.get_acl_users()}

@router.get("/acl/users/{username}")
def get_acl_user_detail(username: str, current_user: CurrentUser):
    return RedisManager.get_acl_user_details(username)

@router.post("/acl/users")
def set_acl_user(user: RedisUser, current_user: CurrentUser):
    # Construct rules string
    # Start with reset to ensure clean slate? Or just append?
    # Usually "reset" is good practice if we want to enforce exactly what's sent,
    # BUT if we want to patch, we shouldn't.
    # The schemas suggest "full update".

    # 1. Base rules
    # If user provided raw 'rules', we use that combined with pass/status

    final_rules = []

    # Enabled/Disabled
    final_rules.append("on" if user.enabled else "off")

    # Password
    if user.password:
        final_rules.append(f">{user.password}")

    # Rules
    # User might provie "+@all ~*". We append it.
    if user.rules:
        final_rules.append(user.rules)

    rule_str = " ".join(final_rules)

    if RedisManager.set_acl_user(user.username, rule_str):
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Failed to set ACL user")

@router.delete("/acl/users/{username}")
def delete_acl_user(username: str, current_user: CurrentUser):
    if RedisManager.delete_acl_user(username):
        return {"status": "deleted"}
    raise HTTPException(status_code=500, detail="Failed to delete ACL user")
