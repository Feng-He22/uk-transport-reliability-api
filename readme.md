# UK Transport Reliability API (MCP-ready)

A RESTful API for collecting and analysing transport disruption incidents in the UK.  
Includes Incident CRUD, TfL (Tube) status ingestion, analytics endpoints (reliability score, time heatmap, anomaly detection), and a **dev-only demo seeder** to generate realistic data for presentations.

---

## Features

### Core
- **Incident CRUD**: create, list (with filters), fetch by id, patch, delete
- **PostgreSQL + Alembic migrations**
- **OpenAPI/Swagger docs** at `/docs`

### Data ingestion
- **TfL Tube Line Status sync**: `POST /sync/tfl`  
  Stores only *non–Good Service* statuses as incidents.

### Analytics
- **Reliability score**: `GET /analytics/reliability`
- **Delay/incident time heatmap**: `GET /analytics/heatmap`
- **Anomaly detection (rolling z-score)**: `GET /analytics/anomalies`

### Dev tools (demo)
- **Seed demo incidents**: `POST /dev/seed`  
  Generates multi-day incidents with peak-hour bias so heatmaps/anomalies are visible in demos.

---

## Tech Stack
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL (Docker)
- pytest

---

## Project Structure (high level)

```
app/
  api/            # FastAPI route modules (incidents, sync, analytics, devtools)
  core/           # config/settings
  db/             # SQLAlchemy engine/session/base
  models/         # ORM models
  schemas/        # Pydantic schemas
  services/       # business logic (CRUD, TfL normalization, analytics)
tests/
alembic/
docker-compose.yml
Dockerfile
requirements.txt
```

---

## Quick Start (Docker)

### 1) Start API + Database
```bash
docker compose up --build
```

Open:
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 2) Run migrations
```bash
docker compose exec api alembic upgrade head
```

### 3) Run tests
```bash
docker compose exec api pytest -q
```

---

## API Usage (Demo Flow)

### A) Seed demo data (recommended for presentations)
1. `POST /dev/seed`
   - Example: `line_id=piccadilly&days=30&per_day=5`

Then call:
- `GET /analytics/heatmap?line_id=piccadilly&from=2026-01-20T00:00:00Z&to=2026-02-21T23:59:59Z&bucket=hour`
- `GET /analytics/anomalies?line_id=piccadilly&from=2026-01-20T00:00:00Z&to=2026-02-21T23:59:59Z&window_days=7&z_threshold=1.2`
- `GET /analytics/reliability?line_id=piccadilly&from=2026-01-20T00:00:00Z&to=2026-02-21T23:59:59Z&formula=v1`

### B) Sync real TfL data (Tube)
1. `POST /sync/tfl`
2. View stored incidents:
   - `GET /incidents?source=tfl&limit=50`
3. Run analytics for a specific `line_id` found in the incidents list.

---

## Endpoints Summary

### System
- `GET /health`

### Incidents (CRUD)
- `POST /incidents`
- `GET /incidents` (filters: `source`, `line_id`, `station_id`, `status`, `occurred_from`, `occurred_to`, `skip`, `limit`)
- `GET /incidents/{incident_id}`
- `PATCH /incidents/{incident_id}`
- `DELETE /incidents/{incident_id}`

### Sync
- `POST /sync/tfl`

### Analytics
- `GET /analytics/reliability`
- `GET /analytics/heatmap`
- `GET /analytics/anomalies`

### Dev tools
- `POST /dev/seed` *(development/demo only)*

---

## Configuration

Environment variables (used in Docker):
- `APP_ENV` (default: `dev`)
- `DATABASE_URL` (default: provided in docker-compose)

Example `.env.example`:
```env
APP_ENV=dev
DATABASE_URL=postgresql+psycopg2://app:app@db:5432/ukrel
```

---

## Notes
- The `/dev/*` endpoints are intended for **demo/testing only** and should not be enabled in production.
- TfL ingestion stores only non–Good Service statuses to reduce noise.

---

## License
For coursework use.
