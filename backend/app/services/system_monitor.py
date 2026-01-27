import psutil
import os
from typing import Dict, Any

class SystemMonitor:
    @staticmethod
    def get_cpu_stats() -> Dict[str, Any]:
        # interval=0 is non-blocking. It returns usage since the last call.
        return {
            "percent": psutil.cpu_percent(interval=0),
            "count": psutil.cpu_count(),
        }

    @staticmethod
    def get_memory_stats() -> Dict[str, Any]:
        vm = psutil.virtual_memory()
        return {
            "total": vm.total,
            "available": vm.available,
            "percent": vm.percent,
            "used": vm.used,
            "free": vm.free,
        }

    @staticmethod
    def get_disk_stats() -> Dict[str, Any]:
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }

    @staticmethod
    def get_load_average() -> Dict[str, Any]:
        try:
            # os.getloadavg() is available on Unix
            load1, load5, load15 = os.getloadavg()
            return {
                "1min": load1,
                "5min": load5,
                "15min": load15,
            }
        except AttributeError:
             # Fallback for Windows (though the user is on Mac/Linux target)
            return {"1min": 0, "5min": 0, "15min": 0}

    @classmethod
    def get_all_stats(cls) -> Dict[str, Any]:
        return {
            "cpu": cls.get_cpu_stats(),
            "memory": cls.get_memory_stats(),
            "disk": cls.get_disk_stats(),
            "load_avg": cls.get_load_average(),
        }
