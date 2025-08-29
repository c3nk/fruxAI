from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.models.crawl_job import CrawlJob, CrawlJobCreate, CrawlJobUpdate
from app.config.database import get_connection
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/crawl-jobs", response_model=CrawlJob)
async def create_crawl_job(job: CrawlJobCreate):
    """Create a new crawl job"""
    job_id = str(uuid.uuid4())

    async with get_connection() as conn:
        try:
            result = await conn.fetchrow("""
                INSERT INTO crawl_jobs (
                    job_id, url, priority, crawl_type, max_depth,
                    respect_robots, rate_limit
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
            """,
                job_id, job.url, job.priority, job.crawl_type,
                job.max_depth, job.respect_robots, job.rate_limit
            )

            return dict(result)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create crawl job: {e}")

@router.get("/crawl-jobs", response_model=List[CrawlJob])
async def list_crawl_jobs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List crawl jobs with optional filtering"""
    async with get_connection() as conn:
        if status:
            query = """
                SELECT * FROM crawl_jobs
                WHERE status = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """
            results = await conn.fetch(query, status, limit, offset)
        else:
            query = """
                SELECT * FROM crawl_jobs
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """
            results = await conn.fetch(query, limit, offset)

        return [dict(row) for row in results]

@router.get("/crawl-jobs/{job_id}", response_model=CrawlJob)
async def get_crawl_job(job_id: str):
    """Get a specific crawl job by ID"""
    async with get_connection() as conn:
        result = await conn.fetchrow(
            "SELECT * FROM crawl_jobs WHERE job_id = $1",
            job_id
        )

        if not result:
            raise HTTPException(status_code=404, detail="Crawl job not found")

        return dict(result)

@router.put("/crawl-jobs/{job_id}", response_model=CrawlJob)
async def update_crawl_job(job_id: str, update: CrawlJobUpdate):
    """Update a crawl job status"""
    async with get_connection() as conn:
        # Build dynamic update query
        update_fields = []
        update_values = []
        param_count = 1

        if update.status is not None:
            update_fields.append(f"status = ${param_count}")
            update_values.append(update.status)
            param_count += 1

        if update.completed_at is not None:
            update_fields.append(f"completed_at = ${param_count}")
            update_values.append(update.completed_at)
            param_count += 1

        if update.error_message is not None:
            update_fields.append(f"error_message = ${param_count}")
            update_values.append(update.error_message)
            param_count += 1

        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        query = f"""
            UPDATE crawl_jobs
            SET {', '.join(update_fields)}
            WHERE job_id = ${param_count}
            RETURNING *
        """
        update_values.append(job_id)

        result = await conn.fetchrow(query, *update_values)

        if not result:
            raise HTTPException(status_code=404, detail="Crawl job not found")

        return dict(result)

@router.delete("/crawl-jobs/{job_id}")
async def delete_crawl_job(job_id: str):
    """Delete a crawl job"""
    async with get_connection() as conn:
        result = await conn.fetchrow(
            "DELETE FROM crawl_jobs WHERE job_id = $1 RETURNING job_id",
            job_id
        )

        if not result:
            raise HTTPException(status_code=404, detail="Crawl job not found")

        return {"message": "Crawl job deleted successfully"}
