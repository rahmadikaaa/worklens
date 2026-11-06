# SOP L1 AGIT Agent Harness V1 --- Development Roadmap

**Status:** Approved Strategic Roadmap (Aligned with Business Baseline Q1–Q51)  
**Business Decision Baseline:** [Workload_Enrichment_Tanya_Jawab_Q1-Q51.md](file:///c:/Users/rahma/OneDrive/Documents/workload_enrichment/Workload_Enrichment_Tanya_Jawab_Q1-Q51.md)  
**Technical Baseline:** [SOP_L1_AGIT_Agent_Harness_PRD_V1.md](file:///c:/Users/rahma/OneDrive/Documents/workload_enrichment/SOP_L1_AGIT_Agent_Harness_PRD_V1.md) & [SOP_L1_AGIT_Agent_Harness_Specification.md](file:///c:/Users/rahma/OneDrive/Documents/workload_enrichment/SOP_L1_AGIT_Agent_Harness_Specification.md)  
**Working branch:** `develop`  
**Approach:** Spec-Driven Development (SDD) & Agent Harness Governance  

------------------------------------------------------------------------

## 1. Objective

Build SOP L1 AGIT Agent Harness incrementally through Spec-Driven Development (SDD), ensuring every development chunk and milestone is strictly derived from verified business decisions (Q1–Q51), specified in testable contracts, implemented, tested, and reviewed before advancing to the next phase.

The system serves as the foundational computational engine and operational workspace for Tim L1 AGIT to assess ~1,000 SOP activities, identify automation opportunities (AO and non-AO), validate existing automations, eliminate unnecessary manual tasks (dismantle), and measure workload reduction with full transparency for Management.

## 2. Governance & Development Principles

- **Primary Business Authority:** All product priorities, terminologies, and operational roles derive strictly from `Workload_Enrichment_Tanya_Jawab_Q1-Q51.md`.
- **Spec-Driven Development (SDD):** Specifications (`Specification.md`, `GLOSSARY.md`, ADRs) precede code changes. Acceptance criteria are expressed in testable Given-When-Then contracts.
- **Strict Separation of Concerns:**
  - Deterministic calculations (enrichment, reduction %, annualized saving) are executed 100% by code.
  - Qualitative assessments (data quality, consistency, automation opportunity) are evaluated by the AI Reviewer without mutating source data or numeric values.
- **Data & Source Immutability:** Source CSV and baseline run directories remain 100% read-only.
- **Zero Premature Bloat (Ponytail):** Build the smallest complete solution (YAGNI). Keep core engines database-free and serverless.
- **Offline / Mock Mode by Default:** Pipeline functions completely offline; external LLM calls require explicit security authorization.
- **Unresolved Decisions Retained:** Items explicitly marked as deferred or undecided in Q1–Q51 are recorded as open gaps and never guessed.

## 3. Product Roadmap Overview (Three Horizons)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       NORTH STAR: BISNIS Q1–Q51                             │
│       Otomasi L1, Kolaborasi L2, Penghematan Workload, 6 Modul MVP          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
┌───────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
│ HORIZON 1: CORE ENGINE V1 │ │ HORIZON 2: MVP DELIVERY   │ │ HORIZON 3: SCALE & OPS    │
│ Milestone 1 - 4 (Headless)│ │ Milestone 5 (Workspace)   │ │ Post-MVP (Automation Ops) │
├───────────────────────────┤ ├───────────────────────────┤ ├───────────────────────────┤
│ • M1: Deterministic Engine│ │ • Modul 1: L1 Workspace   │ │ • Monitoring Operasional  │
│ • M2: Change Detection    │ │ • Modul 2: Mgmt Dashboard │ │   pasca-assessment (Q36)  │
│ • M3: AI Reviewer & Mock  │ │ • Modul 3: Download CSV   │ │ • Live Cloud Sync         │
│ • M4: Pipeline Hardening  │ │ • Modul 4: Gen Report     │ │   (SharePoint Graph API)  │
│   & V1 Core Acceptance    │ │ • Modul 5: Quality Review │ │ • Auto-Trigger Remediation│
│ • 5 Artefak Data Kontrak  │ │ • Modul 6: Follow-up Mgmt │ │   via AION / Script       │
│ • Imutabilitas & Hash     │ │ • Otorisasi L1/Mgmt (Q51) │ │                           │
└───────────────────────────┘ └───────────────────────────┘ └───────────────────────────┘
```

| Horizon | Milestone | Scope | Status |
|---|---|---|---|
| **Horizon 1** | **M1: Deterministic Pipeline** | Ingestion, validation, 6 derived metric calculations, run artifacts | **Approved** |
| **Horizon 1** | **M2: Change Detection** | Content hashing SHA-256, delta classification via `activity_id`, feedback inheritance | **Approved** |
| **Horizon 1** | **M3: AI Assessment Reviewer** | Local sanitization, batching (15-30), mock heuristics, JSONL & Markdown findings | **Approved** |
| **Horizon 1** | **M4: Full Pipeline Hardening & V1 Acceptance** | Connect all engines, rule consistency audit (Q14/Q29-35), E2E test, V1 release gate | **Approved** |
| **Horizon 2** | **M5: Operational Delivery (6 Modul MVP)** | L1 Assessment Workspace, Management Dashboard, CSV download, Report, Quality Review, Follow-up (Q50–Q51) | **Completed** |
| **Horizon 3** | **Post-MVP: Enterprise Scale & Cloud Sync** | Operational monitoring post-assessment (Q36), direct SharePoint/Graph API synchronization | **Future** |

------------------------------------------------------------------------

## 4. Milestone 1 --- Deterministic Pipeline

**Goal:** Build a working local CLI pipeline from CSV input to
deterministic enrichment output.

### Chunk 1 --- Project Foundation [APPROVED]

**Scope** - Inspect the existing project structure. - Establish a
minimal application structure. - Prepare project configuration. - Create
the `run_harness.py` entry point. - Set up basic logging. - Set up the
unit-testing structure and a smoke test.

**Acceptance criteria** - Project structure is ready for subsequent
modules. - CLI entry point executes. - Basic logging works. - Test
framework runs a smoke test successfully. - Existing project documents
and skills remain unchanged.

**Expected output** - Minimal runnable project skeleton. - Documented
command to run the application.

### Chunk 2 --- CSV Ingestion & Data Validation [APPROVED]

**Scope** - Read a local CSV input. - Check file existence and required
headers. - Validate required fields and numeric inputs. - Distinguish
missing, invalid, and negative values. - Isolate row-level errors so one
invalid row does not stop the entire run. - Preserve the source CSV
unchanged.

**Acceptance criteria** - Valid CSV can be loaded. - Missing file and
missing required headers are handled clearly. - Row-level validation
results are traceable. - Invalid rows do not cause silent data
corruption. - Tests cover valid and invalid input cases.

**Expected output** - Validated in-memory dataset. - Validation results
and row-level error information.

### Chunk 3 --- Workload Enrichment Engine [APPROVED]

**Scope**

Implement the six agreed derived columns:

1.  `Workload Saved Est. (Min/Month)`
2.  `Workload Reduction Est. (%)`
3.  `Workload Calculation Status`
4.  `Workload Evidence Status`
5.  `Workload Validation Notes`
6.  `Annualized Workload Saved Est. (Min/Year)`

Use the formulas, status priority, null handling, and evidence rules
already agreed in the PRD and Specification.

**Acceptance criteria** - Calculations are deterministic. - Missing
values are not treated as zero. - Zero workload and negative savings
follow the agreed rules. - Evidence status reflects link presence only;
it does not claim that evidence is valid. - AI/LLM is not used for
arithmetic or deterministic validation. - Unit tests cover the agreed
calculation and status scenarios.

**Expected output** - Enriched dataset containing the six derived
columns. - Passing unit tests for enrichment logic.

### Chunk 4 --- Output Generator [APPROVED]

**Scope** - Create a timestamped run directory using
`runs/YYYYMMDD_HHMMSS/`. - Generate `enriched_assessment.csv`. -
Generate `run_summary.json`. - Include processing counts and relevant
run metadata in the summary, consistent with the Specification.

**Acceptance criteria** - Both output files are generated in the run
directory. - Output format is valid and readable. - Source CSV remains
unchanged. - Output generation is covered by tests.

**Expected output** - `enriched_assessment.csv` - `run_summary.json`

### Chunk 5 --- CLI Integration

**Scope** - Connect CSV ingestion, validation, enrichment, and output
generation. - Support the command:

``` bash
py run_harness.py --input <path_csv>
```

-   Provide clear command-line errors and execution feedback.
-   Keep offline/mock behavior as the default.

**Acceptance criteria** - The command runs the deterministic pipeline
end to end. - Missing or invalid input is reported clearly. - A
successful run produces the expected artifacts. - CLI behavior is
tested.

**Expected output** - Runnable end-to-end deterministic CLI pipeline.

### Chunk 6 --- Milestone 1 Integration Testing & Verification

**Scope** - Run the complete test suite. - Run the CLI against synthetic
test CSV data. - Verify derived values and output files. - Verify
source-file immutability. - Compare implementation behavior with PRD and
Specification acceptance criteria.

**Acceptance criteria** - All required tests pass. - End-to-end CLI
execution succeeds. - Output artifacts are verified. - No unresolved
critical mismatch with the approved specification remains.

**Milestone 1 exit condition**

Milestone 1 is complete only after the deterministic pipeline runs
successfully from CSV input to output and its behavior has been reviewed
against the approved requirements.

------------------------------------------------------------------------

## 5. Milestone 2 --- Change Detection [APPROVED]

**Goal:** Compare the current input with the baseline run and classify row-level changes using `activity_id`.
**Status:** COMPLETED & FORMALLY APPROVED
**Verification Metrics:**
- 65/65 automated tests passed (100% pass rate, 0 warnings).
- Codebase overall line coverage: 95%.
- Change Detection module line coverage: 92%.
- Verified scenarios: TC-CD-01 to TC-CD-06, TC-CD-EX-01 to TC-CD-EX-03.
- Source CSV and baseline directory immutability verified (SHA-256 unchanged).

### Scope & Architectural Decisions

- **Strict `activity_id` Usage:**
  - `activity_id` is the primary and only identifier read and compared by Change Detection.
  - Change Detection **does not formulate, compute, or reconstruct** an ID from other columns (the previous rule combining `APPS + ACTIVITY NAME` is completely removed).
  - Initial ID issuance/generation is separated as an independent upstream concern outside Change Detection.
- **Source CSV Immutability:**
  - Source CSV remains 100% read-only and immutable.
- **Identity Validation & Anomaly Isolation:**
  - Missing or empty `activity_id` (null/blank) $\to$ classified as `REVIEW_REQUIRED` (reason: `EMPTY_ACTIVITY_ID`).
  - Duplicate `activity_id` within the same run $\to$ all colliding rows classified as `REVIEW_REQUIRED` (reason: `DUPLICATE_ACTIVITY_ID`).
  - Duplicate `activity_id` in baseline $\to$ any active run matching row classified as `REVIEW_REQUIRED` (reason: `AMBIGUOUS_MATCH`), preventing silent false matching or false deletion.
  - No guessing or heuristic fallback for invalid IDs.
- **Content Hashing:**
  - SHA-256 content hash computed deterministically across source data columns for each valid `activity_id` (derived columns excluded).
- **Change Classification:**
  - `UNCHANGED`: Matching `activity_id` and identical content hash.
  - `MODIFIED`: Matching `activity_id` with differing content hash.
  - `ADDED`: New `activity_id` present in current run but absent in baseline.
  - `DELETED`: `activity_id` present in baseline but missing in current run.
  - `REVIEW_REQUIRED`: Rows with empty, duplicate, or ambiguous `activity_id`.
- **Feedback Inheritance & AI Queue:**
  - `UNCHANGED` rows inherit previous AI assessment findings without LLM invocation. Deduplicated automatically.
  - Only `MODIFIED` and `ADDED` rows are routed to the AI assessment queue.
  - `DELETED` and `REVIEW_REQUIRED` rows are recorded in `change_log.json` and excluded from automated AI review.

### Acceptance Criteria

1. Change Detection reads `activity_id` directly from input rows without synthesizing or modifying it.
2. Rows with missing or empty `activity_id` are classified as `REVIEW_REQUIRED` without crashing the pipeline.
3. Duplicate `activity_id` values within a run are detected and classified as `REVIEW_REQUIRED`.
4. Valid rows matching previous baseline with identical content hash are classified as `UNCHANGED` and inherit previous feedback.
5. Valid rows matching previous baseline with modified values are classified as `MODIFIED`.
6. New `activity_id` values are classified as `ADDED`.
7. Baseline `activity_id` values missing from the new file are classified as `DELETED`.
8. `change_log.json` accurately logs all classifications, reasons for `REVIEW_REQUIRED`, modified fields, and summary counts.
9. Source CSV files remain completely untouched.

### Test Cases (Milestone 2)

| Test ID | Scenario | Input Baseline vs Current | Expected Classification | Expected Behavior / Output |
|---|---|---|---|---|
| **TC-CD-01** | Identical Row | Baseline: `id="ACT-01", hash="H1"`<br>Current: `id="ACT-01", hash="H1"` | `UNCHANGED` | Inherit previous AI feedback; exclude from AI queue |
| **TC-CD-02** | Attribute Modified | Baseline: `id="ACT-02", workload=100`<br>Current: `id="ACT-02", workload=80` | `MODIFIED` | Route to AI queue; record changed fields in `change_log.json` |
| **TC-CD-03** | New Activity Added | Baseline: absent<br>Current: `id="ACT-03", ...` | `ADDED` | Route to AI queue; log as added in `change_log.json` |
| **TC-CD-04** | Activity Deleted | Baseline: `id="ACT-04", ...`<br>Current: absent | `DELETED` | Log in `change_log.json`; do not send to AI queue |
| **TC-CD-05** | Empty `activity_id` | Current: `activity_id=""` or `None` | `REVIEW_REQUIRED` | Reason `EMPTY_ACTIVITY_ID`; do not guess ID; do not send to AI |
| **TC-CD-06** | Duplicate `activity_id` | Current: two rows with `activity_id="ACT-05"` | `REVIEW_REQUIRED` | Reason `DUPLICATE_ACTIVITY_ID`; both rows isolated; do not send to AI |

### Expected Output

- `change_log.json` containing change counts, delta details, and `REVIEW_REQUIRED` records.
- In-memory delta classification available for AI Reviewer and feedback inheritance.

------------------------------------------------------------------------

## 6. Milestone 3 --- AI Assessment Reviewer [APPROVED]

**Goal:** Produce evidence-based, traceable assessment feedback without
changing deterministic calculations or source data.
**Status:** COMPLETED & FORMALLY APPROVED
**Verification Metrics:**
- 92/92 automated tests passed (100% pass rate, 0 warnings).
- Codebase overall line coverage: 98%.
- AI Reviewer module line coverage: 98%.
- Verified scenarios: TC-AI-01, TC-AI-02, TC-AI-03, Local Sanitization, Grouping & Batching, Feedback Inheritance, JSONL and Markdown Artifact generation.
- Strict immutability of source CSV and baseline run directories verified (SHA-256 unchanged).

### Chunk areas

**A. Privacy & Payload Preparation [APPROVED]** - Local sanitization rules applied before external transmission (IPv4, IPv6, email, credentials, secrets masked). External API sending disabled unless security approval and `GEMINI_API_KEY` present. Offline mock mode works with zero network access.

**B. Grouping & Batching [APPROVED]** - Deterministic grouping by `Application + Activity Type` into batches of 15--30 rows. Singleton groups evaluate Data Quality and Automation Opportunity only, skipping comparative consistency review.

**C. AI Reviewer [APPROVED]** - Evaluates Data Quality (TC-AI-03), Assessment Consistency (TC-AI-01), and Automation Opportunity (TC-AI-02). Separates evidence from reasoning and recommendations. Confidence levels (`HIGH`, `MEDIUM`, `LOW`) assigned. Every finding has source-row and `activity_id` traceability.

**D. Feedback Outputs [APPROVED]** - Generates `feedback_report.jsonl` and `feedback_report.md` in timestamped run directory. Executive summary and findings grouped by Application and Focus Area. Deterministic separation guaranteed (total saved requiring review calculated strictly from deterministic enrichment results).

**Acceptance criteria** - Mock reviewer works without an API key or
network access. - Every finding is traceable to source data. - AI does
not overwrite source values or deterministic calculations. - External
API use remains subject to security approval. - Feedback outputs follow
the agreed data contract.

------------------------------------------------------------------------

## 7. Milestone 4 --- Full Pipeline Hardening & V1 Core Engine Acceptance

**Goal:** Menyatukan seluruh engine (Deterministik, Change Detection, dan AI Reviewer) ke dalam satu alur CLI terpadu yang kokoh, menyerap aturan konsistensi bisnis (Q14, Q29–Q35, Q42–Q44), dan memvalidasi ke-5 artefak standar terhadap kriteria penerimaan PRD V1.

**Status:** COMPLETED & VERIFIED (Ready for Approval)  
**Dependencies:** Milestone 1, Milestone 2, dan Milestone 3 telah selesai.
**Verification Metrics:**
- 112/112 automated tests passed (100% pass rate, 0 warnings).
- Codebase overall line coverage: 97%.
- Verified scenarios: TC-M4-01 to TC-M4-09.
- Ke-5 artefak standar terbit lengkap dan valid pada initial run maupun chained run.
- Source CSV dan baseline directory 100% immutable (SHA-256 identik).

### Business Decisions Baseline (Q1–Q51) yang Diintegrasikan di M4
- **Q2 & Q3 (Cakupan & Unit):** Memproses 100% baris `Breakdown Activity` (~1.000 aktivitas) secara utuh; 1 baris = 1 aktivitas (RFC 4180).
- **Q14 & Q18 (Konsistensi Mapping & Imutabilitas):** Deteksi inkonsistensi target mapping (`Automation` $\to$ `Already Automation`, `As Is` $\to$ `To Be Automated`, `Dismantled` $\to$ `Dismantled`) sebagai penanda review bagi L1; **dilarang auto-correct source CSV**.
- **Q29–Q35 (Status Tools & Solusi):** Penandaan status `Not Yet Solution` dan verifikasi bahwa tools sudah dibuat untuk `Already Automation`.
- **Q37–Q41 (Kalkulasi Workload):** Validasi deterministik penghematan bulanan, reduksi %, dan annualized saving.
- **Q42–Q44 (Konteks Follow-up):** Metadata penugasan tindak lanjut (`Action by`: L0, L1, atau L2) disematkan pada struktur temuan.

### Scope M4
1. **Business Rule Audit di AI Reviewer / Data Quality:**
   - Menambahkan deteksi otomatis inkonsistensi target mapping Q14 pada AI Reviewer.
   - Menambahkan tagging `Action by` (L0/L1/L2) pada kontrak temuan AI.
2. **Multi-Run CLI Orchestration & Edge Case Robustness:**
   - Eksekusi tunggal maupun berantai dengan `--prev-run` menghasilkan ke-5 artefak secara atomik.
3. **End-to-End Test Suite:**
   - Pengujian integrasi multi-skenario (identik, modified, added, deleted, review_required).
4. **V1 Core Release Gate:**
   - Verifikasi formal terhadap seluruh Acceptance Criteria PRD V1.

### Deliverables M4
Setiap run sukses menghasilkan 5 artefak standar di `runs/YYYYMMDD_HHMMSS/`:
1. `enriched_assessment.csv`: 1:1 baris sumber + 6 kolom turunan deterministik.
2. `run_summary.json`: Metadata eksekusi, hash sumber, count status kalkulasi, dan statistik AI.
3. `change_log.json`: Audit komparasi delta baris terhadap baseline sebelumnya.
4. `feedback_report.jsonl`: Kontrak mesin terstruktur untuk setiap temuan AI.
5. `feedback_report.md`: Laporan kerja manusia terstruktur per Aplikasi dan Fokus Area.

### Acceptance Criteria M4
- [x] **AC-M4-01 (Rule Mapping Q14):** Deviasi dari target mapping Q14 ditandai sebagai finding `ASSESSMENT_CONSISTENCY` (Confidence: `HIGH`, `action_by: "L1"`) tanpa mengubah data sumber.
- [x] **AC-M4-02 (Not Yet Solution Q29–31):** Aktivitas `To Be Automated` tanpa tools terisi ditandai untuk konfirmasi L2 atau pencarian solusi alternatif (`action_by: "L2"`).
- [x] **AC-M4-03 (Action by Tagging Q42–44):** Setiap finding AI memuat metadata penanggung jawab tindak lanjut (`Action by`: L0/L1/L2).
- [x] **AC-M4-04 (5 Artefak Standar):** Eksekusi CLI `--input` (dengan atau tanpa `--prev-run`) menghasilkan 5 file artefak secara lengkap dan valid.
- [x] **AC-M4-05 (Zero Regression):** 100% test suite pytest lulus dengan line coverage $\ge 90\%$ (aktual: 112/112 lulus, coverage 97%).
- [x] **AC-M4-06 (Source Immutability):** Hash SHA-256 file CSV input terbukti 100% identik sebelum dan sesudah eksekusi.

------------------------------------------------------------------------

## 8. Milestone 5 --- Operational Delivery & Assessment Workspace (6 Modul MVP)

**Goal:** Mentransformasikan hasil Core Engine V1 menjadi produk operasional nyata yang interaktif bagi Tim L1 AGIT dan Manajemen, mengimplementasikan 6 Modul MVP (Q50), pembagian otorisasi pengguna (Q51), serta integrasi arsitektur operasional perusahaan:
- **SharePoint Excel (`SOP L1 AGIT.xlsx`, sheet `Breakdown Activity`)**: *Operational Source of Truth*.
- **Power Automate**: Trigger, ekstraksi data, dan sinkronisasi kembali (*orchestration*).
- **Workload Enrichment Engine**: Pemrosesan deterministik, validasi, deteksi perubahan, dan AI assessment review.
- **Dashboard**: Assessment Workspace (L1) dan Monitoring (Management).

**Status:** COMPLETED & VERIFIED  
**Dependencies:** Milestone 4 Core Engine V1 telah disahkan (kontrak data 5 artefak stabil).
**Verification Metrics:**
- 141/141 automated tests passed (100% pass rate, 0 warnings).
- Codebase overall line coverage: 97%.
- Operational sync module line coverage: 96%.
- Dashboard module line coverage: 100%.
- Verified scenarios: TC-M5-01 to TC-M5-06 (6 MVP modules, role permissions, JSON operational intake, client-side CSV download, quality review isolation, follow-up tracker, SharePoint delta sync payload, formula protection, anti-trigger-loop idempotency).
- Imutabilitas formula Excel dan data sumber asli terjaga 100%.

### Business Decisions Baseline (Q1–Q51) yang Diimplementasikan di M5
- **Q45–Q49 (Dashboard & Peran Pengguna):**
  - Dashboard sebagai output utama yang berfungsi ganda: **Assessment Workspace (L1)** dan **Monitoring Dashboard (Management)**.
  - Informasi dashboard: Summary, Assessment, Quality, Automation, dan Follow-up.
- **Q50 (6 Modul MVP):**
  1. **Assessment Workspace (L1):** Ruang kerja L1 untuk meninjau dan mengelola hasil per baris aktivitas, dilengkapi dirty tracking untuk persiapan sinkronisasi.
  2. **Monitoring Dashboard (Management):** Ringkasan efisiensi, statistik status, progres, dan kemampuan *drill-down* ke rincian aktivitas.
  3. **Export & SharePoint Sync:** Pengunduhan hasil kalkulasi CSV terkini (backup/analisis lokal) dan ekspor delta payload terstruktur (JSON) untuk Power Automate sync ke SharePoint Excel.
  4. **Generate Assessment Report:** Pembuatan laporan berkala hasil evaluasi dan rekomendasi otomasi (Print / PDF Ready).
  5. **Quality Review:** Panel khusus untuk menyelesaikan inkonsistensi data, deviasi Q14, dan baris `REVIEW_REQUIRED`.
  6. **Follow-up Management:** Pelacakan tindak lanjut, koordinasi dukungan L2, dan status implementasi per `Action by`.
- **Q51 (Otorisasi Akses):**
  - **L1:** Hak edit penuh pada assessment, `Improvement Category`, `Category Notes`, `Quality Review`, dan `Follow-up`.
  - **Management:** Hak akses *Read-Only* (Summary + drill-down ke detail aktivitas).
- **Integrasi Arsitektur Operasional (SharePoint Excel + Power Automate):**
  - Ingestion mendukung data operasional dari Power Automate extract (JSON/Excel snapshot) serta CSV RFC 4180 sebagai fallback & test harness.
  - Imutabilitas workbook SharePoint terjaga: L1 mengekspor delta updates yang disinkronkan oleh Power Automate, mencegah penimpaan tidak sengaja pada formula lookup `A:AI`.

### Deliverables M5
1. **Interactive Assessment Workspace & Monitoring Dashboard** (`dashboard.html` di setiap run, memuat seluruh 6 modul MVP).
2. **Quality & Review Resolver Module** (penyelesaian anomali semantik dan target mapping Q14).
3. **Follow-up & Coordination Module** (penugasan PIC L0/L1/L2 dan pelacakan status).
4. **Export & SharePoint Sync Exporter** (Delta JSON payload untuk Power Automate + CSV fallback + HTML/MD print generator).
5. **Operational Data Ingestion Adapter** (Dukungan konsumsi data JSON ekspor Power Automate di samping CSV).
6. **Operational Sync Validation Module** (`harness/operational_sync.py` & CLI `--validate-sync`).
7. **Production Office Scripts Suite** (`scripts/office_scripts/export_breakdown_activity.ts` & `sync_breakdown_activity.ts`).
8. **Panduan Integrasi Operasional Terpadu** (`docs/OPERATIONAL_INTEGRATION_GUIDE.md`).
9. **CLI Local Server** (`run_harness.py --serve [run_dir] --port [port]`).

### Acceptance Criteria M5
- [x] **AC-M5-01 (6 Modul MVP):** Seluruh 6 modul MVP (Q50) dapat diakses dan berfungsi sesuai alur pengguna pada `dashboard.html`.
- [x] **AC-M5-02 (Hak Edit L1 vs Read-Only Management):** L1 dapat mengedit kategori dan tindak lanjut; mode Management terkunci *read-only* (Q51).
- [x] **AC-M5-03 (Quality Review Isolation):** Seluruh anomali data, deviasi Q14, dan baris review_required diisolasi terpisah dengan saran resolusi.
- [x] **AC-M5-04 (Follow-up Tagging):** Aktivitas terkelompok rapi berdasarkan `Action by` (L0/L1/L2).
- [x] **AC-M5-05 (Export & SharePoint Sync):** Menyediakan unduhan CSV dan ekspor SharePoint sync payload (JSON delta) tanpa merusak file sumber.
- [x] **AC-M5-06 (Operational Ingestion Contract):** Pipeline mampu mengonsumsi data operasional (JSON payload Power Automate) dengan tetap mempertahankan ingestion CSV.

------------------------------------------------------------------------

## 9. Horizon 3 --- Post-MVP: Enterprise Scale & Automated Operations

**Goal:** Menghubungkan sistem ke ekosistem otomasi live dan integrasi enterprise skala penuh.

**Status:** FUTURE (Di luar lingkup V1 dan MVP awal)

### Scope
- **Operational Monitoring (Q36):** Monitoring pasca-assessment untuk melacak keandalan tools otomasi yang sudah berjalan di sistem live.
- **Direct Bidirectional Cloud Sync:** Integrasi API langsung dengan Microsoft Graph API (SharePoint / Teams) dan sistem tiket/LKPP.
- **Auto-remediation Triggers:** Memicu pembuatan bot otomasi AION atau script runner secara langsung berdasarkan hasil evaluasi `To Be Automated`.

------------------------------------------------------------------------

## 10. Keputusan Bisnis yang Sengaja Ditunda / Belum Final (Unresolved Items)

Sesuai prinsip SDD dan catatan resmi Q1–Q51 Bagian G & I, hal-hal berikut **tetap ditandai sebagai unresolved** dan tidak boleh diasumsikan sepihak dalam implementasi:

1. **Format Representasi Gabungan (Q31, Q.G.4):** Format penulisan sel jika suatu aktivitas berstatus `To Be Automated` sekaligus `Not Yet Solution` dalam satu kolom `Category Notes`.
2. **Detail Komponen UI Dashboard (Q.G.5):** Rincian layout halaman, komponen filter, palet warna, dan jenis visualisasi grafik dashboard belum dirinci.
3. **Hak Komentar/Feedback Management (Q51, Q.I):** Hak Management untuk memberikan komentar atau feedback pada aktivitas belum ditetapkan (hanya diputuskan read-only summary + drill-down).
4. **Alur Status Awal ke Done (Q.G.1):** Rincian tahapan state machine operasional dari draft awal hingga berstatus `Done`.
5. **Formula Workload Saving Excel:** Formula saving tidak disalin manual, melainkan tetap merujuk pada artefak formal proyek (PRD Sec 4.2).

------------------------------------------------------------------------

## 11. Development Workflow (SDD Cycle)

Setiap chunk dan milestone mengikuti siklus Spec-Driven Development (SDD):

1. **Inspect & Model:** Analisis baseline bisnis (Q1–Q51), perbarui `Specification.md` dan `GLOSSARY.md`.
2. **Draft Testable Contract:** Definisikan acceptance criteria dalam bentuk Given-When-Then test cases.
3. **Implement Smallest Solution (Ponytail):** Tulis kode seminimal mungkin untuk memenuhi kontrak, hindari abstraksi berlebih.
4. **Test & Verify:** Jalankan `py -m pytest`, pastikan 100% pass rate dan $\ge 90\%$ line coverage.
5. **Git Discipline:** Commit menggunakan Conventional Commits di branch `develop`.
6. **Review & Approval Gate:** Berhenti dan tunggu verifikasi sebelum melangkah ke milestone berikutnya.

------------------------------------------------------------------------

## 12. Scope Boundaries

- **Lingkup M4 (Core Engine V1):** Headless CLI, local sanitization, deterministic enrichment, change detection, AI reviewer findings, 5 standardized artifacts. Dilarang menambah web framework atau database server di M4.
- **Lingkup M5 (MVP Delivery):** 6 Modul MVP dan layer konsumsi data (Workspace L1 & Management Dashboard).
- **Di Luar Lingkup (Out of Scope V1 & M5):**
  - Database server eksternal (PostgreSQL/Oracle/MongoDB).
  - LKPP API integration.
  - Egress pengiriman API publik tanpa security approval enterprise.
  - Modifikasi source CSV secara in-place.

------------------------------------------------------------------------

## 13. Current Starting Point

**Active Milestone:** Milestone 5 --- Operational Delivery, Assessment Workspace & SharePoint Integration  
**Working Branch:** `develop`  
**Status:** M5 Completed and Verified. Ready for Final Deployment Review.

------------------------------------------------------------------------

## 14. Progress Tracker

| Milestone / Chunk | Scope / Komponen | Status | Governance Review |
|---|---|---|---|
| **M1 --- Chunk 1: Foundation** | Project skeleton, config, logging, smoke test | Completed | Approved |
| **M1 --- Chunk 2: CSV Ingestion** | Fail-fast validation, numeric parsing, null handling | Completed | Approved |
| **M1 --- Chunk 3: Enrichment** | 6 derived metrics calculation, deterministic priority | Completed | Approved |
| **M1 --- Chunk 4: Output Generator**| Run directory `runs/YYYYMMDD_HHMMSS/`, CSV & summary | Completed | Approved |
| **M1 --- Chunk 5: CLI Integration** | `run_harness.py --input` CLI pipeline | Completed | Approved |
| **M1 --- Chunk 6: Integration Test**| End-to-end deterministic verification | Completed | Approved |
| **M2 --- Change Detection** | Content hashing SHA-256, delta tracking `activity_id` | Completed | Approved |
| **M3 --- AI Reviewer** | Local sanitization, batching, mock heuristics, JSONL/MD | Completed | Approved |
| **M4 --- Pipeline Hardening & Acceptance** | Business rule audit (Q14/Q29-35), E2E test, V1 release gate | Completed | Approved |
| **M5 --- Operational Workspace & Sync** | 6 Modul MVP, SharePoint Excel & Power Automate Sync | Completed | Approved |
| **Post-MVP --- Enterprise Operations** | Live monitoring (Q36), direct cloud sync | Planned | Future Horizon |
