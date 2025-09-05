import asyncpg
import os
import logging
from typing import Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv("SUPABASE_DB_HOST", "localhost")
        self.port = int(os.getenv("SUPABASE_DB_PORT", "5432"))
        self.database = os.getenv("SUPABASE_DB_NAME", "fruxai")
        self.user = os.getenv("SUPABASE_DB_USER", "postgres")
        self.password = os.getenv("SUPABASE_DB_PASSWORD", "")

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

# Global database config
db_config = DatabaseConfig()

# Connection pool
_pool: Optional[asyncpg.Pool] = None

async def get_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            db_config.connection_string,
            min_size=5,
            max_size=20,
            command_timeout=60,
        )
        logger.info("Database connection pool created")
    return _pool

@asynccontextmanager
async def get_connection():
    """Get database connection from pool"""
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection

async def init_db():
    """Initialize database and create tables if they don't exist"""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Create crawl_jobs table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_jobs (
                    id SERIAL PRIMARY KEY,
                    job_id VARCHAR(255) UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    priority INTEGER DEFAULT 1,
                    crawl_type VARCHAR(50) DEFAULT 'full',
                    max_depth INTEGER DEFAULT 2,
                    respect_robots BOOLEAN DEFAULT TRUE,
                    rate_limit INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT
                )
            """)

            # Create metadata table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    id SERIAL PRIMARY KEY,
                    crawl_job_id INTEGER REFERENCES crawl_jobs(id),
                    url TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    keywords TEXT,
                    content_type VARCHAR(100),
                    file_size INTEGER,
                    crawl_depth INTEGER DEFAULT 0,
                    response_time DECIMAL(5,2),
                    status_code INTEGER,
                    extracted_text TEXT,
                    company_name TEXT,
                    company_website TEXT,
                    company_email TEXT,
                    company_phone TEXT,
                    company_address TEXT,
                    metadata_json JSONB,
                    local_file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create tender-related tables
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tenders (
                    id SERIAL PRIMARY KEY,
                    state VARCHAR(2) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    contract_number VARCHAR(50),
                    project_id VARCHAR(50),
                    bid_opening_date DATE,
                    title TEXT,
                    location TEXT,
                    winner_firm_id VARCHAR(100),
                    winner_amount DECIMAL(15,2),
                    currency VARCHAR(3) DEFAULT 'USD',
                    extraction_info JSONB,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(state, file_name),
                    UNIQUE(state, contract_number),
                    UNIQUE(state, project_id)
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS firms (
                    state VARCHAR(2) NOT NULL,
                    firm_id VARCHAR(100) NOT NULL,
                    name_official TEXT,
                    cslb_number VARCHAR(50),
                    address TEXT,
                    city VARCHAR(100),
                    state_code VARCHAR(2),
                    zip VARCHAR(10),
                    phone VARCHAR(20),
                    fax VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (state, firm_id)
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bids (
                    id SERIAL PRIMARY KEY,
                    state VARCHAR(2) NOT NULL,
                    tender_id INTEGER,
                    firm_id VARCHAR(100) NOT NULL,
                    bid_amount DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) DEFAULT 'USD',
                    rank INTEGER,
                    preference VARCHAR(10),
                    cslb_number VARCHAR(50),
                    name_official TEXT,
                    UNIQUE(state, tender_id, firm_id)
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tender_winner_history (
                    id SERIAL PRIMARY KEY,
                    state VARCHAR(2) NOT NULL,
                    tender_id INTEGER,
                    firm_id VARCHAR(100),
                    source VARCHAR(20),
                    changed_by VARCHAR(100),
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    note TEXT
                )
            """)

            # Create indexes for better performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_crawl_jobs_status ON crawl_jobs(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_crawl_jobs_created_at ON crawl_jobs(created_at)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_metadata_crawl_job_id ON metadata(crawl_job_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_metadata_url ON metadata(url)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_metadata_company_name ON metadata(company_name)")

            # Tender-related indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tenders_state ON tenders(state)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tenders_file_name ON tenders(file_name)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tenders_contract_number ON tenders(contract_number)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tenders_project_id ON tenders(project_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_bids_state ON bids(state)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_bids_tender_id ON bids(tender_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_firms_state ON firms(state)")

            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def close_db():
    """Close database connection pool"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")
