Build a state-aware tender PDF ingestion service (Docling + SQLite) with per-table Markdown exports — with external DQ policy
Role & goal
Act as a senior Python engineer. Create a production-ready, free-to-run service that ingests tender result PDFs, extracts meta + bids, validates data, and writes to a single SQLite database partitioned by U.S. state. Also export one JSON per PDF and save every detected table as a separate GitHub-flavored Markdown (.md) file downloadable via HTTP. Initial scope is California (CA), but design must generalize to more states.
Authoritative DQ policy (DO NOT inline; load & follow):
Use the file validation-matrix.md (provided alongside the codebase) as the single source of truth for required fields, checks, scoring, statuses, and load actions.
Location when running locally: include it at project root or mount it to the container and load it at startup.
The app must surface the policy version and path in logs and in each per-PDF DQ report (policy_version, policy_path fields).
Stack constraints (free only)
Python 3.x, Docling for PDF parsing.
SQLite (single DB file). No paid services.
Optional: FastAPI for a small HTTP API, CLI for n8n to call.
No background workers; keep it deterministic.
State isolation in a single DB
Every record includes a non-null state.
Composite uniqueness:
tenders: UNIQUE(state, file_name); UNIQUE(state, contract_number) if not null; UNIQUE(state, project_id) if not null.
firms: UNIQUE(state, firm_id).
bids: UNIQUE(state, tender_id, firm_id).
Enforce same-state FKs: bids.state = tenders.state, tender_winner_history.state = tenders.state.
Filesystem convention
/data/{STATE}/incoming/ PDFs to process
/data/{STATE}/processed/ processed PDFs
/data/{STATE}/exports/{pdf_stem}/ outputs (see “Exports”)
Ingestion flow
Triggered by CLI (n8n will call it) and by HTTP endpoint.
Input: PDF path (or upload) and a fixed state (e.g., “CA”).
Use Docling to parse: capture meta, extract all tables, and build bids.
Extraction rules
Exactly follow the DQ policy in validation-matrix.md for Bid Amount:
If a Total column/field is present, use that exact value as bid_amount.
If there is a single “Bid Amount” column, use it.
If only Cost/Time are present and Total is missing, mark Hard FAIL.
No text heuristics for winner; apply the winner rules from validation-matrix.md.
Validation & DQ
Implement the Hard/Soft/Optional field classes, weights, thresholds, and issue tags exactly as defined in validation-matrix.md.
Produce a per-PDF DQ report with status, score, issues[], and dimension_breakdown.
Only PASS/WARN records advance to Core; FAIL remains in Staging and triggers an alert.
Exports (per PDF)
Save under /data/{STATE}/exports/{pdf_stem}/.
summary.json: meta + winner (if any) + counts + DQ result (include policy_version + policy_path).
bids.csv: all bids.
Tables as Markdown: write each detected table to its own .md in /data/{STATE}/exports/{pdf_stem}/tables/ (table-001.md, table-002.md, …).
Provide HTTP endpoints to list and download these .md files.
HTTP API (minimal)
POST /ingest?state=CA → run ingestion; return DQ summary + pointers to exports.
GET /state/{state}/tenders (filters supported).
GET /state/{state}/tenders/{tender_id}/bids.
GET /state/{state}/exports/{pdf_stem}/tables (list Markdown tables).
GET /state/{state}/exports/{pdf_stem}/tables/{name}.md (download).
PUT /state/{state}/tenders/{tender_id}/winner → manual override; append to tender_winner_history and update active winner.
GET /state/{state}/dq/summary → state-level PASS/WARN/FAIL counts + top issues.
Staging → Core workflow
Always write raw extraction + DQ report to Staging.
If Hard-required pass: transactional upserts into Core, then move PDF to processed/.
If FAIL: keep in Staging (quarantine), do not write to Core.
Idempotency & safety
All Core writes inside a transaction.
Upsert firms by (state, firm_id).
Upsert bids by (state, tender_id, firm_id).
Upsert tenders by (state, file_name) and by contract_number/project_id if present.
Observability
Log the DQ policy path/version on startup and for each ingestion.
Structured logs for table counts, bid rows, new firms, warnings, failures, and issue tags.
Acceptance criteria
Given a CA PDF with a single Bid Amount column: stores to SQLite, emits summary.json, bids.csv, and per-table Markdown files.
Given a CA PDF with Cost/Time/Total: uses printed Total as bid_amount; exports tables as .md.
If Cost/Time but no Total: DQ = FAIL; remains in Staging.
Winner selection follows rank/lowest rules (no text heuristics).
Manual winner override updates tenders.winner_firm_id and appends to tender_winner_history.
Table listing/download endpoints serve the .md files for the PDF.
Composite uniqueness and state-matching FKs prevent cross-state mixing.
DQ endpoints report PASS/WARN/FAIL counts and top issues for CA.
All checks/weights/terms match validation-matrix.md exactly.