from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import redis

from app.api.workflows import router as workflow_router
from app.api.approvals import router as approval_router
from app.api.audit_logs import router as audit_logs_router

from app.core.config import settings
from app.database.connection import engine


app = FastAPI(
    title="Multi-Agent Business Workflow Orchestrator",
    description="AI-powered multi-agent workflow orchestration platform",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(workflow_router)
app.include_router(approval_router)
app.include_router(audit_logs_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Multi-Agent Workflow Orchestrator is running",
        "status": "healthy",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    postgres_status = "down"
    postgres_message = "Database connection failed"

    redis_status = "down"
    redis_message = "Redis connection failed"

    # PostgreSQL
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        postgres_status = "healthy"
        postgres_message = "Database connection successful"

    except Exception as exc:
        postgres_message = str(exc)

    # Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()

        redis_status = "healthy"
        redis_message = "Redis connection successful"

        redis_client.close()

    except Exception as exc:
        redis_message = str(exc)

    overall_status = (
        "healthy"
        if postgres_status == "healthy"
        and redis_status == "healthy"
        else "degraded"
    )

    return {
        "status": overall_status,
        "environment": settings.APP_ENV,
        "services": {
            "postgresql": {
                "status": postgres_status,
                "message": postgres_message,
            },
            "redis": {
                "status": redis_status,
                "message": redis_message,
            },
        },
    }