from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    name: str | None = None
    message: str
    semantic: Dict[Any, Any] | None = None
    errors: List[str] | None


class PersonalProfile(BaseModel):
    cpf_number: str = Field(serialization_alias="cpfNumber")


class ProfileRequest(BaseModel):
    ref: str
    sdk_token: str = Field(serialization_alias="sdkToken")
    personal: PersonalProfile


class ProfileData(BaseModel):
    created: bool


class ProfileResponse(BaseModel):
    data: ProfileData


class ProfileFlowStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_MANUAL_ACTION = "WAITING_MANUAL_ACTION"
    FINISHED = "FINISHED"
    INVALID = "INVALID"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"


class FlowStageStatus(str, Enum):
    FINISHED = "FINISHED"


class TrustLevel(str, Enum):
    HIGH = "HIGH"


class FlowStageType(str, Enum):
    LIVENESS = "LIVENESS"
    FACELINK = "FACELINK"


class LivenessStageResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    smile_images: List[str] = Field(validation_alias="smileImages")
    default_images: List[str] = Field(validation_alias="defaultImages")
    confidence: float
    error: str | None = None


class FacelinkStageResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    last_profile_image_face: str = Field(validation_alias="lastProfileImageFace")
    cpf: str
    message: str | None = None
    trust_level: str = Field(validation_alias="trustLevel")
    error_message: str | None = Field(validation_alias="errorMessage", default=None)


class FlowStage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    stage_id: str = Field(validation_alias="stageId")
    stage_ref: str = Field(validation_alias="stageRef")
    type: str
    status: str
    conditions: List[str]
    slug: str | None = None
    title: str
    updated_at: datetime = Field(validation_alias="updatedAt")
    response: LivenessStageResponse | FacelinkStageResponse | None = None


class FlowInput(BaseModel):
    flow_id: str = Field(validation_alias="flowId")
    provider_id: str = Field(validation_alias="profileRef")
    trigger_type: str = Field(validation_alias="triggerType")


class ProfileFlow(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    created_at: datetime = Field(validation_alias="createdAt")
    stages: List[FlowStage]
    status: ProfileFlowStatus
    input: FlowInput
    trigger_type: str = Field(validation_alias="triggerType")
    provider_id: str = Field(validation_alias="profileRef")
    flow_version: int | None = Field(validation_alias="flowVersion", default=None)
    flow_name: str = Field(validation_alias="flowName")
    flow_id: str = Field(validation_alias="flowId")
    updated_at: datetime = Field(validation_alias="updatedAt")


class Pagination(BaseModel):
    limit: int
    page: int
    total: int
    pages: int


class ProfileFlowsResponse(BaseModel):
    data: List[ProfileFlow]
    pagination: Pagination


class StartProfileFlowData(BaseModel):
    created: bool
    profile_flow_id: str = Field(validation_alias="profileFlowId")


class StartProfileFlowResponse(BaseModel):
    data: StartProfileFlowData
