from fastapi import APIRouter, HTTPException
from typing import List
from app.api.deps import CurrentUser
from app.services.supervisor_manager import SupervisorManager
from app.schemas.supervisor import SupervisorProcess, SupervisorConfigUpdate, SupervisorConfigCreate

router = APIRouter()


@router.get("/status")
def get_supervisor_status(current_user: CurrentUser):
    """Check if supervisor daemon is running"""
    return SupervisorManager.is_running()


@router.get("/processes", response_model=List[SupervisorProcess])
def get_processes(current_user: CurrentUser):
    return SupervisorManager.get_processes()


@router.post("/processes/{name}/start")
def start_process(name: str, current_user: CurrentUser):
    if not SupervisorManager.start_process(name):
        raise HTTPException(status_code=500, detail="Failed to start process")
    return {"status": "started"}


@router.post("/processes/{name}/stop")
def stop_process(name: str, current_user: CurrentUser):
    if not SupervisorManager.stop_process(name):
        raise HTTPException(status_code=500, detail="Failed to stop process")
    return {"status": "stopped"}


@router.post("/processes/{name}/restart")
def restart_process(name: str, current_user: CurrentUser):
    if not SupervisorManager.restart_process(name):
        raise HTTPException(status_code=500, detail="Failed to restart process")
    return {"status": "restarted"}


@router.get("/processes/{name}/logs")
def get_logs(current_user: CurrentUser, name: str, offset: int = 0, length: int = 2000):
    log = SupervisorManager.read_log(name, offset, length)
    return {"log": log, "offset": offset + len(log)}


@router.get("/processes/{name}/config")
def get_config(name: str, current_user: CurrentUser):
    content = SupervisorManager.get_config_content(name)
    return {"content": content}


@router.put("/processes/{name}/config")
def update_config(name: str, config: SupervisorConfigUpdate, current_user: CurrentUser):
    if not SupervisorManager.save_config_content(name, config.content):
        raise HTTPException(status_code=500, detail="Failed to save config")
    return {"status": "saved"}


@router.post("/processes")
def create_process(config: SupervisorConfigCreate, current_user: CurrentUser):
    if not SupervisorManager.create_config(config.model_dump()):
        raise HTTPException(status_code=500, detail="Failed to create process configuration")
    return {"status": "created"}

