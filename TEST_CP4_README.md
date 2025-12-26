# CP4 Thermostat Test Application

This is a CLI test application for testing EPH Ember thermostat controls, specifically designed to test the CP4 (COMBIPACK4) device type 258 support.

## Features

The test application allows you to:
- View all zones and select one to control
- Display current temperature, target temperature, mode, and boost status
- View raw point data for debugging
- Set zone mode (AUTO/MANUAL/OFF)
- Set target temperature
- Activate/deactivate boost
- Set boost temperature
- Set advance mode (for devices that support it)

## Requirements

- Python 3.7+
- pyephember2 package installed

## Installation

1. Install the package in development mode:
```bash
cd /home/user/pyephember2
pip install -e .
```

## Usage

Run the test application:
```bash
python3 test_cp4.py
```

Or, since it's executable:
```bash
./test_cp4.py
```

## What the Application Does

1. **Login**: Prompts for your EPH Ember username (email) and password
2. **Zone Selection**: Lists all available zones with their device types
3. **Zone Information**: Displays detailed information about the selected zone:
   - Current and target temperatures
   - Current mode (AUTO/MANUAL/OFF)
   - Boost status and settings
   - Zone activity status
   - Raw point data (all indices and values)

4. **Control Menu**: Provides options to:
   - Refresh zone information
   - Change zone mode
   - Set temperatures
   - Control boost function
   - Switch between zones

## Testing CP4 Features

For a CP4 thermostat (device type 258), you should be able to:

### ✓ View Information
- Current temperature (Index 5)
- Target temperature (Index 6)
- Current mode (Index 11: 0=AUTO, 1=MANUAL, 4=OFF)
- Boost active state (Index 13: 0=Inactive, 1=Active)
- Boost end time (Index 15)

### ✓ Set Mode
- AUTO mode (schedules active)
- MANUAL mode (manual control)
- OFF mode

### ✓ Control Temperature
- Set target temperature (adjusts based on current mode)
- Set boost temperature

### ✓ Control Boost
- Activate boost with duration (1-3 hours)
- Set boost temperature
- Deactivate boost

### ⚠ Not Supported on CP4
- Advance mode (will show as not supported)

## Example Session

```
$ python3 test_cp4.py

======================================================================
EPH Ember Thermostat Test Application
CP4 (Device Type 258) and Other Thermostats
======================================================================

Enter username (email): your.email@example.com
Enter password: ********

Connecting to EPH Ember API...
✓ Connected successfully

Loading zones...
✓ Found 1 zone(s)

Available zones:

Home: My Home
  1. Living Room (Device Type: 258)

Select zone number (or 'q' to quit): 1

======================================================================
Zone: Living Room
Device Type: 258
Zone ID: 12345
======================================================================
TEMPERATURE:
  Current: 19.3°C
  Target:  20.0°C

MODE: ON

BOOST:
  Active: False

OTHER:
  Zone Active: True
  Advance Active: False
  Hot Water Device: False

RAW POINT DATA:
  Index  5: 193
  Index  6: 200
  Index 11: 1
  Index 13: 0
  ...
======================================================================

CONTROL MENU
...
```

## Troubleshooting

### Connection Issues
- Verify your username and password are correct
- Check your internet connection
- Ensure the EPH Ember service is accessible

### No Zones Found
- Verify your account has zones configured in the EPH Ember app
- Try refreshing the app or waiting a moment for the API to sync

### Command Fails
- The application will display error messages
- Check the raw point data to see current values
- Some operations may take a few seconds to reflect in the API
- Try refreshing (option 1) to see updated values

## Notes

- Changes may take a few seconds to appear in the API
- Always refresh before checking if a command worked
- The raw point data section is useful for debugging
- Device type 258 (CP4) follows similar patterns to device type 773

## Support

For issues with the pyephember2 library, visit:
https://github.com/curtistarr/pyephember2
