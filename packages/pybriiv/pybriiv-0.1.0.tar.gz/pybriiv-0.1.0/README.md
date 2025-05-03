# PyBriiv

A Python library for communicating with Briiv Air Purifier devices.

## Installation

```bash
pip install pybriiv
```

## Usage

```python
import asyncio
from pybriiv import BriivAPI

async def main():
    # Discover devices
    devices = await BriivAPI.discover(timeout=15)
    print(f"Found {len(devices)} devices: {devices}")
    
    # Connect to a specific device
    api = BriivAPI(host="192.168.1.123", port=3334, serial_number="BRIIV12345")
    
    # Start listening for updates
    await api.start_listening(asyncio.get_event_loop())
    
    # Control the device
    await api.set_power(True)
    await api.set_fan_speed(50)
    await api.set_boost(True)
    
    # Clean up
    await api.stop_listening()

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

* Device discovery via UDP
* Power control (on/off)
* Fan speed adjustment
* Boost mode control
* Real-time device state updates

## License

MIT
