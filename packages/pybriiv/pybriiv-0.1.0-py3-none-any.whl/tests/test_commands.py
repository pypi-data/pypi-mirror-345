"""Tests for the pybriiv.commands module."""

import unittest
from pybriiv import BriivCommands


class TestBriivCommands(unittest.TestCase):
    """Test the BriivCommands class."""

    def test_create_command(self):
        """Test create_command method."""
        cmd = BriivCommands.create_command("TEST123", "test_command", value=42)
        self.assertEqual(cmd["serial_number"], "TEST123")
        self.assertEqual(cmd["command"], "test_command")
        self.assertEqual(cmd["value"], 42)

    def test_power_command(self):
        """Test power_command method."""
        # Power on
        cmd_on = BriivCommands.power_command("TEST123", True)
        self.assertEqual(cmd_on["serial_number"], "TEST123")
        self.assertEqual(cmd_on["command"], "power")
        self.assertEqual(cmd_on["power"], 1)

        # Power off
        cmd_off = BriivCommands.power_command("TEST123", False)
        self.assertEqual(cmd_off["power"], 0)

    def test_fan_speed_command(self):
        """Test fan_speed_command method."""
        cmd = BriivCommands.fan_speed_command("TEST123", 75)
        self.assertEqual(cmd["serial_number"], "TEST123")
        self.assertEqual(cmd["command"], "fan_speed")
        self.assertEqual(cmd["fan_speed"], 75)

    def test_boost_command(self):
        """Test boost_command method."""
        # Boost on
        cmd_on = BriivCommands.boost_command("TEST123", True)
        self.assertEqual(cmd_on["serial_number"], "TEST123")
        self.assertEqual(cmd_on["command"], "boost")
        self.assertEqual(cmd_on["boost"], 1)

        # Boost off
        cmd_off = BriivCommands.boost_command("TEST123", False)
        self.assertEqual(cmd_off["boost"], 0)


if __name__ == "__main__":
    unittest.main()
