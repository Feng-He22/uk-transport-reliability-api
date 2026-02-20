from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
import hashlib

TFL_LINE_STATUS_URL = "https://api.tfl.gov.uk/Line/Mode/tube/Status"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def normalize_tfl_line_status(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    把 TfL Line Status 变成 IncidentCreate 需要的字段字典（可直接入库）
    设计思路：
    - 每条 lineStatus 视为一个 incident（如果 status 不是 Good Service）
    - reason_text 尽量取 disruption description / statusSeverityDescription
    - delay_minutes TfL 不直接给 -> 先留空（None）
    - raw_payload 保存原始，便于追溯（加分点）
    """
    incidents: list[dict[str, Any]] = []
    occurred_at = _now_utc()
    fp = make_fingerprint("tfl", line_id, str(reason), occurred_at)

    for line in payload:
        line_id = line.get("id")
        line_name = line.get("name")
        statuses = line.get("lineStatuses") or []

        for st in statuses:
            desc = st.get("statusSeverityDescription")  # e.g. "Good Service"
            # Good Service 就不入库（你也可以选择入库但会噪声很大）
            if not desc or desc.lower() == "good service":
                continue

            disruption = st.get("disruption") or {}
            reason = disruption.get("description") or st.get("reason") or desc

            # severity：用 TfL statusSeverity（数值越小越严重，通常 10=Good Service）
            # 我们映射到 1-5：严重(1) -> 轻微(5)
            tfl_sev = st.get("statusSeverity")
            mapped_sev = 3
            if isinstance(tfl_sev, int):
                if tfl_sev <= 3:
                    mapped_sev = 1
                elif tfl_sev <= 6:
                    mapped_sev = 2
                elif tfl_sev <= 9:
                    mapped_sev = 3
                else:
                    mapped_sev = 4

            incidents.append(
                {
                    "source": "tfl",
                    "mode": "tube",
                    "line_id": line_id,
                    "line_name": line_name,
                    "station_id": None,
                    "station_name": None,
                    "occurred_at": occurred_at,
                    "severity": mapped_sev,
                    "delay_minutes": None,
                    "reason_code": "tfl_status",
                    "reason_text": str(reason)[:256],
                    "status": "open",
                    "geo_lat": None,
                    "geo_lng": None,
                    "raw_payload": {"line": line, "lineStatus": st},
                    "fingerprint": fp,
                }
            )

    return incidents


async def fetch_tfl_line_status() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(TFL_LINE_STATUS_URL)
        r.raise_for_status()
        return r.json()
    
def make_fingerprint(source: str, line_id: str | None, reason: str, occurred_at: datetime) -> str:
    # 用分钟粒度，避免同一条状态每秒变化导致去重失败
    minute = occurred_at.replace(second=0, microsecond=0).isoformat()
    raw = f"{source}|{line_id}|{reason}|{minute}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

created = 0
skipped = 0
for item in normalized:
    res = incident_svc.create_incident(db, IncidentCreate(**item))
    if res:
        created += 1
    else:
        skipped += 1

return {"created_incidents": created, "skipped_duplicates": skipped, ...}