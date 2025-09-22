"""
Configuration management for the antenna synthesis application.
Handles loading and saving of global parameters to maintain user preferences.
"""

import json
import sys
import os
from typing import Dict, Any
from pathlib import Path
from .constants import ConfigLimits

def resource_path(relative_path):
    """ Gets the absolute path to the resource, works for development and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # Dev mode
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ConfigManager:
    """Manages application configuration settings."""
    
    def __init__(self, app_name: str = "AntennaSynthesisApp", config_file: str = "config.json"):
        """Initialize configuration manager.
        
        Args:
            config_file: Name of the configuration file (will be saved in user's config directory)
        """
        self.app_name = app_name
        self.config_file_name = config_file

        self.user_config_path = self._get_user_config_path()
        self.bundled_config_path = self._get_bundled_config_path()        
        self.default_config = self._get_default_config()
        
    def _get_user_config_path(self) -> Path:
        """
        Get the full path to the configuration file.
        Example: C:/Users/YourUser/AppData/Roaming/AntennaSynthesisApp/config.json
        """
        # Use the application directory for simplicity
        config_dir = Path.home() / self.app_name
        config_dir.mkdir(exist_ok=True) # Create folder if it doesn't exist
        return config_dir / self.config_file_name
    
    def _get_bundled_config_path(self) -> str:
        """
        Gets the path to config.json that is bundled inside the .exe.
        Uses our resource_path function.
        """
        # The relative path from project root is "config/config.json"
        return resource_path(os.path.join("config", self.config_file_name))
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values using centralized constants."""
        return {
            'precision_decimals': ConfigLimits.PRECISION_DEFAULT,
            'font_size': 12,
            'angle_unit_input': ConfigLimits.DEFAULT_ANGLE_UNIT,
            'angle_unit_rectangular': ConfigLimits.DEFAULT_ANGLE_UNIT,
            'angle_unit_polar': ConfigLimits.DEFAULT_ANGLE_UNIT,
            'element_phase_unit': ConfigLimits.DEFAULT_ANGLE_UNIT,
            'rectangular_scale': ConfigLimits.DEFAULT_SCALE,
            'polar_scale': ConfigLimits.DEFAULT_SCALE,
            'resolution': ConfigLimits.RESOLUTION_DEFAULT,
            'threshold_db': ConfigLimits.THRESHOLD_DEFAULT,
            'normalize_array_factor': ConfigLimits.DEFAULT_NORMALIZE_ARRAY_FACTOR,
            'last_method': None,
            'method_inputs': {}
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration.
        Priority:
        1. Try to load from USER path.
        2. If it fails, try to load from BUNDLED path (inside .exe).
        3. If everything fails, use default values.
        """
        config_to_load = None
        
        # 1. First, try to load user configuration
        if self.user_config_path.exists():
            try:
                with open(self.user_config_path, 'r', encoding='utf-8') as f:
                    config_to_load = json.load(f)
            except (json.JSONDecodeError, PermissionError):
                # User file is corrupted or inaccessible, move to next option
                config_to_load = None
        
        # 2. If there's no user configuration, load the one that comes with the app
        if config_to_load is None:
            try:
                # Note: self.bundled_config_path is already a string
                with open(self.bundled_config_path, 'r', encoding='utf-8') as f:
                    config_to_load = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError, PermissionError):
                # If even the bundled file fails, we'll use defaults
                config_to_load = None
        
        # If no file could be loaded, return defaults
        if config_to_load is None:
            print("Warning: Could not load any config file. Using hardcoded defaults.")
            return self.default_config.copy()
            
        # Merge with defaults to ensure no new keys are missing
        final_config = self.default_config.copy()
        final_config.update(config_to_load)
        
        return self._validate_config(final_config)   
    
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration values are within acceptable ranges using centralized constants."""
        validated_config = config.copy()
        
        # Validate precision_decimals
        precision = validated_config.get('precision_decimals', ConfigLimits.PRECISION_DEFAULT)
        if not (ConfigLimits.PRECISION_MIN <= precision <= ConfigLimits.PRECISION_MAX):
            validated_config['precision_decimals'] = ConfigLimits.PRECISION_DEFAULT
            
        # Validate resolution
        resolution = validated_config.get('resolution', ConfigLimits.RESOLUTION_DEFAULT)
        if not (ConfigLimits.RESOLUTION_MIN <= resolution <= ConfigLimits.RESOLUTION_MAX):
            validated_config['resolution'] = ConfigLimits.RESOLUTION_DEFAULT
            
        # Validate threshold_db
        threshold = validated_config.get('threshold_db', ConfigLimits.THRESHOLD_DEFAULT)
        if not (ConfigLimits.THRESHOLD_MIN <= threshold <= ConfigLimits.THRESHOLD_MAX):
            validated_config['threshold_db'] = ConfigLimits.THRESHOLD_DEFAULT
            
        # Validate angle units
        for key in ['angle_unit_input', 'angle_unit_rectangular', 'angle_unit_polar', 'element_phase_unit']:
            if validated_config.get(key) not in ConfigLimits.VALID_ANGLE_UNITS:
                validated_config[key] = self.default_config[key]
                
        # Validate scale options
        for key in ['rectangular_scale', 'polar_scale']:
            if validated_config.get(key) not in ConfigLimits.VALID_SCALES:
                validated_config[key] = self.default_config[key]
        
        # Validate normalize_array_factor (must be boolean)
        if not isinstance(validated_config.get('normalize_array_factor'), bool):
            validated_config['normalize_array_factor'] = ConfigLimits.DEFAULT_NORMALIZE_ARRAY_FACTOR
                
        return validated_config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration ALWAYS to USER path.
        """
        try:
            # Ensure user folder exists
            self.user_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config_to_save = {}
            for key in self.default_config.keys():
                if key in config:
                    config_to_save[key] = config[key]
            
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            return True
            
        except (PermissionError, OSError) as e:
            print(f"Error: Could not save config file to {self.user_config_path} ({e}).")
            return False
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """Reset configuration to default values."""
        try:
            if self.user_config_path.exists():
                self.user_config_path.unlink()  # Delete user's config file
        except (PermissionError, OSError):
            pass
            
        return self.default_config.copy()   
    
    def save_method_state(self, method_name: str, inputs: Dict[str, Any]) -> bool:
        """Save the current method and its inputs.
        
        Args:
            method_name: Name of the current method
            inputs: Dictionary with method-specific input values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load current config
            config = self.load_config()
            
            # Update method state
            config['last_method'] = method_name
            if 'method_inputs' not in config:
                config['method_inputs'] = {}
            config['method_inputs'][method_name] = inputs.copy()
            
            # Save updated config
            return self.save_config(config)
            
        except Exception as e:
            print(f"Error saving method state: {e}")
            return False
    
    def load_method_state(self) -> tuple[str | None, Dict[str, Any]]:
        """Load the last used method and its inputs.
        
        Returns:
            tuple: (method_name, inputs_dict)
        """
        try:
            config = self.load_config()
            last_method = config.get('last_method')
            method_inputs = config.get('method_inputs', {})
            
            if last_method and last_method in method_inputs:
                return last_method, method_inputs[last_method].copy()
            else:
                return None, {}
                
        except Exception as e:
            print(f"Error loading method state: {e}")
            return None, {}
    
    def get_method_inputs(self, method_name: str) -> Dict[str, Any]:
        """Get saved inputs for a specific method.
        
        Args:
            method_name: Name of the method
            
        Returns:
            Dictionary with saved inputs for the method
        """
        try:
            config = self.load_config()
            method_inputs = config.get('method_inputs', {})
            return method_inputs.get(method_name, {}).copy()
            
        except Exception as e:
            print(f"Error getting method inputs: {e}")
            return {}