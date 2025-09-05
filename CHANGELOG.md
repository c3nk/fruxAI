# Changelog

All notable changes to fruxAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and setup
- FastAPI backend with crawl job management
- Python crawler worker with PDF/HTML processing
- Supabase/PostgreSQL database integration
- n8n workflow orchestration
- Docker Compose configuration
- Prometheus metrics and monitoring
- Grafana dashboards
- Loki logging aggregation
- Kong Gateway API routing
- Frontend dashboard structure
- Comprehensive documentation

### Added - Tender PDF Ingestion Service (Latest)
- ✅ **State-aware PDF Processing**: Complete tender PDF ingestion service with state isolation
- ✅ **Database Schema**: New PostgreSQL tables (tenders, bids, firms, tender_winner_history) with state partitioning
- ✅ **Docling Integration**: Advanced PDF parsing with table extraction and metadata processing
- ✅ **HEAD_ALIASES System**: Configurable column mapping for different PDF formats
- ✅ **API Endpoints**: State-aware REST API for tender and bid management
- ✅ **File System Organization**: State-based folder structure (/data/{STATE}/incoming/processed/exports/)
- ✅ **Export Functionality**: JSON, CSV, and GitHub-flavored Markdown exports per PDF
- ✅ **Background Processing**: Asynchronous PDF processing with queue management
- ✅ **Multi-State Support**: Designed for CA and future state expansions

### Added - Caltrans Workflow Development
- ✅ Complete Caltrans bid data scraping workflow
- ✅ 7-step automated workflow (Start → Main Page → Extract Links → Process Links → Get Weekly Pages → Extract Table Data → Format Data)
- ✅ Parallel processing for all 5 weekly bid pages
- ✅ Advanced HTML parsing with CSS selectors
- ✅ Structured JSON output with bidders, contracts, and metadata
- ✅ Error handling and JSON syntax fixes
- ✅ Production-ready workflow configuration

### Changed
- Separated from IntegrityGuard project
- Reorganized project structure for independent development
- Enhanced n8n workflow with advanced data processing capabilities

### Fixed
- JSON syntax errors in n8n workflow configurations
- Expression parsing issues in HTTP Request nodes
- Data formatting inconsistencies

### Technical Details
- **API**: FastAPI with async support
- **Database**: PostgreSQL with asyncpg
- **Worker**: Python with aiohttp and beautifulsoup4
- **Monitoring**: Prometheus + Grafana + Loki
- **Orchestration**: n8n workflows
- **Gateway**: Kong for API management
- **Workflow Engine**: Advanced n8n with custom JavaScript processing
- **Data Processing**: Automated HTML parsing and JSON transformation

## [0.1.0] - 2024-01-27

### Added
- Project initialization
- Basic documentation structure
- Development guidelines and rules
- Architecture planning and bootstrap prompt

### Infrastructure
- Git repository setup
- Project structure planning
- Initial documentation

---

## Types of changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities

## Versioning
This project follows [Semantic Versioning](https://semver.org/).

Given a version number MAJOR.MINOR.PATCH, increment the:

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes

---

## Development Notes

### Current Status
- ✅ Project structure completed
- ✅ Backend services implemented
- ✅ Documentation prepared
- ✅ GitHub setup ready
- ✅ **Caltrans Workflow**: Complete and production-ready
- ✅ **Tender PDF Ingestion**: State-aware PDF processing service
- ✅ **Database Schema**: State-partitioned PostgreSQL tables
- ✅ **API Endpoints**: REST API for tender/bid management
- ✅ **Docling Integration**: Advanced PDF parsing and table extraction
- 🚧 Frontend development in progress
- 🚧 Testing and validation pending
- ✅ **Workflow Engine**: Advanced n8n integration completed

### Next Steps - Roadmap

#### Phase 1: PDF Processing & API Enhancement (Current Priority)
1. ✅ **API Integration**: REST API endpoints for tender/bid management completed
2. ✅ **Database Storage**: State-partitioned PostgreSQL schema implemented
3. ✅ **Docling Integration**: PDF parsing and table extraction working
4. 🚧 **Data Quality (DQ) Policy**: Implement validation and scoring system
5. 🚧 **N8n Integration**: Connect PDF ingestion with existing workflows
6. 🚧 **Testing**: Comprehensive testing with real PDF data
7. **Monitoring**: Integrate PDF processing metrics with Prometheus

#### Phase 2: Frontend Development
1. Complete React dashboard implementation
2. Add data visualization components
3. Implement real-time workflow monitoring
4. Create user management interface

#### Phase 3: Production Deployment
1. Set up CI/CD pipeline with GitHub Actions
2. Configure staging and production environments
3. Implement backup and disaster recovery
4. Performance optimization and scaling

#### Phase 3: Multi-State Expansion
1. **State-Specific Processing**: Add support for TX, FL, NY state agencies
2. **HEAD_ALIASES Extension**: State-specific column mappings
3. **Data Standardization**: Unified data format across states
4. **Performance Optimization**: Multi-state query optimization

#### Phase 4: Advanced Features
1. **DQ Policy Implementation**: Complete validation and scoring system
2. **Machine Learning**: Bid analysis and anomaly detection
3. **Automated Reporting**: PDF reports and notifications
4. **API Rate Limiting**: Production-ready API management
5. **Caching Layer**: Redis integration for performance

### Files for Development

#### Primary Files
- **`services/fruxAI/n8n/workflows/caltrans_fixed.json`** - Production-ready Caltrans workflow
- **`services/fruxAI/api/app/main.py`** - FastAPI backend
- **`services/fruxAI/api/app/routes/tenders.py`** - Tender PDF ingestion API
- **`services/fruxAI/api/app/services/docling_processor.py`** - PDF processing service
- **`services/fruxAI/worker/main.py`** - Python worker service

#### Configuration Files
- **`services/fruxAI/docker-compose.yml`** - Docker services configuration
- **`services/fruxAI/config/config.yaml`** - Application configuration
- **`services/fruxAI/n8n/config/`** - n8n workflow configurations

#### Database & Schema
- **`services/fruxAI/config/init-db.sql`** - Database initialization
- **`services/fruxAI/api/app/models/`** - SQLAlchemy models
- **`services/fruxAI/api/app/models/tender.py`** - Tender, Bid, Firm models (state-aware)
- **`validation-matrix.md`** - Data Quality (DQ) policy specification

#### Documentation
- **`README.md`** - Main project documentation
- **`CHANGELOG.md`** - This changelog file
- **`FRUX_BOOTSTRAP_PROMPT.md`** - Development guidelines

---

For more detailed information about each release, check the [GitHub Releases](https://github.com/your-username/fruxAI/releases) page.
