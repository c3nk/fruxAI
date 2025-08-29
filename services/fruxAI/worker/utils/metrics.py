import time
import logging
from typing import Dict, Any
import psutil
from prometheus_client import Counter, Gauge, Histogram, start_http_server

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self, port: int = 8002):
        self.port = port

        # Prometheus metrics
        self.jobs_processed = Counter(
            'frux_jobs_processed_total',
            'Total number of jobs processed'
        )

        self.jobs_failed = Counter(
            'frux_jobs_failed_total',
            'Total number of jobs failed'
        )

        self.crawl_duration = Histogram(
            'frux_crawl_duration_seconds',
            'Time spent crawling pages',
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
        )

        self.content_size = Histogram(
            'frux_content_size_bytes',
            'Size of crawled content',
            buckets=(100, 1000, 10000, 100000, 1000000, 10000000)
        )

        self.active_jobs = Gauge(
            'frux_active_jobs',
            'Number of currently active jobs'
        )

        self.memory_usage = Gauge(
            'frux_memory_usage_bytes',
            'Memory usage of the worker'
        )

        self.cpu_usage = Gauge(
            'frux_cpu_usage_percent',
            'CPU usage percentage of the worker'
        )

        # Internal metrics
        self._start_time = time.time()
        self._jobs_in_progress = 0

    async def start(self):
        """Start metrics collection"""
        try:
            start_http_server(self.port)
            logger.info(f"Metrics server started on port {self.port}")
        except Exception as e:
            logger.warning(f"Failed to start metrics server: {e}")

    async def stop(self):
        """Stop metrics collection"""
        logger.info("Metrics collection stopped")

    async def increment_jobs_processed(self):
        """Increment the jobs processed counter"""
        self.jobs_processed.inc()

    async def increment_jobs_failed(self):
        """Increment the jobs failed counter"""
        self.jobs_failed.inc()

    async def record_crawl_success(self, duration: float, content_size: int):
        """Record successful crawl metrics"""
        self.crawl_duration.observe(duration)
        self.content_size.observe(content_size)

    async def record_crawl_failure(self):
        """Record failed crawl metrics"""
        pass  # Could add specific failure metrics here

    async def job_started(self):
        """Mark that a job has started"""
        self._jobs_in_progress += 1
        self.active_jobs.set(self._jobs_in_progress)

    async def job_finished(self):
        """Mark that a job has finished"""
        self._jobs_in_progress = max(0, self._jobs_in_progress - 1)
        self.active_jobs.set(self._jobs_in_progress)

    async def update_system_metrics(self):
        """Update system-level metrics"""
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)

            self.memory_usage.set(memory.used)
            self.cpu_usage.set(cpu)
        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics"""
        return {
            "uptime_seconds": time.time() - self._start_time,
            "jobs_processed": self.jobs_processed._value,
            "jobs_failed": self.jobs_failed._value,
            "active_jobs": self._jobs_in_progress,
            "memory_usage_mb": psutil.virtual_memory().used / 1024 / 1024,
            "cpu_usage_percent": psutil.cpu_percent()
        }
