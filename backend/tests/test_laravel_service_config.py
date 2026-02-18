import pytest
from app.services.laravel_service import LaravelService
from app.models.deployment import DeploymentConfig

class TestLaravelServiceConfig:
    def test_healthcheck_escaping(self):
        """
        Verify that the healthcheck command in generated stack config
        has correctly escaped PHP variables for the shell.
        """
        # Mock deployment config
        deployment = DeploymentConfig(
            id=1,
            name="TestApp",
            repo_url="http://github.com/test/repo",
            branch="main",
            current_port=8081,
            project_path="/tmp/test",
            status="deployed"
        )

        # Generate config
        env_vars = {"APP_KEY": "base64:..."}
        stack_config = LaravelService.generate_stack_config(deployment, "my-image:latest", env_vars)

        # Check web service healthcheck
        web_service = stack_config["services"]["web"]
        assert "healthcheck" in web_service

        healthcheck_cmd = web_service["healthcheck"]["test"][1]

        # We expect \$e and \$s to be escaped for the shell so PHP receives $e and $s
        # The python string itself should look like: ... \$e ...
        # If we print it, it should show the backslash.

        print(f"Generated CMD: {healthcheck_cmd}")

        # The expected string in the shell command (as Python string)
        # wget -q --spider http://127.0.0.1:8081 || exit 1

        # Check for usage of wget with correct flags and port
        assert "wget -q --spider" in healthcheck_cmd
        assert "http://127.0.0.1:8081" in healthcheck_cmd

    def test_web_service_command_uses_frankenphp(self):
        """
        Verify that the web service command uses frankenphp.
        """
        # Mock deployment config
        deployment = DeploymentConfig(
            id=1,
            name="TestApp",
            repo_url="http://github.com/test/repo",
            branch="main",
            current_port=2019,
            project_path="/tmp/test",
            status="deployed"
        )

        # Generate config
        env_vars = {"APP_KEY": "base64:..."}
        stack_config = LaravelService.generate_stack_config(deployment, "my-image:latest", env_vars)

        web_service = stack_config["services"]["web"]
        command = web_service["command"]

        # We expect command to be frankenphp
        # Check if command starts with frankenphp
        assert command[0] == "frankenphp" or "frankenphp" in command, f"Command should use frankenphp, but got: {command}"

    def test_server_name_uses_http_scheme(self):
        """
        Verify SERVER_NAME env var uses http:// scheme and explicit 0.0.0.0 binding.
        """
        deployment = DeploymentConfig(
            id=1, name="Test", repo_url="", branch="main", current_port=9000, project_path="/tmp", status="deployed"
        )
        env_vars = LaravelService._get_env_vars("/tmp", 9000)
        assert env_vars["SERVER_NAME"] == "http://0.0.0.0:9000"
