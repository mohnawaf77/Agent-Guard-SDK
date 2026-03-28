import os
from .config import load_config, save_config
from .exceptions import AgentGuardAuthError

PROXY_URL = "https://proxy.agent-guard.dev"
API_URL = "https://api.agent-guard.dev"

def load_credentials() -> tuple[str, str]:
    """
    Load token and master key in this order:
    1. Environment variables
    2. Local config file
    3. Interactive prompt
    Returns (token, master_key)
    """
    # 1. Check environment variables
    token = os.environ.get("AGENTGUARD_TOKEN")
    master_key = os.environ.get("AGENTGUARD_MASTER_KEY")

    if token and master_key:
        return token, master_key

    # 2. Check config file
    config = load_config()
    token = config.get("token")
    master_key = config.get("master_key")

    if token and master_key:
        return token, master_key

    # 3. Interactive prompt
    print("\n  AgentGuard Authentication")
    print("  " + "-" * 30)
    token = input("  Enter your AgentGuard token: ").strip()
    master_key = input("  Enter your master key: ").strip()

    if not token or not master_key:
        raise AgentGuardAuthError("Token and master key are required.")

    save_prompt = input("  Save for future use? (y/n): ").strip().lower()
    if save_prompt == "y":
        save_config(token, master_key)
        print("  OK Saved to ~/.agentguard/config.json\n")

    return token, master_key

def validate_token(token: str) -> bool:
    """
    Validate token against AgentGuard API.
    Returns True if valid, raises AgentGuardAuthError if not.
    """
    import requests
    try:
        res = requests.get(
            f"{API_URL}/health",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if res.status_code == 401:
            raise AgentGuardAuthError(
                "Invalid AgentGuard token. Check your token at agent-guard.dev"
            )
        return True
    except requests.exceptions.ConnectionError:
        raise AgentGuardAuthError(
            "Could not connect to AgentGuard. Check your internet connection."
        )
