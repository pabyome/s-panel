# Changes

## Modified Files
- `backend/app/services/system_monitor.py`: Added `get_disk_io_stats` and `get_net_io_stats` methods; updated `get_all_stats` to include these new metrics.
- `frontend/src/views/Monitor.vue`: Added widgets for Network I/O and Disk I/O speeds; implemented logic to calculate real-time speeds from total bytes.

## Created Files
- `backend/tests/test_monitor.py`: Added unit tests to verify the structure and error handling of the new system monitor statistics.
