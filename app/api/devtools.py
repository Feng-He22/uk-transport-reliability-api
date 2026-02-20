from datetime import datetime, timedelta, timezone
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.tfl import make_fingerprint

from app.core.config import settings
from app.db.session import get_db
from app.schemas.incident import IncidentCreate
from app.services import incidents as incident_svc

router = APIRouter(prefix="/dev", tags=["devtools"])

@router.post("/seed")
def seed_demo_data(
    line_id: str = "piccadilly",
    days: int = 30,
    per_day: int = 5,
    db: Session = Depends(get_db),
):
    if settings.app_env != "dev":
        raise HTTPException(status_code=403, detail="Seeding is only allowed in dev")

    now = datetime.now(timezone.utc)
    created = 0

    # 模拟：早晚高峰更容易出问题（8-10, 17-19）
    peak_hours = [8, 9, 10, 17, 18, 19]
    off_hours = [0, 1, 2, 3, 12, 13, 14, 22, 23]

    for d in range(days):
        day = now - timedelta(days=d)
        for _ in range(per_day):
            hour = random.choice(peak_hours + peak_hours + off_hours)  # 高峰加权
            minute = random.randint(0, 59)
            occurred_at = day.replace(hour=hour, minute=minute, second=0, microsecond=0)

            sev = random.choice([2, 3, 3, 4])  # 多数中等
            # 偶尔来一次严重异常（用于 anomalies）
            if random.random() < 0.08:
                sev = 1

            payload = IncidentCreate(
                source="demo",
                mode="tube",
                line_id=line_id,
                line_name=line_id.title(),
                station_id=None,
                station_name=None,
                occurred_at=occurred_at,
                severity=sev,
                delay_minutes=None,
                reason_code="demo_seed",
                reason_text="Demo seeded incident",
                status="open",
                geo_lat=None,
                geo_lng=None,
                raw_payload={"seed": True},
                fingerprint=make_fingerprint("demo", line_id, "demo_seed", occurred_at),
            )
            incident_svc.create_incident(db, payload)
            created += 1

    return {"line_id": line_id, "days": days, "per_day": per_day, "created": created}