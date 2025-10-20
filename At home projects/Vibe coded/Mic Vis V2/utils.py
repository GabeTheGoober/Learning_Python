import os
import json

def find_or_create_mv_pr():
    """Find or create the MV_pr.json file and MV_accessories/characters folders.
    
    Returns:
        tuple: (config_path, accessories_dir, characters_dir)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_filename = "MV_pr.json"
    
    # Create MV_accessories folder
    accessories_dir = os.path.join(script_dir, "MV_accessories")
    try:
        os.makedirs(accessories_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating MV_accessories: {e}")
    
    # Create MV_characters folder
    characters_dir = os.path.join(script_dir, "MV_characters")
    try:
        os.makedirs(characters_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating MV_characters: {e}")
    
    # Check for MV_pr.json
    file_path = os.path.join(script_dir, target_filename)
    
    # Create default config if not found
    if not os.path.exists(file_path):
        default_config = {
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
        try:
            with open(file_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default configuration at {file_path}")
        except Exception as e:
            print(f"Error creating MV_pr.json: {e}")
    
    return file_path, accessories_dir, characters_dir