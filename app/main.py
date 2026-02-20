from fastapi import FastAPI
from app.api.incidents import router as incidents_router
from app.api.sync import router as sync_router
from app.api.analytics import router as analytics_router

app = FastAPI(title="UK Transport Reliability API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(incidents_router)
app.include_router(sync_router)
app.include_router(analytics_router)