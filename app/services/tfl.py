from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import hashlib

import httpx

TFL_LINE_STATUS_URL = "https://api.tfl.gov.uk/Line/Mode/tube/Status"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def make_fingerprint(source: str, line_id: str | None, reason: str, occurred_at: datetime) -> str:
    # 用分钟粒度，避免同一条状态每秒变化导致去重失败
    minute = occurred_at.replace(second=0, microsecond=0).isoformat()
    raw = f"{source}|{line_id}|{reason}|{minute}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_tfl_line_status(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    TfL Line Status -> IncidentCreate dict list
    - 只保存非 Good Service
    - delay_minutes TfL 不提供 -> None
    - raw_payload 保留原始数据
    - fingerprint 用于去重（unique）
    """
    incidents: list[dict[str, Any]] = []
    occurred_at = _now_utc()

    for line in payload:
        line_id = line.get("id")
        line_name = line.get("name")
        statuses = line.get("lineStatuses") or []

        for st in statuses:
            desc = st.get("statusSeverityDescription")  # e.g. "Good Service"
            if not desc or desc.lower() == "good service":
                continue

            disruption = st.get("disruption") or {}
            reason = disruption.get("description") or st.get("reason") or desc

            # severity 映射到 1-5（1 最严重）
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

            fp = make_fingerprint("tfl", line_id, str(reason), occurred_at)

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