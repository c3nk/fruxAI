from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.database import init_db
from app.routes import health, crawl_jobs, metadata, reports, caltrans_bids, tenders
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting fruxAI API...")
    await init_db()
    yield
    logger.info("Shutting down fruxAI API...")

app = FastAPI(
    title="fruxAI API",
    version="1.0.0",
    description="Crawler orchestration and metadata management API for fruxAI.",
    lifespan=lifespan
)

# CORS for multiple frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health, prefix="/fruxAI/api/v1")
app.include_router(crawl_jobs, prefix="/fruxAI/api/v1")
app.include_router(metadata, prefix="/fruxAI/api/v1")
app.include_router(reports, prefix="/fruxAI/api/v1")
app.include_router(caltrans_bids, prefix="/fruxAI/api/v1")
app.include_router(tenders, prefix="/fruxAI/api/v1")

@app.get("/fruxAI/api/v1/health")
async def health_check():
    """Kong Gateway health check endpoint"""
    return {
        "status": "ok",
        "service": "fruxAI",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "fruxAI API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Crawler orchestration",
            "PDF/HTML processing",
            "Metadata extraction",
            "Supabase integration",
            "Real-time monitoring"
        ],
        "endpoints": {
            "health": "/fruxAI/api/v1/health",
            "crawl_jobs": "/fruxAI/api/v1/crawl-jobs",
            "metadata": "/fruxAI/api/v1/metadata",
            "reports": "/fruxAI/api/v1/reports",
            "documentation": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
