from unittest.mock import patch, MagicMock
from app.services.system_monitor import SystemMonitor

def test_get_all_stats_structure():
    with patch("psutil.disk_io_counters") as mock_disk_io:
        with patch("psutil.net_io_counters") as mock_net_io:
            mock_disk_io.return_value = MagicMock(read_bytes=1000, write_bytes=2000)
            mock_net_io.return_value = MagicMock(bytes_sent=3000, bytes_recv=4000)

            stats = SystemMonitor.get_all_stats()

            assert "disk_io" in stats
            assert stats["disk_io"]["read_bytes"] == 1000
            assert stats["disk_io"]["write_bytes"] == 2000

            assert "net_io" in stats
            assert stats["net_io"]["bytes_sent"] == 3000
            assert stats["net_io"]["bytes_recv"] == 4000

def test_get_disk_io_stats_error():
    with patch("psutil.disk_io_counters", side_effect=Exception("Error")):
        stats = SystemMonitor.get_disk_io_stats()
        assert stats == {"read_bytes": 0, "write_bytes": 0}

def test_get_net_io_stats_error():
    with patch("psutil.net_io_counters", side_effect=Exception("Error")):
        stats = SystemMonitor.get_net_io_stats()
        assert stats == {"bytes_sent": 0, "bytes_recv": 0}
