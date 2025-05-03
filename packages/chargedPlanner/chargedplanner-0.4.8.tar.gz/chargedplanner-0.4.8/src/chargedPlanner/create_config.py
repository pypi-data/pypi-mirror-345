import os
import json

def create_default_config():
    default_devs = {
        "devs": [
            {"name": "Dev A"},
            {"name": "Dev B"}
        ]
    }
    config_dir = os.path.expanduser('~/.config/chargedPlanner/')
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, 'devs.json')
    with open(config_path, 'w') as f:
        json.dump(default_devs, f, indent=4)
    print(f'Default configuration created at {config_path}')

create_default_config()