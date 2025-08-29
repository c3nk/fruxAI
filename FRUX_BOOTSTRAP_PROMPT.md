# Cursor Prompt — Frux + n8n + Supabase (local) Bootstrap

**You are a senior platform engineer.** Create a new repository named **`frux`** that plugs into an existing Docker-Compose tech stack with Kong Gateway, FastAPI, Strapi CMS, Prometheus, Grafana, Loki/Promtail. We’re adding:

- **Frux API**: FastAPI service for crawl job orchestration & metadata.
- **Frux Worker**: Python worker for heavy parsing steps (optional future use).
- **n8n**: Orchestrates crawling (HTTP + HTML/PDF ingest) and writes to Supabase.
- **Supabase (local via CLI)**: Postgres + Studio; we use Supabase as the primary DB.
- **Local storage**: PDFs & raw HTML saved under a mounted folder.
- **Observability**: Promtail → Loki for logs; Prometheus metrics for Frux; Grafana dashboards.

... (content shortened here in code, full bootstrap instructions included in assistant’s prior message) ...
