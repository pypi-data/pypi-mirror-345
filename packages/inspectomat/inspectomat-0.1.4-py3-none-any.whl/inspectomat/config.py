"""
Configuration system for the cleaner package.
Handles loading, saving, and accessing configuration settings.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List, Union

# Import the logger
from cleaner.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Default configuration directory
DEFAULT_CONFIG_DIR = os.path.expanduser('~/.cleaner')
DEFAULT_CONFIG_FILE = 'config.json'

# Default configuration settings
DEFAULT_CONFIG = {
    'general': {
        'default_mode': 'script',  # 'interactive' or 'script'
        'auto_repair': True,            # Automatically repair dependencies
        'confirm_destructive': True,    # Confirm before destructive operations
    },
    'logging': {
        'console_level': 'INFO',        # Console log level
        'file_level': 'DEBUG',          # File log level
        'log_file': None,               # Custom log file path
        'enable_console': True,         # Enable console logging
        'enable_file': True,            # Enable file logging
    },
    'paths': {
        'default_search_paths': [],     # Default paths to search
        'excluded_paths': [],           # Paths to exclude from search
    },
    'modules': {
        # Module-specific settings
        'clean_empty_dirs': {
            'confirm_delete': True,     # Confirm before deleting
        },
        'find_big_files': {
            'min_size': 100000000,      # Minimum file size in bytes (100MB)
            'sort_by': 'size',          # Sort by 'size', 'name', or 'date'
        },
        'media_deduplicate': {
            'similarity_threshold': 0.9,  # Similarity threshold (0.0-1.0)
        },
    }
}

class ConfigManager:
    """
    Configuration manager for the cleaner package.
    """
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file (default: ~/.cleaner/config.json)
        """
        if config_file is None:
            # Create default config directory if it doesn't exist
            os.makedirs(DEFAULT_CONFIG_DIR, exist_ok=True)
            self.config_file = os.path.join(DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE)
        else:
            self.config_file = config_file
            # Create config directory if it doesn't exist
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
        
        # Load configuration
        self.config = self.load()
        # Store the original configuration for reset
        import copy
        self._original_config = copy.deepcopy(self.config)

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.debug(f"Loaded configuration from {self.config_file}")
                
                # Merge with default configuration to ensure all keys exist
                merged_config = self._merge_configs(DEFAULT_CONFIG.copy(), config)
                return merged_config
            else:
                logger.info(f"Configuration file {self.config_file} not found, using defaults")
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return DEFAULT_CONFIG.copy()
    
    def save(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.debug(f"Saved configuration to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (dot-separated path, e.g., 'general.default_mode')
            default: Default value if key is not found
            
        Returns:
            Any: Configuration value
        """
        try:
            parts = key.split('.')
            value = self.config
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot-separated path, e.g., 'general.default_mode')
            value: Configuration value
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            parts = key.split('.')
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
            return True
        except Exception as e:
            logger.error(f"Error setting configuration value: {e}")
            return False
    
    def reset(self):
        """
        Reset configuration to defaults.
        """
        import copy
        self.config = copy.deepcopy(self._original_config)
        logger.info("Configuration reset to defaults")

    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user configuration with default configuration.
        
        Args:
            default: Default configuration
            user: User configuration
            
        Returns:
            Dict[str, Any]: Merged configuration
        """
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

# Create a global configuration manager instance
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        ConfigManager: Configuration manager instance
    """
    return config_manager

def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a configuration value from the global configuration manager.
    
    Args:
        key: Configuration key (dot-separated path, e.g., 'general.default_mode')
        default: Default value if key is not found
        
    Returns:
        Any: Configuration value
    """
    return config_manager.get(key, default)

def set_config_value(key: str, value: Any) -> bool:
    """
    Set a configuration value in the global configuration manager.
    
    Args:
        key: Configuration key (dot-separated path, e.g., 'general.default_mode')
        value: Configuration value
        
    Returns:
        bool: True if successful, False otherwise
    """
    result = config_manager.set(key, value)
    if result:
        config_manager.save()
    return result

def reset_config() -> None:
    """
    Reset configuration to defaults.
    """
    config_manager.reset()
    config_manager.save()

def save_config() -> bool:
    """
    Save configuration to file.
    
    Returns:
        bool: True if successful, False otherwise
    """
    return config_manager.save()
