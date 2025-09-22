# Configuration System

This directory contains the configuration management system for the antenna synthesis application.

## Files

- **`constants.py`** - Centralized configuration limits and constants
- **`settings.py`** - Configuration manager class
- **`__init__.py`** - Package exports
- **`config.json`** - User configuration file (auto-generated)

## Configuration Limits

All parameter limits are centralized in `ConfigLimits` class for easy maintenance:

### Resolution
- **Range**: 100 - 10,000 points
- **Default**: 5,000 points
- **Constants**: `ConfigLimits.RESOLUTION_MIN`, `ConfigLimits.RESOLUTION_MAX`, `ConfigLimits.RESOLUTION_DEFAULT`

### Threshold
- **Range**: -120 to -10 dB  
- **Default**: -30 dB
- **Constants**: `ConfigLimits.THRESHOLD_MIN`, `ConfigLimits.THRESHOLD_MAX`, `ConfigLimits.THRESHOLD_DEFAULT`

### Precision
- **Range**: 1 - 10 decimal places
- **Default**: 2 decimal places  
- **Constants**: `ConfigLimits.PRECISION_MIN`, `ConfigLimits.PRECISION_MAX`, `ConfigLimits.PRECISION_DEFAULT`

### Angle Units
- **Valid Options**: `["degrees", "radians", "grados", "radianes"]`
- **Default**: `"radians"`
- **Constants**: `ConfigLimits.VALID_ANGLE_UNITS`, `ConfigLimits.DEFAULT_ANGLE_UNIT`

### Scale Options
- **Valid Options**: `["dB", "linear", "lineal"]`
- **Default**: `"dB"`
- **Constants**: `ConfigLimits.VALID_SCALES`, `ConfigLimits.DEFAULT_SCALE`

## Usage Example

```python
from config import ConfigLimits, ConfigManager

# Access limits directly
print(f"Resolution range: {ConfigLimits.RESOLUTION_MIN} - {ConfigLimits.RESOLUTION_MAX}")
print(f"Threshold range: {ConfigLimits.THRESHOLD_MIN} - {ConfigLimits.THRESHOLD_MAX}")

# Use in UI components
spin_box.setRange(ConfigLimits.RESOLUTION_MIN, ConfigLimits.RESOLUTION_MAX)
spin_box.setValue(ConfigLimits.RESOLUTION_DEFAULT)

# Configuration management
config_manager = ConfigManager()
config = config_manager.load_config()  # Automatically validated
config_manager.save_config(config)
```

## Benefits

- **Centralized**: All limits in one place
- **Easy Maintenance**: Change limits in `constants.py` only
- **Type Safety**: Constants prevent typos and magic numbers
- **Validation**: Automatic validation ensures values stay within bounds
- **Documentation**: Self-documenting code with clear constant names