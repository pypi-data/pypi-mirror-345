"""Command definitions for Briiv devices."""

from typing import Any
import logging

LOGGER = logging.getLogger(__name__)


class BriivCommands:
    """Command definitions for Briiv devices."""

    SPEED_MAPPING = {0: 0, 1: 25, 2: 50, 3: 75, 4: 100}

    @staticmethod
    def create_command(
        serial_number: str,
        command_type: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a command dictionary with the required format."""
        cmd = {"serial_number": serial_number, "command": command_type, **kwargs}
        LOGGER.debug("Created command: %s", cmd)
        return cmd

    @staticmethod
    def power_command(
        serial_number: str,
        state: bool,
    ) -> dict[str, Any]:
        """Create power on/off command."""
        LOGGER.debug(
            "Creating power command: serial=%s, state=%s", serial_number, state
        )
        return BriivCommands.create_command(
            serial_number=serial_number, command_type="power", power=1 if state else 0
        )

    @staticmethod
    def fan_speed_command(
        serial_number: str,
        speed: int,
    ) -> dict[str, Any]:
        """Create fan speed command."""
        LOGGER.debug(
            "Creating fan speed command: serial=%s, speed=%s", serial_number, speed
        )
        return BriivCommands.create_command(
            serial_number=serial_number, command_type="fan_speed", fan_speed=speed
        )

    @staticmethod
    def boost_command(
        serial_number: str,
        boost: bool,
    ) -> dict[str, Any]:
        """Create boost mode command."""
        LOGGER.debug(
            "Creating boost command: serial=%s, boost=%s", serial_number, boost
        )
        return BriivCommands.create_command(
            serial_number=serial_number, command_type="boost", boost=1 if boost else 0
        )
