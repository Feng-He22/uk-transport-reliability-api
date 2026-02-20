import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(20), default="user", index=True)

    mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    line_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    line_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    station_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    station_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    severity: Mapped[int] = mapped_column(Integer, default=1)
    delay_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    reason_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason_text: Mapped[str | None] = mapped_column(String(256), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="open", index=True)

    geo_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True, index=True)