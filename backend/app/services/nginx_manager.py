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
            print(f"Command failed: {e}")
            return False

    @classmethod
    def generate_config(cls, domain: str, port: int) -> str:
        # Extra safety: Ensure domain has no newlines to prevent config injection
        if "\n" in domain or "\r" in domain:
            raise ValueError("Invalid domain: contains newline characters")

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
    def create_site(cls, domain: str, port: int) -> bool:
        config_content = cls.generate_config(domain, port)
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
        if cls._run_command(["nginx", "-t"]):
            return cls._run_command(["nginx", "-s", "reload"])
        return False

    @staticmethod
    def secure_site(domain: str, email: str) -> bool:
        # certbot --nginx -d domain.com --non-interactive --agree-tos -m email
        cmd = [
            "certbot", "--nginx",
            "-d", domain,
            "--non-interactive",
            "--agree-tos",
            "-m", email
        ]
        return NginxManager._run_command(cmd)
