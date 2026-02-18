import os
import subprocess
import shlex
import shutil
import re
from typing import Optional
from app.models.waf import WafConfig


class NginxManager:
    SITES_AVAILABLE = "/etc/nginx/sites-available"
    SITES_ENABLED = "/etc/nginx/sites-enabled"

    @staticmethod
    def _run_command(command: list[str]) -> bool:
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            # Don't print to stdout in production, maybe log?
            return False

    @staticmethod
    def _run_command_detailed(command: list[str]) -> tuple[bool, str]:
        """Runs a command and returns (success, output/error_message)"""
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr or str(e)
        except FileNotFoundError:
            return False, f"Command not found: {command[0]}"
        except Exception as e:
            return False, str(e)

    @classmethod
    def generate_config(cls, domain: str, port: int, is_static: bool = False, project_path: str = None, waf_config: Optional[WafConfig] = None, ssl_enabled: bool = False) -> str:
        # Extra safety: Ensure domain has no newlines to prevent config injection
        if "\n" in domain or "\r" in domain:
            raise ValueError("Invalid domain: contains newline characters")

        # SSL Configuration
        listen_block = f"listen {port};" if is_static else "listen 80;"
        redirect_block = ""

        if ssl_enabled:
            # Assuming standard Certbot paths
            listen_block = f"""listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;"""

            redirect_block = f"""
server {{
    listen 80;
    server_name {domain};
    return 301 https://$host$request_uri;
}}
"""

        # WAF Configuration Generation
        waf_zone = ""
        waf_rules = ""

        if waf_config and waf_config.enabled:
            safe_domain = re.sub(r'[^a-zA-Z0-9]', '_', domain)

            # CC Defense: Rate Limiting
            # Defined globally (or file scope), applied in server
            # 1m stores ~16k states
            waf_zone = f"limit_req_zone $binary_remote_addr zone={safe_domain}:1m rate={waf_config.cc_deny_rate}r/s;\n"

            waf_rules += f"\n    # WAF: CC Defense\n    limit_req zone={safe_domain} burst={waf_config.cc_deny_burst} nodelay;\n"

            # Scanner Blocking
            if waf_config.rule_scan_block:
                waf_rules += """
    # WAF: Block Scanners
    if ($http_user_agent ~* (netcrawler|npbot|malicious|scanner|test|python|curl|wget|nikto|sqlmap)) {
        return 403;
    }
"""

            # Hacking Blocking (Basic SQLi/XSS)
            if waf_config.rule_hacking_block:
                waf_rules += """
    # WAF: Block Hacking Attempts
    if ($query_string ~* "union.*select.*\\(") { return 403; }
    if ($query_string ~* "concat.*\\(") { return 403; }
    if ($query_string ~* "<script>") { return 403; }
    if ($query_string ~* "base64_decode\\(") { return 403; }
"""

            # Keyword Blocking
            if waf_config.rule_keywords:
                waf_rules += "\n    # WAF: Keyword Blocking"
                for keyword in waf_config.rule_keywords:
                    if not keyword: continue
                    # Escape double quotes for Nginx config string
                    safe_keyword = re.escape(keyword).replace('"', '\\"')
                    waf_rules += f"""
    if ($request_uri ~* "{safe_keyword}") {{ return 403; }}"""
                waf_rules += "\n"

        if is_static:
            # Static site configuration - serve files directly
            if not project_path:
                raise ValueError("project_path is required for static sites")
            return f"""{waf_zone}{redirect_block}
server {{
    {listen_block}
    server_name {domain};

    root {project_path};
    index index.html index.htm;

    access_log /var/log/nginx/{domain}.access.log;
    error_log /var/log/nginx/{domain}.error.log;

    # WAF Rules
{waf_rules}

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
            return f"""{waf_zone}{redirect_block}
server {{
    {listen_block}
    server_name {domain};

    access_log /var/log/nginx/{domain}.access.log;
    error_log /var/log/nginx/{domain}.error.log;

    # WAF Rules
{waf_rules}

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
    def create_site(cls, domain: str, port: int, is_static: bool = False, project_path: str = None, waf_config: Optional[WafConfig] = None, ssl_enabled: bool = False) -> bool:
        config_content = cls.generate_config(domain, port, is_static, project_path, waf_config, ssl_enabled)
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
    def secure_site(domain: str, email: str) -> tuple[bool, str]:
        # certbot --nginx -d domain.com --non-interactive --agree-tos -m email
        cmd = ["certbot", "--nginx", "-d", domain, "--non-interactive", "--agree-tos", "-m", email]
        return NginxManager._run_command_detailed(cmd)

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
