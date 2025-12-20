# Bug Analysis Report for pyephember2

**Analysis Date:** 2025-12-20
**Repository:** https://github.com/roberty99/pyephember2
**Version Analyzed:** 0.4.12

## Table of Contents
- [Critical Bugs](#critical-bugs)
- [High Priority Bugs](#high-priority-bugs)
- [Medium Priority Issues](#medium-priority-issues)
- [Low Priority / Code Quality Issues](#low-priority--code-quality-issues)
- [Summary](#summary)

---

## 🔴 Critical Bugs

### 1. RuntimeError Not Raised
**Severity:** CRITICAL
**File:** `pyephember2/pyephember2.py:74`
**Impact:** Function silently returns `None` instead of failing on unknown PointIndex

**Current Code:**
```python
def GetPointIndex(zone, pointIndex) -> int:
    # ... match cases ...
    case _:
        RuntimeError('Unknown PointIndex:' + pointIndex)  # ❌ Created but not raised!
```

**Fixed Code:**
```python
def GetPointIndex(zone, pointIndex) -> int:
    # ... match cases ...
    case _:
        raise RuntimeError('Unknown PointIndex:' + str(pointIndex))  # ✅ Now raises exception
```

**Why it matters:** Currently, when an unknown PointIndex is passed, the function creates a RuntimeError object but doesn't raise it, causing the function to return `None`. This can cause silent failures downstream.

---

### 2. Broken Example Files - Import Path Issues
**Severity:** CRITICAL
**Files:**
- `example.py:10`
- `messagelogger.py:11`

**Impact:** Examples cannot run - immediate ImportError

**Current Code:**
```python
from pyephember.pyephember import EphEmber  # ❌ Package name is wrong
```

**Fixed Code:**
```python
from pyephember2.pyephember2 import EphEmber  # ✅ Correct package name
```

**Why it matters:** The package name is `pyephember2`, not `pyephember`. Anyone trying to run the example scripts will immediately get an ImportError.

---

### 3. Non-existent Method Called in Example
**Severity:** CRITICAL
**File:** `example.py:38`
**Impact:** Example script fails with AttributeError

**Current Code:**
```python
# Get the full home information
print(json.dumps(t.get_home(), indent=4, sort_keys=True))  # ❌ Method doesn't exist
```

**Fixed Code:**
```python
# Get the full home information
print(json.dumps(t.get_home_details(), indent=4, sort_keys=True))  # ✅ Correct method
```

**Why it matters:** The `EphEmber` class has no `get_home()` method. Only `get_home_details()` and `get_homes()` exist.

---

## 🟠 High Priority Bugs

### 4. Missing Return Statements in zone_mode()
**Severity:** HIGH
**File:** `pyephember2/pyephember2.py:420-459`
**Impact:** Function returns `None` for unexpected mode values, causing AttributeError later

**Current Code:**
```python
def zone_mode(zone):
    """Get mode for this zone"""
    modeValue = zone_pointdata_value(zone, PointIndex.MODE)
    match modeValue:
        case 0:
            return ZoneMode.AUTO
        case 1 | 9:
            match zone["deviceType"]:
                case 773:
                    return ZoneMode.ON
                case _:
                    return ZoneMode.ALL_DAY
        case 2 | 10:
            return ZoneMode.ON
        case 3 | 4:
            return ZoneMode.OFF
    # ❌ No default return! Returns None if no match
```

**Fixed Code:**
```python
def zone_mode(zone):
    """Get mode for this zone"""
    modeValue = zone_pointdata_value(zone, PointIndex.MODE)
    match modeValue:
        case 0:
            return ZoneMode.AUTO
        case 1 | 9:
            match zone["deviceType"]:
                case 773:
                    return ZoneMode.ON
                case _:
                    return ZoneMode.ALL_DAY
        case 2 | 10:
            return ZoneMode.ON
        case 3 | 4:
            return ZoneMode.OFF
        case _:
            # ✅ Handle unexpected values
            raise ValueError(f"Unknown zone mode value: {modeValue} for device type {zone.get('deviceType')}")
```

**Why it matters:** Callers expect a `ZoneMode` enum, not `None`. This will cause errors like `AttributeError: 'NoneType' object has no attribute 'name'`.

---

### 5. Missing Return in get_zone_mode_value()
**Severity:** HIGH
**File:** `pyephember2/pyephember2.py:460-487`
**Impact:** Returns `None` instead of a valid mode value

**Current Code:**
```python
def get_zone_mode_value(zone, mode) -> int:
    if mode == ZoneMode.AUTO:
        return 0

    match zone['deviceType']:
        case 773:
            match mode:
                case ZoneMode.ON:
                    return 1
                case ZoneMode.OFF:
                    return 4
        case 514:
            match mode:
                case ZoneMode.ALL_DAY:
                    return 9
                case ZoneMode.ON:
                    return 10
                case ZoneMode.OFF:
                    return 4
        case _:
            match mode:
                case ZoneMode.ALL_DAY:
                    return 1
                case ZoneMode.ON:
                    return 2
                case ZoneMode.OFF:
                    return 3
    # ❌ No default return for unmatched cases
```

**Fixed Code:**
```python
def get_zone_mode_value(zone, mode) -> int:
    if mode == ZoneMode.AUTO:
        return 0

    device_type = zone['deviceType']

    match device_type:
        case 773:
            match mode:
                case ZoneMode.ON:
                    return 1
                case ZoneMode.OFF:
                    return 4
                case _:
                    raise ValueError(f"Unsupported mode {mode} for device type 773")
        case 514:
            match mode:
                case ZoneMode.ALL_DAY:
                    return 9
                case ZoneMode.ON:
                    return 10
                case ZoneMode.OFF:
                    return 4
                case _:
                    raise ValueError(f"Unsupported mode {mode} for device type 514")
        case _:
            match mode:
                case ZoneMode.ALL_DAY:
                    return 1
                case ZoneMode.ON:
                    return 2
                case ZoneMode.OFF:
                    return 3
                case _:
                    raise ValueError(f"Unsupported mode {mode} for device type {device_type}")
```

**Why it matters:** The function signature promises to return an `int`, but can return `None`, breaking type expectations.

---

### 6. Potential NoneType Error in boost_timestamp()
**Severity:** HIGH
**File:** `pyephember2/pyephember2.py:1046-1051`
**Impact:** Crashes if boost timestamp is None

**Current Code:**
```python
def boost_timestamp(self, zoneid):
    """Get the timestamp recorded for the boost"""
    zone = self.get_zone(zoneid)
    return datetime.datetime.fromtimestamp(zone_boost_timestamp(zone))  # ❌ Crashes if None
```

**Fixed Code:**
```python
def boost_timestamp(self, zoneid):
    """Get the timestamp recorded for the boost"""
    zone = self.get_zone(zoneid)
    timestamp = zone_boost_timestamp(zone)
    if timestamp is None:
        return None
    return datetime.datetime.fromtimestamp(timestamp)
```

**Why it matters:** If `zone_boost_timestamp()` returns `None`, `datetime.fromtimestamp(None)` raises a TypeError.

---

### 7. Potential NoneType Comparison in is_target_temperature_reached()
**Severity:** HIGH
**File:** `pyephember2/pyephember2.py:1053-1058`
**Impact:** TypeError when comparing None values

**Current Code:**
```python
def is_target_temperature_reached(self, zoneid):
    """Check if a zone temperature has reached the target temperature"""
    zone = self.get_zone(zoneid)
    return zone_current_temperature(zone) >= zone_target_temperature(zone)  # ❌ Can't compare None
```

**Fixed Code:**
```python
def is_target_temperature_reached(self, zoneid):
    """Check if a zone temperature has reached the target temperature"""
    zone = self.get_zone(zoneid)
    current_temp = zone_current_temperature(zone)
    target_temp = zone_target_temperature(zone)

    # Hot water devices (514) don't have temperature control
    if current_temp is None or target_temp is None:
        return False

    return current_temp >= target_temp
```

**Why it matters:** For device type 514 (hot water), both temperatures return `None`. Comparing `None >= None` raises a TypeError.

---

### 8. Version Conflict in setup.py
**Severity:** HIGH
**File:** `setup.py:5 and :15`
**Impact:** Confusing version management, potential packaging issues

**Current Code:**
```python
setup(
    name='pyephember2',
    version='0.4.12',  # ❌ Hardcoded version
    # ...
    use_scm_version=True,  # ❌ Git-based versioning - conflicts!
    # ...
)
```

**Fixed Code:**
```python
setup(
    name='pyephember2',
    # ✅ Remove hardcoded version, rely on SCM
    # ...
    use_scm_version=True,
    setup_requires=['setuptools_scm'],  # ✅ Add required dependency
    # ...
)
```

**Why it matters:** Having both creates confusion. `use_scm_version=True` overrides the hardcoded version anyway, making it misleading.

---

### 9. Invalid setup.py Parameter Name
**Severity:** HIGH
**File:** `setup.py:21`
**Impact:** Test dependencies not installed

**Current Code:**
```python
setup(
    # ...
    test_requires=[  # ❌ Wrong parameter name
        'tox',
        'flake8',
        'pylint'
    ]
)
```

**Fixed Code:**
```python
setup(
    # ...
    tests_require=[  # ✅ Correct parameter name (note the 's')
        'tox',
        'flake8',
        'pylint'
    ]
)
```

**Why it matters:** `test_requires` is not a valid setuptools parameter. Should be `tests_require` or use `extras_require`.

---

## 🟡 Medium Priority Issues

### 10. Function Name Collision
**Severity:** MEDIUM
**Files:** `pyephember2/pyephember2.py:190-195 and :871-875`
**Impact:** Code duplication, confusion

**Current Code:**
```python
# Module level (line 190)
def lastKey(dict):
    return list(dict.keys())[-1]

def firstKey(dict):
    return list(dict.keys())[0]

# ... later in EphEmber class (line 871) ...
class EphEmber:
    # ...
    def lastKey(dict):  # ❌ Duplicate definition!
        return list(dict.keys())[-1]

    def firstKey(dict):  # ❌ Duplicate definition!
        return list(dict.keys())[0]
```

**Fixed Code:**
```python
# Module level (line 190) - keep these
def lastKey(dict):
    return list(dict.keys())[-1]

def firstKey(dict):
    return list(dict.keys())[0]

# ... later in EphEmber class ...
class EphEmber:
    # ✅ Remove duplicate methods - they're never used anyway
    pass
```

**Additional Improvement:**
```python
# Better: Use more descriptive names and add type hints
def get_last_key(dictionary: dict):
    """Get the last key from a dictionary."""
    return list(dictionary.keys())[-1]

def get_first_key(dictionary: dict):
    """Get the first key from a dictionary."""
    return list(dictionary.keys())[0]
```

**Why it matters:** Code duplication is confusing. Also, shadowing the built-in `dict` name is bad practice.

---

### 11. Inconsistent Return Types in zone_get_running_program()
**Severity:** MEDIUM
**File:** `pyephember2/pyephember2.py:229-269`
**Impact:** Error-prone for callers, hard to use correctly

**Current Code:**
```python
def zone_get_running_program(zone):
    # Can return:
    # - dict (single program)
    # - list of 2 dicts [runningProgram, nextProgram]
    # - None

    if mode == ZoneMode.AUTO:
        # ... sometimes returns single dict ...
        return program
        # ... sometimes returns list of 2 dicts ...
        return [runningProgram, program]
    elif mode == ZoneMode.ALL_DAY:
        # ... returns list of 2 dicts ...
        return [startProgram, endProgram]

    return None
```

**Suggested Fix:**
```python
from typing import Optional, Union, List, Dict

def zone_get_running_program(zone) -> Optional[Union[Dict, List[Dict]]]:
    """
    Get the currently running program for a zone.

    Returns:
        - None if no program is active
        - dict for a single program (most device types in AUTO mode)
        - list of 2 dicts for certain device types or ALL_DAY mode
    """
    # ... implementation ...

# Better approach: Always return a consistent structure
def zone_get_running_program(zone) -> Optional[Dict]:
    """
    Get the currently running program for a zone.

    Returns a dict with 'current' and optionally 'next' keys,
    or None if no program is active.
    """
    # ... refactor to always return same structure ...
```

**Why it matters:** Inconsistent return types make the function hard to use and prone to errors. Callers must do `type()` checks.

---

### 12. Argparse Bool Type Issue
**Severity:** MEDIUM
**File:** `example.py:22`
**Impact:** --cache-home flag doesn't work as intended

**Current Code:**
```python
parser.add_argument(
    '--cache-home', type=bool, default=False,  # ❌ Doesn't work as expected
    help="cache data between API requests"
)
```

**Fixed Code:**
```python
parser.add_argument(
    '--cache-home', action='store_true',  # ✅ Correct way for boolean flags
    help="cache data between API requests"
)
```

**Why it matters:** Using `type=bool` with argparse doesn't work as expected. `bool("False")` evaluates to `True`! Any value passed makes it `True`.

---

### 13. MQTT Callback Signature Mismatch
**Severity:** MEDIUM
**File:** `messagelogger.py:90`
**Impact:** Potential callback errors with paho-mqtt VERSION2

**Current Code:**
```python
# In pyephember2.py:544
mclient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.client_id)

# In messagelogger.py:90
def on_connect(client, userdata, flags, result_code):  # ❌ Wrong signature for VERSION2
    """Simple callback on MQTT connection"""
    ts_print("Connected with result code:", result_code)
    client.subscribe(POINTDATA_TOPIC_UPLOAD, 0)
```

**Fixed Code:**
```python
def on_connect(client, userdata, flags, reason_code, properties):  # ✅ Correct VERSION2 signature
    """Simple callback on MQTT connection"""
    ts_print("Connected with reason code:", reason_code)
    client.subscribe(POINTDATA_TOPIC_UPLOAD, 0)
```

**Alternative Fix:**
```python
# Use VERSION1 if you want to keep the old signature
mclient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.client_id)
```

**Why it matters:** paho-mqtt VERSION2 expects 5 parameters, not 4. This may cause TypeErrors or warnings.

---

### 14. Unsafe Dictionary Access
**Severity:** MEDIUM
**File:** `messagelogger.py:147-149`
**Impact:** Potential KeyError if API response structure changes

**Current Code:**
```python
POINTDATA_TOPIC_UPLOAD = "/".join([
    t.get_home_details()['homes']['productId'],  # ❌ No error handling
    t.get_home_details()['homes']['uid'],
    "upload/pointdata"
])
```

**Fixed Code:**
```python
home_details = t.get_home_details()
homes = home_details.get('homes', {})
product_id = homes.get('productId')
uid = homes.get('uid')

if not product_id or not uid:
    raise RuntimeError("Unable to get product ID and UID from home details")

POINTDATA_TOPIC_UPLOAD = "/".join([product_id, uid, "upload/pointdata"])
```

**Why it matters:** Nested dictionary access without checks will raise `KeyError` if the API structure changes.

---

## 🔵 Low Priority / Code Quality Issues

### 15. Plain Text Password Storage in Memory
**Severity:** LOW
**File:** `pyephember2/pyephember2.py:1148-1152`
**Impact:** Security consideration for sensitive applications

**Current Code:**
```python
self._user = {
    'user_id': None,
    'username': username,
    'password': password  # ⚠️ Stored in plain text
}
```

**Note:** While this is common for API client libraries, consider:
- Clearing password after authentication
- Warning users in documentation
- Using environment variables instead of passing passwords directly

**Suggested Documentation:**
```python
"""
Security Note: Passwords are stored in memory during the session.
Consider using environment variables for credentials:

    username = os.environ.get('EPH_USERNAME')
    password = os.environ.get('EPH_PASSWORD')
"""
```

---

### 16. No Unit Tests
**Severity:** LOW
**Impact:** Hard to catch regressions, lower code confidence

**Current State:**
- `tox.ini` exists but only runs linters (flake8, pylint)
- No test files in repository
- `requirements_test.txt` referenced but doesn't exist

**Recommendation:**
Create a test suite using pytest:

```
tests/
  ├── __init__.py
  ├── test_zone_functions.py
  ├── test_ephember.py
  ├── test_messenger.py
  └── conftest.py
```

Example test file:
```python
# tests/test_zone_functions.py
import pytest
from pyephember2.pyephember2 import zone_mode, ZoneMode, PointIndex

def test_zone_mode_auto():
    zone = {
        'deviceType': 2,
        'pointDataList': [
            {'pointIndex': 7, 'value': 0}
        ]
    }
    assert zone_mode(zone) == ZoneMode.AUTO

def test_zone_mode_unknown_value_raises_error():
    zone = {
        'deviceType': 2,
        'pointDataList': [
            {'pointIndex': 7, 'value': 99}  # Unknown mode
        ]
    }
    with pytest.raises(ValueError):
        zone_mode(zone)
```

---

### 17. Missing Error Handling for Network Failures
**Severity:** LOW
**Files:** Multiple locations
**Impact:** Unhelpful error messages on network issues

**Example Locations:**
- `_http()` method
- `list_homes()`
- `get_home_details()`

**Current Code:**
```python
def _http(self, endpoint, *, method=requests.post, headers=None,
          send_token=False, data=None, timeout=10):
    # ...
    response = method(url, data=data, headers=headers, timeout=timeout)  # ❌ No try/except

    if response.status_code != 200:
        raise RuntimeError("{} response code".format(response.status_code))

    return response
```

**Improved Code:**
```python
import requests.exceptions

def _http(self, endpoint, *, method=requests.post, headers=None,
          send_token=False, data=None, timeout=10):
    # ...

    try:
        response = method(url, data=data, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request to {endpoint} timed out after {timeout}s")
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f"Connection error for {endpoint}: {e}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed for {endpoint}: {e}")

    if response.status_code != 200:
        raise RuntimeError(
            f"HTTP {response.status_code} response from {endpoint}"
        )

    return response
```

---

### 18. Hardcoded Magic Numbers
**Severity:** LOW
**File:** `pyephember2/pyephember2.py` (multiple locations)
**Impact:** Code readability

**Current Code:**
```python
match zone["deviceType"]:
    case 773:  # ❓ What is this?
        # ...
    case 514:  # ❓ What is this?
        # ...
    case 2 | 4:  # ❓ What are these?
        # ...
```

**Improved Code:**
```python
# At top of file
class DeviceType:
    """EPH Ember device type constants"""
    HEATING_ZONE = 2
    HOT_WATER = 4
    HOT_WATER_ALT = 514
    RADIATOR_VALVE = 773

# In code
match zone["deviceType"]:
    case DeviceType.RADIATOR_VALVE:
        # ...
    case DeviceType.HOT_WATER_ALT:
        # ...
    case DeviceType.HEATING_ZONE | DeviceType.HOT_WATER:
        # ...
```

---

### 19. GitHub Workflow Triggers on Every Push
**Severity:** LOW
**File:** `.github/workflows/publish-to-test-pypi.yml:3`
**Impact:** Wastes CI resources

**Current Code:**
```yaml
on: push  # ❌ Runs build on every push
```

**Fixed Code:**
```yaml
on:
  push:
    tags:
      - '*'  # ✅ Only run on tag pushes
  workflow_dispatch:  # Allow manual trigger
```

**Why it matters:** The build job runs on every push, but publishing only happens on tags. This wastes GitHub Actions minutes unnecessarily.

---

## 📊 Summary

### Issue Count by Severity
- 🔴 **Critical:** 3 issues (will cause runtime failures)
- 🟠 **High Priority:** 6 issues (likely to cause production issues)
- 🟡 **Medium Priority:** 5 issues (code quality and maintainability)
- 🔵 **Low Priority:** 5 issues (best practices and improvements)

**Total Issues Found:** 19

### Most Important Fixes (Priority Order)

1. **Fix RuntimeError not being raised** (`pyephember2.py:74`)
2. **Fix import paths in example files** (`example.py:10`, `messagelogger.py:11`)
3. **Fix non-existent method call** (`example.py:38`)
4. **Add return statements for edge cases** (`zone_mode()`, `get_zone_mode_value()`)
5. **Add None checks for temperature operations**
6. **Clean up setup.py** (version conflict, parameter names)
7. **Add comprehensive unit tests**

### Recommendations

1. **Immediate Actions:**
   - Fix all critical bugs (Issues #1-3)
   - Add None checks to prevent TypeErrors (Issues #6-7)
   - Fix setup.py configuration (Issues #8-9)

2. **Short-term Improvements:**
   - Add proper error handling throughout
   - Create unit test suite
   - Add type hints to all functions

3. **Long-term Enhancements:**
   - Refactor inconsistent return types
   - Define constants for magic numbers
   - Improve documentation
   - Consider using dataclasses for zone/home data

### Testing Recommendations

Create test files covering:
- Zone mode detection for all device types
- Temperature reading and setting
- MQTT command generation
- API authentication flow
- Edge cases (None values, missing data, network failures)

### Documentation Needs

- Add docstrings with type hints
- Document all device types and their behaviors
- Add API error code reference
- Create troubleshooting guide

---

**End of Report**
