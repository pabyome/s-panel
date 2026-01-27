import psutil
import os
import time
import platform
from typing import Dict, Any

class SystemMonitor:
    @staticmethod
    def get_cpu_stats() -> Dict[str, Any]:
        try:
            return {
                "percent": psutil.cpu_percent(interval=0),
                "count": psutil.cpu_count(),
            }
        except Exception:
            return {"percent": 0, "count": 0}

    @staticmethod
    def get_memory_stats() -> Dict[str, Any]:
        try:
            vm = psutil.virtual_memory()
            return {
                "total": vm.total,
                "available": vm.available,
                "percent": vm.percent,
                "used": vm.used,
                "free": vm.free,
            }
        except Exception:
            return {"total": 0, "available": 0, "percent": 0, "used": 0, "free": 0}

    @staticmethod
    def get_disk_stats() -> Dict[str, Any]:
        try:
            disk = psutil.disk_usage('/')
            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            }
        except Exception:
             return {"total": 0, "used": 0, "free": 0, "percent": 0}

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
        except Exception:
             # Fallback
            return {"1min": 0, "5min": 0, "15min": 0}

    @staticmethod
    def get_uptime() -> int:
        try:
            return int(time.time() - psutil.boot_time())
        except Exception:
             return 0

    @staticmethod
    def get_os_info() -> Dict[str, str]:
        try:
            return {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version()
            }
        except Exception:
            return {"system": "Unknown", "release": "Unknown", "version": "Unknown"}

    @staticmethod
    def get_top_processes(limit: int = 20) -> list[Dict[str, Any]]:
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    # fetch info
                    pInfo = proc.info
                    processes.append(pInfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # Sort by cpu_percent desc
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            return processes[:limit]
        except Exception:
            return []

    @classmethod
    def get_all_stats(cls) -> Dict[str, Any]:
        # Individual methods now handle exceptions and return defaults
        return {
            "cpu": cls.get_cpu_stats(),
            "memory": cls.get_memory_stats(),
            "disk": cls.get_disk_stats(),
            "load_avg": cls.get_load_average(),
            "uptime": cls.get_uptime(),
            "os_info": cls.get_os_info()
        }
