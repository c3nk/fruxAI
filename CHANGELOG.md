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

### Added - Caltrans Workflow Development (Latest)
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
- 🚧 Frontend development in progress
- 🚧 Testing and validation pending
- ✅ **Workflow Engine**: Advanced n8n integration completed

### Next Steps - Roadmap

#### Phase 1: Workflow Enhancement (Current Priority)
1. **API Integration**: Convert workflow output to REST API endpoints
2. **Database Storage**: Implement PostgreSQL storage for scraped data
3. **Data Validation**: Add schema validation and error handling
4. **Monitoring**: Integrate workflow metrics with existing Prometheus setup

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

#### Phase 4: Advanced Features
1. Multi-source data integration (other state agencies)
2. Machine learning for bid analysis
3. Automated reporting and notifications
4. API rate limiting and caching

### Files for Development

#### Primary Files
- **`services/fruxAI/n8n/workflows/caltrans_fixed.json`** - Production-ready Caltrans workflow
- **`services/fruxAI/api/app/main.py`** - FastAPI backend
- **`services/fruxAI/worker/main.py`** - Python worker service

#### Configuration Files
- **`services/fruxAI/docker-compose.yml`** - Docker services configuration
- **`services/fruxAI/config/config.yaml`** - Application configuration
- **`services/fruxAI/n8n/config/`** - n8n workflow configurations

#### Database & Schema
- **`services/fruxAI/config/init-db.sql`** - Database initialization
- **`services/fruxAI/api/app/models/`** - SQLAlchemy models

#### Documentation
- **`README.md`** - Main project documentation
- **`CHANGELOG.md`** - This changelog file
- **`FRUX_BOOTSTRAP_PROMPT.md`** - Development guidelines

---

For more detailed information about each release, check the [GitHub Releases](https://github.com/your-username/fruxAI/releases) page.
