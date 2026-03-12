# UK Transport Reliability API 

A data-driven REST API for collecting, storing, and analysing UK transport disruption incidents. The project combines standard CRUD functionality with external data ingestion, database-backed persistence, analytics endpoints, and MCP-compatible tooling for agent-oriented access.

This coursework was developed for **COMP3011 Web Services and Web Data**.

---

## Project Overview

The API is designed around transport reliability analysis rather than simple record storage. In addition to incident management, it supports:

- transport incident **CRUD** operations backed by a relational database
- **TfL Tube line status ingestion** for real-world disruption data
- reliability analytics for a selected line and time period
- hourly heatmap aggregation for disruption patterns
- anomaly detection over incident activity
- an **MCP-ready interface** for agent-style tool calling and demonstration

The system is intended to demonstrate both core web API engineering and a more creative, analytics-oriented extension beyond minimum coursework requirements.

---

## Live Deployment

A live deployment of the API is available on PythonAnywhere:

- **Base URL:** `https://meowcolate.pythonanywhere.com`
- **Swagger UI:** `https://meowcolate.pythonanywhere.com/docs`
- **OpenAPI JSON:** `https://meowcolate.pythonanywhere.com/openapi.json`
- **Health check:** `https://meowcolate.pythonanywhere.com/health`

> Note: the production deployment on PythonAnywhere uses SQLite for simplicity of hosting, while local development via Docker uses PostgreSQL.

---

## Main Features

### Core API
- Create, read, update, and delete transport incidents
- Filter incidents by source, line, station, status, and time range
- Store data in PostgreSQL using SQLAlchemy ORM
- Manage schema changes with Alembic migrations

### External Data Integration
- `POST /sync/tfl`
- Pulls current TfL Tube status data
- Stores only non-`Good Service` entries as incidents to reduce noise

### Analytics
- `GET /analytics/reliability` — computes a reliability score for a line across a time window
- `GET /analytics/heatmap` — aggregates incidents by hour to reveal temporal patterns
- `GET /analytics/anomalies` — detects unusual disruption activity using a rolling z-score approach

### Demonstration Support
- `POST /dev/seed`
- Seeds realistic demo incidents across multiple days so analytics visualisations are easier to demonstrate in the oral exam

### Agent-Ready Extension
- MCP demo client support is included so the API can be exposed as callable tools for external agent workflows

---

## Tech Stack

- **Language:** Python 3
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Testing:** pytest
- **Containerisation:** Docker / Docker Compose

---

## Dataset / External Data Source

This project uses Transport for London operational status data:

- **Source:** TfL Unified API
- **Relevant dataset:** London Underground / line status data
- **URL:** https://api.tfl.gov.uk/

The TfL source is used during sync operations to transform live service-status disruptions into stored incident records for later querying and analysis.

---

## Repository Structure

```text
app/
  api/            # FastAPI route modules
  core/           # configuration and settings
  db/             # engine, session, base
  models/         # ORM models
  schemas/        # request/response schemas
  services/       # business logic, sync, analytics
mcp_server/       # MCP demo tooling
alembic/          # migration files
tests/            # test suite
docs/             # submitted coursework documents
Dockerfile
docker-compose.yml
requirements.txt
README.md
```

---

## Submitted Materials

The `docs/` folder contains the supporting coursework materials submitted alongside the repository.

Expected files:
- `docs/API_Documentation.pdf`
- `docs/Technical_Report.pdf`
- `docs/Presentation_Slides.pptx` or exported PDF equivalent
- supplementary appendix material for GenAI declaration where applicable

### Documentation Links
- **API Documentation (PDF):** `docs/API_Documentation.pdf`
- **Technical Report (PDF):** `docs/Technical_Report.pdf`
- **Presentation Slides:** `docs/Presentation_Slides.pptx`

> Update the filenames above if your final exported files use slightly different names.

---

## Quick Start

### 1. Start the API and database

```bash
docker compose up --build
```

### 2. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 3. Open the API locally

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 4. Run tests

```bash
docker compose exec api pytest -q
```

---

## Typical Demo Flow

### Option A: Seed demonstration data

This is the recommended presentation flow because it guarantees visible analytics output.

1. Seed data:

```bash
curl -X POST "http://localhost:8000/dev/seed?line_id=piccadilly&days=30&per_day=5"
```

2. Run analytics:

```bash
curl "http://localhost:8000/analytics/heatmap?line_id=piccadilly&from=2026-01-20T00:00:00Z&to=2026-02-21T23:59:59Z&bucket=hour"
```

```bash
curl "http://localhost:8000/analytics/anomalies?line_id=piccadilly&from=2026-01-20T00:00:00Z&to=2026-02-21T23:59:59Z&window_days=7&z_threshold=1.2"
```

```bash
curl "http://localhost:8000/analytics/reliability?line_id=piccadilly&from=2026-01-20T00:00:00Z&to=2026-02-21T23:59:59Z&formula=v1"
```

### Option B: Sync real TfL data

1. Trigger sync:

```bash
curl -X POST "http://localhost:8000/sync/tfl"
```

2. Inspect imported incidents:

```bash
curl "http://localhost:8000/incidents?source=tfl&limit=50"
```

3. Use a returned `line_id` in the analytics endpoints.

---

## API Endpoints Summary

### System
- `GET /health`

### Incidents (CRUD)
- `POST /incidents`
- `GET /incidents`
- `GET /incidents/{incident_id}`
- `PATCH /incidents/{incident_id}`
- `DELETE /incidents/{incident_id}`

Supported list filters include:
- `source`
- `line_id`
- `station_id`
- `status`
- `occurred_from`
- `occurred_to`
- `skip`
- `limit`

### Sync
- `POST /sync/tfl`

### Analytics
- `GET /analytics/reliability`
- `GET /analytics/heatmap`
- `GET /analytics/anomalies`

### Development / Demo
- `POST /dev/seed`

---

## Example Request and Response

### Example: Create an incident

**Request**

```http
POST /incidents
Content-Type: application/json
```

```json
{
  "source": "manual",
  "line_id": "piccadilly",
  "station_id": "kings-cross",
  "status": "Severe Delays",
  "description": "Signal failure causing service disruption",
  "occurred_at": "2026-02-01T08:30:00Z"
}
```

**Example response**

```json
{
  "id": 1,
  "source": "manual",
  "line_id": "piccadilly",
  "station_id": "kings-cross",
  "status": "Severe Delays",
  "description": "Signal failure causing service disruption",
  "occurred_at": "2026-02-01T08:30:00Z",
  "created_at": "2026-02-01T08:31:05Z"
}
```

---

## Configuration

Environment variables used in Docker:

- `APP_ENV` — application environment, default `dev`
- `DATABASE_URL` — database connection string

Example:

```env
APP_ENV=dev
DATABASE_URL=postgresql+psycopg2://app:app@db:5432/ukrel
```

---

## Authentication and Error Handling

### Authentication
This coursework prototype does **not require authentication**.

### Common Error Codes
- `200 OK` — successful read or calculation
- `201 Created` — successful resource creation
- `400 Bad Request` — invalid parameters or malformed input
- `404 Not Found` — requested resource does not exist
- `422 Unprocessable Entity` — validation failure
- `500 Internal Server Error` — unexpected server-side failure

Detailed request/response schemas and endpoint-specific behaviour are documented in the API documentation PDF.

---

## Testing

The project includes automated tests for core behaviour.

Run the test suite with:

```bash
docker compose exec api pytest -q
```

Testing is used to check endpoint behaviour, validation, and reliability of the implemented functionality.

---

## MCP Demo

To run the MCP-compatible demo client inside Docker:

```bash
docker compose exec -e API_BASE=http://api:8000 api python3 -m mcp_server.demo_call
```

This exposes the API through callable tool-style operations for demonstration of agent-ready integration.

---

## Notes

- `/dev/*` endpoints are intended only for demonstration and development use.
- TfL ingestion intentionally stores only disrupted service states rather than normal service states.
- The repository version should match the version demonstrated during the oral presentation.

---

## Coursework Context

This repository is the implementation component of the COMP3011 individual API development coursework. It is supported by separate API documentation, technical report, and presentation slides included in the submission materials.
