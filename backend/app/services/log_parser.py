import re
from collections import defaultdict
from datetime import datetime
import os

class LogParser:
    @staticmethod
    def get_traffic_stats(log_path: str) -> dict:
        """
        Parses Nginx access logs to get daily traffic statistics.
        Returns a dictionary with labels (dates), requests (counts), and unique_visitors (counts).
        """
        if not os.path.exists(log_path):
            return {"labels": [], "requests": [], "unique_visitors": []}

        # Regex for standard Nginx combined log format
        # 127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 ...
        # Group 1: IP, Group 2: Timestamp
        log_pattern = re.compile(r'^(\S+) - - \[(\d{2}/[A-Za-z]{3}/\d{4}):\d{2}:\d{2}:\d{2} [+\-]\d{4}\]')

        daily_requests = defaultdict(int)
        daily_visitors = defaultdict(set)

        try:
            with open(log_path, 'r', errors='ignore') as f:
                for line in f:
                    match = log_pattern.search(line)
                    if match:
                        ip = match.group(1)
                        date_str = match.group(2) # 10/Oct/2023

                        try:
                            dt = datetime.strptime(date_str, '%d/%b/%Y')
                            date_key = dt.strftime('%Y-%m-%d')

                            daily_requests[date_key] += 1
                            daily_visitors[date_key].add(ip)
                        except ValueError:
                            continue
        except Exception:
            return {"labels": [], "requests": [], "unique_visitors": []}

        # Sort by date
        sorted_dates = sorted(daily_requests.keys())

        return {
            "labels": sorted_dates,
            "requests": [daily_requests[d] for d in sorted_dates],
            "unique_visitors": [len(daily_visitors[d]) for d in sorted_dates]
        }
