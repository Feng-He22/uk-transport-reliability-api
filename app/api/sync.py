from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.incident import IncidentCreate
from app.services import incidents as incident_svc
from app.services.tfl import fetch_tfl_line_status, normalize_tfl_line_status

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/tfl")
async def sync_tfl(db: Session = Depends(get_db)):
    try:
        payload = await fetch_tfl_line_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TfL fetch failed: {e}")

    normalized = normalize_tfl_line_status(payload)

    created = 0
    skipped = 0

    for item in normalized:
        res = incident_svc.create_incident(db, IncidentCreate(**item))
        if res is None:
            skipped += 1
        else:
            created += 1

    return {
        "source": "tfl",
        "fetched_lines": len(payload),
        "created_incidents": created,
        "skipped_duplicates": skipped,
        "note": "Only non-Good Service statuses are stored as incidents.",
    }