PyEphEmber2
========================================

PyEphEmber2 is a Python module implementing an interface to the [EPH Control Systems Ember API](http://emberapp.ephcontrols.com/).  It allows a user to interact with their EPH heating system for the purposes of monitoring their heating system. This requires you to 
have the EPH Gateway to provide external internet access for your heating system.

Credit goes to ttroy50 who developed pyephember. This version was created as ttroy50 is no longer available to maintain pyephember. 



Example basic usage
-------------------

    >>> from pyephember2.pyephember2 import EphEmber
    >>> e = EphEmber('my@username.com', 'mypassword')
    >>> e.get_zone_temperature("MyZone")

API
---

The API is a basic HTTPS API returning data in JSON format. For more details see [here](API.md)

CLI Testing Tool
---

An interactive CLI tool (`eph_ember_cli.py`) is included for testing and controlling your EPH Ember thermostats:

    >>> python3 eph_ember_cli.py

Features:
- Interactive zone selection and control
- View current/target temperatures and device status
- Change zone modes (AUTO/MANUAL/OFF)
- Activate/deactivate boost functionality
- Set target and boost temperatures
- Credential persistence via `.env` file
- Display raw point data for debugging

The tool supports all EPH Ember thermostat types including CP4 (COMBIPACK4, device type 258).

Disclaimer: I have no connection with EPH Controls so cannot guarentee that these API calls will always be valid.
