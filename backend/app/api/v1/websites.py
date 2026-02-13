from fastapi import APIRouter, Depends, HTTPException
from typing import List
import os
import subprocess
import tempfile
from app.api.deps import SessionDep, CurrentUser
from app.schemas.website import WebsiteCreate, WebsiteRead, WebsiteUpdate, NginxConfigUpdate
from app.models.website import Website
from app.models.deployment import DeploymentConfig
from app.services.website_manager import WebsiteManager
from app.services.laravel_service import LaravelService

from app.services.nginx_manager import NginxManager

router = APIRouter()


@router.get("/nginx", response_model=dict)
def get_nginx_info(session: SessionDep, current_user: CurrentUser):
    status = NginxManager.get_status()
    binary_path = NginxManager.get_binary_path()
    return {
        "version": status["version"],
        "path": binary_path,
        "running": status["running"],
        "status_text": status["status_text"]
    }


@router.post("/nginx/validate")
def validate_nginx_config(config_data: NginxConfigUpdate, current_user: CurrentUser):
    """Validate nginx configuration without saving"""
    content = config_data.content
    if not content:
        raise HTTPException(status_code=400, detail="Content is required")

    # Write to temp file for validation
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(content)
            temp_path = f.name

        # Test config syntax using nginx -t with included test file
        result = subprocess.run(
            ["nginx", "-t", "-c", "/etc/nginx/nginx.conf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        os.unlink(temp_path)

        if result.returncode == 0:
            return {"valid": True, "message": "Configuration syntax is valid"}
        else:
            return {"valid": False, "message": result.stderr}
    except Exception as e:
        return {"valid": False, "message": str(e)}


@router.get("/{website_id}/config")
def get_website_config(website_id: int, session: SessionDep, current_user: CurrentUser):
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
    website_id: int, config_data: NginxConfigUpdate, session: SessionDep, current_user: CurrentUser
):
    """Update nginx config for a website with backup and revert on failure"""
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    new_content = config_data.content
    if not new_content:
        raise HTTPException(status_code=400, detail="Content is required")

    config_path = f"/etc/nginx/sites-available/{website.domain}"
    backup_path = f"{config_path}.backup"

    # 1. Backup old config
    old_content = None
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                old_content = f.read()
            with open(backup_path, "w") as f:
                f.write(old_content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to backup config: {str(e)}")

    # 2. Write new config
    try:
        with open(config_path, "w") as f:
            f.write(new_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write config: {str(e)}")

    # 3. Test config
    test_result = subprocess.run(["nginx", "-t"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if test_result.returncode != 0:
        # Revert to backup
        if old_content:
            try:
                with open(config_path, "w") as f:
                    f.write(old_content)
            except:
                pass
        return {"ok": False, "message": f"Nginx config test failed. Changes reverted.\n{test_result.stderr}"}

    # 4. Reload nginx
    if NginxManager.reload_nginx():
        # Clean up backup on success
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except:
                pass
        return {"ok": True, "message": "Config saved and Nginx reloaded successfully"}
    else:
        # Revert on reload failure
        if old_content:
            try:
                with open(config_path, "w") as f:
                    f.write(old_content)
                NginxManager.reload_nginx()
            except:
                pass
        return {"ok": False, "message": "Config test passed but failed to reload Nginx. Changes reverted."}


@router.get("/{website_id}/logs")
def get_website_logs(
    website_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    type: str = "access",  # access or error
    lines: int = 100,
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
def create_website(website: WebsiteCreate, session: SessionDep, current_user: CurrentUser):
    manager = WebsiteManager(session)
    return manager.create_website(website)


@router.get("/", response_model=List[WebsiteRead])
def read_websites(session: SessionDep, current_user: CurrentUser):
    manager = WebsiteManager(session)
    return manager.get_all_websites()


@router.get("/{website_id}", response_model=WebsiteRead)
def get_website(website_id: int, session: SessionDep, current_user: CurrentUser):
    """Get a single website by ID"""
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    return website


@router.put("/{website_id}", response_model=WebsiteRead)
def update_website(website_id: int, update_data: WebsiteUpdate, session: SessionDep, current_user: CurrentUser):
    """Update website settings (name, port, project_path, is_static). Domain cannot be changed."""
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    old_port = website.port
    old_is_static = website.is_static
    old_project_path = website.project_path

    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(website, key, value)

    # Check if we need to regenerate nginx config
    needs_nginx_update = (
        (update_data.port is not None and update_data.port != old_port)
        or (update_data.is_static is not None and update_data.is_static != old_is_static)
        or (update_data.project_path is not None and update_data.project_path != old_project_path and website.is_static)
    )

    if needs_nginx_update:
        new_config = NginxManager.generate_config(
            website.domain, website.port, is_static=website.is_static, project_path=website.project_path
        )
        config_path = f"/etc/nginx/sites-available/{website.domain}"
        try:
            with open(config_path, "w") as f:
                f.write(new_config)
            if not NginxManager.reload_nginx():
                # Revert changes in DB if nginx reload fails
                website.port = old_port
                website.is_static = old_is_static
                website.project_path = old_project_path
                session.add(website)
                session.commit()
                raise HTTPException(status_code=500, detail="Failed to reload Nginx after config change")
        except IOError as e:
            raise HTTPException(status_code=500, detail=f"Failed to update nginx config: {str(e)}")

    session.add(website)
    session.commit()
    session.refresh(website)
    return website


@router.delete("/{website_id}")
def delete_website(website_id: int, session: SessionDep, current_user: CurrentUser):
    manager = WebsiteManager(session)
    success = manager.delete_website(website_id)
    if not success:
        raise HTTPException(status_code=404, detail="Website not found")
    return {"ok": True}


@router.post("/{website_id}/ssl")
def enable_ssl(website_id: int, email: str, session: SessionDep, current_user: CurrentUser):
    manager = WebsiteManager(session)
    success = manager.enable_ssl(website_id, email)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to enable SSL. Check domains or server logs.")
    return {"ok": True}


@router.post("/{website_id}/artisan")
def run_artisan(website_id: int, command: str, session: SessionDep, current_user: CurrentUser):
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    if not website.is_laravel:
        raise HTTPException(status_code=400, detail="Not a Laravel site")
    if not website.deployment_id:
        raise HTTPException(status_code=400, detail="No deployment config linked")

    deployment = session.get(DeploymentConfig, website.deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment config not found")

    success, output = LaravelService.run_artisan(deployment, command)
    return {"success": success, "output": output}


@router.get("/{website_id}/stack")
def get_stack_status(website_id: int, session: SessionDep, current_user: CurrentUser):
    website = session.get(Website, website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    if not website.is_laravel:
        raise HTTPException(status_code=400, detail="Not a Laravel site")
    if not website.deployment_id:
        # Return empty/default status if no deployment yet
        return {"web": {"replicas": 0, "status": "unknown"}, "worker": {"replicas": 0}, "scheduler": {"replicas": 0}}

    deployment = session.get(DeploymentConfig, website.deployment_id)
    if not deployment:
         return {"web": {"replicas": 0, "status": "unknown"}, "worker": {"replicas": 0}, "scheduler": {"replicas": 0}}

    return LaravelService.get_stack_status(deployment)
