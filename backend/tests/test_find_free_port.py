import socket
import pytest
from unittest.mock import patch, MagicMock
from app.services.system_monitor import SystemMonitor

def test_find_free_port_success():
    """Test that a free port is found."""
    # We mock socket.socket so that binding succeeds for a specific port
    with patch("socket.socket") as mock_socket_cls:
        mock_socket = MagicMock()
        mock_socket_cls.return_value.__enter__.return_value = mock_socket

        # Scenario: Port 3000 is free
        # Note: If the implementation uses psutil, this test might not exercise the socket code unless psutil is also mocked or fails.
        # But we are testing the optimized version which relies on socket.
        port = SystemMonitor.find_free_port(3000, 3005)
        assert port == 3000

def test_find_free_port_occupied():
    """Test skipping occupied ports."""
    # We want 3000 to fail binding (OSError), and 3001 to succeed
    with patch("socket.socket") as mock_socket_cls:
        mock_socket = MagicMock()
        mock_socket_cls.return_value.__enter__.return_value = mock_socket

        # Side effect for bind: raise OSError for 3000, succeed for 3001
        def side_effect(address):
            if address[1] == 3000:
                raise OSError("Address already in use")
            return None

        mock_socket.bind.side_effect = side_effect

        # We also need to mock psutil if the current implementation is still active and we want to ensure it doesn't interfere,
        # but for the optimized version, psutil won't be called.

        port = SystemMonitor.find_free_port(3000, 3005)
        # In the optimized version, it should try 3000, fail, then 3001, succeed.
        assert port == 3001

def test_find_free_port_none_available():
    """Test when no ports are available in range."""
    with patch("socket.socket") as mock_socket_cls:
        mock_socket = MagicMock()
        mock_socket_cls.return_value.__enter__.return_value = mock_socket

        # All binds fail
        mock_socket.bind.side_effect = OSError("Address already in use")

        port = SystemMonitor.find_free_port(3000, 3005)
        assert port is None
