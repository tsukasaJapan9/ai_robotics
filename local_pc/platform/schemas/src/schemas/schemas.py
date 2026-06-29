from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    module: str
    media_type: str | None = None


class InferData(BaseModel):
    type: str  # "image" | "audio" | "text"
    content: str  # base64 encoded or plain text
    media_type: str  # e.g. "image/jpeg"


class InferRequest(BaseModel):
    prompt: str
    json_schema: dict
    data: InferData | None = None


class InferResponse(BaseModel):
    result: dict
    model: str
    timestamp: str


class ActionRequest(BaseModel):
    type: str
    params: dict = {}


class ActionResponse(BaseModel):
    ok: bool
