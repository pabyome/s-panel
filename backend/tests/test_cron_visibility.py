from unittest.mock import patch, MagicMock
from app.services.cron_manager import CronManager


@patch("app.services.cron_manager.CronManager._get_cron")
def test_list_jobs_parses_ssl_job(mock_get_cron):
    # Setup mock cron data
    mock_cron = MagicMock()
    mock_job = MagicMock()
    # The actual comment format used in ensure_job
    mock_job.comment = "spanel-id:ssl-auto-renew | Global SSL Auto-Renewal"
    mock_job.command = 'certbot renew --quiet --deploy-hook "nginx -s reload"'
    mock_job.slices = "0 3 * * *"
    mock_job.is_enabled.return_value = True

    mock_cron.__iter__.return_value = [mock_job]
    mock_get_cron.return_value = mock_cron

    # Call list_jobs
    jobs = CronManager.list_jobs(user="root")

    assert len(jobs) == 1
    job = jobs[0]

    # Assert ID is parsed correctly
    assert job["id"] == "ssl-auto-renew"
    assert job["comment"] == "spanel-id:ssl-auto-renew | Global SSL Auto-Renewal"
    assert job["command"] == 'certbot renew --quiet --deploy-hook "nginx -s reload"'
