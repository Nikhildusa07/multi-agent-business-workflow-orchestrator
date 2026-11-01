from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApprovalCreate(BaseModel):
    workflow_id: int
    task_id: int | None = None
    requested_by: str


class ApprovalAction(BaseModel):
    approved_by: str


class ApprovalResponse(BaseModel):
    id: int
    workflow_id: int
    task_id: int | None
    requested_by: str
    status: str
    approved_by: str | None
    created_at: datetime
    approved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)