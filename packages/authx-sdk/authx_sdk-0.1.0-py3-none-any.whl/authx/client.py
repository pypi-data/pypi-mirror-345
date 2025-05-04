import requests
from .config import BASE_URL, REQUEST_TIMEOUT
from .utils import normalize_scope

class AuthX:
    def __init__(self, user_id: str, provider: str, scopes: list[str], client_id: str = "default_client"):
        """
        Initialize the AuthX SDK.

        Args:
            user_id: Unique identifier of the user
            provider: OAuth provider (e.g., 'google')
            scopes: List of OAuth scopes
            client_id: The client using this SDK (e.g., 'marc_app')
        """
        self.user_id = user_id
        self.provider = provider
        self.scopes = scopes
        self.client_id = client_id
        self.scope_key = normalize_scope(scopes)

    def get_token(self) -> dict:
        """
        Retrieve a valid access token, or get the auth URL if user needs to authenticate.

        Returns:
            dict containing:
            - access_token, expires_at, refresh_token (if token is valid)
            - OR {'auth_url': ...} to begin OAuth flow
        """
        url = f"{BASE_URL}/auth/{self.provider}/start"
        params = {
            "user_id": self.user_id,
            "client_id": self.client_id,
            "scope": self.scopes  # sent as multiple values (e.g. ?scope=a&scope=b)
        }

        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"[AuthX] Network error: {e}")

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "already_authenticated":
                return data["tokens"]
            elif data.get("status") == "needs_auth":
                return {"auth_url": data["url"]}
            else:
                raise RuntimeError(f"[AuthX] Unexpected response format: {data}")
        else:
            raise RuntimeError(f"[AuthX] Unexpected error {response.status_code}: {response.text}")

    def callback(self, code: str, state: str) -> dict:
        """
        Complete the OAuth flow using the code and state received from the provider.

        Args:
            code: Authorization code from the provider (e.g., Google)
            state: The original state string returned in the redirect

        Returns:
            dict containing the stored token information
        """
        url = f"{BASE_URL}/auth/{self.provider}/callback"
        params = {
            "code": code,
            "state": state
        }

        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"[AuthX] Callback network error: {e}")

        if response.status_code == 200:
            return response.json()
        else:
            raise RuntimeError(f"[AuthX] Callback failed: {response.status_code} - {response.text}")
