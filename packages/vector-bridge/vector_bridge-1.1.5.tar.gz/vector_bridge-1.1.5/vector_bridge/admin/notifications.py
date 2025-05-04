from typing import Optional

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.notifications import NotificationsList


class NotificationsAdmin:
    """Admin client for notifications endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def list_notifications(
        self,
        integration_name: str = None,
        limit: int = 25,
        last_evaluated_key: Optional[str] = None,
    ) -> NotificationsList:
        """
        List notifications.

        Args:
            integration_name: The name of the Integration
            limit: Number of notifications to return
            last_evaluated_key: Last evaluated key for pagination

        Returns:
            NotificationsList with notifications and pagination information
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/notifications"
        params = {"integration_name": integration_name, "limit": limit}
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response)
        return NotificationsList.model_validate(result)
