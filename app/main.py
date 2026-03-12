from fastapi import FastAPI

from app.api.incidents import router as incidents_router
from app.api.sync import router as sync_router
from app.api.analytics import router as analytics_router
from app.api.devtools import router as dev_router
from app.auth.router import router as auth_router
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.db.session import engine
from app.db.base import Base

from app.models.user import User  

app = FastAPI(title="UK Transport Reliability API", version="0.1.0")

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


app.add_middleware(SecurityHeadersMiddleware)

app.include_router(auth_router)
app.include_router(incidents_router)
app.include_router(sync_router)
app.include_router(analytics_router)
app.include_router(dev_router)