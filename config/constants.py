"""
Constants for configuration limits and validation.
Centralizes all parameter ranges for easy maintenance.
"""

# Global parameter limits
class ConfigLimits:
    """Configuration parameter limits and defaults."""
    
    # Precision decimals
    PRECISION_MIN = 1
    PRECISION_MAX = 10
    PRECISION_DEFAULT = 4
    
    # Resolution
    RESOLUTION_MIN = 100
    RESOLUTION_MAX = 10000
    RESOLUTION_DEFAULT = 5000
    
    # Threshold (dB)
    THRESHOLD_MIN = -300
    THRESHOLD_MAX = -10
    THRESHOLD_DEFAULT = -60
    
    # Valid angle units (English only - UI translation handled by translations.py)
    VALID_ANGLE_UNITS = ["degrees", "radians"]
    DEFAULT_ANGLE_UNIT = "degrees"
    
    # Valid scale options (English only - UI translation handled by translations.py)
    VALID_SCALES = ["dB", "linear"]
    DEFAULT_SCALE = "linear"
    
    # Array factor normalization option
    DEFAULT_NORMALIZE_ARRAY_FACTOR = True