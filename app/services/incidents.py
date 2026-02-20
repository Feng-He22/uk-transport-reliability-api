from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate

def create_incident(db: Session, data: IncidentCreate) -> Incident:
    obj = Incident(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_incident(db: Session, incident_id: UUID) -> Optional[Incident]:
    return db.get(Incident, incident_id)

def list_incidents(
    db: Session,
    *,
    source: Optional[str] = None,
    line_id: Optional[str] = None,
    station_id: Optional[str] = None,
    status: Optional[str] = None,
    occurred_from: Optional[datetime] = None,
    occurred_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Incident]:
    stmt = select(Incident)

    if source:
        stmt = stmt.where(Incident.source == source)
    if line_id:
        stmt = stmt.where(Incident.line_id == line_id)
    if station_id:
        stmt = stmt.where(Incident.station_id == station_id)
    if status:
        stmt = stmt.where(Incident.status == status)
    if occurred_from:
        stmt = stmt.where(Incident.occurred_at >= occurred_from)
    if occurred_to:
        stmt = stmt.where(Incident.occurred_at <= occurred_to)

    stmt = stmt.order_by(Incident.occurred_at.desc()).offset(skip).limit(min(limit, 200))
    return list(db.scalars(stmt).all())

def update_incident(db: Session, obj: Incident, patch: IncidentUpdate) -> Incident:
    data = patch.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_incident(db: Session, obj: Incident) -> None:
    db.delete(obj)
    db.commit()

def create_incident(db: Session, data: IncidentCreate) -> Incident | None:
    obj = Incident(**data.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(obj)
    return obj