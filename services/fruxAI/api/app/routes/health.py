from fastapi import APIRouter
from app.config.database import get_pool
import psutil
import time
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "fruxAI-api"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    try:
        pool = await get_pool()

        # Get database connection count
        db_stats = await pool.fetchval("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")

        # System metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "fruxAI-api",
            "database": {
                "connections": db_stats,
                "status": "connected"
            },
            "system": {
                "memory_used_percent": memory.percent,
                "cpu_used_percent": cpu_percent,
                "uptime_seconds": time.time() - psutil.boot_time()
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "fruxAI-api",
            "error": str(e)
        }
