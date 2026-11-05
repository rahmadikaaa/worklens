# WORKLENS Architecture Baseline

> **Version:** 1.0.0-draft  
> **Status:** Active Baseline  
> **Repository:** `worklens`  
> **Branch:** `develop`

---

## 1. System Overview

**WORKLENS (Workload Intelligence Platform)** is a unified platform engineered to ingest, enrich, validate, track, and analyze workload automation assessments.

```mermaid
flowchart TD
    subgraph ClientLayer ["Client & Interface Layer"]
        UI["React + Vite + Tailwind Dashboard"]
        MCP["MCP Clients / AI Agents"]
    end

    subgraph APILayer ["Backend API Layer (FastAPI)"]
        API["FastAPI REST Endpoints (/api/v1)"]
        UploadHandler["Manual JSON/CSV Ingestion"]
        DataStore["In-Memory BreakdownDataStore"]
    end

    subgraph EngineLayer ["Core Processing Engines"]
        M1["M1: Deterministic Enrichment Engine"]
        M2["M2: Change Detection Engine"]
        M3["M3: AI Assessment Reviewer"]
    end

    subgraph StorageLayer ["Immutable Run Storage"]
        Runs["runs/YYYYMMDD_HHMMSS/"]
    end

    UI -->|HTTP / JSON| API
    MCP -->|JSON-RPC / stdio| API
    API --> UploadHandler
    UploadHandler --> DataStore
    DataStore --> M1
    M1 --> M2
    M2 --> M3
    M1 & M2 & M3 --> Runs
```

---

## 2. Architectural Pillars & Core Constraints

1. **Source Immutability:**
   - Raw input assessments (JSON/CSV) are treated as strictly read-only.
   - Processing pipelines produce new enriched outputs without modifying source inputs.

2. **Deterministic vs. AI Separation:**
   - **Deterministic Processing (M1 & M2):** All 6 derived metrics (`Workload Saved`, `Workload Reduction %`, `Annualized Saved`, `Calculation Status`, `Evidence Status`, `Validation Notes`) and content hashing are calculated via strict code logic and mathematical formulas. AI/LLM never computes or alters numbers.
   - **AI Reviewer (M3):** Focuses strictly on qualitative observations (Data Quality, Assessment Consistency, Automation Opportunities). Results are stored in separate findings artifacts (`feedback_report.jsonl` and `.md`).

3. **Zero External Database Dependency (V1):**
   - The platform relies on an in-memory indexed query engine (`BreakdownDataStore`) for sub-millisecond query performance during interactive sessions.
   - Run results and audit trails are persisted as timestamped artifact directories (`runs/YYYYMMDD_HHMMSS/`).

4. **No Desktop Sync / Cloud Egress Overhead:**
   - Microsoft Graph API and OneDrive Desktop Sync dependencies are completely eliminated in WORKLENS.
   - Ingestion is handled exclusively via manual JSON/CSV uploads through the API/Dashboard.

---

## 3. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend Framework** | Python 3.11+ / FastAPI | High-performance asynchronous API, auto-generated OpenAPI docs, seamless Pydantic integration. |
| **Data Validation** | Pydantic v2 | Strict request/response typing, schema validation, and runtime data integrity. |
| **Data Indexing** | In-Memory `BreakdownDataStore` | Fast multi-criteria search, filtering by application, status, and activity without database setup. |
| **AI Reviewer** | Google Gemini API (Mock default) | Pluggable qualitative assessment with offline deterministic mock mode for local testing. |
| **Agent Protocol** | FastMCP (Model Context Protocol) | Exposes workload analytics directly to AI coding agents and LLM workspaces. |
| **Frontend Framework** | React 18+ / TypeScript / Vite | Modern, lightning-fast SPA with strict compile-time type safety. |
| **UI & Styling** | Tailwind CSS / Lucide React | Utility-first, clean, modern dashboard aesthetic with responsive layouts. |
| **Testing** | Pytest (Backend) / Vitest (Frontend) | Comprehensive automated unit, integration, and regression test suites. |

---

## 4. Component Porting & Adaptation Strategy

```mermaid
flowchart LR
    subgraph Legacy ["Legacy: workload_enrichment"]
        L_M1["harness/enrichment.py & schema.py"]
        L_M2["harness/change_detection.py"]
        L_M3["harness/ai_reviewer.py"]
        L_MCP["harness/mcp_service.py"]
        L_DASH["harness/dashboard.py (static HTML)"]
        L_SYNC["harness/operational_sync.py (OneDrive)"]
    end

    subgraph Worklens ["New: WORKLENS Platform"]
        W_M1["backend/app/core/enrichment.py (REUSED)"]
        W_M2["backend/app/core/change_detection.py (REUSED)"]
        W_M3["backend/app/core/ai_reviewer.py (REUSED)"]
        W_STORE["backend/app/services/datastore.py (ADAPTED)"]
        W_API["backend/app/api/v1 (NEW REST API)"]
        W_FE["frontend/ (REBUILT: React + Tailwind)"]
    end

    L_M1 -->|Preserve formulas & priorities| W_M1
    L_M2 -->|Preserve hashing & delta state machine| W_M2
    L_M3 -->|Preserve sanitization & review heuristics| W_M3
    L_MCP -->|Refactor into thread-safe service| W_STORE
    L_DASH -.->|Replaced by modern SPA| W_FE
    L_SYNC -.->|ELIMINATED / EXCLUDED| X[Dropped]
```

### Detailed Component Assessment

1. **Reused Core (Zero business logic change):**
   - `CalculationStatus` priority hierarchy (`INVALID_INPUT` $\to$ `MISSING_INPUT` $\to$ `NEGATIVE_INPUT` $\to$ `ZERO_WORKLOAD` $\to$ `NEGATIVE_SAVINGS` $\to$ `CALCULATED`).
   - `EvidenceStatus` verification (`LINK_PROVIDED` vs `NO_LINK_ATTACHED`).
   - SHA-256 deterministic row content hashing with excluded calculated keys.
   - Delta classification state machine (`UNCHANGED`, `MODIFIED`, `ADDED`, `DELETED`, `REVIEW_REQUIRED`).
   - Local privacy sanitization regex (IPv4, IPv6, email, credential patterns).

2. **Adapted Components:**
   - `BreakdownDataStore`: Enhanced to support atomic dataset swapping upon manual upload with validation feedback.
   - Configuration: Migrated to Pydantic `BaseSettings` reading environment variables with typed fallbacks.
   - MCP Integration: Integrated as a first-class service callable via CLI, stdio, or REST endpoints.

3. **Rebuilt Components:**
   - **Frontend Dashboard:** Rich interactive UI replacing static HTML reports, featuring live filtering, KPI counters, application grouping, diff viewers, and review recommendation drawers.
   - **REST API:** Clean OpenAPI-compliant endpoints serving data to both the frontend and external automation scripts.

4. **Eliminated Components:**
   - `operational_sync.py`: All OneDrive Desktop sync and Microsoft Graph API synchronization logic removed.
