import xmlrpc.client
import os
import socket
from typing import List, Dict, Any, Tuple


class SupervisorManager:
    RPC_URL = "http://localhost:9001/RPC2"
    CONF_DIR = "/etc/supervisor/conf.d"

    @classmethod
    def _get_rpc(cls):
        return xmlrpc.client.ServerProxy(cls.RPC_URL)

    @classmethod
    def is_running(cls) -> Dict[str, Any]:
        """Check if supervisor is running and RPC is accessible"""
        try:
            with cls._get_rpc() as supervisor:
                state = supervisor.supervisor.getState()
                # state returns {'statecode': 1, 'statename': 'RUNNING'}
                return {
                    "running": True,
                    "state": state.get("statename", "UNKNOWN"),
                    "version": supervisor.supervisor.getSupervisorVersion(),
                    "error": None,
                }
        except socket.error as e:
            return {
                "running": False,
                "state": "STOPPED",
                "version": None,
                "error": "Supervisor is not running or XML-RPC not enabled on port 9001",
            }
        except Exception as e:
            return {"running": False, "state": "ERROR", "version": None, "error": str(e)}

    @classmethod
    def get_processes(cls) -> List[Dict[str, Any]]:
        try:
            with cls._get_rpc() as supervisor:
                processes = supervisor.supervisor.getAllProcessInfo()
                # Enrich with uptime calculation
                for proc in processes:
                    if proc.get("start", 0) > 0 and proc.get("statename") == "RUNNING":
                        import time

                        proc["uptime_seconds"] = int(time.time()) - proc["start"]
                    else:
                        proc["uptime_seconds"] = 0
                return processes
        except Exception as e:
            print(f"Supervisor RPC Error: {e}")
            return []

    @classmethod
    def start_process(cls, name: str) -> bool:
        try:
            with cls._get_rpc() as supervisor:
                return supervisor.supervisor.startProcess(name)
        except Exception:
            return False

    @classmethod
    def stop_process(cls, name: str) -> bool:
        try:
            with cls._get_rpc() as supervisor:
                return supervisor.supervisor.stopProcess(name)
        except Exception:
            return False

    @classmethod
    def restart_process(cls, name: str) -> bool:
        try:
            cls.stop_process(name)
            return cls.start_process(name)
        except Exception:
            return False

    @classmethod
    def read_log(cls, name: str, offset: int = 0, length: int = 2000) -> str:
        try:
            with cls._get_rpc() as supervisor:
                # readProcessStdoutLog(name, offset, length)
                return supervisor.supervisor.readProcessStdoutLog(name, offset, length)
        except Exception as e:
            return f"Error reading logs: {e}"

    @classmethod
    def get_config_content(cls, program_name: str) -> str:
        # Best guess mapping: program_name "myapp" -> myapp.conf
        # But user might have weird naming. For MVP, assume name.conf
        path = os.path.join(cls.CONF_DIR, f"{program_name}.conf")
        if not os.path.exists(path):
            return ""
        try:
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            return f"# Error reading config: {e}"

    @classmethod
    def save_config_content(cls, program_name: str, content: str) -> bool:
        path = os.path.join(cls.CONF_DIR, f"{program_name}.conf")
        try:
            with open(path, "w") as f:
                f.write(content)
            # Reload supervisor to apply changes
            with cls._get_rpc() as supervisor:
                supervisor.supervisor.reloadConfig()
                supervisor.supervisor.addProcessGroup(program_name)  # Ensure it's added if new
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
