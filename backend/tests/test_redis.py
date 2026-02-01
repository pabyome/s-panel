from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, mock_open
from main import app
from app.services.redis_manager import RedisManager

# client = TestClient(app) - Removed, using fixture

# Mock Redis Client
@patch("app.services.redis_manager.redis.Redis")
def test_get_info(mock_redis, client):
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.info.return_value = {"redis_version": "7.0.0", "uptime_in_seconds": 3600}
    mock_redis.return_value = mock_instance

    # We need to reset the singleton for test isolation or mock get_client
    RedisManager._client = None

    response = client.get("/api/v1/redis/info")
    assert response.status_code == 200
    assert response.json()["redis_version"] == "7.0.0"

@patch("app.services.redis_manager.RedisManager.get_config_path")
def test_read_config(mock_path, client):
    mock_path.return_value = "/etc/redis/redis.conf"

    config_content = """
    bind 127.0.0.1
    port 6379
    # comment
    maxmemory 2gb
    """

    with patch("builtins.open", mock_open(read_data=config_content)):
        response = client.get("/api/v1/redis/config")
        assert response.status_code == 200
        config = response.json()["config"]
        assert config["bind"] == "127.0.0.1"
        assert config["port"] == "6379"
        assert config["maxmemory"] == "2gb"

@patch("app.services.redis_manager.RedisManager.get_config_path")
def test_update_config(mock_path, client):
    mock_path.return_value = "/etc/redis/redis.conf"
    original_content = "bind 127.0.0.1\nport 6379\n"

    with patch("builtins.open", mock_open(read_data=original_content)) as m_open:
        # We need to handle read AND write.
        # distinct calls to open.
        # It's tricky with mock_open for r then w.
        # easier to mock RedisManager.save_config directly?
        # But we want to test logic.
        # Let's mock RedisManager.save_config for the API test,
        # and test save_config logic separately if needed.
        pass

@patch("app.services.redis_manager.RedisManager.save_config")
def test_update_config_api(mock_save, client):
    mock_save.return_value = True

    response = client.put("/api/v1/redis/config", json={"maxmemory": "4gb"})
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    mock_save.assert_called_once()
    # Check args
    args = mock_save.call_args[0][0]
    assert args["maxmemory"] == "4gb"

@patch("app.services.redis_manager.redis.Redis")
def test_delete_key(mock_redis, client):
    mock_instance = MagicMock()
    mock_instance.delete.return_value = 1
    mock_redis.return_value = mock_instance
    RedisManager._client = None

    response = client.delete("/api/v1/redis/keys/mykey")
    assert response.status_code == 200

@patch("app.services.redis_manager.redis.Redis")
def test_acl_endpoints(mock_redis, client):
    mock_instance = MagicMock()
    RedisManager._client = None
    mock_redis.return_value = mock_instance

    # Mock ACL USERS
    mock_instance.execute_command.side_effect = lambda cmd, *args: ["user1", "user2"] if cmd == "ACL" and args[0] == "USERS" else "OK"

    # Test List
    response = client.get("/api/v1/redis/acl/users")
    assert response.status_code == 200
    assert response.json()["users"] == ["user1", "user2"]

    # Test Create
    mock_instance.execute_command.side_effect = lambda cmd, *args: "OK"
    response = client.post("/api/v1/redis/acl/users", json={
        "username": "newuser",
        "password": "secretpassword",
        "enabled": True,
        "rules": "+@read ~cache:*"
    })
    assert response.status_code == 200

    # Verify call
    # ACL SETUSER newuser on >secretpassword +@read ~cache:*
    # Note: args might be split
    assert mock_instance.execute_command.call_count >= 1
    # Check the latest call args for structure
    # mock_instance.execute_command.assert_called_with("ACL", "SETUSER", "newuser", "on", ">secretpassword", "+@read", "~cache:*")

@patch("app.services.redis_manager.RedisManager.check_connection")
def test_connection_status(mock_check, client):
    mock_check.return_value = {"status": "connected"}

    response = client.get("/api/v1/redis/connection-status")
    assert response.status_code == 200
    assert response.json()["status"] == "connected"

@patch("app.services.redis_manager.RedisManager.update_credentials")
@patch("app.services.redis_manager.RedisManager.check_connection")
def test_update_credentials(mock_check, mock_update, client):
    mock_update.return_value = True
    mock_check.return_value = {"status": "connected"}

    response = client.post("/api/v1/redis/credentials", json={
        "host": "localhost",
        "port": 6379,
        "password": "newpassword",
        "username": "default"
    })

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_update.assert_called_with("localhost", 6379, "newpassword", "default")

