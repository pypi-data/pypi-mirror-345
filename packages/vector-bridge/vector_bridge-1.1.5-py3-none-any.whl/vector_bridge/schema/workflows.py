from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    ON_HOLD = "on_hold"


class WorkflowCache(BaseModel):
    method_name: str
    args: List
    kwargs: Dict
    started_at: str
    processed_at: str
    processing_time: float
    logs: Optional[str] = ""
    traceback: Optional[str] = ""
    result: Optional[str] = ""


class WorkflowBase(BaseModel):
    workflow_id: str
    workflow_name: str
    description: str
    cache: Dict[str, WorkflowCache] = Field(default_factory=dict)
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING)


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    cache: Dict[str, WorkflowCache] = Field(default_factory=dict)
    status: Optional[WorkflowStatus] = Field(default=None)


class WorkflowData(WorkflowBase):
    integration_id: str
    expire_at: int
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str


class PaginatedWorkflows(BaseModel):
    workflows: List[WorkflowData] = Field(default_factory=list)
    limit: int
    last_evaluated_key: Optional[str] = None
    has_more: bool = False
