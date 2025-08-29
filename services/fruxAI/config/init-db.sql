-- fruxAI Database Initialization Script

-- Create crawl_jobs table
CREATE TABLE IF NOT EXISTS crawl_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 1,
    crawl_type VARCHAR(50) DEFAULT 'full',
    max_depth INTEGER DEFAULT 2,
    respect_robots BOOLEAN DEFAULT TRUE,
    rate_limit DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Create metadata table
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
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_status ON crawl_jobs(status);
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_created_at ON crawl_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_metadata_crawl_job_id ON metadata(crawl_job_id);
CREATE INDEX IF NOT EXISTS idx_metadata_url ON metadata(url);
CREATE INDEX IF NOT EXISTS idx_metadata_company_name ON metadata(company_name);
CREATE INDEX IF NOT EXISTS idx_metadata_created_at ON metadata(created_at);

-- Create n8n workflow executions table
CREATE TABLE IF NOT EXISTS n8n_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(255) UNIQUE NOT NULL,
    workflow_id VARCHAR(255),
    status VARCHAR(50),
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create metrics table for custom metrics storage
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(10,2),
    labels JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some sample data for testing
INSERT INTO crawl_jobs (job_id, url, status, priority) VALUES
('sample-job-1', 'https://example.com', 'pending', 1),
('sample-job-2', 'https://httpbin.org', 'pending', 2)
ON CONFLICT (job_id) DO NOTHING;

-- Create a view for company reports
CREATE OR REPLACE VIEW company_reports AS
SELECT
    company_name,
    COUNT(*) as total_pages,
    AVG(response_time) as avg_response_time,
    SUM(file_size) as total_file_size,
    COUNT(DISTINCT crawl_job_id) as crawl_sessions,
    MAX(created_at) as last_crawl,
    ARRAY_AGG(DISTINCT company_website) FILTER (WHERE company_website IS NOT NULL) as websites,
    ARRAY_AGG(DISTINCT company_email) FILTER (WHERE company_email IS NOT NULL) as emails,
    ARRAY_AGG(DISTINCT company_phone) FILTER (WHERE company_phone IS NOT NULL) as phones
FROM metadata
WHERE company_name IS NOT NULL
GROUP BY company_name
ORDER BY total_pages DESC;

-- Grant permissions (if needed for different users)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO fruxai_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO fruxai_user;
