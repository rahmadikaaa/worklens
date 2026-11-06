# WORKLENS (Workload Intelligence Platform) — Canonical Agent Rules

> **Status:** Active & Mandatory  
> **Scope:** Project-wide across all directories, backend, frontend, tools, and subagents  
> **Repository:** `worklens`  
> **Current Working Branch:** `develop` (Never commit directly to `main`)  
> **Active Milestone:** Platform Foundation & Knowledge Migration  
> **Legacy Reference (READ-ONLY):** `C:\Users\rahma\OneDrive\Documents\workload_enrichment`  

---

## 1. Project Context & Document Authority

Every agent operating in this repository must align strictly with the approved baseline documentation:

1. **`docs/domain/PRD_V1.md`** (LOCKED BASELINE): Core objectives, functional requirements, and 6 derived workload metrics.
2. **`docs/domain/TECHNICAL_SPECIFICATION.md`**: Authoritative technical specification for schemas, formulas, status priorities, and data structures.
3. **`docs/domain/BUSINESS_DECISIONS_Q1_Q51.md`**: Primary business authority deriving all operational decisions, roles, and target mappings.
4. **`docs/domain/GLOSSARY.md`**: Standardized ubiquitous domain terminology.
5. **`docs/domain/DATA_DICTIONARY.md`**: 35-column schema mapping and lookup relations.
6. **`docs/ARCHITECTURE.md`**: Technical architecture for FastAPI backend, in-memory query engine, React frontend, and MCP service.
7. **`docs/GIT_WORKFLOW.md`**: Branching policy, Conventional Commits, and safe recovery workflows.

**Hierarchy Rule:** PRD, Technical Specification, and Business Baseline Q1–Q51 override assumptions. If an ambiguity or specification conflict arises, report it and clarify; never guess business logic.

---

## 2. Milestone Governance & Scope Boundaries

### Closed & Locked Baseline (Preserve Logic 100%)
- **M1 — Deterministic Enrichment Pipeline:**
  - Formula penghematan durasi: $\text{Workload Saved} = \text{Workload} - \text{Workload after}$.
  - Formula reduksi: $\text{Workload Reduction \%} = ((\text{Workload} - \text{Workload after}) / \text{Workload}) \times 100$ (hanya saat $\text{Workload} > 0$).
  - Formula tahunan: $\text{Annualized Saved} = \text{Workload Saved} \times 12.0$.
  - Hierarki prioritas kalkulasi (6 level): `INVALID_INPUT` $\to$ `MISSING_INPUT` $\to$ `NEGATIVE_INPUT` $\to$ `ZERO_WORKLOAD` $\to$ `NEGATIVE_SAVINGS` $\to$ `CALCULATED`.
  - Evaluasi bukti: `EvidenceStatus` (`LINK_PROVIDED` vs `NO_LINK_ATTACHED`).
  - **Rule:** AI must NEVER calculate, recalculate, estimate, or overwrite derived metrics or source data.
- **M2 — Change Detection Engine:**
  - Strict `activity_id` comparison, SHA-256 content hashing (excluding derived fields), delta classification (`UNCHANGED`, `MODIFIED`, `ADDED`, `DELETED`, `REVIEW_REQUIRED`), feedback inheritance.
  - **Rule:** Do not synthesize or compute composite IDs.
- **M3 — AI Assessment Reviewer:**
  - Qualitative assessment across Data Quality, Consistency, and Automation Opportunities.
  - Local sanitization (IP, email, credentials) before prompt evaluation.
  - Offline mock mode by default.

### Scope Boundaries for WORKLENS
- **In Scope:**
  - Python FastAPI asynchronous & synchronous REST API.
  - React + TypeScript + Vite + Tailwind CSS interactive dashboard.
  - Model Context Protocol (FastMCP) integration.
  - In-memory query engine with atomic swapping upon manual upload.
- **Strictly Out of Scope for V1:**
  - No external database servers (PostgreSQL / SQLite / MySQL).
  - No key-value caches (Redis / Memcached).
  - No OneDrive Desktop Sync, Microsoft Graph API sync, or SharePoint token dependencies.
  - No unapproved third-party dependencies or external cloud egress without security approval.

---

## 3. Skill-First Engineering Workflow

The repository provides 10 modular engineering skills in `.agents/skills/`. Before executing any task, evaluate and activate the appropriate skills:

| Skill | Classification | Core Responsibility |
|---|---|---|
| **`ponytail`** | **Mandatory** | Enforces "Smallest Complete Solution" (YAGNI). Maximizes standard library, rejects premature abstractions, zero bloat. |
| **`grill-with-docs`** | **Mandatory** | Orchestrates 4-phase lifecycle: Discovery $\to$ Grilling $\to$ Decision Capture $\to$ Progressive Documentation. |
| **`domain-modeling`** | **Mandatory** | Standardizes domain terminology, challenges semantic drift, updates `GLOSSARY.md`, and drafts ADRs. |
| **`grilling`** | **Recommended** | Relentlessly stress-tests design decisions, maps foundational decisions, and probes failure modes. |
| **`show-me`** | **Recommended** | Visualizes architectures, call trees, and data flows using clean Mermaid diagrams. |
| **`code-review-and-quality`**| **Mandatory** | 5-axis review (Correctness, Readability, Architecture, Security, Performance) before commits. |
| **`test-driven-development`**| **Mandatory** | Red-Green-Refactor loop, Prove-It pattern for bug fixes, edge case coverage via `pytest` and `vitest`. |
| **`security-and-hardening`** | **Mandatory** | STRIDE threat modeling, trust boundaries, credential masking, input sanitization, file upload security. |
| **`fastapi-expert`** | **Mandatory** | Idiomatic FastAPI, Pydantic v2 schemas, dependency injection, async I/O vs sync CPU threading. |
| **`react-typescript`** | **Mandatory** | Modern React 18+, strict TypeScript interfaces, Vite proxy, Tailwind utilities, zero-bloat state. |

**Mandatory Response Footer:**
Every substantive response must conclude with:
- Skills declared: `[Skills Applied: <skill1>, <skill2> | None]`
- Ponytail footer: One or two lines stating what was skipped/YAGNI and any relevant trade-offs or risks.

---

## 4. Data Integrity & Source Immutability

1. **Absolute Source Immutability:**
   - Raw assessment datasets are strictly **READ-ONLY**.
   - Under no circumstances may an agent write to, modify in-place, rename, or delete raw input files.
2. **Baseline Immutability:**
   - Historical run folders (`runs/YYYYMMDD_HHMMSS/`) are immutable audit records.
3. **Isolated Output Artifacts:**
   - Processing pipelines write artifacts exclusively into dedicated timestamped folders.

---

## 5. Implementation, Testing & Regression Standards

1. **Test Runners:**
   - Backend: `py -m pytest` inside `backend/`
   - Frontend: `npm run test` (Vitest) inside `frontend/`
2. **Coverage & Pass Rate:**
   - Maintain 100% test pass rate with zero warnings.
   - All 168 tests from legacy must continue to pass when ported to WORKLENS.
3. **Traceability:**
   - Every error, validation issue, or AI finding must reference the primary identifier: `activity_id`.

---

## 6. Definition of Done (DoD)

A task or milestone chunk is complete ONLY when all of the following conditions are verified:

- [ ] **PRD & Spec Alignment:** Implementation strictly satisfies active chunk acceptance criteria.
- [ ] **Source Immutability:** Source files and legacy repositories remain 100% untouched.
- [ ] **Logic Separation:** Deterministic enrichment remains completely separate from AI feedback.
- [ ] **Automated Testing:** `py -m pytest` passes with 100% success rate and zero warnings.
- [ ] **Ponytail Audit:** No extraneous wrappers, premature abstractions, or unneeded dependencies introduced.
- [ ] **Git Discipline:** Changes verified with `git status` and `git diff`; commits follow Conventional Commits on `develop` or feature branch.
- [ ] **Output Verification:** Skill declarations and ponytail trade-off summary provided in final response.

