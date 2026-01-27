from crontab import CronTab
import uuid
from typing import List, Dict, Optional

class CronManager:
    # We manage the ROOT crontab (or the user running the panel)

    @staticmethod
    def _get_cron(user: str = None) -> CronTab:
        if user:
            return CronTab(user=user)
        return CronTab(user=True)

    @staticmethod
    def list_jobs(user: str = None) -> List[Dict[str, str]]:
        # If user is None, we default to current user (root if svc running as root)
        # Note: listing ALL users' cron jobs is consistent with panel admin rights?
        # For now, let's list just the requested user, defaulting to root.
        # But wait, if FE doesn't pass user, we see root's.

        cron = CronManager._get_cron(user)
        jobs = []
        for job in cron:
            # We look for our marker in comment
            comment = job.comment or ""
            job_id = None
            if comment.startswith("spanel-id:"):
                raw_id = comment.split("spanel-id:")[1]
                if "|" in raw_id:
                    job_id = raw_id.split("|")[0].strip()
                else:
                    job_id = raw_id.strip()

            jobs.append({
                "id": job_id, # Might be None if not created by us
                "command": job.command,
                "schedule": str(job.slices), # e.g. "* * * * *"
                "comment": comment,
                "enabled": job.is_enabled(),
                "user": user or "root" # approximate
            })
        return jobs

    @staticmethod
    def add_job(command: str, schedule: str, comment: str = "", user: str = "root") -> Dict[str, str]:
        cron = CronManager._get_cron(user)

        # Generate ID
        job_id = str(uuid.uuid4())
        full_comment = f"spanel-id:{job_id}"
        if comment:
             full_comment += f" | {comment}"

        job = cron.new(command=command, comment=full_comment)
        job.setall(schedule)

        if not job.is_valid():
             return {"error": "Invalid schedule"}

        cron.write()

        return {
            "id": job_id,
            "command": command,
            "schedule": schedule,
            "comment": full_comment,
            "user": user
        }

    @staticmethod
    def delete_job(job_id: str, user: str = "root") -> bool:
        # We need to know WHICH user to delete from.
        # If user is not provided, we might fail if job is on another user.
        # But for MVP, let's assume UI passes user or we check root.
        cron = CronManager._get_cron(user)
        found = False
        # Iterate and remove.
        # python-crontab remove_all(comment=...) works partially but regex might be safer loop
        for job in cron:
            if job.comment and f"spanel-id:{job_id}" in job.comment:
                cron.remove(job)
                found = True
                break

        # If not found on requested user, and user was default ("root"), maybe check others?
        # Nah, strict is better. UI should know the user.

        if found:
            cron.write()
            return True
        return False

    @staticmethod
    def update_job(job_id: str, command: str = None, schedule: str = None, user: str = "root") -> bool:
        cron = CronManager._get_cron(user)
        found = False
        for job in cron:
             if job.comment and f"spanel-id:{job_id}" in job.comment:
                if command:
                    job.set_command(command)
                if schedule:
                    job.setall(schedule)
                if not job.is_valid():
                    return False
                found = True
                break

        if found:
            cron.write()
            return True
        return False
