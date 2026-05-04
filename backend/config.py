import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

def load_config(path: str = CONFIG_PATH) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")

def save_config(config: dict, path: str = CONFIG_PATH) -> None:
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
