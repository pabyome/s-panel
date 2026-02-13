import psutil
import os
import time
import platform
import socket
import subprocess
from typing import Dict, Any, List, Optional


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
            disk = psutil.disk_usage("/")
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
            return {"system": platform.system(), "release": platform.release(), "version": platform.version()}
        except Exception:
            return {"system": "Unknown", "release": "Unknown", "version": "Unknown"}

    @staticmethod
    def get_top_processes(limit: int = 20) -> list[Dict[str, Any]]:
        processes = []
        try:
            for proc in psutil.process_iter(
                ["pid", "name", "username", "cpu_percent", "memory_percent", "create_time"]
            ):
                try:
                    # fetch info
                    pInfo = proc.info
                    processes.append(pInfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # Sort by cpu_percent desc
            processes.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)
            return processes[:limit]
        except Exception:
            return []

    # --- Port Utilities ---

    @staticmethod
    def is_port_in_use(port: int) -> bool:
        """Check if a specific port is in use."""
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.laddr.port == port and conn.status == "LISTEN":
                    return True
            return False
        except (psutil.AccessDenied, Exception):
            # Fallback: try to bind to the port

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    return False
                except OSError:
                    return True

    @staticmethod
    def get_port_info(port: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about what's using a specific port."""
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.laddr.port == port and conn.status == "LISTEN":
                    info = {
                        "port": port,
                        "in_use": True,
                        "pid": conn.pid,
                        "status": conn.status,
                        "address": conn.laddr.ip,
                        "process_name": None,
                        "process_user": None,
                    }
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            info["process_name"] = proc.name()
                            info["process_user"] = proc.username()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    return info
            return {"port": port, "in_use": False}
        except (psutil.AccessDenied, Exception) as e:
            return {"port": port, "in_use": None, "error": str(e)}

    @staticmethod
    def get_listening_ports() -> List[Dict[str, Any]]:
        """Get all listening ports on the system."""
        ports = []
        try:
            seen_ports = set()
            for conn in psutil.net_connections(kind="inet"):
                if conn.status == "LISTEN" and conn.laddr.port not in seen_ports:
                    seen_ports.add(conn.laddr.port)
                    info = {
                        "port": conn.laddr.port,
                        "address": conn.laddr.ip,
                        "pid": conn.pid,
                        "process_name": None,
                        "process_user": None,
                    }
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            info["process_name"] = proc.name()
                            info["process_user"] = proc.username()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    ports.append(info)
            ports.sort(key=lambda x: x["port"])
            return ports
        except (psutil.AccessDenied, Exception):
            return []

    @staticmethod
    def find_free_port(start: int = 3000, end: int = 9000) -> Optional[int]:
        """Find the next available port in a range."""
        for port in range(start, end + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    return port
                except OSError:
                    continue
        return None

    @staticmethod
    def get_process_ports(pid: int) -> List[int]:
        """Get all ports that a specific process is listening on."""
        ports = []
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.pid == pid and conn.status == "LISTEN":
                    ports.append(conn.laddr.port)
            return sorted(ports)
        except (psutil.AccessDenied, Exception):
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
            "os_info": cls.get_os_info(),
        }

    @staticmethod
    def clear_system_memory() -> bool:
        """Clear system memory (page cache, dentries, and inodes)."""
        try:
            # Sync to ensure data is written to disk
            subprocess.run("sync", shell=True, check=True)
            # Drop caches
            # Note: This requires root privileges
            subprocess.run("echo 3 > /proc/sys/vm/drop_caches", shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False
