from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.deps import CurrentUser
from app.schemas.firewall import FirewallRuleCreate, FirewallRuleRead
from app.services.firewall_manager import FirewallManager

router = APIRouter()


@router.get("/status")
def get_ufw_status(current_user: CurrentUser):
    """Check if UFW is active"""
    return FirewallManager.get_ufw_status()


@router.get("/", response_model=List[FirewallRuleRead])
def get_rules(current_user: CurrentUser):
    return FirewallManager.get_status()


@router.post("/")
def add_rule(rule: FirewallRuleCreate, current_user: CurrentUser):
    success, message = FirewallManager.add_rule(rule)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, current_user: CurrentUser):
    success, message = FirewallManager.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}
