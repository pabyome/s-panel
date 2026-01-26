from crontab import CronTab
import uuid
from typing import List, Dict, Optional

class CronManager:
    # We manage the ROOT crontab (or the user running the panel)

    @staticmethod
    def _get_cron() -> CronTab:
        return CronTab(user=True)

    @staticmethod
    def list_jobs() -> List[Dict[str, str]]:
        cron = CronManager._get_cron()
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
                "enabled": job.is_enabled()
            })
        return jobs

    @staticmethod
    def add_job(command: str, schedule: str, comment: str = "") -> Dict[str, str]:
        cron = CronManager._get_cron()

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
            "comment": full_comment
        }

    @staticmethod
    def delete_job(job_id: str) -> bool:
        cron = CronManager._get_cron()
        found = False
        # Iterate and remove.
        # python-crontab remove_all(comment=...) works partially but regex might be safer loop
        for job in cron:
            if job.comment and f"spanel-id:{job_id}" in job.comment:
                cron.remove(job)
                found = True
                break

        if found:
            cron.write()
            return True
        return False

    @staticmethod
    def update_job(job_id: str, command: str = None, schedule: str = None) -> bool:
        cron = CronManager._get_cron()
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
