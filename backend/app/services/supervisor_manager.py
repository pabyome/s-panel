import xmlrpc.client
import os
import socket
import psutil
from typing import List, Dict, Any, Tuple


class SupervisorManager:
    RPC_URL = "http://localhost:9001/RPC2"
    CONF_DIR = "/etc/supervisor/conf.d"

    @classmethod
    def _get_rpc(cls):
        return xmlrpc.client.ServerProxy(cls.RPC_URL)

    @classmethod
    def _get_process_ports(cls, pid: int) -> List[int]:
        """Get all ports that a specific process is listening on."""
        ports = []
        if not pid:
            return ports
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.pid == pid and conn.status == "LISTEN":
                    ports.append(conn.laddr.port)
            return sorted(ports)
        except (psutil.AccessDenied, Exception):
            return []

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
                # Enrich with uptime calculation and port detection
                for proc in processes:
                    if proc.get("start", 0) > 0 and proc.get("statename") == "RUNNING":
                        import time

                        proc["uptime_seconds"] = int(time.time()) - proc["start"]
                        # Detect listening ports for running processes
                        proc["ports"] = cls._get_process_ports(proc.get("pid"))
                    else:
                        proc["uptime_seconds"] = 0
                        proc["ports"] = []
                return processes
        except Exception as e:
            print(f"Supervisor RPC Error: {e}")
            return []

    @classmethod
    def start_process(cls, name: str) -> Tuple[bool, str]:
        try:
            with cls._get_rpc() as supervisor:
                supervisor.supervisor.startProcess(name)
                return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def stop_process(cls, name: str) -> Tuple[bool, str]:
        try:
            with cls._get_rpc() as supervisor:
                supervisor.supervisor.stopProcess(name)
                return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def restart_process(cls, name: str) -> Tuple[bool, str]:
        try:
            success_stop, err_stop = cls.stop_process(name)
            # Process might be already stopped, which is fine usually?
            # XMLRPC stopProcess throws if not running?
            # If stop fails because NOT_RUNNING (fault 70), we proceed.
            # But stop_process catches all exception.
            # Let's verify stop_process behavior.
            pass  # proceed to start

            success_start, err_start = cls.start_process(name)
            if success_start:
                return True, None
            return False, err_start
        except Exception as e:
            return False, str(e)

    @classmethod
    def read_log(cls, name: str, offset: int = 0, length: int = 2000, channel: str = "stdout") -> str:
        try:
            with cls._get_rpc() as supervisor:
                if channel == "stderr":
                    return supervisor.supervisor.readProcessStderrLog(name, offset, length)
                return supervisor.supervisor.readProcessStdoutLog(name, offset, length)
        except Exception as e:
            # Fallback: Try reading file directly if XML-RPC fails (e.g. invalid XML chars)
            try:
                with cls._get_rpc() as supervisor:
                    info = supervisor.supervisor.getProcessInfo(name)

                    logfile = info.get("stdout_logfile")
                    if channel == "stderr":
                        logfile = info.get("stderr_logfile")

                    if logfile and os.path.exists(logfile):
                        # Respect offset/length semantics roughly
                        # Supervisor offset is from beginning of file.
                        file_size = os.path.getsize(logfile)
                        if (
                            offset < 0
                        ):  # Tail mode logic if needed, but usually offset provided is positive or recursive
                            offset = max(0, file_size + offset)

                        with open(logfile, "rb") as f:
                            f.seek(offset)
                            data = f.read(length)
                            return data.decode("utf-8", errors="replace")
            except Exception as e2:
                print(f"Fallback log read failed: {e2}")

            return f"Error reading logs: {e}"

    @classmethod
    def clear_log(cls, name: str) -> bool:
        try:
            with cls._get_rpc() as supervisor:
                return supervisor.supervisor.clearProcessLogs(name)
        except Exception:
            return False

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
                try:
                    supervisor.supervisor.addProcessGroup(program_name)
                except xmlrpc.client.Fault as e:
                    if e.faultCode == 80:  # ALREADY_ADDED
                        pass
                    else:
                        print(f"Supervisor RPC Error adding group: {e}")
                        # Don't fail the request if just adding the group failed but config is saved
                        # But maybe we should return success with warning?
                        # For now, just logging it is safer than crashing 500.

            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    @classmethod
    def create_config(cls, config: Dict[str, Any]) -> bool:
        """
        Generate and save a supervisor configuration file.
        config dict matches SupervisorConfigCreate schema.
        """
        name = config["name"]

        # Basic INI generation
        content = f"""[program:{name}]
command={config['command']}
"""
        if config.get("directory"):
            content += f"directory={config['directory']}\n"

        user = config.get("user") or "root"
        content += f"user={user}\n"

        autostart = "true" if config.get("autostart") else "false"
        content += f"autostart={autostart}\n"

        autorestart = "true" if config.get("autorestart") else "false"
        content += f"autorestart={autorestart}\n"

        numprocs = config.get("numprocs", 1)
        if numprocs > 1:
            content += f"numprocs={numprocs}\n"
            content += f"process_name=%(program_name)s_%(process_num)02d\n"

        content += "stderr_logfile=/var/log/supervisor/%(program_name)s.err.log\n"
        content += "stdout_logfile=/var/log/supervisor/%(program_name)s.out.log\n"

        return cls.save_config_content(name, content)

    @classmethod
    def delete_config(cls, program_name: str) -> bool:
        """
        Delete a supervisor configuration file and remove the process.
        """
        path = os.path.join(cls.CONF_DIR, f"{program_name}.conf")

        try:
            # Remove process group from supervisor
            with cls._get_rpc() as supervisor:
                try:
                    supervisor.supervisor.stopProcessGroup(program_name)
                except:
                    pass  # May already be stopped
                try:
                    supervisor.supervisor.removeProcessGroup(program_name)
                except xmlrpc.client.Fault as e:
                    if e.faultCode != 10:  # 10 = BAD_NAME (not found)
                        print(f"Warning: Could not remove process group: {e}")

                # Reload config to pick up deletion
                supervisor.supervisor.reloadConfig()
        except Exception as e:
            print(f"Warning: RPC error during config deletion: {e}")

        # Delete the config file
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except Exception as e:
                print(f"Error deleting config file: {e}")
                return False

        return True  # File didn't exist, consider it a success
