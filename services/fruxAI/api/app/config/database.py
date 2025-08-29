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

            # Create indexes for better performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_crawl_jobs_status ON crawl_jobs(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_crawl_jobs_created_at ON crawl_jobs(created_at)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_metadata_crawl_job_id ON metadata(crawl_job_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_metadata_url ON metadata(url)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_metadata_company_name ON metadata(company_name)")

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
