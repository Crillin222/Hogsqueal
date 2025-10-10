import os, json
from pathlib import Path

def _config_path():
    base = Path(os.getenv("APPDATA", Path.home())) / "Hogsqueal"
    base.mkdir(parents=True, exist_ok=True)
    return base / "login_config.json"

def save_login_config(config):
    with open(_config_path(), "w", encoding="utf-8") as f:
        json.dump(config, f)

def load_login_config():
    p = _config_path()
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
