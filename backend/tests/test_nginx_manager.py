from app.services.nginx_manager import NginxManager

def test_generate_nginx_config():
    domain = "example.com"
    port = 3000
    config = NginxManager.generate_config(domain, port)


    assert "server_name example.com;" in config
    assert "proxy_pass http://127.0.0.1:3000;" in config
    assert "listen 80;" in config
    assert "access_log /var/log/nginx/example.com.access.log;" in config
    assert "error_log /var/log/nginx/example.com.error.log;" in config

def test_generate_static_nginx_config():
    domain = "static.example.com"
    port = 8080
    project_path = "/var/www/static"
    config = NginxManager.generate_config(domain, port, is_static=True, project_path=project_path)

    assert "server_name static.example.com;" in config
    assert f"root {project_path};" in config
    assert "access_log /var/log/nginx/static.example.com.access.log;" in config
    assert "error_log /var/log/nginx/static.example.com.error.log;" in config

