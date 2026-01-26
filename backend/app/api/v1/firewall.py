from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.deps import CurrentUser
from app.schemas.firewall import FirewallRuleCreate, FirewallRuleRead
from app.services.firewall_manager import FirewallManager

router = APIRouter()

@router.get("/", response_model=List[FirewallRuleRead])
def get_rules(current_user: CurrentUser):
    return FirewallManager.get_status()

@router.post("/", response_model=bool)
def add_rule(rule: FirewallRuleCreate, current_user: CurrentUser):
    success = FirewallManager.add_rule(rule)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add rule")
    return True

@router.delete("/{rule_id}", response_model=bool)
def delete_rule(rule_id: int, current_user: CurrentUser):
    success = FirewallManager.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete rule")
    return True
