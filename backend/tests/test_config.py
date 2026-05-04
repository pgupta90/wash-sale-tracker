import pytest
import tempfile
import os
import yaml
from backend.config import load_config, save_config

def test_load_config_reads_yaml():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({'robinhood': {'username': 'test@test.com', 'password': 'secret'}}, f)
        path = f.name
    try:
        config = load_config(path)
        assert config['robinhood']['username'] == 'test@test.com'
        assert config['robinhood']['password'] == 'secret'
    finally:
        os.unlink(path)

def test_load_config_raises_if_missing():
    with pytest.raises(FileNotFoundError):
        load_config('/nonexistent/path/config.yaml')

def test_save_config_writes_yaml():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        path = f.name
    try:
        config = {'robinhood': {'username': 'user@test.com', 'password': 'pw'}}
        save_config(config, path)
        with open(path) as f:
            loaded = yaml.safe_load(f)
        assert loaded['robinhood']['username'] == 'user@test.com'
    finally:
        os.unlink(path)
