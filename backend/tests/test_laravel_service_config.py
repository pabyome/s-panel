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
        # php -r "\$e=0; \$s=''; if(!@fsockopen('127.0.0.1', 8081, \$e, \$s, 2)) exit(1);"

        # Check for presence of escaped variables
        assert "\\$e" in healthcheck_cmd, "Variable $e should be escaped as \\$e in the shell command"
        assert "\\$s" in healthcheck_cmd, "Variable $s should be escaped as \\$s in the shell command"

        # Also verify it uses fsockopen on correct port
        assert "fsockopen('127.0.0.1', 8081" in healthcheck_cmd
