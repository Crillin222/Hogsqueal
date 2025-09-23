import json

LOGIN_CONFIG_PATH = "login_config.json"

def save_login_config(config):
    """
    Saves the login configuration to a JSON file.
    """
    try:
        with open(LOGIN_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f)
    except Exception as e:
        # Optionally log error
        pass

def load_login_config():
    """
    Loads the login configuration from a JSON file.
    Returns an empty dict if not found.
    """
    try:
        with open(LOGIN_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}