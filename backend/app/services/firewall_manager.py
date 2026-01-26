import subprocess
import re
from typing import List
from app.schemas.firewall import FirewallRuleRead, FirewallRuleCreate

class FirewallManager:
    @staticmethod
    def _run_command(command: list[str]) -> str:
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Firewall command failed: {e}")
            return ""

    @classmethod
    def get_status(cls) -> List[FirewallRuleRead]:
        # ufw status numbered output parsing
        # Example:
        # Status: active
        #      To                         Action      From
        #      --                         ------      ----
        # [ 1] 22/tcp                     ALLOW IN    Anywhere
        # [ 2] 3000                       ALLOW IN    Anywhere

        output = cls._run_command(["ufw", "status", "numbered"])
        rules = []
        if not output or "Status: inactive" in output:
            return []

        lines = output.splitlines()
        for line in lines:
            # Parse line like: "[ 1] 22/tcp ALLOW IN Anywhere"
            # Regex to capture: ID, To, Action, From
            match = re.search(r"\[\s*(\d+)\]\s+(.*?)\s+(ALLOW|DENY)\s+(.*?)\s+(.*)", line)
            # Re-check regex for simple cases
            # Let's try simpler split.
            if line.startswith("["):
                parts = line.split()
                # parts example: ['[', '1]', '22/tcp', 'ALLOW', 'IN', 'Anywhere']
                # or ['[', '10]', ...]
                try:
                    # Filter out '[' and ']' or combine them
                    clean_parts = [p for p in parts if p not in ['[', ']']]
                    # Fix ID parsing if it was split like '[' '1]'
                    id_str = parts[1].replace(']', '')

                    # Basic reconstruction
                    rule_id = int(id_str)
                    to_port = parts[2]
                    action = parts[3] # ALLOW
                    from_ip = parts[5] # Anywhere (skip IN/OUT direction for MVP or assume IN)

                    rules.append(FirewallRuleRead(
                        id=rule_id,
                        to_port=to_port,
                        action=action,
                        from_ip=from_ip
                    ))
                except (IndexError, ValueError):
                    continue
        return rules

    @classmethod
    def add_rule(cls, rule: FirewallRuleCreate) -> bool:
        # ufw allow 80/tcp
        cmd = ["ufw", rule.action, f"{rule.port}/{rule.protocol}"]
        output = cls._run_command(cmd)
        return "Rule added" in output or "Skipping" in output

    @classmethod
    def delete_rule(cls, rule_id: int) -> bool:
        # ufw --force delete <id>
        # --force is needed to avoid "Proceed with operation (y|n)?" interaction
        cmd = ["ufw", "--force", "delete", str(rule_id)]
        output = cls._run_command(cmd)
        return "Rule deleted" in output
