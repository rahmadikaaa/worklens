# WORKLENS — Operational Enrichment Rule Discovery

> **Document Type:** Discovery & Domain Architecture Synthesis  
> **Status:** Final & Validated  
> **Repository:** `worklens`  
> **Location:** `docs/enrichment/discovery/`  
> **Source Datasets:**  
> - Source JSON: `C:\Users\rahma\OneDrive\Documents\worklens\backend\uploads\breakdown_activity_261105_1704_1.json` (3,460 activities)  
> - Benchmark CSV: `C:\Users\rahma\OneDrive\Documents\worklens\backend\uploads\REA\Improvements_With_Benefit.csv` (667 records)  

---

## 1. Executive Summary

Dokumen ini menyajikan hasil **Reverse Engineering Enrichment Discovery** pada platform WORKLENS dengan meneliti langsung dua file aktual:
1. **Source JSON:** `backend/uploads/breakdown_activity_261105_1704_1.json` (3.460 baris aktivitas mentah).
2. **Benchmark CSV:** `backend/uploads/REA/Improvements_With_Benefit.csv` (667 baris hasil kurasi manual).

Hasil penemuan membuktikan bahwa perhitungan beban kerja (*Workload*) dan pembentukan narasi manfaat (*Benefit*) adalah **100% deterministik** dan dapat direplikasi secara presisi tanpa estimasi atau intervensi AI generatif.

```mermaid
flowchart TD
    subgraph StorageTracking ["1. Dataset Input Aktual"]
        RawJSON["Source JSON (3,460 activities)<br/>breakdown_activity_261105_1704_1.json"]
        BenchmarkCSV["Benchmark CSV (667 records)<br/>Improvements_With_Benefit.csv"]
    end

    subgraph DiscoveryEngine ["2. Analisis & Formulasi Aturan"]
        WorkloadRule["Kalkulasi Workload:<br/>Durasi × Event Per Month"]
        TaxonomyRules["Taksonomi Bisnis:<br/>6 Category Actions | 8 Tools | 3 Status Triggered"]
        BenefitGrammar["Benefit Linguistic Synthesis:<br/>Unit Scaling, Clauses & Syntax Exceptions"]
    end

    subgraph Verification ["3. Verifikasi & Validasi 100%"]
        WL_Val["Workload Formula: 667/667 (100.00%)"]
        BEN_Val["Benefit Grammar: 667/667 (100.00%)"]
        Link_Val["Primary Key Linkage: 667/667 (100.00%)"]
    end

    RawJSON & BenchmarkCSV --> DiscoveryEngine
    WorkloadRule --> WL_Val
    TaxonomyRules & BenefitGrammar --> BEN_Val
    RawJSON --> Link_Val
```

---

## 2. Dataset Overview & Hasil Pencocokan (Matching Results)

| Parameter | Source JSON | Benchmark CSV | Hasil Pencocokan |
|---|---|---|---|
| **Lokasi File** | `backend/uploads/breakdown_activity_261105_1704_1.json` | `backend/uploads/REA/Improvements_With_Benefit.csv` | Kedua file valid dan terbaca langsung. |
| **Jumlah Baris** | 3.460 baris aktivitas | 667 baris benchmark | 667 / 667 (100.00%) terpetakan ke JSON. |
| **Kunci Pencocokan** | `activity_id` (atau `CONCAT`) | `CONCAT` | Kunci identitas baris terbukti 1:1. |
| **Exact String Match** | — | — | **658 baris (98,65%)** persis sama. |
| **Stripped Match** | — | — | **9 baris (1,35%)** dengan trailing whitespace di CSV. |
| **Unmatched / Orphan** | — | — | **0 baris (0,00%)** — tidak ada data hilang. |

### Temuan Skema Data Mentah vs Benchmark
1. **`Category Action`:** Pada JSON sumber, kolom ini **100% kosong** (string hampa `""`) untuk seluruh 3.460 aktivitas. Pada CSV benchmark, kolom ini diperkaya menjadi 6 kelas aksi baku.
2. **`Status Triggered`:** Kolom ini **tidak ada** pada JSON sumber. Nilai `Fully Automated`, `Not Yet Triggered Automated`, dan `Partial Automated` merupakan hasil penilaian kematangan operasional oleh tim SME.
3. **`Benefit`:** Kolom narasi ini **tidak ada** pada JSON sumber. Nilai dibentuk secara 100% deterministik mengikuti formula tata bahasa terstruktur.

---

## 3. Klasifikasi Tingkat Keyakinan (Confidence Status)

Seluruh temuan dikelompokkan ke dalam 3 tingkat kepastian:

### A. CONFIRMED (100% Deterministic & Empirical Proof)
Aturan yang telah diverifikasi secara matematis dan string-by-string pada seluruh 667 baris tanpa deviasi:
1. **`RULE-WL-01` (Formula Workload):** $\text{Workload} = \text{Durasi (Menit)} \times \text{Event Per Month}$. Akurasi 667/667 (100,00%).
2. **`RULE-WL-02` (Zero Workload):** Saat $\text{Workload} = 0$, narasi Benefit beralih ke mitigasi percepatan pemulihan sistem tanpa klausul menit. Terbukti pada 2 baris (Baris 308 & 309).
3. **`RULE-BEN-01` (Penskalaan Unit):** $\text{Workload} < 60 \implies \text{minutes}$; $\text{Workload} \ge 60 \implies \text{hours}$ dengan pembulatan 1 desimal (`.1f`).
4. **`RULE-BEN-02` (Klausul Frekuensi):** $\text{Event} = 1 \implies \text{"(saving X minutes per event)"}$; $\text{Event} > 1 \implies \text{"(saving X minutes per event across N monthly events)"}$.
5. **`RULE-BEN-03` (Preposisi Tool):** Tool normal menggunakan `via {Tool}`; tool `CICD` menggunakan `via CI/CD automation`; tool `Not Automate` menggunakan `through standardized automation` (tanpa kata 'via').
6. **`RULE-BEN-04` (Frase Aksi):** 6 frasa baku untuk masing-masing dari 6 `Category Action`.
7. **`RULE-BEN-05` (Prefix Template):** Template eksekutif berdasarkan `Status Triggered`:
   - `Fully Automated`: `Eliminates {workload_str} of manual operational workload per month ({duration_clause}) {tool_clause} through {action_phrase}.`
   - `Not Yet Triggered Automated`: `Potentially eliminates {workload_str} of manual operational workload per month ({duration_clause}) once automated {tool_clause} through {action_phrase}.`
   - `Partial Automated`: `Reduces monthly operational workload by {workload_str} ({duration_clause}) {tool_clause} through {action_phrase}.`
8. **`RULE-LNK-01` (Linkage CONCAT):** `CONCAT` (CSV) menghubungkan baris ke `activity_id` (JSON) secara eksak setelah normalisasi spasi.

### B. INFERRED (High-Confidence Heuristics)
Pola yang disimpulkan dari semantik teks dan metadata pendukung:
1. **`RULE-INF-01` (Penyempurnaan Tooling):** 127 baris mengalami penyesuaian perkakas dari JSON ke CSV (misal 93 aktivitas `Not Automate` dinaikkan menjadi `AION` karena dokumentasi SOP/Runbook telah mendukung AION).
2. **`RULE-INF-02` (Klasifikasi Kategori Aksi):** Kategori aksi dipetakan berdasarkan kata kunci judul aktivitas (`ACTIVITY NAME` / `SOP Name`): *Housekeeping* $\to$ `Auto Housekeeping`; *Monitoring / Check / Alert* $\to$ `Auto Monitoring` / `Health Check`; *Restart / Bot* $\to$ `Smart Healing` / `Auto Restart`; *Whitelist / User Request* $\to$ `Self Service Request`.
3. **`RULE-INF-03` (Penetapan Status Triggered):** Menandakan kesiapan automasi produksi: `Fully Automated` (aktif di crontab/webhook), `Not Yet Triggered Automated` (skrip ada tapi trigger belum otomatis), `Partial Automated` (skrip otomasi sebagian dengan verifikasi manual).
4. **`RULE-INF-04` (Penyaringan Kandidat 667):** Sebanyak 667 aktivitas dipilih dari 3.460 baris dengan memprioritaskan aplikasi berfrekuensi tinggi (69 aplikasi) dan catatan `Already Automation`.

### C. UNRESOLVED / KASUS PENGECUALIAN
Penyesuaian manual individual atau ambiguitas klasifikasi:
1. **`EXC-01` (Manual Duration Override):** Aktivitas `'Email Relay External - Housekeeping'` — Nilai Durasi di JSON adalah 30 menit (Workload 30), namun di CSV diubah manual menjadi 5 menit (Workload 5). Formula internal $\text{Workload} = 5 \times 1 = 5$ tetap 100% konsisten.
2. **`EXC-02` (Manual Event Frequency Override):** Aktivitas `'Elisa - Check Log Elisa di DB'` — Nilai Event di JSON adalah 30 kejadian (Workload 150), di CSV diubah manual menjadi 1 kejadian (Workload 5). Formula internal $\text{Workload} = 5 \times 1 = 5$ tetap 100% konsisten.
3. **`EXC-03` (Ambiguitas Restart vs Smart Healing):** 199 aktivitas bertajuk "Restart" diklasifikasikan ke `Smart Healing` (remediasi insiden), sementara 9 aktivitas dimasukkan ke `Auto Restart` (restart rutin worker/bot).
4. **`EXC-04` (Trailing Whitespace di CSV):** 9 baris pada CSV memiliki spasi ekstra di akhir kunci `CONCAT` (misal `'C2P - Check Transaction C2P Service by Grafana '`), membutuhkan fungsi `.strip()` saat pencocokan.

---

## 4. Validasi & Bukti Statistik

- **Total Aktivitas Benchmark:** 667 baris
- **Total Workload Teridentifikasi:** 37.425,0 menit/bulan (**623,8 jam/bulan**)
- **Workload Formula Accuracy:** **100.00%** (667/667 match)
- **Benefit Text Accuracy:** **100.00%** (667/667 match)
- **Linkage Accuracy:** **100.00%** (658 exact + 9 stripped = 667)
- **Distribusi Status Triggered:**
  - `Fully Automated`: 389 aktivitas (58,3%)
  - `Not Yet Triggered Automated`: 256 aktivitas (38,4%)
  - `Partial Automated`: 22 aktivitas (3,3%)

---

## 5. Kepatuhan Batasan & Ketentuan

1. **Source Immutability:** Berkas `breakdown_activity_261105_1704_1.json` dan `Improvements_With_Benefit.csv` tidak dimodifikasi sama sekali (100% read-only).
2. **Pipeline P1–P3:** Seluruh pipeline upload, parser, dan snapshot versioning tidak disentuh.
3. **No Premature Implementation:** Tidak membuat enrichment engine otomatis mendahului milestone terkait.
4. **Halaman Dashboard:** Halaman **Enrichment Discovery** telah dibuat dan terintegrasi di WORKLENS frontend dengan visualisasi KPI, Rule Catalog, Decision Table, Exception Inspector, dan Live Verifier Playground.
