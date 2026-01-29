import unittest
from unittest.mock import patch, MagicMock
from app.services.postgres_manager import PostgresManager

class TestPostgresInjection(unittest.TestCase):

    @patch('app.services.postgres_manager.PostgresManager._run_command')
    def test_create_user_sql_injection(self, mock_run_command):
        mock_run_command.return_value = (False, "")
        malicious_password = "password'; DROP TABLE users; --"

        PostgresManager.create_user("testuser", malicious_password)

        args, _ = mock_run_command.call_args
        cmd_list = args[0]
        sql_arg = cmd_list[-1]

        escaped_password = malicious_password.replace("'", "''")
        self.assertIn(f"PASSWORD '{escaped_password}'", sql_arg)
        self.assertIn("'password''; DROP TABLE users; --'", sql_arg)

    @patch('app.services.postgres_manager.PostgresManager._run_command')
    def test_change_password_sql_injection(self, mock_run_command):
        mock_run_command.return_value = (False, "")
        malicious_password = "newpass'; DROP TABLE users; --"

        PostgresManager.change_password("testuser", malicious_password)

        args, _ = mock_run_command.call_args
        cmd_list = args[0]
        sql_arg = cmd_list[-1]

        escaped_password = malicious_password.replace("'", "''")
        self.assertIn(f"PASSWORD '{escaped_password}'", sql_arg)

    @patch('app.services.postgres_manager.PostgresManager._run_command')
    def test_grant_access_sql_injection(self, mock_run_command):
        mock_run_command.return_value = (True, "")
        malicious_db = 'mydb"; DROP DATABASE mydb; --'

        PostgresManager.grant_access(malicious_db, "user")

        calls = mock_run_command.call_args_list
        found_escaped = False
        for call in calls:
            args, _ = call
            cmd_list = args[0]
            if not isinstance(cmd_list, list): continue

            if "-c" in cmd_list:
                idx = cmd_list.index("-c")
                if idx + 1 < len(cmd_list):
                    sql = cmd_list[idx+1]
                    escaped_db = malicious_db.replace('"', '""')
                    expected_ident = f'"{escaped_db}"'
                    if expected_ident in sql:
                        found_escaped = True

        self.assertTrue(found_escaped, "Properly escaped identifier not found in grant_access calls")

    @patch('app.services.postgres_manager.PostgresManager._run_command')
    def test_manage_extension_sql_injection(self, mock_run_command):
        mock_run_command.return_value = (True, "")
        malicious_ext = 'pg_crypto; DROP TABLE users; --'

        PostgresManager.manage_extension("mydb", malicious_ext, "create")

        args, _ = mock_run_command.call_args
        cmd_list = args[0]
        sql_arg = cmd_list[-1]

        expected_ident = f'"{malicious_ext}"'
        self.assertIn(f"CREATE EXTENSION IF NOT EXISTS {expected_ident}", sql_arg)

    @patch('app.services.postgres_manager.PostgresManager._run_command')
    def test_normal_operations(self, mock_run_command):
        mock_run_command.return_value = (True, "")

        # Test create_user normal
        PostgresManager.create_user("normaluser", "securePass123")
        args, _ = mock_run_command.call_args
        sql = args[0][-1]
        self.assertIn("PASSWORD 'securePass123'", sql) # Normal password shouldn't be changed if no quotes

        # Test grant_access normal
        PostgresManager.grant_access("mydb", "normaluser")
        # Check last call (grant on schema)
        args, _ = mock_run_command.call_args
        sql = args[0][-1]
        self.assertIn('TO "normaluser";', sql) # User should be quoted

if __name__ == '__main__':
    unittest.main()
