# WORKLENS Component Analysis & Porting Plan

> **Authoritative Baseline:** Analysis of `workload_enrichment` legacy components for clean migration into `WORKLENS`.

---

## 1. Executive Summary

This document categorizes all modules from the legacy repository (`workload_enrichment`) into four distinct migration buckets:
1. **Reused:** Preserved with 100% fidelity to lock in approved business logic, calculations, and contracts.
2. **Adapted:** Refactored into idiomatic FastAPI/Pydantic service structures.
3. **Rebuilt:** Completely redesigned for modern UX and maintainability (e.g. React frontend replacing single-file static HTML).
4. **Dropped / Excluded:** Explicitly discarded (e.g., OneDrive Desktop Sync and Microsoft Graph API).

---

## 2. Component Categorization Matrix

| Legacy Component | Target WORKLENS Module | Action | Justification & Technical Details |
|---|---|---|---|
| `harness/enrichment.py` | `backend/app/core/enrichment.py` | **Reuse** | Contains M1 deterministic calculations. Priority hierarchy (`INVALID_INPUT` $\to$ `MISSING_INPUT` $\to$ `NEGATIVE_INPUT` $\to$ `ZERO_WORKLOAD` $\to$ `NEGATIVE_SAVINGS` $\to$ `CALCULATED`) and `EvidenceStatus` are locked. |
| `harness/schema.py` | `backend/app/core/schema.py` | **Reuse** | Canonical header rules (`Workload`, `Workload after`, `APPS`, etc.), whitespace tolerance, and unlabelled column detection. |
| `harness/csv_reader.py` | `backend/app/core/csv_reader.py` | **Reuse** | Ingestion parser, row indexing, and normalization logic. |
| `harness/output_generator.py` | `backend/app/core/output_generator.py` | **Reuse** | Deterministic artifact generation (`enriched_assessment.csv`, `run_summary.json`). |
| `harness/change_detection.py` | `backend/app/core/change_detection.py` | **Reuse** | M2 delta state machine (`UNCHANGED`, `MODIFIED`, `ADDED`, `DELETED`, `REVIEW_REQUIRED`), `activity_id` validation, SHA-256 row content hashing. |
| `harness/ai_reviewer.py` | `backend/app/core/ai_reviewer.py` | **Reuse** | M3 qualitative review logic: local regex sanitization (`[IP_MASKED]`, `[EMAIL_MASKED]`, `[CREDENTIAL_MASKED]`), deterministic batching (15–30 rows), mock heuristic evaluation, feedback markdown & JSONL generation. |
| `harness/mcp_service.py` | `backend/app/services/datastore.py` | **Adapt** | `BreakdownDataStore` adapted into a dependency-injectable in-memory service supporting atomic dataset swaps upon manual upload. |
| `mcp_server.py` | `backend/app/services/mcp_server.py` | **Adapt** | FastMCP server tools wrapped to query the active `BreakdownDataStore` or run alongside FastAPI. |
| `harness/config.py` | `backend/app/config.py` | **Adapt** | Migrated from plain dictionary/argparse mappings to Pydantic `BaseSettings` (`SettingsConfigDict`) reading `.env` and environment variables. |
| `harness/dashboard.py` | `frontend/` (React + Tailwind) | **Rebuild** | Replaced static monolithic HTML table generator (`ops_category_dashboard.html`) with an interactive React dashboard with search, filtering, and live metric cards. |
| `run_harness.py` | `backend/app/main.py` & CLI | **Adapt** | CLI entrypoint adapted to coexist with FastAPI REST API endpoints. |
| `harness/operational_sync.py` | *None* | **Drop** | OneDrive Desktop sync and Microsoft Graph API sync are strictly excluded per project requirements. |

---

## 3. Preserved Business Logic Contracts

### 3.1 M1: Deterministic Enrichment Rules
- **No arithmetic by LLMs:** Mathematical computations are strictly executed by `enrichment.py`.
- **Formulas:**
  - $\text{Workload Saved} = \text{Workload} - \text{Workload after}$
  - $\text{Workload Reduction \%} = \left(\frac{\text{Workload} - \text{Workload after}}{\text{Workload}}\right) \times 100$ (only when $\text{Workload} > 0$)
  - $\text{Annualized Saved} = \text{Workload Saved} \times 12.0$
- **Priority Hierarchy:**
  1. `INVALID_INPUT` (non-numeric data)
  2. `MISSING_INPUT` (empty/null value; not treated as 0)
  3. `NEGATIVE_INPUT` (negative duration)
  4. `ZERO_WORKLOAD` (division by zero avoided; reduction % undefined)
  5. `NEGATIVE_SAVINGS` (workload after > workload)
  6. `CALCULATED` (valid normal calculation)

### 3.2 M2: Change Detection Rules
- Primary key: `activity_id` read directly from source.
- Missing or duplicate `activity_id` $\to$ `REVIEW_REQUIRED`.
- Content Hash: SHA-256 over normalized source data, strictly excluding derived metrics.

### 3.3 M3: AI Assessment Reviewer Rules
- Focus areas: `DATA_QUALITY`, `ASSESSMENT_CONSISTENCY`, `AUTOMATION_OPPORTUNITY`.
- Offline mock mode by default using heuristic evaluation.
- Local sanitization before prompt generation to mask IP addresses, emails, and credentials.

---

## 4. Architectural Decisions & Open Considerations

1. **State Management:**
   - *Current Decision:* In-memory singleton (`BreakdownDataStore`) initialized on startup with fallback to local JSON/CSV file.
   - *Consideration:* When a user uploads a new assessment via the web UI, the backend validates the file, atomically updates the in-memory store, and writes a timestamped record to `runs/YYYYMMDD_HHMMSS/`.

2. **MCP Coexistence:**
   - *Current Decision:* The MCP server can run as a standalone stdio process using FastMCP or be invoked via REST API endpoints for agentic tools.
