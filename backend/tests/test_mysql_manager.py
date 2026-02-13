import unittest
from unittest.mock import patch, MagicMock
from app.services.mysql_manager import MysqlManager

class TestMysqlManager(unittest.TestCase):

    @patch('shutil.which')
    def test_is_installed(self, mock_which):
        mock_which.return_value = '/usr/bin/mysql'
        self.assertTrue(MysqlManager.is_installed())

        mock_which.return_value = None
        self.assertFalse(MysqlManager.is_installed())

    @patch('app.services.mysql_manager.MysqlManager._run_command')
    def test_get_version(self, mock_run):
        mock_run.return_value = (True, "mysql  Ver 8.0.36-0ubuntu0.22.04.1 for Linux on x86_64 ((Ubuntu))")
        self.assertEqual(MysqlManager.get_version(), "8.0.36")

        mock_run.return_value = (False, "Error")
        self.assertEqual(MysqlManager.get_version(), "Unknown")

    @patch('app.services.mysql_manager.MysqlManager._run_command')
    @patch('app.services.mysql_manager.MysqlManager.is_installed')
    def test_get_service_status(self, mock_installed, mock_run):
        mock_installed.return_value = True

        # Simulate active service
        mock_run.side_effect = [
            (True, "active"), # systemctl is-active
            (True, "8.0.36"), # get_version -> mysql --version
            (True, "/var/lib/mysql"), # get data dir
            (True, "0.0.0.0"), # get bind address
        ]

        status = MysqlManager.get_service_status()
        self.assertTrue(status['installed'])
        self.assertTrue(status['running'])
        self.assertEqual(status['data_dir'], "/var/lib/mysql")
        self.assertTrue(status['remote_access'])

    @patch('app.services.mysql_manager.MysqlManager._run_mysql')
    def test_list_databases(self, mock_run_mysql):
        # Mock output for sizes and databases
        mock_run_mysql.side_effect = [
            (True, "db1\t10.50\ndb2\t5.00"), # Sizes
            (True, "db1\ndb2\ninformation_schema"), # DB List
        ]

        dbs = MysqlManager.list_databases()
        self.assertEqual(len(dbs), 2)
        self.assertEqual(dbs[0]['name'], 'db1')
        self.assertEqual(dbs[0]['size'], '10.50 MB')
        self.assertEqual(dbs[1]['name'], 'db2')

    @patch('app.services.mysql_manager.MysqlManager._run_mysql')
    def test_create_database(self, mock_run_mysql):
        mock_run_mysql.return_value = (True, "")
        success, msg = MysqlManager.create_database("test_db")
        self.assertTrue(success)
        mock_run_mysql.assert_called_with("CREATE DATABASE `test_db`;")

        # Test invalid name
        success, msg = MysqlManager.create_database("invalid-name")
        self.assertFalse(success)

    @patch('app.services.mysql_manager.MysqlManager._run_mysql')
    def test_create_user(self, mock_run_mysql):
        mock_run_mysql.return_value = (True, "")

        success, msg = MysqlManager.create_user("newuser", "password")
        self.assertTrue(success)
        # Should create user for %
        args, _ = mock_run_mysql.call_args_list[0]
        self.assertIn("CREATE USER 'newuser'@'%'", args[0])

    @patch('app.services.mysql_manager.MysqlManager._run_mysql')
    def test_delete_user(self, mock_run_mysql):
        mock_run_mysql.return_value = (True, "")

        success, msg = MysqlManager.delete_user("user@%")
        self.assertTrue(success)
        mock_run_mysql.assert_called_with("DROP USER 'user'@'%';")

        # Invalid format
        success, msg = MysqlManager.delete_user("user")
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()
