from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.services.analytics import heatmap 
from app.services.analytics import anomalies

from app.db.session import get_db
from app.services.analytics import reliability_v1

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/reliability")
def get_reliability(
    line_id: str = Query(..., min_length=1),
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    formula: str = Query("v1"),
    k: float = Query(20.0, gt=0),
    db: Session = Depends(get_db),
):
    if to < from_:
        raise HTTPException(status_code=400, detail="'to' must be >= 'from'")
    if formula != "v1":
        raise HTTPException(status_code=400, detail="Only formula=v1 is supported for now")
    return reliability_v1(db, line_id=line_id, from_=from_, to=to, k=k)

@router.get("/heatmap")
def get_heatmap(
    line_id: str = Query(..., min_length=1),
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    bucket: str = Query("hour"),
    db: Session = Depends(get_db),
):
    if to < from_:
        raise HTTPException(status_code=400, detail="'to' must be >= 'from'")
    try:
        return heatmap(db, line_id=line_id, from_=from_, to=to, bucket=bucket)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/anomalies")
def get_anomalies(
    line_id: str = Query(..., min_length=1),
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    window_days: int = Query(7, ge=2, le=60),
    z_threshold: float = Query(2.0, gt=0),
    db: Session = Depends(get_db),
):
    if to < from_:
        raise HTTPException(status_code=400, detail="'to' must be >= 'from'")
    return anomalies(db, line_id=line_id, from_=from_, to=to, window_days=window_days, z_threshold=z_threshold)