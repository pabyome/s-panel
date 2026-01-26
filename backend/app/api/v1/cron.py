from fastapi import APIRouter, HTTPException
from typing import List
from app.api.deps import CurrentUser
from app.services.cron_manager import CronManager
from app.schemas.cron import CronJob, CronJobCreate, CronJobUpdate

router = APIRouter()

@router.get("/", response_model=List[CronJob])
def list_jobs(current_user: CurrentUser):
    return CronManager.list_jobs()

@router.post("/", response_model=CronJob)
def add_job(job_in: CronJobCreate, current_user: CurrentUser):
    res = CronManager.add_job(job_in.command, job_in.schedule, job_in.comment)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@router.delete("/{job_id}")
def delete_job(job_id: str, current_user: CurrentUser):
    if CronManager.delete_job(job_id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Job not found")

@router.put("/{job_id}")
def update_job(job_id: str, job_in: CronJobUpdate, current_user: CurrentUser):
    if CronManager.update_job(job_id, job_in.command, job_in.schedule):
        return {"status": "updated"}
    raise HTTPException(status_code=400, detail="Failed to update job (invalid params or not found)")
