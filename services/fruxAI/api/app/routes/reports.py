from fastapi import APIRouter, Query
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.config.database import get_connection

router = APIRouter()

@router.get("/reports/crawl-stats")
async def get_crawl_stats():
    """Get overall crawl statistics"""
    async with get_connection() as conn:
        # Job statistics
        job_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_jobs,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_jobs,
                AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_job_duration
            FROM crawl_jobs
        """)

        # Metadata statistics
        metadata_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) as total_metadata,
                COUNT(DISTINCT company_name) as unique_companies,
                AVG(file_size) as avg_file_size,
                SUM(file_size) as total_file_size,
                AVG(response_time) as avg_response_time
            FROM metadata
        """)

        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_activity = await conn.fetchrow("""
            SELECT
                COUNT(*) as jobs_last_24h,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_last_24h
            FROM crawl_jobs
            WHERE created_at >= $1
        """, yesterday)

        return {
            "job_statistics": dict(job_stats),
            "metadata_statistics": dict(metadata_stats),
            "recent_activity": dict(recent_activity),
            "generated_at": datetime.utcnow().isoformat()
        }

@router.get("/reports/daily-activity")
async def get_daily_activity(days: int = Query(7, ge=1, le=90)):
    """Get daily crawl activity for the specified number of days"""
    async with get_connection() as conn:
        results = await conn.fetch("""
            SELECT
                DATE(created_at) as date,
                COUNT(*) as total_jobs,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
                COUNT(DISTINCT m.company_name) as companies_crawled
            FROM crawl_jobs cj
            LEFT JOIN metadata m ON cj.id = m.crawl_job_id
            WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """, days)

        return [dict(row) for row in results]

@router.get("/reports/content-types")
async def get_content_types():
    """Get statistics by content type"""
    async with get_connection() as conn:
        results = await conn.fetch("""
            SELECT
                content_type,
                COUNT(*) as count,
                AVG(file_size) as avg_size,
                SUM(file_size) as total_size
            FROM metadata
            WHERE content_type IS NOT NULL
            GROUP BY content_type
            ORDER BY count DESC
        """)

        return [dict(row) for row in results]

@router.get("/reports/response-times")
async def get_response_times():
    """Get response time statistics"""
    async with get_connection() as conn:
        results = await conn.fetch("""
            SELECT
                CASE
                    WHEN response_time < 1 THEN '< 1s'
                    WHEN response_time < 5 THEN '1-5s'
                    WHEN response_time < 10 THEN '5-10s'
                    WHEN response_time < 30 THEN '10-30s'
                    ELSE '> 30s'
                END as response_bucket,
                COUNT(*) as count,
                AVG(response_time) as avg_response_time
            FROM metadata
            WHERE response_time IS NOT NULL
            GROUP BY
                CASE
                    WHEN response_time < 1 THEN '< 1s'
                    WHEN response_time < 5 THEN '1-5s'
                    WHEN response_time < 10 THEN '5-10s'
                    WHEN response_time < 30 THEN '10-30s'
                    ELSE '> 30s'
                END
            ORDER BY avg_response_time
        """)

        return [dict(row) for row in results]

@router.get("/reports/top-companies")
async def get_top_companies(limit: int = Query(20, ge=1, le=100)):
    """Get top companies by crawled pages"""
    async with get_connection() as conn:
        results = await conn.fetch("""
            SELECT
                company_name,
                COUNT(*) as pages_crawled,
                AVG(response_time) as avg_response_time,
                MAX(created_at) as last_crawl,
                COUNT(DISTINCT crawl_job_id) as crawl_sessions
            FROM metadata
            WHERE company_name IS NOT NULL
            GROUP BY company_name
            ORDER BY pages_crawled DESC
            LIMIT $1
        """, limit)

        return [dict(row) for row in results]

@router.get("/reports/crawl-errors")
async def get_crawl_errors():
    """Get crawl error statistics"""
    async with get_connection() as conn:
        results = await conn.fetch("""
            SELECT
                status_code,
                COUNT(*) as count,
                COUNT(DISTINCT crawl_job_id) as affected_jobs
            FROM metadata
            WHERE status_code >= 400
            GROUP BY status_code
            ORDER BY count DESC
        """)

        failed_jobs = await conn.fetch("""
            SELECT
                error_message,
                COUNT(*) as count
            FROM crawl_jobs
            WHERE status = 'failed' AND error_message IS NOT NULL
            GROUP BY error_message
            ORDER BY count DESC
            LIMIT 10
        """)

        return {
            "http_errors": [dict(row) for row in results],
            "job_failures": [dict(row) for row in failed_jobs]
        }
