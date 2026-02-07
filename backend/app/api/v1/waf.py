from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional

from app.api.deps import get_current_user, get_session, CurrentUser
from app.models.waf import WafConfig
from app.models.website import Website
from app.schemas.waf import WafConfigCreate, WafConfigUpdate, WafConfigRead
from app.services.nginx_manager import NginxManager

router = APIRouter()

@router.get("/{website_id}", response_model=WafConfigRead)
def get_waf_config(
    website_id: int,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    statement = select(WafConfig).where(WafConfig.website_id == website_id)
    waf_config = session.exec(statement).first()

    if not waf_config:
        # Return default disabled config if not exists
        # We need to return a WafConfigRead compatible object.
        # Since WafConfigRead requires id, but we don't have one, we can either:
        # 1. Create a default one in DB (better for consistency)
        # 2. Return a dummy ID (0)

        # Let's create a default one in DB to ensure stability
        waf_config = WafConfig(website_id=website_id, enabled=False)
        session.add(waf_config)
        session.commit()
        session.refresh(waf_config)

    return waf_config

@router.post("/{website_id}", response_model=WafConfigRead)
def update_waf_config(
    website_id: int,
    config_in: WafConfigUpdate,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    statement = select(WafConfig).where(WafConfig.website_id == website_id)
    waf_config = session.exec(statement).first()

    if not waf_config:
        # Create new
        waf_config = WafConfig(website_id=website_id, **config_in.model_dump())
        session.add(waf_config)
    else:
        # Update existing
        update_data = config_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(waf_config, key, value)
        session.add(waf_config)

    session.commit()
    session.refresh(waf_config)

    # Apply changes to Nginx
    # Note: This regenerates the config file. If SSL was manually applied via Certbot,
    # it might be lost unless handled by re-running Certbot or using templates.
    # Currently assuming standard create_site flow.
    success = NginxManager.create_site(
        domain=website.domain,
        port=website.port,
        is_static=website.is_static,
        project_path=website.project_path,
        waf_config=waf_config,
        ssl_enabled=website.ssl_enabled
    )

    if not success:
        # We committed the config but failed to apply.
        # Should we rollback? Or just warn?
        # Warning via HTTP 500 is appropriate.
        raise HTTPException(status_code=500, detail="WAF configuration saved but failed to apply to Nginx")

    return waf_config
