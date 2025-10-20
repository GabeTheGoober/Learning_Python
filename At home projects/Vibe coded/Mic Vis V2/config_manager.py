import json
import os

class ConfigManager:
    """Manages loading and saving of configuration files."""
    def __init__(self, config_path):
        self.config_path = config_path
        self.default_config = {
            'threshold': 300,
            'head_color': [100, 150, 255],
            'mouth_color': [255, 0, 0],
            'wave_color': [255, 255, 255],
            'wave_count': 5,
            'window_x': 100,
            'window_y': 100,
            'window_width': 800,
            'window_height': 800,
            'last_device': None,
            'theme': 'default',
            'accessories': [],
            'character_scale': 1.0,
            'character_model': 'default',
            'wave_pattern': 'circular',
            'frequency_analysis': False,
            'low_freq_color': [0, 0, 255],
            'mid_freq_color': [0, 255, 0],
            'high_freq_color': [255, 0, 0],
            'background_effect': 'none',
            'bg_effect_color': [255, 255, 255, 50],
            'animation_preset': 'none',
            'facial_expressions': True
        }

    def load_config(self, file_path=None):
        """Load configuration from a JSON file or return default config."""
        try:
            path = file_path if file_path else self.config_path
            if os.path.exists(path):
                with open(path, 'r') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    for key in self.default_config:
                        if key not in config:
                            config[key] = self.default_config[key]
                        # Handle legacy accessory fields
                        if key == 'accessories' and 'selected_accessory' in config and config['selected_accessory'] != 'None':
                            config['accessories'].append({
                                'name': config['selected_accessory'],
                                'x_offset': config.get('accessory_x_offset', 0),
                                'y_offset': config.get('accessory_y_offset', 0),
                                'scale': config.get('accessory_scale', 1.0)
                            })
                    # Remove legacy fields
                    for old_key in ['selected_accessory', 'accessory_x_offset', 'accessory_y_offset', 'accessory_scale']:
                        config.pop(old_key, None)
                    return config
            return self.default_config.copy()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {path}: {e}")
            return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config from {path}: {e}")
            return self.default_config.copy()

    def save_config(self, config):
        """Save configuration to the JSON file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"Error saving config to {self.config_path}: {e}")