# Frux – Cursor Rules (Architecture, Code, Ops)

## Prime Directives
- This repo is **Frux**: a local-first crawler/orchestrator built around **n8n**, **FastAPI**, and **Supabase**.  
- **Local only, no auth**. Do not add login or tokens unless explicitly requested.  
- Respect polite crawling: default **~1 req/sec** per site; exponential backoff on errors.  
- Persist PDFs/HTML to local mounted storage; persist metadata and normalized text to **Supabase (Postgres)**.  
- Expose only two public gateway paths via Kong:  
  - `/frux/api/v1/*` → FastAPI  
  - `/n8n/*` → n8n  
- Observability: **stdout logs → Promtail → Loki**; **/metrics → Prometheus**; **dashboards → Grafana**.

... (content shortened here in code, full rules included in assistant’s prior message) ...
