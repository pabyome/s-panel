import subprocess
import re
from typing import List, Tuple
from app.schemas.firewall import FirewallRuleRead, FirewallRuleCreate


class FirewallManager:
    @staticmethod
    def _run_command(command: list[str]) -> Tuple[str, str, int]:
        """Run command and return (stdout, stderr, return_code)"""
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 1
        except Exception as e:
            return "", str(e), 1

    @classmethod
    def get_ufw_status(cls) -> dict:
        """Get UFW status (active/inactive)"""
        stdout, stderr, code = cls._run_command(["ufw", "status"])
        if code != 0:
            return {"active": False, "error": stderr or "UFW not available"}

        is_active = "Status: active" in stdout
        return {"active": is_active, "error": None}

    @classmethod
    def get_status(cls) -> List[FirewallRuleRead]:
        """Get list of UFW rules"""
        stdout, stderr, code = cls._run_command(["ufw", "status", "numbered"])
        rules = []

        if code != 0 or not stdout or "Status: inactive" in stdout:
            return []

        lines = stdout.splitlines()
        for line in lines:
            # Parse line like: "[ 1] 22/tcp                     ALLOW IN    Anywhere"
            if not line.strip().startswith("["):
                continue

            # Use regex to properly parse the line
            # Format: [ 1] 22/tcp   ALLOW IN    Anywhere
            # Or: [ 2] 5432 on docker0  ALLOW       Anywhere
            match = re.match(r"\[\s*(\d+)\]\s+(.*?)\s+(ALLOW|DENY|REJECT|LIMIT)(\s+(IN|OUT|FWD))?\s+(.*)", line.strip())
            if match:
                rule_id = int(match.group(1))
                to_port = match.group(2).strip()
                action = match.group(3)
                # Group 4 is direction (e.g. " IN")
                from_ip = match.group(6).strip() or "Anywhere"

                rules.append(FirewallRuleRead(id=rule_id, to_port=to_port, action=action, from_ip=from_ip))
        return rules

    @classmethod
    def add_rule(cls, rule: FirewallRuleCreate) -> Tuple[bool, str]:
        """Add a UFW rule. Returns (success, message)"""
        # Build the command: ufw allow 80/tcp or ufw deny 80/tcp
        action = rule.action.lower()
        if action not in ["allow", "deny"]:
            return False, f"Invalid action: {action}"

        port_spec = f"{rule.port}/{rule.protocol.lower()}"
        cmd = ["ufw", action, port_spec]

        stdout, stderr, code = cls._run_command(cmd)

        # UFW returns 0 on success and outputs "Rule added" or "Skipping adding existing rule"
        if code == 0:
            if "Rule added" in stdout or "Skipping" in stdout or "Rules updated" in stdout:
                return True, stdout.strip()
            # Sometimes UFW returns 0 but with different message
            return True, stdout.strip() or "Rule processed"

        return False, stderr.strip() or stdout.strip() or "Unknown error"

    @classmethod
    def delete_rule(cls, rule_id: int) -> Tuple[bool, str]:
        """Delete a UFW rule by ID. Returns (success, message)"""
        # --force is needed to avoid "Proceed with operation (y|n)?" interaction
        cmd = ["ufw", "--force", "delete", str(rule_id)]
        stdout, stderr, code = cls._run_command(cmd)

        if code == 0 and ("deleted" in stdout.lower() or "Rule deleted" in stdout):
            return True, "Rule deleted"

        return False, stderr.strip() or stdout.strip() or "Failed to delete rule"
