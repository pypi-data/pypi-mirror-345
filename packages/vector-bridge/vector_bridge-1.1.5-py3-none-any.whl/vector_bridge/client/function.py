from typing import Any, Dict

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.functions import StreamingResponse


class FunctionClient:
    """User client for function endpoints that require an API key."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def run_function(
        self,
        function_name: str,
        function_args: Dict[str, Any],
        integration_name: str = None,
        instruction_name: str = "default",
        agent_name: str = "default",
    ) -> Any:
        """
        Run a function.

        Args:
            function_name: The name of the function to run
            function_args: Arguments to pass to the function
            integration_name: The name of the Integration
            instruction_name: The name of the instruction
            agent_name: The name of the agent

        Returns:
            Function execution result
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/stream/function/{function_name}/run"
        params = {
            "integration_name": integration_name,
            "instruction_name": instruction_name,
            "agent_name": agent_name,
        }

        headers = self.client._get_api_key_headers(self.client.api_key)
        response = self.client.session.post(url, headers=headers, params=params, json=function_args, stream=True)
        if response.status_code >= 400:
            self.client._handle_response(response)

        return StreamingResponse(response).response()
