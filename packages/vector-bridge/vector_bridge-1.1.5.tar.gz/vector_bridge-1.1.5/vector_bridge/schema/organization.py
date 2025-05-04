from pydantic import BaseModel, ConfigDict, Field


class Organization(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_name: str
    ai_agent_id: str = Field(default="")
    s3_storage_used_bytes: int = Field(default=0)
    created_by: str
    created_at: str
    deleted: bool = Field(default=False)

    @property
    def uuid(self):
        return self.id
