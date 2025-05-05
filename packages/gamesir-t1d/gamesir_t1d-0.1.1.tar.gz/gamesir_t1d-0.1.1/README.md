<p align="center">
  <img src="https://github.com/user-attachments/assets/9b71a95f-e17d-4606-841e-fb90a1f603aa" alt="GameSir T1d Pygame Wrapper" width="300" />
</p>

# GameSir T1d Pygame Wrapper

A Python package that provides a Pygame-compatible interface for the GameSir T1d controller, making it easy to use in Pygame applications. This package handles BLE connections, reconnections, and provides a convenient API.

## Features

- Bluetooth Low Energy (BLE) connection to GameSir T1d controllers
- Automatic reconnection handling
- Pygame-compatible interface for easy integration
- Raw controller data access
- Mapped buttons and axes with proper normalization
- BLE scanner tool to discover controller names

## Installation

```bash
pip install gamesir-t1d
```

Or with uv:

```bash
uv add gamesir-t1d
```

## Finding Your Controller Name

Before using the package, you need to know your controller's exact name. Each GameSir T1d controller broadcasts with a name like "Gamesir-T1d-XXXX" where XXXX is a unique identifier.

Use the included scanner tool to discover your controller:

```bash
# After installing the package
gamesir-scan
```

Make sure your controller is turned on and in pairing mode (typically hold the power button until LEDs flash rapidly). The scanner will show all discovered Bluetooth devices and try to identify GameSir controllers.

The scanner has additional options:

```bash
# Skip the "Press Enter" prompt and start scanning immediately
gamesir-scan --no-prompt

# Adjust the scan timeout (in seconds)
gamesir-scan --timeout 5.0

# Get help on available options
gamesir-scan --help
```

## Basic Usage

```python
from gamesir_t1d import GameSirT1dPygame

# Create the controller object with your controller's name
controller = GameSirT1dPygame("Gamesir-T1d-XXXX")  # Replace XXXX with your controller ID

# Initialize the controller (starts BLE connection)
controller.init()

# Read axes and buttons using the pygame-compatible interface
left_x = controller.get_axis(0)  # Range: -1.0 to 1.0
left_y = controller.get_axis(1)  # Range: -1.0 to 1.0
a_button = controller.get_button(0)  # 1 for pressed, 0 for not pressed

# Check if the controller is connected
if controller.is_connected():
    print("Controller is connected!")

# Clean up when done
controller.quit()
```

## Pygame Example

The package includes an example Pygame application that demonstrates how to use the controller:

```python
# Assuming you've installed the package with the [examples] extra
# pip install gamesir-t1d[examples]
from gamesir_t1d.examples import run

# Run the demo
run("Gamesir-T1d-XXXX")  # Replace XXXX with your controller ID
```

## License

MIT License - see the LICENSE file for details.
