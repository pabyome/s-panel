from unittest.mock import patch
from app.services.firewall_manager import FirewallManager
from app.schemas.firewall import FirewallRuleCreate

@patch("app.services.firewall_manager.subprocess.run")
def test_get_status_parsing(mock_run):
    # Mock UFW output
    mock_output = """Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 80/tcp                     ALLOW IN    Anywhere
[ 2] 22/tcp                     ALLOW IN    Anywhere
"""
    mock_run.return_value.stdout = mock_output

    rules = FirewallManager.get_status()

    assert len(rules) == 2
    assert rules[0].id == 1
    assert rules[0].to_port == "80/tcp"
    assert rules[0].action == "ALLOW"

@patch("app.services.firewall_manager.subprocess.run")
def test_add_rule(mock_run):
    mock_run.return_value.stdout = "Rule added"
    rule = FirewallRuleCreate(port=8080, protocol="tcp", action="allow")

    success = FirewallManager.add_rule(rule)

    assert success is True
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "ufw" in args
    assert "allow" in args
    assert "8080/tcp" in args
