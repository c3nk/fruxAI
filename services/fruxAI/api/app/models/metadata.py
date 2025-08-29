from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class MetadataBase(BaseModel):
    crawl_job_id: int
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    crawl_depth: int = 0
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    extracted_text: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None
    company_address: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    local_file_path: Optional[str] = None

class MetadataCreate(MetadataBase):
    pass

class MetadataUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    extracted_text: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None
    company_address: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    local_file_path: Optional[str] = None

class Metadata(MetadataBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CompanyReport(BaseModel):
    company_name: str
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    total_pages: int
    avg_response_time: float
    total_file_size: int
    crawled_urls: list[str]
    last_crawl: Optional[datetime] = None
