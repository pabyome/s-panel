import os
import sys
import shutil
import subprocess
from pathlib import Path

def generate_service_file():
    # Detect paths
    current_dir = Path.cwd()
    if not (current_dir / "main.py").exists():
        print("Error: Please run this script from the 'backend' directory where main.py is located.")
        return

    # User input for Port and UV Path
    default_port = 8000
    port_input = input(f"Enter Port for s-panel (default {default_port}): ").strip()
    port = port_input if port_input else default_port

    # Find UV
    uv_path = "/usr/local/bin/uv" # Default common path

    # Try to detect via `which uv`
    detected_uv = shutil.which("uv")

    if detected_uv:
        uv_path = detected_uv
    else:
        # Check internet and ask to install
        print("⚠️  'uv' not found.")
        install_uv = input("Do you want to install it now? (y/n) [y]: ").strip().lower()
        if install_uv in ["", "y", "yes"]:
             print("Downloading and installing latest 'uv'...")
             try:
                 subprocess.run("curl -LsSf https://astral.sh/uv/install.sh | sh", shell=True, check=True)
                 # Update path
                 new_uv = os.path.expanduser("~/.local/bin/uv") # Default install location
                 if os.path.exists(new_uv):
                     uv_path = new_uv
                 elif shutil.which("uv"):
                     uv_path = shutil.which("uv")
                 else:
                     print("Could not find uv after install. Please specify path manually.")
             except subprocess.CalledProcessError:
                 print("Failed to install uv automatically.")


    uv_input = input(f"Enter path to 'uv' executable (default {uv_path}): ").strip()
    if uv_input:
        uv_path = uv_input

    # Use 'uv run' to execute uvicorn
    # --host 0.0.0.0 is needed for external access (e.g. from Nginx reverse proxy)
    exec_cmd = f"{uv_path} run uvicorn main:app --host 0.0.0.0 --port {port} --workers 4"

    service_content = f"""[Unit]
Description=s-panel Backend Service
After=network.target

[Service]
User=root
WorkingDirectory={current_dir}
ExecStart={exec_cmd}
Restart=always
RestartSec=5
EnvironmentFile={current_dir}/.env
# Ensure HOME is set for uv to find its cache/tools if needed
Environment="HOME=/root"

[Install]
WantedBy=multi-user.target
"""
    output_path = "spanel.service"
    with open(output_path, "w") as f:
        f.write(service_content)

    print(f"\n✅ Generated {output_path}")
    print(f"   - Command: {exec_cmd}")
    print("\nTo install:")
    print(f"   sudo mv {output_path} /etc/systemd/system/")
    print("   sudo systemctl daemon-reload")
    print("   sudo systemctl enable spanel")
    print("   sudo systemctl start spanel")
    print("   sudo systemctl status spanel")

    print("\n🔹 NGINX CONFIGURATION SNIPPET 🔹")
    print(f"If you change the port to {port}, ensure your Nginx config proxies /api correctly:")
    print("location /api/ {")
    print(f"    proxy_pass http://127.0.0.1:{port};")
    print("    proxy_set_header Host $host;")
    print("    proxy_set_header X-Real-IP $remote_addr;")
    print("}")

if __name__ == "__main__":
    generate_service_file()
