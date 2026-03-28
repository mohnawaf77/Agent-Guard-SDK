import requests
from urllib.parse import urlparse
from .auth import load_credentials, validate_token, PROXY_URL
from .exceptions import (
    AgentGuardAuthError,
    AgentGuardCredentialError,
    AgentGuardMasterKeyError,
    AgentGuardProxyError,
    AgentGuardRateLimitError,
)

class AgentGuardSession:
    """
    Drop-in replacement for requests.Session that routes all calls
    through the AgentGuard proxy.

    Usage:
        session = AgentGuardSession()
        response = session.post(
            "https://api.tavily.com/search",
            credential_id="your_credential_id",
            json={"query": "hello"}
        )
    """

    def __init__(self, token: str = None, master_key: str = None):
        """
        Initialize session. If token and master_key not provided,
        loads from env vars, config file, or prompts user.
        """
        if token and master_key:
            self.token = token
            self.master_key = master_key
        else:
            self.token, self.master_key = load_credentials()

        # Validate token on init
        validate_token(self.token)
        print("  OK Connected to AgentGuard\n")

    def _build_proxy_url(self, url: str) -> str:
        """
        Convert full API URL to proxy URL.
        https://api.tavily.com/search → https://proxy.agent-guard.dev/search
        """
        parsed = urlparse(url)
        path = parsed.path
        query = f"?{parsed.query}" if parsed.query else ""
        return f"{PROXY_URL}{path}{query}"

    def _build_headers(self, credential_id: str, extra_headers: dict = None) -> dict:
        """Build headers required by AgentGuard proxy"""
        headers = {
            "X-AgentGuard-Token": self.token,
            "X-AgentGuard-Master-Key": self.master_key,
            "X-AgentGuard-Credential": credential_id,
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _handle_response(self, response: requests.Response) -> requests.Response:
        """Handle error responses from proxy"""
        if response.status_code == 401:
            try:
                code = response.json().get("code", "")
                if code == "master_key_required" or code == "decryption_failed":
                    raise AgentGuardMasterKeyError(
                        "Invalid master key. Check your master key at agent-guard.dev"
                    )
            except Exception:
                pass
            raise AgentGuardAuthError(
                "Unauthorized. Check your AgentGuard token."
            )
        if response.status_code == 403:
            raise AgentGuardCredentialError(
                "Credential access denied. Make sure this credential belongs to your agent."
            )
        if response.status_code == 404:
            raise AgentGuardCredentialError(
                "Credential not found. Check your credential ID at agent-guard.dev"
            )
        if response.status_code == 429:
            raise AgentGuardRateLimitError(
                "Rate limit exceeded. Slow down requests or upgrade your plan."
            )
        if response.status_code == 502:
            raise AgentGuardProxyError(
                "Could not reach the target API. Check the target URL in your credential."
            )
        return response

    def _request(self, method: str, url: str, credential_id: str, **kwargs) -> requests.Response:
        """Internal request handler"""
        proxy_url = self._build_proxy_url(url)
        extra_headers = kwargs.pop("headers", {})
        headers = self._build_headers(credential_id, extra_headers)
        response = requests.request(
            method,
            proxy_url,
            headers=headers,
            **kwargs
        )
        return self._handle_response(response)

    def get(self, url: str, credential_id: str, **kwargs) -> requests.Response:
        return self._request("GET", url, credential_id, **kwargs)

    def post(self, url: str, credential_id: str, **kwargs) -> requests.Response:
        return self._request("POST", url, credential_id, **kwargs)

    def put(self, url: str, credential_id: str, **kwargs) -> requests.Response:
        return self._request("PUT", url, credential_id, **kwargs)

    def patch(self, url: str, credential_id: str, **kwargs) -> requests.Response:
        return self._request("PATCH", url, credential_id, **kwargs)

    def delete(self, url: str, credential_id: str, **kwargs) -> requests.Response:
        return self._request("DELETE", url, credential_id, **kwargs)
