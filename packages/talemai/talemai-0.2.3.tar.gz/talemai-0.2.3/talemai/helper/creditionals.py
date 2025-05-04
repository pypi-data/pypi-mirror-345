import os
import json
from types import SimpleNamespace

CONFIG_FILE = "astra_config.json"  # Make sure this is defined globally

def read_db_config():
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            data = json.load(file)
            return SimpleNamespace(**data)

    return None

def write_db_config(api_endpoint, token):
    config = {
        "api_endpoint": api_endpoint.strip(),
        "token": token.strip()
    }
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)
        
