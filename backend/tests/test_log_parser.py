import os
import tempfile
from app.services.log_parser import LogParser
import pytest

@pytest.fixture
def sample_log_file():
    content = """127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 612 "-" "Mozilla/5.0"
192.168.1.1 - - [10/Oct/2023:14:00:00 +0000] "GET /about HTTP/1.1" 200 123 "-" "Mozilla/5.0"
127.0.0.1 - - [10/Oct/2023:15:00:00 +0000] "GET /contact HTTP/1.1" 404 456 "-" "Mozilla/5.0"
10.0.0.1 - - [11/Oct/2023:10:00:00 +0000] "GET / HTTP/1.1" 200 789 "-" "Chrome/90"
invalid log line
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)

def test_get_traffic_stats_parsing(sample_log_file):
    stats = LogParser.get_traffic_stats(sample_log_file)

    assert stats['labels'] == ['2023-10-10', '2023-10-11']
    # 2023-10-10: 3 requests (2 from 127.0.0.1, 1 from 192.168.1.1)
    # Unique visitors: 2
    assert stats['requests'][0] == 3
    assert stats['unique_visitors'][0] == 2

    # 2023-10-11: 1 request
    # Unique visitors: 1
    assert stats['requests'][1] == 1
    assert stats['unique_visitors'][1] == 1

def test_get_traffic_stats_missing_file():
    stats = LogParser.get_traffic_stats("/non/existent/path.log")
    assert stats['labels'] == []
    assert stats['requests'] == []
    assert stats['unique_visitors'] == []

def test_get_traffic_stats_empty_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        path = f.name
    try:
        stats = LogParser.get_traffic_stats(path)
        assert stats['labels'] == []
        assert stats['requests'] == []
        assert stats['unique_visitors'] == []
    finally:
        os.unlink(path)
