"""
BLE Scanner for GameSir T1d controllers.

This module provides a utility to scan for and identify GameSir T1d controllers
on the Bluetooth Low Energy (BLE) network.
"""

import asyncio
import sys
from bleak import BleakClient, BleakScanner

# The name our controller should broadcast as
CONTROLLER_NAME = "Gamesir-T1d"


async def main(timeout=5.0):
    """Scan for BLE devices and identify GameSir T1d controllers."""
    print("Starting BLE scan for GameSir-T1d controller...")

    # First, scan for all available BLE devices
    print(f"Scanning for BLE devices (timeout: {timeout}s)...")
    devices = await BleakScanner.discover(timeout=timeout)

    # Print all found devices to help with debugging
    print(f"Found {len(devices)} Bluetooth devices:")
    for i, device in enumerate(devices):
        print(f"{i+1}. Name: {device.name}, Address: {device.address}")

    # Try to find our controller and any other potential candidates
    target_device = None
    potential_controllers = []
    
    for device in devices:
        if device.name and CONTROLLER_NAME.lower() in device.name.lower():
            potential_controllers.append(device)
            if not target_device:  # Keep the first match as our primary target
                target_device = device
                print(f"Found controller: {device.name}, Address: {device.address}")
    
    # Show other potential controllers that might be relevant
    if len(potential_controllers) > 1:
        print("\nAll potential controllers found:")
        for i, device in enumerate(potential_controllers):
            print(f"  {i+1}. {device.name} ({device.address})")
    
    # Also list any devices that might be game controllers but don't match the name pattern
    other_controllers = []
    keywords = ["controller", "gamepad", "joystick", "game", "pad"]
    for device in devices:
        if device not in potential_controllers and device.name:
            for keyword in keywords:
                if keyword.lower() in device.name.lower():
                    other_controllers.append(device)
                    break
    
    if other_controllers:
        print("\nOther possible controllers found:")
        for i, device in enumerate(other_controllers):
            print(f"  {i+1}. {device.name} ({device.address})")
            
    if not target_device:
        print(f"\nNo device found with name containing '{CONTROLLER_NAME}'")
        print("Is the controller turned on and in pairing mode?")
        return

    # Try to connect to the controller
    print(f"Attempting to connect to {target_device.name}...")
    try:
        async with BleakClient(target_device.address, timeout=10.0) as client:
            if client.is_connected:
                print(f"Successfully connected to {target_device.name}!")

                # List available services and characteristics
                print("\nAvailable services and characteristics:")
                for service in client.services:
                    print(f"Service: {service.uuid}")
                    for char in service.characteristics:
                        print(f"  Characteristic: {char.uuid}")
                        print(f"    Properties: {char.properties}")

                # Wait a moment so we can see the connection is established
                print("\nConnection successful. Press Ctrl+C to exit...")
                await asyncio.sleep(10)
            else:
                print("Failed to connect")
    except Exception as e:
        print(f"Error connecting to device: {e}")


def run_scanner():
    """
    Entry point for the scanner tool. This function is called when the 
    user runs the 'gamesir-scan' command after installing the package.
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Scan for GameSir T1d controllers")
    parser.add_argument("--timeout", type=float, default=3.0,
                      help="Scan timeout in seconds (default: 3.0)")
    parser.add_argument("--no-prompt", action="store_true",
                      help="Start scanning immediately without prompting")
    args = parser.parse_args()
    
    # Make sure controller is in pairing mode before running this
    print("Make sure the GameSir-T1d controller is turned on and in pairing mode.")
    print("(Typically hold power button until LEDs flash rapidly)")
    
    if not args.no_prompt:
        try:
            # Only request input in interactive mode
            if sys.stdin.isatty():
                input("Press Enter to start scanning...")
            else:
                print("Starting scan automatically...")
        except (EOFError, KeyboardInterrupt):
            print("\nStarting scan automatically...")
    else:
        print("Starting scan automatically...")
    
    # Run the async main function
    try:
        asyncio.run(main(timeout=args.timeout))
        return 0
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        return 1
    except Exception as e:
        print(f"\nError during scan: {e}")
        return 1


if __name__ == "__main__":
    # Run directly as a script
    sys.exit(run_scanner())
