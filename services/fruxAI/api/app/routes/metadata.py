from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.metadata import Metadata, MetadataCreate, MetadataUpdate, CompanyReport
from app.config.database import get_connection

router = APIRouter()

@router.post("/metadata", response_model=Metadata)
async def create_metadata(metadata: MetadataCreate):
    """Create new metadata entry"""
    async with get_connection() as conn:
        try:
            result = await conn.fetchrow("""
                INSERT INTO metadata (
                    crawl_job_id, url, title, description, keywords,
                    content_type, file_size, crawl_depth, response_time,
                    status_code, extracted_text, company_name, company_website,
                    company_email, company_phone, company_address,
                    metadata_json, local_file_path
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
                RETURNING *
            """,
                metadata.crawl_job_id, metadata.url, metadata.title, metadata.description,
                metadata.keywords, metadata.content_type, metadata.file_size, metadata.crawl_depth,
                metadata.response_time, metadata.status_code, metadata.extracted_text,
                metadata.company_name, metadata.company_website, metadata.company_email,
                metadata.company_phone, metadata.company_address, metadata.metadata_json,
                metadata.local_file_path
            )

            return dict(result)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create metadata: {e}")

@router.get("/metadata", response_model=List[Metadata])
async def list_metadata(
    crawl_job_id: Optional[int] = None,
    company_name: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List metadata entries with optional filtering"""
    async with get_connection() as conn:
        conditions = []
        params = []
        param_count = 1

        if crawl_job_id:
            conditions.append(f"crawl_job_id = ${param_count}")
            params.append(crawl_job_id)
            param_count += 1

        if company_name:
            conditions.append(f"company_name ILIKE ${param_count}")
            params.append(f"%{company_name}%")
            param_count += 1

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT * FROM metadata
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        params.extend([limit, offset])

        results = await conn.fetch(query, *params)
        return [dict(row) for row in results]

@router.get("/metadata/{metadata_id}", response_model=Metadata)
async def get_metadata(metadata_id: int):
    """Get specific metadata entry"""
    async with get_connection() as conn:
        result = await conn.fetchrow(
            "SELECT * FROM metadata WHERE id = $1",
            metadata_id
        )

        if not result:
            raise HTTPException(status_code=404, detail="Metadata not found")

        return dict(result)

@router.put("/metadata/{metadata_id}", response_model=Metadata)
async def update_metadata(metadata_id: int, update: MetadataUpdate):
    """Update metadata entry"""
    async with get_connection() as conn:
        # Build dynamic update query
        update_fields = []
        update_values = []
        param_count = 1

        update_dict = update.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                update_fields.append(f"{field} = ${param_count}")
                update_values.append(value)
                param_count += 1

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        query = f"""
            UPDATE metadata
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING *
        """
        update_values.append(metadata_id)

        result = await conn.fetchrow(query, *update_values)

        if not result:
            raise HTTPException(status_code=404, detail="Metadata not found")

        return dict(result)

@router.get("/companies", response_model=List[CompanyReport])
async def get_company_reports():
    """Get aggregated reports by company"""
    async with get_connection() as conn:
        results = await conn.fetch("""
            SELECT
                company_name,
                company_website,
                company_email,
                company_phone,
                company_address,
                COUNT(*) as total_pages,
                AVG(response_time) as avg_response_time,
                SUM(file_size) as total_file_size,
                ARRAY_AGG(DISTINCT url) as crawled_urls,
                MAX(created_at) as last_crawl
            FROM metadata
            WHERE company_name IS NOT NULL
            GROUP BY company_name, company_website, company_email, company_phone, company_address
            ORDER BY total_pages DESC
        """)

        return [dict(row) for row in results]

@router.get("/companies/{company_name}", response_model=CompanyReport)
async def get_company_report(company_name: str):
    """Get detailed report for a specific company"""
    async with get_connection() as conn:
        result = await conn.fetchrow("""
            SELECT
                company_name,
                company_website,
                company_email,
                company_phone,
                company_address,
                COUNT(*) as total_pages,
                AVG(response_time) as avg_response_time,
                SUM(file_size) as total_file_size,
                ARRAY_AGG(DISTINCT url) as crawled_urls,
                MAX(created_at) as last_crawl
            FROM metadata
            WHERE company_name = $1
            GROUP BY company_name, company_website, company_email, company_phone, company_address
        """, company_name)

        if not result:
            raise HTTPException(status_code=404, detail="Company not found")

        return dict(result)
