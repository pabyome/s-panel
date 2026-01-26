import os
import sys
from pathlib import Path

def generate_service_file():
    # Detect paths
    current_dir = Path.cwd()
    if not (current_dir / "main.py").exists():
        print("Error: Please run this script from the 'backend' directory where main.py is located.")
        return

    # Assuming 'uv' creates venv in .venv inside backend or standard location
    venv_python = current_dir / ".venv" / "bin" / "python"
    if not venv_python.exists():
        # Fallback to system python or 'uv run' wrapper idea, but strict path is better for systemd
        # Try to find uv
        venv_python = "uv" # This might be risky if uv is not in global path for root
        # Better: ask user or assume standard install.
        # For this script, let's try to resolve sys.executable if running from venv,
        # or warn user.
        print(f"Warning: Virtualenv python not found at {venv_python}. Using 'uv run' in service file.")
        exec_cmd = "/usr/local/bin/uv run python main.py"
    else:
        exec_cmd = f"{venv_python} main.py"

    service_content = f"""[Unit]
Description=s-panel Backend Service
After=network.target

[Service]
User=root
WorkingDirectory={current_dir}
ExecStart={exec_cmd}
Restart=always
EnvironmentFile={current_dir}/.env

[Install]
WantedBy=multi-user.target
"""

    output_path = "spanel.service"
    with open(output_path, "w") as f:
        f.write(service_content)

    print(f"Generated {output_path}")
    print("To install:")
    print(f"sudo mv {output_path} /etc/systemd/system/")
    print("sudo systemctl daemon-reload")
    print("sudo systemctl enable spanel")
    print("sudo systemctl start spanel")

if __name__ == "__main__":
    generate_service_file()
