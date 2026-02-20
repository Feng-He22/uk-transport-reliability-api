import os
import httpx
from mcp.server.fastmcp import FastMCP

# In Docker, use http://api:8000 ; locally use http://localhost:8000
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

mcp = FastMCP("UK Transport Reliability MCP")

async def _get(path: str, params: dict):
    url = f"{API_BASE}{path}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()

@mcp.tool()
async def get_line_reliability(line_id: str, from_: str, to: str, formula: str = "v1", k: float = 20.0):
    """Return reliability score for a line within [from_, to] (ISO8601 strings)."""
    return await _get("/analytics/reliability", {"line_id": line_id, "from": from_, "to": to, "formula": formula, "k": k})

@mcp.tool()
async def get_delay_heatmap(line_id: str, from_: str, to: str, bucket: str = "hour"):
    """Return heatmap buckets for incident distribution (bucket=hour|dayofweek)."""
    return await _get("/analytics/heatmap", {"line_id": line_id, "from": from_, "to": to, "bucket": bucket})

@mcp.tool()
async def detect_anomalies(line_id: str, from_: str, to: str, window_days: int = 7, z_threshold: float = 1.2):
    """Detect anomaly days based on rolling z-score over weighted impact."""
    return await _get(
        "/analytics/anomalies",
        {"line_id": line_id, "from": from_, "to": to, "window_days": window_days, "z_threshold": z_threshold},
    )

@mcp.tool()
async def recommend_journey(line_id: str, from_: str, to: str):
    """
    Explainable recommendation combining reliability + heatmap + anomalies.
    Returns both human-readable text and structured evidence.
    """
    rel = await get_line_reliability(line_id, from_, to,k=100.0)
    hm = await get_delay_heatmap(line_id, from_, to, bucket="hour")
    an = await detect_anomalies(line_id, from_, to, window_days=7, z_threshold=1.2)

    buckets = hm.get("data", [])
    nonzero = [b for b in buckets if (b.get("count", 0) or 0) > 0]
    worst = sorted(nonzero, key=lambda x: x.get("weighted_impact", 0), reverse=True)[:3]
    best = sorted(nonzero, key=lambda x: x.get("weighted_impact", 0))[:3]

    worst_hours = [b["bucket"] for b in worst]
    best_hours = [b["bucket"] for b in best]
    anomaly_dates = [x["date"] for x in (an.get("anomalies") or [])[:5]]

    data = {
        "line_id": line_id,
        "window": {"from": from_, "to": to},
        "reliability_score": rel.get("score"),
        "prefer_hours": best_hours,
        "avoid_hours": worst_hours,
        "anomaly_days": anomaly_dates,
        "evidence": {
            "reliability": rel,
            "heatmap_top3_worst": worst,
            "heatmap_top3_best": best,
            "anomalies": an.get("anomalies", []),
        },
    }

    text = (
        f"Line '{line_id}' reliability score: {data['reliability_score']}. "
        f"Prefer hours {best_hours}; avoid hours {worst_hours}. "
        + (f"Flagged anomaly days: {anomaly_dates}." if anomaly_dates else "No strong anomaly days detected.")
    )

    return {"text": text, "data": data}

if __name__ == "__main__":
    # MCP stdio server
    mcp.run()