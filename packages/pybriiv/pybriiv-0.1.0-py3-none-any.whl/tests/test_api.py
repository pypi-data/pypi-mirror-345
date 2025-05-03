"""Tests for the pybriiv.api module."""

import asyncio
import json
import socket
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from pybriiv import BriivAPI, BriivError


class TestBriivAPI(unittest.IsolatedAsyncioTestCase):
    """Test the BriivAPI class."""

    def setUp(self):
        """Set up test environment."""
        # Reset class variables between tests
        BriivAPI._instances = {}
        BriivAPI._shared_socket = None
        BriivAPI._is_listening = False
        BriivAPI._device_addresses = {}
        BriivAPI._discovered_devices = {}
        
        # Create test instance
        self.api = BriivAPI(host="192.168.1.100", port=3334, serial_number="TEST123")

    async def tearDown(self):
        """Clean up after tests."""
        await self.api.stop_listening()

    @patch('socket.socket')
    async def test_create_and_bind_socket(self, mock_socket):
        """Test creating and binding socket."""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        
        result = BriivAPI._create_and_bind_socket()
        
        # Verify socket creation and configuration
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_sock.setsockopt.assert_called()
        mock_sock.bind.assert_called()
        mock_sock.setblocking.assert_called_with(False)
        
        self.assertEqual(result, mock_sock)

    @patch.object(BriivAPI, '_create_and_bind_socket')
    @patch.object(BriivAPI, '_shared_read_loop')
    async def test_start_shared_listener(self, mock_read_loop, mock_create_socket):
        """Test starting shared listener."""
        mock_socket = MagicMock()
        mock_create_socket.return_value = mock_socket
        
        loop = asyncio.get_event_loop()
        await BriivAPI.start_shared_listener(loop)
        
        mock_create_socket.assert_called_once()
        mock_read_loop.assert_called_once()
        self.assertTrue(BriivAPI._is_listening)
        self.assertEqual(BriivAPI._shared_socket, mock_socket)

    @patch.object(BriivAPI, 'send_command')
    async def test_set_power(self, mock_send):
        """Test setting power state."""
        mock_send.return_value = None
        
        await self.api.set_power(True)
        
        # Check that send_command was called with correct power command
        mock_send.assert_called_once()
        command = mock_send.call_args[0][0]
        self.assertEqual(command["command"], "power")
        self.assertEqual(command["power"], 1)

    @patch.object(BriivAPI, 'send_command')
    async def test_set_fan_speed(self, mock_send):
        """Test setting fan speed."""
        mock_send.return_value = None
        
        await self.api.set_fan_speed(75)
        
        # Check that send_command was called with correct fan speed command
        mock_send.assert_called_once()
        command = mock_send.call_args[0][0]
        self.assertEqual(command["command"], "fan_speed")
        self.assertEqual(command["fan_speed"], 75)

    @patch.object(BriivAPI, 'send_command')
    async def test_set_boost(self, mock_send):
        """Test setting boost mode."""
        mock_send.return_value = None
        
        await self.api.set_boost(True)
        
        # Check that send_command was called with correct boost command
        mock_send.assert_called_once()
        command = mock_send.call_args[0][0]
        self.assertEqual(command["command"], "boost")
        self.assertEqual(command["boost"], 1)

    @patch.object(BriivAPI, 'start_shared_listener')
    async def test_discover(self, mock_start_listener):
        """Test device discovery."""
        # Mock the shared_listener to set discovered devices directly
        async def set_discovered_devices(*args, **kwargs):
            BriivAPI._discovered_devices = {
                "TEST123": {"host": "192.168.1.100", "serial_number": "TEST123"},
                "TEST456": {"host": "192.168.1.101", "serial_number": "TEST456"},
            }
        
        mock_start_listener.side_effect = set_discovered_devices
        
        # Run discovery
        results = await BriivAPI.discover(timeout=1)
        
        # Verify results
        self.assertEqual(len(results), 2)
        serials = [device["serial_number"] for device in results]
        self.assertIn("TEST123", serials)
        self.assertIn("TEST456", serials)

    def test_callback_registration(self):
        """Test callback registration and removal."""
        async def test_callback(data):
            pass
        
        # Register callback
        self.api.register_callback(test_callback)
        self.assertIn(test_callback, self.api.callbacks)
        
        # Register again should not duplicate
        self.api.register_callback(test_callback)
        self.assertEqual(len(self.api.callbacks), 1)
        
        # Remove callback
        self.api.remove_callback(test_callback)
        self.assertNotIn(test_callback, self.api.callbacks)


if __name__ == "__main__":
    unittest.main()
