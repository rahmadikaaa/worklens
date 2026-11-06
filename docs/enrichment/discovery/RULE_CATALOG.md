# WORKLENS — Enrichment Rule Catalog

> **Status:** Approved Discovery Baseline  
> **Target Scope:** Phase 1 Operational Enrichment Engine  
> **Source Benchmark:** `backend/uploads/REA/Improvements_With_Benefit.csv` (667 records)  
> **Linked Snapshot:** `backend/uploads/breakdown_activity_261105_1704_1.json` (3,460 records)  

---

## 1. Overview

Katalog aturan ini mendokumentasikan spesifikasi aturan bisnis formal hasil proses **Enrichment Rule Discovery** pada dataset operasional WORKLENS. Aturan ini mencakup kalkulasi beban kerja (*Workload*), taksonomi tindakan operasional (*Category Action*), perkakas otomasi (*Tools Automation*), tingkat kesiapan eksekusi (*Status Triggered*), dan pembentukan narasi manfaat (*Benefit Generation*).

---

## 2. Workload Calculation Rules

### `RULE-WL-01: Deterministic Workload Formula`
- **Tujuan:** Menghitung total durasi beban kerja operasional per bulan.
- **Formula:**
  $$\text{Workload (Menit/Bulan)} = \text{Durasi (Menit)} \times \text{Event Per Month}$$
- **Prekondisi:**
  - $\text{Durasi (Menit)} \ge 0$
  - $\text{Event Per Month} \ge 1$
- **Tipe Data & Presisi:**
  - `Durasi (Menit)`: Numerik (float / integer menit).
  - `Event Per Month`: Numerik (integer / float frekuensi bulanan).
  - `Workload`: Numerik (menit per bulan).
- **Hasil Validasi:**
  - **Match:** 667 / 667 baris (100.00%).
  - **Mismatch:** 0.

### `RULE-WL-02: Zero Workload Handling`
- **Kondisi:** $\text{Durasi} = 0$ atau $\text{Workload} = 0$.
- **Perilaku:** Diterima sebagai aktivitas non-durasi terukur (misal stand-by atau event reaktif tanpa durasi manual baseline tercatat). Narasi Benefit menggunakan penanganan khusus tanpa klausul menit.

---

## 3. Operational Taxonomy Rules (Category Action)

Terdapat 6 kategori tindakan operasional terdefinisi:

| Rule ID | Category Action | Definisi Operasional | Frase Aksi Baku dalam Benefit | Frekuensi Data |
|---|---|---|---|---|
| `RULE-CA-01` | `Auto Monitoring` | Pemantauan sistem, proses, metrik, atau log secara otomatis dan proaktif. | `continuous proactive monitoring and real-time anomaly detection` | 190 (28.5%) |
| `RULE-CA-02` | `Smart Healing` | Penanganan kegagalan atau gangguan secara otomatis (self-healing / remediation). | `automated fault detection and self-healing recovery` | 199 (29.8%) |
| `RULE-CA-03` | `Self Service Request` | Pemenuhan permintaan operasional/tiket melalui portal/eksekusi mandiri tanpa keterlibatan manual L1. | `streamlined self-service execution and eliminating manual ticket handling` | 120 (18.0%) |
| `RULE-CA-04` | `Auto Housekeeping` | Pembersihan berkala log file, temporary table, atau disk space. | `scheduled automated log and disk housekeeping` | 112 (16.8%) |
| `RULE-CA-05` | `Health Check` | Pemeriksaan kesehatan berkala infrastruktur, konektivitas, database, dan aplikasi. | `automated system health checks and proactive issue prevention` | 37 (5.5%) |
| `RULE-CA-06` | `Auto Restart` | Restart service, worker, pod, atau bot secara otomatis saat terjadi anomali atau degradasi. | `automated service restarts and rapid downtime mitigation` | 9 (1.3%) |

---

## 4. Automation Tools Rules (Tools Automation)

Pemetaan perkakas otomasi ke klausul teks narasi pada kalimat Benefit:

| Rule ID | Raw Tool Code | Canonical Tool Name | Benefit Preposition Clause | Keterangan | Frekuensi |
|---|---|---|---|---|---|
| `RULE-TA-01` | `AION` | AION Platform | `via AION` | Platform AIOps / Automation utama Telkomsel. | 323 (48.4%) |
| `RULE-TA-02` | `Shell Script` / `Shell script` | Shell Script | `via Shell Script` | Script otomasi OS/Linux (crontab/systemd). | 244 (36.6%) |
| `RULE-TA-03` | `Grafana` | Grafana | `via Grafana` | Dashboard pemantauan dan alerting metrik. | 65 (9.7%) |
| `RULE-TA-04` | `BMC` | BMC Remedy / TrueSight | `via BMC` | IT Service Management & event integration. | 18 (2.7%) |
| `RULE-TA-05` | `DSC` | Desired State Config | `via DSC` | Automation configuration framework. | 8 (1.2%) |
| `RULE-TA-06` | `CICD` | CI/CD Pipeline | `via CI/CD automation` | Pipeline integrasi & deployment otomatis. | 5 (0.7%) |
| `RULE-TA-07` | `AO` | Automation Orchestrator | `via AO` | Sub-modul automation orchestrator. | 2 (0.3%) |
| `RULE-TA-08` | `Not Automate` | Standardized Automation | `through standardized automation` | Otomasi standar tanpa penamaan tool spesifik (tanpa kata 'via'). | 2 (0.3%) |

---

## 5. Execution Readiness Rules (Status Triggered)

Menentukan tingkat kematangan implementasi otomasi dan pola tata bahasa Benefit:

| Rule ID | Status Triggered | Definisi Status | Prefix Narasi Benefit | Reduksi Durasi Baseline | Frekuensi |
|---|---|---|---|---|---|
| `RULE-ST-01` | `Fully Automated` | Otomasi telah aktif penuh di sistem produksi menggantikan tugas manual L1. | `Eliminates {workload_str} of manual operational workload per month ({duration_clause}) {tool_clause} through {action_phrase}.` | 90% durasi tereliminasi (rata-rata) | 389 (58.3%) |
| `RULE-ST-02` | `Not Yet Triggered Automated` | Skrip/alat otomasi telah diidentifikasi/dibuat namun belum terpasang otomatis penuh pada trigger produksi. | `Potentially eliminates {workload_str} of manual operational workload per month ({duration_clause}) once automated {tool_clause} through {action_phrase}.` | Potensi penghematan di masa mendatang | 256 (38.4%) |
| `RULE-ST-03` | `Partial Automated` | Otomasi berjalan sebagian; sisa aktivitas masih memerlukan langkah intervensi verifikasi manual. | `Reduces monthly operational workload by {workload_str} ({duration_clause}) {tool_clause} through {action_phrase}.` | Reduksi terukur sebagian | 22 (3.3%) |

---

## 6. Benefit Text Generation Grammar Rules

### `RULE-BEN-01: Unit Scaling Rule (Minutes vs Hours)`
- **Jika $\text{Workload} < 60$ menit:**
  $$\text{workload\_str} = \begin{cases} \text{int(Workload) } + \text{ " minutes"} & \text{jika integer} \\ \text{str(Workload) } + \text{ " minutes"} & \text{jika pecahan} \end{cases}$$
  *Contoh:* `25 minutes`, `50 minutes`.
- **Jika $\text{Workload} \ge 60$ menit:**
  Konversi ke jam: $\text{Hours} = \text{Workload} / 60.0$.
  $$\text{workload\_str} = \begin{cases} \text{int(Hours) } + \text{ " hours"} & \text{jika } \text{Hours} \in \mathbb{Z} \\ \text{format(Hours, \".1f\") } + \text{ " hours"} & \text{jika pecahan} \end{cases}$$
  *Contoh:* $300 \text{ menit} \to \text{"5 hours"}$; $450 \text{ menit} \to \text{"7.5 hours"}$; $165 \text{ menit} \to \text{"2.8 hours"}$.

### `RULE-BEN-02: Frequency & Duration Clause Construction`
- Bagian durasi per kejadian:
  $$\text{dur\_str} = \text{"saving "} + \text{format\_number(Durasi)} + \text{" minutes per event"}$$
- Bagian frekuensi kejadian bulanan:
  $$\text{event\_clause} = \begin{cases} \text{"" (kosong)} & \text{jika } \text{Event Per Month} = 1 \\ \text{" across "} + \text{int(Event)} + \text{" monthly events"} & \text{jika } \text{Event Per Month} > 1 \end{cases}$$
- Klausul gabungan:
  $$\text{duration\_clause} = \text{"("} + \text{dur\_str} + \text{event\_clause} + \text{")"}$$

### `RULE-BEN-03: Zero Workload Special Narrative`
- **Kondisi:** $\text{Workload} = 0$ (misal aktivitas mitigasi tanpa kalkulasi menit).
- **Template Formula:**
  - Jika `Not Yet Triggered Automated`:
    `"Potentially eliminates manual intervention time and accelerates system recovery once automated " + tool_clause + " through " + action_phrase + "."`
  - Jika `Fully Automated`:
    `"Eliminates manual intervention time and accelerates system recovery " + tool_clause + " through " + action_phrase + "."`

### `RULE-BEN-04: Tool Syntax Exception for 'Not Automate'`
- **Kondisi:** `Tools Automation == 'Not Automate'`.
- **Sintaks:** Menggantikan frase `via Not Automate` menjadi `through standardized automation`.
- **Contoh:** `"... per event) through standardized automation through streamlined self-service execution..."`.

