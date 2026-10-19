from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: HttpUrl
    is_active: bool = True


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    is_active: bool
    created_at: datetime
