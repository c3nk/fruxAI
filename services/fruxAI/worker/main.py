#!/usr/bin/env python3
"""
fruxAI Crawler Worker
Main entry point for the crawler worker service.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from core.crawler import Crawler
from core.queue_manager import QueueManager
from utils.metrics import MetricsCollector

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main worker function"""
    logger.info("Starting fruxAI Crawler Worker...")

    try:
        # Initialize components
        metrics = MetricsCollector()
        queue_manager = QueueManager()
        crawler = Crawler(metrics=metrics)

        # Start metrics collection
        await metrics.start()

        # Start queue processing
        await queue_manager.start()

        # Main processing loop
        while True:
            try:
                # Get next job from queue
                job = await queue_manager.get_next_job()
                if not job:
                    await asyncio.sleep(1)  # Wait before checking again
                    continue

                logger.info(f"Processing job: {job['job_id']} - {job['url']}")

                # Process the crawl job
                await crawler.process_job(job)

                # Mark job as completed
                await queue_manager.mark_job_completed(job['job_id'])

                # Update metrics
                await metrics.increment_jobs_processed()

            except Exception as e:
                logger.error(f"Error processing job: {e}")
                if 'job' in locals():
                    await queue_manager.mark_job_failed(job['job_id'], str(e))
                await metrics.increment_jobs_failed()

    except KeyboardInterrupt:
        logger.info("Shutting down worker...")
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        raise
    finally:
        # Cleanup
        await metrics.stop()
        await queue_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())
