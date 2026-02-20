from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class IncidentBase(BaseModel):
    source: str = Field(default="user", max_length=20)

    mode: Optional[str] = Field(default=None, max_length=20)
    line_id: Optional[str] = Field(default=None, max_length=64)
    line_name: Optional[str] = Field(default=None, max_length=128)

    station_id: Optional[str] = Field(default=None, max_length=64)
    station_name: Optional[str] = Field(default=None, max_length=128)

    occurred_at: datetime
    severity: int = Field(default=1, ge=1, le=5)
    delay_minutes: Optional[int] = Field(default=None, ge=0)

    reason_code: Optional[str] = Field(default=None, max_length=64)
    reason_text: Optional[str] = Field(default=None, max_length=256)

    status: str = Field(default="open", max_length=20)

    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None

    raw_payload: Optional[dict[str, Any]] = None
    fingerprint: str = Field(..., max_length=64)


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    # PATCH：所有字段可选
    source: Optional[str] = Field(default=None, max_length=20)

    mode: Optional[str] = Field(default=None, max_length=20)
    line_id: Optional[str] = Field(default=None, max_length=64)
    line_name: Optional[str] = Field(default=None, max_length=128)

    station_id: Optional[str] = Field(default=None, max_length=64)
    station_name: Optional[str] = Field(default=None, max_length=128)

    occurred_at: Optional[datetime] = None
    severity: Optional[int] = Field(default=None, ge=1, le=5)
    delay_minutes: Optional[int] = Field(default=None, ge=0)

    reason_code: Optional[str] = Field(default=None, max_length=64)
    reason_text: Optional[str] = Field(default=None, max_length=256)

    status: Optional[str] = Field(default=None, max_length=20)

    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None

    raw_payload: Optional[dict[str, Any]] = None


class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reported_at: datetime