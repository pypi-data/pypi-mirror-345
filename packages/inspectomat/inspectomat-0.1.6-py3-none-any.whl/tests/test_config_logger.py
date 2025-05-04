#!/usr/bin/env python3
"""
Unit tests for the configuration and logging systems
"""
import unittest
import os
import sys
import tempfile
import json
import logging
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the inspectomat package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from inspectomat.config import (
    ConfigManager, get_config, get_config_value, set_config_value, reset_config, DEFAULT_CONFIG
)
from inspectomat.logger import (
    get_logger, setup_logging, set_log_level
)


class TestConfigManager(unittest.TestCase):
    """Test the configuration manager"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.test_dir.name, 'test_config.json')
        
        # Create a test configuration manager
        self.config_manager = ConfigManager(self.config_file)
    
    def tearDown(self):
        """Clean up test environment"""
        self.test_dir.cleanup()
    
    def test_default_config(self):
        """Test that default configuration is loaded correctly"""
        # The configuration should be a copy of the default
        self.assertEqual(self.config_manager.config['general']['default_mode'], DEFAULT_CONFIG['general']['default_mode'])
        self.assertEqual(self.config_manager.config['general']['auto_repair'], DEFAULT_CONFIG['general']['auto_repair'])
    
    def test_save_load(self):
        """Test saving and loading configuration"""
        # Get the current default mode
        current_mode = self.config_manager.get('general.default_mode')
        
        # Set to the opposite mode
        new_mode = 'interactive' if current_mode == 'script' else 'script'
        self.config_manager.set('general.default_mode', new_mode)
        self.config_manager.set('logging.console_level', 'DEBUG')
        
        # Save the configuration
        self.assertTrue(self.config_manager.save())
        
        # Check that the file exists
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load the configuration into a new manager
        new_manager = ConfigManager(self.config_file)
        
        # Check that the values were loaded correctly
        self.assertEqual(new_manager.get('general.default_mode'), new_mode)
        self.assertEqual(new_manager.get('logging.console_level'), 'DEBUG')
    
    def test_get_set(self):
        """Test getting and setting configuration values"""
        # Get the current default mode
        current_mode = self.config_manager.get('general.default_mode')
        
        # Set to the opposite mode
        new_mode = 'interactive' if current_mode == 'script' else 'script'
        self.assertTrue(self.config_manager.set('general.default_mode', new_mode))
        
        # Get the value
        self.assertEqual(self.config_manager.get('general.default_mode'), new_mode)
        
        # Get a non-existent value
        self.assertIsNone(self.config_manager.get('non.existent.key'))
        
        # Get a non-existent value with default
        self.assertEqual(self.config_manager.get('non.existent.key', 'default'), 'default')
        
        # Set a nested value that doesn't exist yet
        self.assertTrue(self.config_manager.set('new.nested.key', 'value'))
        
        # Get the nested value
        self.assertEqual(self.config_manager.get('new.nested.key'), 'value')
    
    def test_reset(self):
        """Test resetting configuration to defaults"""
        # Change the default mode to something else
        original_mode = self.config_manager.get('general.default_mode')
        new_mode = 'interactive' if original_mode == 'script' else 'script'
        self.config_manager.set('general.default_mode', new_mode)
        
        # Verify the value was changed
        self.assertEqual(self.config_manager.get('general.default_mode'), new_mode)
        
        # Reset the configuration
        self.config_manager.reset()
        
        # Check that the value was reset to the original value
        self.assertEqual(self.config_manager.get('general.default_mode'), original_mode)
    
    def test_merge_configs(self):
        """Test merging configurations"""
        # Create a user configuration
        user_config = {
            'general': {
                'default_mode': 'interactive',
                'new_key': 'value'
            },
            'new_section': {
                'key': 'value'
            }
        }
        
        # Merge with default configuration
        merged = self.config_manager._merge_configs(DEFAULT_CONFIG, user_config)
        
        # Check that values were merged correctly
        self.assertEqual(merged['general']['default_mode'], 'interactive')
        self.assertEqual(merged['general']['new_key'], 'value')
        self.assertEqual(merged['new_section']['key'], 'value')
        
        # Check that other default values are still present
        self.assertTrue(merged['general']['auto_repair'])
        self.assertTrue('logging' in merged)


class TestGlobalConfigFunctions(unittest.TestCase):
    """Test the global configuration functions"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.test_dir.name, 'test_config.json')
        
        # Patch the global configuration manager
        self.patcher = patch('inspectomat.config.config_manager', ConfigManager(self.config_file))
        self.mock_config_manager = self.patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.patcher.stop()
        self.test_dir.cleanup()
    
    def test_get_config(self):
        """Test getting the global configuration manager"""
        config = get_config()
        self.assertIsInstance(config, ConfigManager)
    
    def test_get_config_value(self):
        """Test getting a configuration value"""
        # Get the current default mode
        current_mode = DEFAULT_CONFIG['general']['default_mode']
        
        # Get a value that exists
        value = get_config_value('general.default_mode')
        self.assertEqual(value, current_mode)
        
        # Get a value with a default
        value = get_config_value('non.existent.key', 'default')
        self.assertEqual(value, 'default')
    
    def test_set_config_value(self):
        """Test setting a configuration value"""
        # Get the current default mode
        current_mode = DEFAULT_CONFIG['general']['default_mode']
        
        # Set to the opposite mode
        new_mode = 'interactive' if current_mode == 'script' else 'script'
        
        # Set a value
        result = set_config_value('general.default_mode', new_mode)
        self.assertTrue(result)
        
        # Check that the value was set
        value = get_config_value('general.default_mode')
        self.assertEqual(value, new_mode)
    
    def test_reset_config(self):
        """Test resetting the configuration"""
        # Get the current default mode
        original_mode = get_config_value('general.default_mode')
        
        # Set to the opposite mode
        new_mode = 'interactive' if original_mode == 'script' else 'script'
        
        # Modify the configuration
        set_config_value('general.default_mode', new_mode)
        
        # Verify the value was changed
        self.assertEqual(get_config_value('general.default_mode'), new_mode)
        
        # Reset the configuration
        reset_config()
        
        # Check that the value was reset to the original value
        value = get_config_value('general.default_mode')
        self.assertEqual(value, original_mode)


class TestLogger(unittest.TestCase):
    """Test the logger module"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.log_file = os.path.join(self.test_dir.name, 'test.log')
    
    def tearDown(self):
        """Clean up test environment"""
        self.test_dir.cleanup()
    
    def test_get_logger(self):
        """Test getting a logger"""
        # Get a logger
        logger = get_logger('test')
        
        # Check that it's a logger
        self.assertIsInstance(logger, logging.Logger)
        
        # Check that the name is correct
        self.assertEqual(logger.name, 'test')
        
        # Getting the same logger should return the same instance
        logger2 = get_logger('test')
        self.assertIs(logger, logger2)
    
    def test_setup_logging(self):
        """Test setting up logging"""
        # Set up logging with a file
        setup_logging(
            console_level=logging.WARNING,
            file_level=logging.DEBUG,
            log_file=self.log_file,
            enable_console=True,
            enable_file=True
        )
        
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Check that the root logger has the correct level
        self.assertEqual(root_logger.level, logging.DEBUG)
        
        # Check that there are two handlers
        self.assertEqual(len(root_logger.handlers), 2)
        
        # Check that the file handler exists and has the correct level
        file_handler = None
        for handler in root_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                file_handler = handler
                break
        
        self.assertIsNotNone(file_handler)
        self.assertEqual(file_handler.level, logging.DEBUG)
        
        # Check that the console handler exists and has the correct level
        console_handler = None
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                console_handler = handler
                break
        
        self.assertIsNotNone(console_handler)
        self.assertEqual(console_handler.level, logging.WARNING)
    
    def test_set_log_level(self):
        """Test setting the log level"""
        # Get a logger
        logger1 = get_logger('test1')
        logger2 = get_logger('test2')
        
        # Set the level for a specific logger
        set_log_level(logging.WARNING, 'test1')
        
        # Check that the level was set
        self.assertEqual(logger1.level, logging.WARNING)
        
        # Check that the other logger's level was not changed
        self.assertNotEqual(logger2.level, logging.WARNING)
        
        # Set the level for all loggers
        set_log_level(logging.ERROR)
        
        # Check that both loggers have the new level
        self.assertEqual(logger1.level, logging.ERROR)
        self.assertEqual(logger2.level, logging.ERROR)


if __name__ == '__main__':
    unittest.main()
