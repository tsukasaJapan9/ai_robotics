from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    module: str
    media_type: str | None = None
