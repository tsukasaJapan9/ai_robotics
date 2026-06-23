from typing import Any
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    module: str
    media_type: str | None = None


class ErrorResponse(BaseModel):
    error: str


class InferData(BaseModel):
    type: str  # "image" | "audio" | "text"
    content: str  # base64 encoded or plain text
    media_type: str


class InferRequest(BaseModel):
    prompt: str
    schema: dict[str, Any] = {}
    data: InferData | None = None


class InferResponse(BaseModel):
    result: Any
    model: str
    timestamp: str


class ActionRequest(BaseModel):
    type: str
    params: dict[str, Any] = {}


class ActionResponse(BaseModel):
    ok: bool


class MoveParams(BaseModel):
    x: int | None = None
    y: int | None = None
