from app.services.nginx_manager import NginxManager

def test_generate_nginx_config():
    domain = "example.com"
    port = 3000
    config = NginxManager.generate_config(domain, port)

    assert "server_name example.com;" in config
    assert "proxy_pass http://127.0.0.1:3000;" in config
    assert "listen 80;" in config
