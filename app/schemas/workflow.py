from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkflowCreate(BaseModel):
    workflow_name: str = Field(..., min_length=1, max_length=255)
    input_data: dict


class WorkflowResponse(BaseModel):
    id: int
    workflow_name: str
    input_data: dict
    status: str
    current_state: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)