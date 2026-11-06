# WORKLENS — Legacy Document Inventory & Gap Analysis

> **Tujuan:** Inventarisasi perbandingan dokumen dari legacy project (`workload_enrichment`) menuju platform `WORKLENS`.  
> **Source Repository (READ-ONLY):** `C:\Users\rahma\OneDrive\Documents\workload_enrichment`  
> **Target Repository:** `C:\Users\rahma\OneDrive\Documents\worklens`  
> **Tanggal Audit:** 2026-11-05

---

## 1. Taksonomi Klasifikasi Gap

Setiap dokumen atau aset pengetahuan dari legacy project diklasifikasikan ke dalam 5 status:

1. **`ALREADY_EXISTS`**: Dokumen atau konten sudah tersedia di repositori WORKLENS dengan konten yang setara atau lebih terbarui.
2. **`MUST_MIGRATE`**: Dokumen/pengetahuan otoritatif yang wajib dipindahkan ke WORKLENS karena berisi business rules, formula, skema, kamus data, atau governance yang masih aktif.
3. **`REFERENCE_ONLY`**: Dokumen, artefak historis, dataset biner, atau source code legacy yang tetap berada di repositori lama dan hanya diakses sebagai referensi read-only.
4. **`OBSOLETE`**: Dokumen yang mendeskripsikan fitur atau batasan yang sudah ditinggalkan secara sengaja (misalnya integrasi SharePoint / OneDrive Desktop Sync / Graph API).
5. **`CONFLICT`**: Dokumen yang memuat spesifikasi yang berbenturan dengan arsitektur target WORKLENS atau terdapat perbedaan antara teks dokumen vs implementasi kode & pengujian.

---

## 2. Tabel Inventaris Dokumen Legacy

| No | Nama Dokumen / File Sumber | Kategori / Subjek | Status Klasifikasi | Target Lokasi di WORKLENS | Catatan Evaluasi & Justifikasi |
|:---:|:---|:---|:---:|:---|:---|
| 1 | `AGENTS.md` | Agent Canonical Rules & Governance | **MUST_MIGRATE** | `AGENTS.md` (Root) | Aturan kanonikal agent, hierarki dokumen, data immutability, pemisahan deterministik vs AI, dan DoD. Perlu diadaptasi untuk arsitektur FastAPI + React WORKLENS. |
| 2 | `GEMINI.md` | Agent Entry Point | **MUST_MIGRATE** | `GEMINI.md` (Root) | Entry point standar Antigravity yang mengarahkan konteks ke `AGENTS.md`. |
| 3 | `GLOSSARY.md` | Domain Ubiquitous Language | **MUST_MIGRATE** | `docs/domain/GLOSSARY.md` | Berisi definisi istilah domain: Activity ID, Activity Type, Improvement Category, Category Notes, Target Mapping, dan metrik workload. |
| 4 | `SOP_L1_AGIT_Agent_Harness_PRD_V1.md` | Product Requirements Document | **MUST_MIGRATE** | `docs/domain/PRD_V1.md` | Baseline PRD V1 yang disetujui (Locked Baseline). Menentukan 6 metrik turunan, status bukti, dan batasan privasi lokal. |
| 5 | `SOP_L1_AGIT_Agent_Harness_Specification.md` | Authoritative Technical Specification | **MUST_MIGRATE** | `docs/domain/TECHNICAL_SPECIFICATION.md` | Spesifikasi formula matematis, 6 hierarki status kalkulasi, algoritma hash SHA-256, dan format output JSONL/Markdown. |
| 6 | `Workload_Enrichment_Tanya_Jawab_Q1-Q51.md` | Business Decisions (Q1–Q51) | **MUST_MIGRATE** | `docs/domain/BUSINESS_DECISIONS_Q1_Q51.md` | Sumber otoritas primer seluruh keputusan bisnis, peran L1 vs L2 vs Management, aturan dismantling, dan target mapping. |
| 7 | `Breakdown_Activity_Lookup_Map.md` | Data Dictionary (Kolom A:AI) | **MUST_MIGRATE** | `docs/domain/DATA_DICTIONARY.md` | Struktur 35 kolom assessment, formula kalkulasi, dan relasi lookup sheet yang menjadi basis validasi skema. |
| 8 | `GIT_WORKFLOW.md` | Standard Version Control & Branching | **MUST_MIGRATE** | `docs/GIT_WORKFLOW.md` | Standar branching `develop`, aturan Conventional Commits, dan panduan recovery aman tanpa `git reset --hard`. |
| 9 | `SOP_L1_AGIT_Agent_Harness_Project_Context.md` | Operational Context & Flow | **MUST_MIGRATE** | `docs/domain/PROJECT_CONTEXT.md` | Latar belakang operasional Tim L1 AGIT, volume data (~1.000 aktivitas), dan arsitektur pipeline tingkat tinggi. |
| 10 | `README.md` (Legacy) | Project Readme | **ALREADY_EXISTS** | `README.md` | WORKLENS telah memiliki `README.md` independen yang disesuaikan dengan arsitektur baru (FastAPI + React). Tidak perlu ditimpa. |
| 11 | `docs/ARCHITECTURE.md` (WORKLENS) | High-Level Architecture | **ALREADY_EXISTS** | `docs/ARCHITECTURE.md` | Sudah dibuat di WORKLENS memetakan arsitektur FastAPI, Pydantic, In-Memory Store, dan React UI. |
| 12 | `docs/COMPONENTS_ANALYSIS.md` (WORKLENS) | Porting Strategy Analysis | **ALREADY_EXISTS** | `docs/COMPONENTS_ANALYSIS.md` | Sudah dibuat di WORKLENS memetakan modul Reused, Adapted, Rebuilt, dan Dropped. |
| 13 | `docs/OPERATIONAL_INTEGRATION_GUIDE.md` | SharePoint & Power Automate Sync | **OBSOLETE** / **CONFLICT** | *None* (Tinggal di Legacy) | Panduan alur Power Automate & sync SharePoint. Usang karena arsitektur WORKLENS secara eksplisit menolak integrasi OneDrive/SharePoint Desktop Sync. |
| 14 | `SOP_L1_AGIT_Agent_Harness_Development_Roadmap_V1.md` | Roadmap Tiga Horizon | **REFERENCE_ONLY** | `docs/domain/LEGACY_ROADMAP_V1.md` | Roadmap legacy chunk-by-chunk. Dijadikan referensi historis pencapaian M1–M4. |
| 15 | `AGENT_SKILL_GENERALIZATION_REPORT.md` | Skill Audit & Generalization Report | **REFERENCE_ONLY** | *None* (Tinggal di Legacy) | Laporan historis generalisasi skill pada 2026-10-30. Bermanfaat sebagai wawasan tetapi tidak operasional. |
| 16 | `SOP L1 AGIT.xlsx` (42 MB) | Source Assessment Workbook | **REFERENCE_ONLY** | *None* (Tinggal di Legacy) | File biner Excel asli; dilarang dipindahkan atau diubah agar tetap menjadi source of truth fisik yang immutabel. |
| 17 | `breakdown_activity (1).json` (3.8 MB) | Dump JSON Assessment | **REFERENCE_ONLY** | *None* (Tinggal di Legacy) | Dataset operasional referensi. Akan disediakan sampel ringkas di WORKLENS untuk pengujian unit fixture. |
| 18 | `SOP L1 AGIT (6).csv` / `_UTF8.csv` | Dataset CSV Ingestion | **REFERENCE_ONLY** | *None* (Tinggal di Legacy) | File data input legacy. |
| 19 | `run_harness.py`, `mcp_server.py`, `harness/*.py` | Legacy Implementation Source Code | **REFERENCE_ONLY** | *None* (Tinggal di Legacy) | Kode implementasi legacy. Akan di-porting secara modular pada fase engineering berikutnya. |

---

## 3. Matriks Hasil Gap Analysis

```text
Total Item Teridentifikasi: 19 aset pengetahuan/dokumen
├── MUST_MIGRATE      : 8 dokumen (Domain Knowledge, Specs, Rules, Dictionary)
├── ALREADY_EXISTS    : 3 dokumen (README, ARCHITECTURE, COMPONENTS_ANALYSIS)
├── REFERENCE_ONLY    : 6 item (Dataset biner, script legacy, roadmap legacy)
└── OBSOLETE/CONFLICT : 2 item (SharePoint/OneDrive Integration Guide)
```

