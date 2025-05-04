from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from vector_bridge.schema.helpers.enums import MessageStorageMode
from vector_bridge.schema.helpers.weaviate_schema import WeaviateInternals


class AICredentials(BaseModel):
    api_key: str = Field(default="")


class AzureAICredentials(BaseModel):
    api_key: str = Field(default="")
    api_version: str = Field(default="2024-10-21")
    endpoint: str = Field(default="")


class Weaviate(BaseModel):
    api_key: str = Field(default="")
    url: str = Field(default="")
    max_similarity_distance: float = Field(default=0.75)
    internals: WeaviateInternals


DEFAULT_INTEGRATION = "default"


class AI(BaseModel):
    open_ai: AICredentials
    azure_open_ai: AzureAICredentials
    anthropic: AICredentials
    deepseek: AICredentials


class DB(BaseModel):
    weaviate: Weaviate
    message_storage_mode: MessageStorageMode = Field(default=MessageStorageMode.DYNAMO_DB)


class Integration(BaseModel):
    organization_id: str
    integration_id: str
    integration_name: str
    integration_description: str
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str
    published: bool
    db: DB
    ai: AI
    env_variables: dict

    @property
    def uuid(self):
        return self.integration_id


class IntegrationCreate(BaseModel):
    integration_name: str
    integration_description: str
    openai_api_key: str
    # azure_openai_api_key: str = Field(default="")
    # azure_openai_endpoint: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    deepseek_api_key: str = Field(default="")
    weaviate_url: str
    weaviate_api_key: str


class IntegrationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    integration_name: Optional[str] = None
    integration_description: Optional[str] = None
    published: Optional[bool] = None

    db: Optional[DB] = None
    env_variables: Optional[Dict[str, str]] = None
