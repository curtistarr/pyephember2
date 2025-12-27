#!/usr/bin/env python3
"""
Test application for EPH Ember thermostat control

Usage: python3 eph_ember_cli.py
"""

import sys
import os
from pyephember2 import pyephember2

# Temperature bounds (in Celsius)
MIN_TEMP = 5
MAX_TEMP = 35

# Environment file path
ENV_FILE = ".env"

def load_credentials():
    """Load credentials from .env file if it exists"""
    if os.path.exists(ENV_FILE):
        credentials = {}
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    credentials[key.strip()] = value.strip()

        username = credentials.get('EPH_USERNAME')
        password = credentials.get('EPH_PASSWORD')

        if username and password:
            return username, password

    return None, None

def save_credentials(username, password):
    """Save credentials to .env file"""
    with open(ENV_FILE, 'w') as f:
        f.write(f"# EPH Ember credentials\n")
        f.write(f"EPH_USERNAME={username}\n")
        f.write(f"EPH_PASSWORD={password}\n")
    print(f"✓ Credentials saved to {ENV_FILE}")

def print_separator():
    print("=" * 70)

def print_zone_info(zone):
    """Display detailed information about a zone"""
    print_separator()
    print(f"Zone: {pyephember2.zone_name(zone)}")
    print(f"Device Type: {zone['deviceType']}")
    print(f"Zone ID: {zone['zoneid']}")
    print_separator()

    # Temperature info
    current_temp = pyephember2.zone_current_temperature(zone)
    target_temp = pyephember2.zone_target_temperature(zone)

    print("TEMPERATURE:")
    print(f"  Current: {current_temp}°C" if current_temp is not None else "  Current: N/A")
    print(f"  Target:  {target_temp}°C" if target_temp is not None else "  Target: N/A")

    # Mode info
    mode = pyephember2.zone_mode(zone)
    print(f"\nMODE: {mode.name if mode else 'N/A'}")

    # Boost info
    boost_active = pyephember2.zone_is_boost_active(zone)
    print(f"\nBOOST:")
    print(f"  Active: {boost_active}")
    if boost_active:
        boost_hours = pyephember2.zone_boost_hours(zone)
        boost_temp = pyephember2.zone_boost_temperature(zone)
        boost_timestamp = pyephember2.zone_boost_timestamp(zone)
        print(f"  Hours: {boost_hours}")
        print(f"  Temperature: {boost_temp}°C")
        print(f"  Timestamp: {boost_timestamp}")

    # Other info
    is_active = pyephember2.zone_is_active(zone)
    advance_active = pyephember2.zone_advance_active(zone)
    is_hotwater = pyephember2.zone_is_hotwater(zone)

    print(f"\nOTHER:")
    print(f"  Zone Active: {is_active}")
    print(f"  Advance Active: {advance_active}")
    print(f"  Hot Water Device: {is_hotwater}")

    # Raw point data
    print(f"\nRAW POINT DATA:")
    for i, datum in enumerate(zone.get('pointDataList', [])):
        print(f"  Index {datum['pointIndex']:2d}: {datum['value']}")

    print_separator()

def get_zone_choice(eph, homes):
    """Let user select a zone"""
    zones = []
    zone_index = 1

    print("\nAvailable zones:")
    for home in homes:
        print(f"\nHome: {home.get('name', 'Unnamed')}")
        for zone in home['zones']:
            zone_name = pyephember2.zone_name(zone)
            device_type = zone['deviceType']
            print(f"  {zone_index}. {zone_name} (Device Type: {device_type})")
            zones.append(zone)
            zone_index += 1

    while True:
        try:
            choice = input("\nSelect zone number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(zones):
                return zones[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(zones)}")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'")

def show_menu():
    """Display the control menu"""
    print("\n" + "=" * 70)
    print("CONTROL MENU")
    print("=" * 70)
    print("1. Refresh zone information")
    print("2. Set zone mode (AUTO/MANUAL/OFF)")
    print("3. Set target temperature")
    print("4. Activate boost")
    print("5. Deactivate boost")
    print("6. Set boost temperature")
    print("7. Set advance (if supported)")
    print("8. Select different zone")
    print("q. Quit")
    print("=" * 70)

def set_zone_mode(eph, zone):
    """Set the zone mode"""
    print("\nAvailable modes:")
    print("0. AUTO")
    print("1. MANUAL/ON")
    print("2. OFF")

    mode_map = {
        '0': pyephember2.ZoneMode.AUTO,
        '1': pyephember2.ZoneMode.ON,
        '2': pyephember2.ZoneMode.OFF
    }

    choice = input("Select mode (0-2): ").strip()

    if choice in mode_map:
        mode = mode_map[choice]
        try:
            success = eph.set_zone_mode(zone['zoneid'], mode)
            if success:
                print(f"✓ Mode set to {mode.name}")
            else:
                print("✗ Failed to set mode")
        except Exception as e:
            print(f"✗ Error setting mode: {e}")
    else:
        print("Invalid choice")

def set_target_temperature(eph, zone):
    """Set the target temperature"""
    try:
        temp = float(input("Enter target temperature (°C): ").strip())
        if MIN_TEMP <= temp <= MAX_TEMP:
            success = eph.set_zone_target_temperature(zone['zoneid'], temp)
            if success:
                print(f"✓ Target temperature set to {temp}°C")
            else:
                print("✗ Failed to set target temperature")
        else:
            print(f"Temperature must be between {MIN_TEMP}°C and {MAX_TEMP}°C")
    except ValueError:
        print("Invalid temperature value")
    except Exception as e:
        print(f"✗ Error setting temperature: {e}")

def activate_boost(eph, zone):
    """Activate boost"""
    try:
        hours_str = input("Enter boost duration in hours (1-3, or leave empty for 1): ").strip()
        hours = int(hours_str) if hours_str else 1

        if not (1 <= hours <= 3):
            print("Hours must be between 1 and 3")
            return

        temp_str = input("Enter boost temperature (or leave empty to use current boost temp): ").strip()
        temp = float(temp_str) if temp_str else None

        success = eph.activate_zone_boost(zone['zoneid'], boost_temperature=temp, num_hours=hours)
        if success:
            print(f"✓ Boost activated for {hours} hour(s)" + (f" at {temp}°C" if temp else ""))
        else:
            print("✗ Failed to activate boost")
    except ValueError:
        print("Invalid input")
    except Exception as e:
        print(f"✗ Error activating boost: {e}")

def deactivate_boost(eph, zone):
    """Deactivate boost"""
    try:
        success = eph.deactivate_zone_boost(zone['zoneid'])
        if success:
            print("✓ Boost deactivated")
        else:
            print("✗ Failed to deactivate boost")
    except Exception as e:
        print(f"✗ Error deactivating boost: {e}")

def set_boost_temperature(eph, zone):
    """Set the boost temperature"""
    if not pyephember2.zone_is_boost_active(zone):
        print("⚠ Warning: Boost is not currently active. Setting boost temperature may not take effect until boost is activated.")

    try:
        temp = float(input("Enter boost temperature (°C): ").strip())
        if MIN_TEMP <= temp <= MAX_TEMP:
            success = eph.set_zone_boost_temperature(zone['zoneid'], temp)
            if success:
                print(f"✓ Boost temperature set to {temp}°C")
            else:
                print("✗ Failed to set boost temperature")
        else:
            print(f"Temperature must be between {MIN_TEMP}°C and {MAX_TEMP}°C")
    except ValueError:
        print("Invalid temperature value")
    except Exception as e:
        print(f"✗ Error setting boost temperature: {e}")

def set_advance(eph, zone):
    """Set advance state"""
    if pyephember2.zone_advance_active(zone) is None:
        print("⚠ Advance mode is not supported on this device type")
        return

    choice = input("Enable advance? (y/n): ").strip().lower()
    if choice in ['y', 'n']:
        advance = (choice == 'y')
        try:
            success = eph.set_zone_advance(zone['zoneid'], advance)
            if success:
                print(f"✓ Advance {'enabled' if advance else 'disabled'}")
            else:
                print("✗ Failed to set advance")
        except Exception as e:
            print(f"✗ Error setting advance: {e}")
    else:
        print("Invalid choice")

def main():
    """Main application loop"""
    print("=" * 70)
    print("EPH Ember Thermostat Test Application")
    print("=" * 70)

    # Try to load credentials from file
    username, password = load_credentials()

    if username and password:
        print(f"\n✓ Loaded credentials from {ENV_FILE}")
        print(f"Username: {username}")
        use_saved = input("Use these credentials? (y/n): ").strip().lower()
        if use_saved != 'y':
            username = None
            password = None

    # Get credentials from user if not loaded
    if not username or not password:
        username = input("\nEnter username (email): ").strip()
        password = input("Enter password: ").strip()

        if not username or not password:
            print("Username and password are required")
            sys.exit(1)

        # Ask if user wants to save credentials
        save_choice = input("Save credentials to .env? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_credentials(username, password)

    # Connect to API
    print("\nConnecting to EPH Ember API...")
    try:
        eph = pyephember2.EphEmber(username, password)
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        sys.exit(1)

    # Get homes and zones
    print("\nLoading zones...")
    try:
        homes = eph.get_zones()
        if not homes:
            print("No homes/zones found")
            sys.exit(1)
        print(f"✓ Found {sum(len(home['zones']) for home in homes)} zone(s)")
    except Exception as e:
        print(f"✗ Failed to load zones: {e}")
        sys.exit(1)

    # Select zone
    current_zone = get_zone_choice(eph, homes)
    if not current_zone:
        print("No zone selected. Exiting.")
        sys.exit(0)

    # Main control loop
    while True:
        # Refresh zone data
        try:
            homes = eph.get_zones()
            # Find the current zone in refreshed data
            zone_found = False
            for home in homes:
                for zone in home['zones']:
                    if zone['zoneid'] == current_zone['zoneid']:
                        current_zone = zone
                        zone_found = True
                        break
                if zone_found:
                    break

            if not zone_found:
                print(f"⚠ Warning: Zone {current_zone['zoneid']} no longer found. Please select a new zone.")
                current_zone = get_zone_choice(eph, homes)
                if not current_zone:
                    print("\nNo zone selected. Exiting.")
                    break
        except Exception as e:
            print(f"⚠ Warning: Failed to refresh zone data: {e}")

        # Display zone info
        print_zone_info(current_zone)

        # Show menu
        show_menu()

        # Get user choice
        choice = input("\nEnter choice: ").strip().lower()

        if choice == 'q':
            print("\nExiting...")
            break
        elif choice == '1':
            print("\nRefreshing...")
            continue
        elif choice == '2':
            set_zone_mode(eph, current_zone)
        elif choice == '3':
            set_target_temperature(eph, current_zone)
        elif choice == '4':
            activate_boost(eph, current_zone)
        elif choice == '5':
            deactivate_boost(eph, current_zone)
        elif choice == '6':
            set_boost_temperature(eph, current_zone)
        elif choice == '7':
            set_advance(eph, current_zone)
        elif choice == '8':
            current_zone = get_zone_choice(eph, homes)
            if not current_zone:
                print("\nNo zone selected. Exiting.")
                break
        else:
            print("Invalid choice")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
