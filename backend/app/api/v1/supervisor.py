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
    success, error = SupervisorManager.start_process(name)
    if not success:
        # Check if error indicates BAD_NAME (404) or ALREADY_STARTED (400) vs System Error
        # XMLRPC faults stringify to <Fault Code: 'Msg'>
        detail = f"Failed to start process: {error}"
        status = 500
        if "BAD_NAME" in str(error):
            status = 404
        elif "ALREADY_STARTED" in str(error):
            status = 400

        raise HTTPException(status_code=status, detail=detail)
    return {"status": "started"}


@router.post("/processes/{name}/stop")
def stop_process(name: str, current_user: CurrentUser):
    success, error = SupervisorManager.stop_process(name)
    if not success:
        # Ignore NOT_RUNNING errors? Usually UI handles state.
        detail = f"Failed to stop process: {error}"
        status = 500
        if "BAD_NAME" in str(error):
            status = 404
        elif "NOT_RUNNING" in str(error):
            status = 400
        raise HTTPException(status_code=status, detail=detail)
    return {"status": "stopped"}


@router.post("/processes/{name}/restart")
def restart_process(name: str, current_user: CurrentUser):
    success, error = SupervisorManager.restart_process(name)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to restart process: {error}")
    return {"status": "restarted"}


@router.get("/processes/{name}/logs")
def get_logs(current_user: CurrentUser, name: str, offset: int = 0, length: int = 2000):
    log = SupervisorManager.read_log(name, offset, length)
    return {"log": log, "offset": offset + len(log)}


@router.post("/processes/{name}/logs/clear")
def clear_process_logs(name: str, current_user: CurrentUser):
    if not SupervisorManager.clear_log(name):
        raise HTTPException(status_code=500, detail="Failed to clear process logs")
    return {"status": "cleared"}


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


@router.delete("/processes/{name}")
def delete_process(name: str, current_user: CurrentUser):
    """Delete a supervisor process configuration"""
    # First stop the process if running
    SupervisorManager.stop_process(name)

    # Delete the config file
    if not SupervisorManager.delete_config(name):
        raise HTTPException(status_code=500, detail="Failed to delete process configuration")
    return {"status": "deleted"}
