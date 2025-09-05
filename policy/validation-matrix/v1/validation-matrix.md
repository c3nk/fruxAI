# Validation Matrix (Data Quality Policy) – v1

This document defines the **validation, data quality (DQ), and load policy** for tender-result PDF ingestion. It is **state-aware** (single DB with `state` column) and **derivation-free** for bid amounts.

---

## 1) Key Principles
- **Single DB, State Partitioned**: every record includes a non-null `state` (e.g., `CA`). All uniqueness and FK rules are defined **with** `state`.
- **No Amount Derivation**: if a table shows **Cost/Time/Total**, the **printed _Total_** is used as `bid_amount`. If only a single “Bid Amount” column exists, use that. If **Cost**/**Time** exist but **Total is missing**, **HARD FAIL** (not loaded to Core).
- **Winner Rules (no text heuristics)**:
  1) If `rank` exists, **winner = bid with `rank == 1`**.
  2) If `rank` is absent, **winner = bid with the lowest `bid_amount`**.
  3) If there is a tie → `winner_missing` **WARN** and manual review.
- **Staging → Core**: every run writes raw extraction + DQ report to **Staging**; only records passing **Hard-required** checks move to **Core**.

---

## 2) Field Classes (Hard / Soft / Optional)

### 2.1. Tenders (one per PDF)
| Field | Description | Type/Format | Requirement | Validation | Action |
|---|---|---|---|---|---|
| `state` | State tag (e.g., CA) | text | **Hard** | non-null | **FAIL** if missing |
| `file_name` | PDF filename | text | **Hard** | non-null; unique by `(state,file_name)` | **FAIL** |
| `contract_number` | Contract No. | text/null | **Hard*** | non-null if `project_id` is null | **FAIL** if both empty |
| `project_id` | Project ID | text/null | **Hard*** | non-null if `contract_number` is null | **FAIL** if both empty |
| `bid_opening_date` | Bid opening date | ISO-8601 `YYYY-MM-DD` | **Hard** | valid date; not in future | **FAIL** |
| `title/description` | Work summary | text | Soft | length > 3 | **WARN** if missing |
| `location` | County/city etc. | text | Soft | — | **WARN** |
| `contract_code` | A/D etc. | text | Soft | — | **WARN** |
| `number_of_items` | Line items | integer ≥ 0 | Optional | — | — |
| `proposals_issued` | Proposals issued | integer ≥ 0 | Optional | — | — |
| `bidders_count` | Declared bidders count | integer ≥ 1 | Soft | ≈ DISTINCT(`bids.firm_id`) | **WARN** if mismatch |
| `engineers_estimate` | Engineer’s estimate | decimal ≥ 0 | Soft | numeric ≥ 0 | **WARN** |
| `working_days` | Working days | integer ≥ 0 | Soft | — | **WARN** |
| `overrun_underrun` | Delta value | decimal | Optional | — | — |
| `over_under_pct` | Delta % | decimal | Optional | — | — |
| `federal_aid` | Federal Aid # | text/null | Optional | — | — |
| `winner_firm_id` | Winner firm_id | text/null | Soft | must exist in bids if present | **WARN** if missing |
| `winner_amount` | Winner amount | decimal/null | Soft | matches winner row’s `bid_amount` | **WARN** |
| `currency` | Currency code | enum | Soft | in allowed set (e.g., USD/EUR/TRY) | **WARN** |
| `extraction_info` | Process metadata | JSON | Optional | version/flags | — |

**Uniqueness (logical):** `UNIQUE(state, file_name)`; and if present: `UNIQUE(state, contract_number)`, `UNIQUE(state, project_id)`.

### 2.2. Bids (multiple rows per tender)
| Field | Description | Type/Format | Requirement | Validation | Action |
|---|---|---|---|---|---|
| `state` | State tag | text | **Hard** | equals tender’s state | **FAIL** if mismatch |
| `tender_id` | FK to tenders | int | **Hard** | must exist | **FAIL** |
| `firm_id` | Bidder unique id | text | **Hard** | non-null; resolves to `firms` on (state,firm_id) | **FAIL** |
| `bid_amount` | Comparison amount | decimal ≥ 0 | **Hard** | numeric ≥ 0 | **FAIL** |
| `currency` | Currency | enum/null | Soft | allowed set | **WARN** |
| `rank` | Rank | int ≥ 1 / null | Soft | at most one rank==1 per tender | **WARN** (`duplicate_rank1`) |
| `preference` | SB/CC, etc. | text/null | Soft | — | **WARN** |
| `cslb_number` | License | text/null | Soft | — | **WARN** |
| `name_official` | Official name | text/null | Soft | length > 3 | **WARN** |
| `address/phone/fax` | Contact | text/null | Optional | — | — |

**Uniqueness:** `UNIQUE(state, tender_id, firm_id)`

### 2.3. Firms (dictionary)
| Field | Description | Requirement | Notes |
|---|---|---|---|
| `state` | State tag | **Hard** | Partition key |
| `firm_id` | Bidder id (PK) | **Hard** | Unique by `(state, firm_id)` |
| `name_official`, `cslb_number`, `address/city/state/zip`, `phone/fax` | Corporate info | Soft/Optional | Upsert on first sight; enrich later |

### 2.4. Tender Winner History
| Field | Description |
|---|---|
| `state`, `tender_id`, `firm_id` | Winner record (auto or manual) |
| `source` | `auto_detect` \| `manual_override` |
| `changed_by`, `changed_at`, `note` | Audit trail |
| **Active winner** | mirrored in `tenders.winner_firm_id` |

---

## 3) DQ Score (0–100) and Status
**Status thresholds**: PASS (≥ 80), WARN (60–79), FAIL (< 60).

**Weights**: Completeness **50**, Consistency **20**, Validity **20**, Integrity **10**.

### 3.1. Hard-missing rule
If any **Hard-required** field is missing or invalid ⇒ **FAIL** and the DQ score is capped at **≤ 59** (record is not written to Core).

### 3.2. Dimension details

**Completeness (50)**  
- Hard-required bundle passed → +30 pts (as a group).  
- Soft-required (20 pts total): distribute evenly across soft fields (e.g., 8 fields ⇒ 2.5 pts each). Missing soft fields deduct proportionally.

**Consistency (20)**  
- `winner_firm_id` must exist among `bids.firm_id` if set → −6 if not.  
- Rank: at most one `rank == 1` → −6 otherwise.  
- `bidders_count` ≈ DISTINCT(`bids.firm_id`) → −4 if mismatch.  
- Single-currency per tender (if required by policy) → −4 if mixed.

**Validity (20)**  
- `bid_opening_date` valid ISO, not in future → −6 if invalid.  
- `bid_amount` positive numeric → −6 if invalid.  
- `currency` in allowed set → −4 if not.  
- `rank` positive integer if present → −4 if not.

**Integrity (10)**  
- `bids.firm_id` resolves to `firms(state, firm_id)` → −5 if not.  
- `bids.state == tenders.state`; FK links valid → −5 if not.

---

## 4) Status & Actions

| Status | Condition | Action |
|---|---|---|
| **PASS** | Score ≥ 80; no critical errors | Load to Core; move PDF to `processed/`; emit exports |
| **WARN** | 60–79; soft issues only | Load to Core; tag warnings; include in weekly DQ reports |
| **FAIL** | < 60; or any Hard missing | Keep in Staging; quarantine + alert; eligible for re-processing |
  
**Re-processing** is label-driven (e.g., `unknown_headers`, `low_header_coverage`, `possible_ocr_needed`, `winner_missing`).

---

## 5) Issue Tags (examples)
`missing_state`, `missing_file_name`, `missing_identity`, `invalid_date`, `no_bid_rows`, `missing_firm_id`, `missing_bid_amount`, `duplicate_rank1`, `winner_missing`, `bidders_count_mismatch`, `currency_unrecognized`, `low_header_coverage`, `unknown_headers`, `integrity_violation`.

---

## 6) Staging → Core Flow
1) Always write raw extraction + DQ report to **Staging**.  
2) Only **PASS/WARN** move to **Core** (transactional upserts).  
3) **FAIL** stays in Staging; PDF is quarantined; alert is sent.  
4) Manual winner overrides append to `tender_winner_history` and update active winner in `tenders`.
