import unittest
import os
import json
from config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.test_config_path = "test_config.json"
        self.config_manager = ConfigManager(self.test_config_path)
    
    def tearDown(self):
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
    
    def test_load_default_config(self):
        """Test loading the default configuration."""
        config = self.config_manager.load_config()
        self.assertEqual(config['threshold'], 300)
        self.assertEqual(config['theme'], 'default')
        self.assertEqual(config['accessories'], [])
    
    def test_save_and_load_config(self):
        """Test saving and loading a custom configuration."""
        custom_config = {
            'threshold': 500,
            'theme': 'green',
            'accessories': [{'name': 'hat', 'x_offset': 10, 'y_offset': 20, 'scale': 1.5}]
        }
        self.config_manager.save_config(custom_config)
        loaded_config = self.config_manager.load_config()
        self.assertEqual(loaded_config['threshold'], 500)
        self.assertEqual(loaded_config['theme'], 'green')
        self.assertEqual(loaded_config['accessories'], custom_config['accessories'])
    
    def test_load_corrupted_config(self):
        """Test loading a corrupted JSON file."""
        with open(self.test_config_path, 'w') as f:
            f.write("invalid json")
        config = self.config_manager.load_config()
        self.assertEqual(config['threshold'], 300)  # Should return default config

if __name__ == '__main__':
    unittest.main()