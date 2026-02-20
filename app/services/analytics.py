from __future__ import annotations

from datetime import datetime
from math import exp
from typing import Optional
from collections import defaultdict
from statistics import mean, pstdev
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident


def reliability_v1(db: Session, *, line_id: str, from_: datetime, to: datetime, k: float = 20.0):
    stmt = (
        select(Incident)
        .where(Incident.line_id == line_id)
        .where(Incident.occurred_at >= from_)
        .where(Incident.occurred_at <= to)
    )
    rows = list(db.scalars(stmt).all())
    n = len(rows)

    # 权重：severity 1..5 -> weight 5..1
    weights = [(6 - (r.severity or 3)) for r in rows]
    w = sum(weights)

    score = 100.0 * exp(-w / k) if n > 0 else 100.0

    return {
        "line_id": line_id,
        "from": from_.isoformat(),
        "to": to.isoformat(),
        "formula": "v1",
        "score": round(score, 2),
        "sample_size": n,
        "weighted_impact": w,
        "explain": {
            "weight_rule": "weight = 6 - severity (severity 1..5 => weight 5..1)",
            "score_rule": "score = 100 * exp(-weighted_impact / k)",
            "k": k,
        },
    }

def heatmap(db: Session, *, line_id: str, from_: datetime, to: datetime, bucket: str = "hour"):
    stmt = (
        select(Incident)
        .where(Incident.line_id == line_id)
        .where(Incident.occurred_at >= from_)
        .where(Incident.occurred_at <= to)
    )
    rows = list(db.scalars(stmt).all())

    if bucket not in {"hour", "dayofweek"}:
        raise ValueError("bucket must be 'hour' or 'dayofweek'")

    # key: hour(0-23) or dow(0-6 Mon..Sun)
    counts = defaultdict(int)
    weighted = defaultdict(int)

    for r in rows:
        dt = r.occurred_at
        key = dt.hour if bucket == "hour" else dt.weekday()
        w = 6 - (r.severity or 3)
        counts[key] += 1
        weighted[key] += w

    # 输出固定长度桶，方便前端/报告画图
    if bucket == "hour":
        keys = list(range(24))
        label = "hour"
    else:
        keys = list(range(7))
        label = "dayofweek"

    data = []
    for k in keys:
        c = counts.get(k, 0)
        wi = weighted.get(k, 0)
        data.append({"bucket": k, "count": c, "weighted_impact": wi})

    return {
        "line_id": line_id,
        "from": from_.isoformat(),
        "to": to.isoformat(),
        "bucket_type": label,
        "data": data,
        "explain": {
            "count": "number of incidents in bucket",
            "weighted_impact": "sum(6 - severity) in bucket",
        },
    }

def anomalies(db: Session, *, line_id: str, from_: datetime, to: datetime, window_days: int = 7, z_threshold: float = 2.0):
    """
    按天聚合 incidents 的 weighted_impact，然后做 rolling z-score。
    """
    # 取全量行
    stmt = (
        select(Incident)
        .where(Incident.line_id == line_id)
        .where(Incident.occurred_at >= from_)
        .where(Incident.occurred_at <= to)
    )
    rows = list(db.scalars(stmt).all())

    # 按天聚合
    daily = {}
    for r in rows:
        d = r.occurred_at.date().isoformat()
        daily.setdefault(d, {"count": 0, "weighted_impact": 0})
        daily[d]["count"] += 1
        daily[d]["weighted_impact"] += (6 - (r.severity or 3))

    # 构造连续日期序列（没有事件的天也补 0）
    day0 = from_.date()
    dayN = to.date()
    series = []
    cur = day0
    while cur <= dayN:
        key = cur.isoformat()
        wi = daily.get(key, {}).get("weighted_impact", 0)
        c = daily.get(key, {}).get("count", 0)
        series.append({"date": key, "count": c, "weighted_impact": wi})
        cur = cur + timedelta(days=1)

    # rolling z-score
    out = []
    w = max(2, window_days)
    for i in range(len(series)):
        if i < w:
            continue
        hist = [x["weighted_impact"] for x in series[i - w : i]]
        mu = mean(hist)
        sigma = pstdev(hist)  # population std
        cur_val = series[i]["weighted_impact"]

        z = 0.0 if sigma == 0 else (cur_val - mu) / sigma
        if abs(z) >= z_threshold and cur_val != 0:
            out.append(
                {
                    "date": series[i]["date"],
                    "weighted_impact": cur_val,
                    "baseline_mean": round(mu, 3),
                    "baseline_std": round(sigma, 3),
                    "z_score": round(z, 3),
                }
            )

    return {
        "line_id": line_id,
        "from": from_.isoformat(),
        "to": to.isoformat(),
        "window_days": w,
        "z_threshold": z_threshold,
        "anomalies": out,
        "explain": {
            "aggregation": "daily weighted_impact = sum(6 - severity)",
            "method": "rolling z-score against previous window_days",
            "note": "requires enough history; days with 0 incidents are included as 0",
        },
    }