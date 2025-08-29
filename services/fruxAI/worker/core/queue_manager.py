import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self):
        self.api_base_url = os.getenv("FRUX_API_URL", "http://localhost:8001/fruxAI/api/v1")
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.poll_interval = 5  # seconds

    async def start(self):
        """Start the queue manager"""
        self.session = aiohttp.ClientSession()
        self.running = True
        logger.info("Queue manager started")

    async def stop(self):
        """Stop the queue manager"""
        self.running = False
        if self.session:
            await self.session.close()
        logger.info("Queue manager stopped")

    async def get_next_job(self) -> Optional[Dict[str, Any]]:
        """Get next pending job from the API"""
        try:
            async with self.session.get(f"{self.api_base_url}/crawl-jobs?status=pending&limit=1") as response:
                if response.status == 200:
                    jobs = await response.json()
                    if jobs:
                        return jobs[0]
                else:
                    logger.warning(f"Failed to fetch jobs: HTTP {response.status}")
        except Exception as e:
            logger.error(f"Error fetching next job: {e}")

        return None

    async def mark_job_completed(self, job_id: str):
        """Mark a job as completed"""
        try:
            update_data = {
                "status": "completed",
                "completed_at": None  # Will be set to current timestamp by API
            }

            async with self.session.put(
                f"{self.api_base_url}/crawl-jobs/{job_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to mark job {job_id} as completed: HTTP {response.status}")
                else:
                    logger.info(f"Job {job_id} marked as completed")
        except Exception as e:
            logger.error(f"Error marking job {job_id} as completed: {e}")

    async def mark_job_failed(self, job_id: str, error_message: str):
        """Mark a job as failed"""
        try:
            update_data = {
                "status": "failed",
                "error_message": error_message,
                "completed_at": None
            }

            async with self.session.put(
                f"{self.api_base_url}/crawl-jobs/{job_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to mark job {job_id} as failed: HTTP {response.status}")
                else:
                    logger.info(f"Job {job_id} marked as failed: {error_message}")
        except Exception as e:
            logger.error(f"Error marking job {job_id} as failed: {e}")

    async def create_metadata(self, metadata: Dict[str, Any]) -> Optional[int]:
        """Create metadata entry"""
        try:
            async with self.session.post(
                f"{self.api_base_url}/metadata",
                json=metadata,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Metadata created for {metadata.get('url')}")
                    return result.get('id')
                else:
                    logger.error(f"Failed to create metadata: HTTP {response.status}")
                    response_text = await response.text()
                    logger.error(f"Response: {response_text}")
        except Exception as e:
            logger.error(f"Error creating metadata: {e}")

        return None

    async def update_job_status(self, job_id: str, status: str, **kwargs):
        """Update job status with additional fields"""
        try:
            update_data = {"status": status}
            update_data.update(kwargs)

            async with self.session.put(
                f"{self.api_base_url}/crawl-jobs/{job_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to update job {job_id}: HTTP {response.status}")
                else:
                    logger.info(f"Job {job_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")

    async def poll_jobs(self):
        """Continuously poll for new jobs"""
        while self.running:
            try:
                job = await self.get_next_job()
                if job:
                    # Update job status to running
                    await self.update_job_status(job['job_id'], 'running')

                    # Return job for processing
                    return job
                else:
                    await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error polling jobs: {e}")
                await asyncio.sleep(self.poll_interval)

        return None
