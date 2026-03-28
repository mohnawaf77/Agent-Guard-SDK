import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".agentguard"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> dict:
    """Load config from ~/.agentguard/config.json"""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(token: str, master_key: str) -> None:
    """Save token and master key to ~/.agentguard/config.json"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"token": token, "master_key": master_key}, f)
    # Set file permissions to owner-only for security
    os.chmod(CONFIG_FILE, 0o600)

def clear_config() -> None:
    """Delete saved config"""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
