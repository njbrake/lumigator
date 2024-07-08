import datetime
from uuid import UUID

from pydantic import BaseModel

from mzai.schemas.deployments import DeploymentStatus


class GroundTruthDeploymentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class GroundTruthDeploymentResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: DeploymentStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class GroundTruthDeploymentLogsResponse(BaseModel):
    id: UUID
    status: DeploymentStatus
    logs: list[str]