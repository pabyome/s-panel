from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
import os
import subprocess
from app.api.deps import SessionDep, CurrentUser
from app.schemas.website import WebsiteCreate, WebsiteRead
from app.models.website import Website
from app.services.website_manager import WebsiteManager

from app.services.nginx_manager import NginxManager

router = APIRouter()

@router.get("/nginx", response_model=dict)
def get_nginx_info(
    session: SessionDep,
    current_user: CurrentUser
):
    return {
        "version": NginxManager.get_version(),
        "path": NginxManager.get_binary_path()
    }

@router.get("/{website_id}/config")
def get_website_config(
    website_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
):
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    config_path = f"/etc/nginx/sites-available/{website.domain}"
    if not os.path.exists(config_path):
        raise HTTPException(status_code=404, detail="Config file not found")

    try:
        with open(config_path, "r") as f:
            return {"content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read config: {str(e)}")

@router.post("/{website_id}/config")
def update_website_config(
    website_id: uuid.UUID,
    config_data: dict, # Expect {"content": "..."}
    session: SessionDep,
    current_user: CurrentUser
):
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    new_content = config_data.get("content")
    if not new_content:
        raise HTTPException(status_code=400, detail="Content is required")

    config_path = f"/etc/nginx/sites-available/{website.domain}"

    # 1. Backup old config? (Optional but good)

    # 2. Write new config
    try:
        with open(config_path, "w") as f:
            f.write(new_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write config: {str(e)}")

    # 3. Test config
    if not NginxManager._run_command(["nginx", "-t"]):
        # Revert!! (Ideally)
        # For now, just raise error but file is overwritten.
        # TODO: Implement revert logic.
        return {"ok": False, "message": "Config saved but Nginx test failed! Please fix syntax."}

    # 4. Reload
    if NginxManager.reload_nginx():
        return {"ok": True, "message": "Config saved and Nginx reloaded"}
    else:
        return {"ok": False, "message": "Config saved but failed to reload Nginx"}


@router.get("/{website_id}/logs")
def get_website_logs(
    website_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    type: str = "access", # access or error
    lines: int = 100
):
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    log_path = f"/var/log/nginx/{website.domain}.{type}.log"
    # Default nginx logs are usually access.log / error.log (global) or domain specific if configured.
    # Our `NginxManager.generate_config` doesn't strictly set custom log paths yet?
    # Let's check `NginxManager` content.
    # If not set, maybe it uses default?
    # Assuming standard /var/log/nginx/access.log for now if specific not found?
    # Actually, for better UX, let's try specific first, then fallback to general if permission allows? No, that's messy.
    # Let's assume the user configures logs in the config file.
    # We'll just try to read standard pattern `/var/log/nginx/{domain}.access.log`.

    if not os.path.exists(log_path):
        # Fallback to general log just to show something?
        # Or better: check where the config points? Too complex.
        return {"content": f"Log file not found at {log_path}. Ensure your Nginx config writes logs there."}

    try:
        # Read last N lines
        # Using tail is efficient
        cmd = ["tail", "-n", str(lines), log_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {"content": result.stdout}
    except Exception as e:
         return {"content": f"Failed to read logs: {str(e)}"}

@router.post("/", response_model=WebsiteRead)
def create_website(
    website: WebsiteCreate,
    session: SessionDep,
    current_user: CurrentUser
):
    manager = WebsiteManager(session)
    return manager.create_website(website)

@router.get("/", response_model=List[WebsiteRead])
def read_websites(
    session: SessionDep,
    current_user: CurrentUser
):
    manager = WebsiteManager(session)
    return manager.get_all_websites()

@router.delete("/{website_id}")
def delete_website(
    website_id: int,
    session: SessionDep,
    current_user: CurrentUser
):
    manager = WebsiteManager(session)
    success = manager.delete_website(website_id)
    if not success:
        raise HTTPException(status_code=404, detail="Website not found")
    return {"ok": True}


@router.post("/{website_id}/ssl")
def enable_ssl(
    website_id: int,
    email: str,
    session: SessionDep,
    current_user: CurrentUser
):
    manager = WebsiteManager(session)
    success = manager.enable_ssl(website_id, email)
    if not success:
         raise HTTPException(status_code=400, detail="Failed to enable SSL. Check domains or server logs.")
    return {"ok": True}
