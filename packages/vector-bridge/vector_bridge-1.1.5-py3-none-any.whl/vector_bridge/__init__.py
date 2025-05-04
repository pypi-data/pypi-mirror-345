from typing import Any, Dict, TypeVar

import requests
from pydantic import BaseModel

from vector_bridge.schema.error import HTTPException

# Type definitions from OpenAPI spec
T = TypeVar("T")


# Models based on OpenAPI schema
class Token(BaseModel):
    access_token: str
    token_type: str


class VectorBridgeClient:
    """
    Python client for the VectorBridge.ai API.

    Provides access to all functionality of the VectorBridge platform including
    authentication, user management, AI processing, vector operations, and more.
    """

    def __init__(
        self,
        base_url: str = "https://api.vectorbridge.ai",
        api_key: str = None,
        integration_name: str = "default",
    ):
        """
        Initialize the VectorBridge client.

        Args:
            base_url: The base URL of the VectorBridge API. Defaults to the development server.
        """
        from vector_bridge.admin import AdminClient
        from vector_bridge.client.ai import AIClient
        from vector_bridge.client.ai_message import AIMessageClient
        from vector_bridge.client.function import FunctionClient
        from vector_bridge.client.query import QueryClient
        from vector_bridge.client.workflows import WorkflowClient

        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.api_key = api_key
        self.integration_name = integration_name

        # Initialize admin client
        self.admin = AdminClient(self)

        # Initialize user client
        self.ai = AIClient(self)
        self.ai_message = AIMessageClient(self)
        self.functions = FunctionClient(self)
        self.workflows = WorkflowClient(self)
        self.queries = QueryClient(self)

    def login(self, username: str, password: str) -> Token:
        """
        Log in to obtain an access token.

        Args:
            username: User's email
            password: User's password

        Returns:
            Token object containing access_token and token_type
        """
        url = f"{self.base_url}/token"
        data = {
            "username": username,
            "password": password,
        }
        response = self.session.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        result = self._handle_response(response)
        self.access_token = result["access_token"]

        print(f"Hey, {username}! You have been logged in...")
        print(
            """
██╗   ██╗███████╗ ██████╗████████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██╗██████╗  ██████╗ ███████╗    █████╗ ██╗
██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗██╔════╝ ██╔════╝   ██╔══██╗██║
██║   ██║█████╗  ██║        ██║   ██║   ██║██████╔╝██████╔╝██████╔╝██║██║  ██║██║  ███╗█████╗     ███████║██║
╚██╗ ██╔╝██╔══╝  ██║        ██║   ██║   ██║██╔══██╗██╔══██╗██╔══██╗██║██║  ██║██║   ██║██╔══╝     ██╔══██║██║
 ╚████╔╝ ███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║██████╔╝██║  ██║██║██████╔╝╚██████╔╝███████╗██╗██║  ██║██║
  ╚═══╝  ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═╝╚═╝
                                                                                              version: 1.1.5
API: https://api.vectorbridge.ai/docs
DOCS: https://docs.vectorbridge.ai/
CLOUD: https://workspace.vectorbridge.ai/
                """
        )

        return Token(**result)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with bearer token authentication."""
        if not self.access_token:
            raise ValueError("Authentication required. Call login() first.")

        return {"Authorization": f"Bearer {self.access_token}"}

    def _get_api_key_headers(self, api_key: str) -> Dict[str, str]:
        """Get headers with API key authentication."""
        api_key_headers = {"Api-Key": api_key}
        if self.access_token:
            api_key_headers["Authorization"] = f"Bearer {self.access_token}"

        return api_key_headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and errors."""
        if 200 <= response.status_code < 300:
            if response.status_code == 204:
                return None
            try:
                return response.json()
            except ValueError:
                return response.text
        else:
            try:
                error_data = response.json()
                exc = HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("detail"),
                )
            except ValueError:
                exc = HTTPException(
                    status_code=response.status_code,
                    detail=response.text,
                )
            raise exc

    def ping(self) -> str:
        """
        Ping the API to check if it's available.

        Returns:
            Response string
        """
        url = f"{self.base_url}/v1/ping"
        response = self.session.get(url)
        return self._handle_response(response)

    def generate_crypto_key(self) -> str:
        """
        Generate a crypto key.

        Returns:
            Generated crypto key
        """
        url = f"{self.base_url}/v1/secrets/generate-crypto-key"
        response = self.session.get(url)
        return self._handle_response(response)
