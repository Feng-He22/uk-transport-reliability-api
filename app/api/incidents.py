from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate
from app.services import incidents as svc

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    return svc.create_incident(db, payload)

@router.get("", response_model=list[IncidentOut])
def list_incidents(
    db: Session = Depends(get_db),
    source: str | None = None,
    line_id: str | None = None,
    station_id: str | None = None,
    status_: str | None = Query(default=None, alias="status"),
    occurred_from: datetime | None = Query(default=None),
    occurred_to: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    return svc.list_incidents(
        db,
        source=source,
        line_id=line_id,
        station_id=station_id,
        status=status_,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
        skip=skip,
        limit=limit,
    )

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: UUID, db: Session = Depends(get_db)):
    obj = svc.get_incident(db, incident_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Incident not found")
    return obj

@router.patch("/{incident_id}", response_model=IncidentOut)
def patch_incident(incident_id: UUID, payload: IncidentUpdate, db: Session = Depends(get_db)):
    obj = svc.get_incident(db, incident_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Incident not found")
    return svc.update_incident(db, obj, payload)

@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_incident(incident_id: UUID, db: Session = Depends(get_db)):
    obj = svc.get_incident(db, incident_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Incident not found")
    svc.delete_incident(db, obj)
    return None