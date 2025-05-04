from datetime import datetime
from typing import Optional

from dateutil.parser import isoparse
from pydantic import BaseModel, Field


class APIKey(BaseModel):
    hash_key: Optional[str] = Field(default=None)
    organization_id: str
    api_key: str
    key_name: str
    integration_name: str
    user_id: str = Field(default="")
    security_group_id: str = Field(default="")
    expire_timestamp: str
    monthly_request_limit: int
    created_by: str
    created_at: str

    def is_expired(self) -> bool:
        """Check if the API key is expired based on the expire_timestamp."""
        current_time = datetime.utcnow()
        expiration_time = isoparse(self.expire_timestamp)
        return current_time >= expiration_time


class APIKeyCreate(BaseModel):
    key_name: str
    integration_name: str
    user_id: str = Field(default="")
    security_group_id: str = Field(default="")
    expire_days: int
    monthly_request_limit: int
