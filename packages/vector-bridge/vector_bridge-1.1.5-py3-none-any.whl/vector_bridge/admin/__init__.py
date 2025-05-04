from vector_bridge import VectorBridgeClient
from vector_bridge.admin.ai_knowledge import AIKnowledgeAdmin
from vector_bridge.admin.api_keys import APIKeysAdmin
from vector_bridge.admin.chat import ChatAdmin
from vector_bridge.admin.functions import FunctionsAdmin
from vector_bridge.admin.instructions import InstructionsAdmin
from vector_bridge.admin.integrations import IntegrationsAdmin
from vector_bridge.admin.logs import LogsAdmin
from vector_bridge.admin.message import MessageAdmin
from vector_bridge.admin.notifications import NotificationsAdmin
from vector_bridge.admin.organization import OrganizationAdmin
from vector_bridge.admin.query import QueryAdmin
from vector_bridge.admin.security_groups import SecurityGroupsAdmin
from vector_bridge.admin.settings import SettingsAdmin
from vector_bridge.admin.usage import UsageAdmin
from vector_bridge.admin.user import UserAdmin
from vector_bridge.admin.vector_db import VectorDBAdmin
from vector_bridge.admin.workflows import WorkflowsAdmin


class AdminClient:
    """Admin client providing access to all admin endpoints that require authentication."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

        # Initialize admin subclients
        self.settings = SettingsAdmin(client)
        self.logs = LogsAdmin(client)
        self.notifications = NotificationsAdmin(client)
        self.usage = UsageAdmin(client)
        self.user = UserAdmin(client)
        self.organization = OrganizationAdmin(client)
        self.security_groups = SecurityGroupsAdmin(client)
        self.integrations = IntegrationsAdmin(client)
        self.instructions = InstructionsAdmin(client)
        self.functions = FunctionsAdmin(client)
        self.workflows = WorkflowsAdmin(client)
        self.api_keys = APIKeysAdmin(client)
        self.chat = ChatAdmin(client)
        self.message = MessageAdmin(client)
        self.ai_knowledge = AIKnowledgeAdmin(client)
        self.vector_db = VectorDBAdmin(client)
        self.queries = QueryAdmin(client)
