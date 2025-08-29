from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CrawlJobBase(BaseModel):
    job_id: str
    url: str
    priority: int = 1
    crawl_type: str = "full"  # full, shallow, metadata_only
    max_depth: int = 2
    respect_robots: bool = True
    rate_limit: int = 1  # requests per second

class CrawlJobCreate(CrawlJobBase):
    pass

class CrawlJobUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class CrawlJob(CrawlJobBase):
    id: int
    status: str = "pending"  # pending, running, completed, failed, cancelled
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
