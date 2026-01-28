import os
import subprocess
import shlex
import shutil


class NginxManager:
    SITES_AVAILABLE = "/etc/nginx/sites-available"
    SITES_ENABLED = "/etc/nginx/sites-enabled"

    @staticmethod
    def _run_command(command: list[str]) -> bool:
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            # Don't print to stdout in production, maybe log?
            return False

    @classmethod
    def generate_config(cls, domain: str, port: int, is_static: bool = False, project_path: str = None) -> str:
        # Extra safety: Ensure domain has no newlines to prevent config injection
        if "\n" in domain or "\r" in domain:
            raise ValueError("Invalid domain: contains newline characters")

        if is_static:
            # Static site configuration - serve files directly
            if not project_path:
                raise ValueError("project_path is required for static sites")
            return f"""server {{
    listen {port};
    server_name {domain};

    root {project_path};
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ /index.html;
    }}

    # Cache static assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
}}
"""
        else:
            # Dynamic site configuration - proxy to local port
            return f"""
server {{
    listen 80;
    server_name {domain};

    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }}
}}
"""

    @classmethod
    def create_site(cls, domain: str, port: int, is_static: bool = False, project_path: str = None) -> bool:
        config_content = cls.generate_config(domain, port, is_static, project_path)
        file_path = os.path.join(cls.SITES_AVAILABLE, domain)

        # Security: sanitize path (though os.path.join handles basic, we assume domain is validated)
        # Note: Writing to /etc requires root.
        # In dev environment (Mac), this will likely fail if not handled or mocked.
        try:
            with open(file_path, "w") as f:
                f.write(config_content)
        except PermissionError:
            print(f"Permission denied writing to {file_path}. Are you root?")
            return False

        return cls.enable_site(domain)

    @classmethod
    def enable_site(cls, domain: str) -> bool:
        available_path = os.path.join(cls.SITES_AVAILABLE, domain)
        enabled_path = os.path.join(cls.SITES_ENABLED, domain)

        if not os.path.exists(enabled_path):
            try:
                os.symlink(available_path, enabled_path)
            except OSError as e:
                print(f"Symlink failed: {e}")
                return False

        return cls.reload_nginx()

    @classmethod
    def remove_site(cls, domain: str) -> bool:
        available_path = os.path.join(cls.SITES_AVAILABLE, domain)
        enabled_path = os.path.join(cls.SITES_ENABLED, domain)

        if os.path.exists(enabled_path):
            try:
                os.remove(enabled_path)
            except OSError as e:
                print(f"Failed to remove symlink: {e}")
                return False

        if os.path.exists(available_path):
            try:
                os.remove(available_path)
            except OSError as e:
                print(f"Failed to remove config file: {e}")
                return False

        return cls.reload_nginx()

    @classmethod
    def reload_nginx(cls) -> bool:
        # 1. Test config first
        if not cls._run_command(["nginx", "-t"]):
            return False

        # 2. Try standard reload
        if cls._run_command(["nginx", "-s", "reload"]):
            return True

        # 3. Fallback: If PID file is invalid (common in s6/docker), send HUP signal manually
        # This matches 'service nginx reload' behavior on many systems without systemd
        print("Standard reload failed, attempting signal reload...")
        return cls._run_command(["pkill", "-HUP", "nginx"])

    @staticmethod
    def get_status() -> dict:
        """
        Check actual Nginx process status.
        Returns dict with running (bool) and details (str).
        """
        # Check if process is running
        is_running = False
        try:
            # pgrep returns 0 if found, 1 if not
            subprocess.run(["pgrep", "nginx"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            is_running = True
        except subprocess.CalledProcessError:
            is_running = False

        version = NginxManager.get_version()

        return {
            "running": is_running,
            "version": version if is_running else None,
            "status_text": "Running" if is_running else "Stopped"
        }

    @staticmethod
    def secure_site(domain: str, email: str) -> bool:
        # certbot --nginx -d domain.com --non-interactive --agree-tos -m email
        cmd = ["certbot", "--nginx", "-d", domain, "--non-interactive", "--agree-tos", "-m", email]
        return NginxManager._run_command(cmd)

    @staticmethod
    def get_version() -> str:
        try:
            # nginx -v writes to stderr
            result = subprocess.run(["nginx", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # Output format: "nginx version: nginx/1.18.0 (Ubuntu)"
            output = result.stderr.strip()
            if "nginx version:" in output:
                return output.split("nginx version:")[1].strip()
            return output
        except Exception:
            return "Unknown"

    @staticmethod
    def get_binary_path() -> str:
        try:
            return shutil.which("nginx") or "Not found"
        except Exception:
            return "Unknown"
