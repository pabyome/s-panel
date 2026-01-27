from fastapi import APIRouter, HTTPException
from typing import List
from app.api.deps import CurrentUser
from app.services.cron_manager import CronManager
from app.schemas.cron import CronJob, CronJobCreate, CronJobUpdate

router = APIRouter()

@router.get("/", response_model=List[CronJob])
def list_jobs(current_user: CurrentUser):
    # Aggregate jobs from common users
    # TODO: Make this list dynamic or configurable?
    users_to_check = ["root", "www"]
    all_jobs = []

    for u in users_to_check:
        try:
             jobs = CronManager.list_jobs(user=u)
             all_jobs.extend(jobs)
        except Exception:
             # User might not exist or no permission
             continue

    return all_jobs

@router.post("/", response_model=CronJob)
def add_job(job_in: CronJobCreate, current_user: CurrentUser):
    res = CronManager.add_job(job_in.command, job_in.schedule, job_in.comment, user=job_in.user)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@router.delete("/{job_id}")
def delete_job(job_id: str, current_user: CurrentUser, user: str = "root"):
    # Attempt delete from specified user
    if CronManager.delete_job(job_id, user=user):
        return {"status": "deleted"}

    # Fallback: if user was not specified correctly, maybe check common users?
    # But explicitly:
    raise HTTPException(status_code=404, detail=f"Job not found for user {user}")

@router.put("/{job_id}")
def update_job(job_id: str, job_in: CronJobUpdate, current_user: CurrentUser, user: str = "root"):
    if CronManager.update_job(job_id, job_in.command, job_in.schedule, user=user):
        return {"status": "updated"}
    raise HTTPException(status_code=400, detail="Failed to update job (invalid params or not found)")
