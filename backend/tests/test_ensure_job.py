from unittest.mock import patch, MagicMock
from app.services.cron_manager import CronManager


# Mock the CronManager service to avoid messing with actual crontab
@patch("app.services.cron_manager.CronManager._get_cron")
def test_ensure_job_create_new(mock_get_cron):
    # Setup mock cron data - no existing jobs
    mock_cron = MagicMock()
    mock_cron.__iter__.return_value = []

    mock_job = MagicMock()
    mock_cron.new.return_value = mock_job
    mock_get_cron.return_value = mock_cron

    # Call ensure_job
    result = CronManager.ensure_job(
        job_id="test-job", command="echo test", schedule="* * * * *", comment="Test Job", user="testuser"
    )

    # Verify job creation
    mock_cron.new.assert_called_with(command="echo test", comment="spanel-id:test-job | Test Job")
    mock_job.setall.assert_called_with("* * * * *")
    mock_cron.write.assert_called_once()

    assert result["id"] == "test-job"
    assert result["command"] == "echo test"


@patch("app.services.cron_manager.CronManager._get_cron")
def test_ensure_job_update_existing(mock_get_cron):
    # Setup mock cron data - one existing job
    mock_cron = MagicMock()
    mock_existing_job = MagicMock()
    mock_existing_job.comment = "spanel-id:test-job | Old Comment"
    mock_existing_job.command = "echo old"
    mock_existing_job.slices = "0 * * * *"  # Different schedule

    mock_cron.__iter__.return_value = [mock_existing_job]
    mock_get_cron.return_value = mock_cron

    # Call ensure_job with new details
    result = CronManager.ensure_job(
        job_id="test-job", command="echo new", schedule="* * * * *", comment="New Comment", user="testuser"
    )

    # Verify updates
    mock_existing_job.set_command.assert_called_with("echo new")
    mock_existing_job.setall.assert_called_with("* * * * *")
    mock_existing_job.set_comment.assert_called_with("spanel-id:test-job | New Comment")
    mock_cron.write.assert_called_once()

    # ensure new wasn't called
    mock_cron.new.assert_not_called()


@patch("app.services.cron_manager.CronManager._get_cron")
def test_ensure_job_no_change(mock_get_cron):
    # Setup mock cron data - identical existing job
    mock_cron = MagicMock()
    mock_existing_job = MagicMock()
    mock_existing_job.comment = "spanel-id:test-job | Same Comment"
    mock_existing_job.command = "echo same"
    # Note: slice comparison is string-based in our impl, mock needs to match strict
    # but we cast to str(job.slices) in ensure_job.
    # Mocking slice object behavior
    mock_existing_job.slices = "* * * * *"

    mock_cron.__iter__.return_value = [mock_existing_job]
    mock_get_cron.return_value = mock_cron

    # Call ensure_job with same details
    result = CronManager.ensure_job(
        job_id="test-job", command="echo same", schedule="* * * * *", comment="Same Comment", user="testuser"
    )

    # Verify NO updates
    mock_existing_job.set_command.assert_not_called()
    mock_existing_job.setall.assert_not_called()
    mock_existing_job.set_comment.assert_not_called()
    mock_cron.write.assert_not_called()
