from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import predict, search, report, chat, data
from utils.config import settings
from database.sqlite_db import engine, Base
from loguru import logger

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sentinel AI",
    description="Version 2.0 — AI-Powered Military Intelligence Decision Support Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(predict.router, prefix="/api/v1/predict", tags=["Risk Assessment"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Incident Search"])
app.include_router(report.router, prefix="/api/v1/report", tags=["Report Generation"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Intelligence Copilot"])
app.include_router(data.router, prefix="/api/v1/data", tags=["Dataset & Analytics"])


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "operational",
        "system": "Sentinel AI",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["System"])
def root():
    return {
        "system": "Sentinel AI",
        "version": "2.0.0",
        "description": "AI-Powered Military Intelligence Decision Support Platform",
        "docs": "/docs"
    }


logger.info("Sentinel AI V2.0 API initialized.")
