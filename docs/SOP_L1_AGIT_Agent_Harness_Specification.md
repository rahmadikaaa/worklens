# Spesifikasi Teknis: SOP L1 AGIT Agent Harness (V1)

> **Status Dokumen:** DRAFT SPESIFIKASI — Menunggu Review dan Persetujuan Bisnis  
> **Referensi Induk:** [SOP_L1_AGIT_Agent_Harness_Project_Context.md](file:///c:/Users/rahma/OneDrive/Documents/workload_enrichment/SOP_L1_AGIT_Agent_Harness_Project_Context.md)  
> **Prinsip Utama:** Tidak mengubah source CSV, memisahkan komputasi deterministik dari analisis AI, dan tidak menetapkan ambang batas bisnis tanpa persetujuan.

---

## 1. Data Validation

Komponen Data Validation bertugas memverifikasi kelayakan data mentah sebelum diproses oleh Enrichment Engine dan AI Reviewer.

### 1.1 Status Aturan Validasi

| Kategori Aturan | Deskripsi & Ruang Lingkup | Status Keputusan |
|---|---|---|
| **Tipe Data Numerik** | `Workload` dan `Workload after` harus dapat di-parse sebagai angka desimal/integer (satuan menit). | **Terkonfirmasi** |
| **Penanganan Nilai Kosong** | Nilai kosong (*null*, *blank*, *NaN*) **bukan nol** dan tidak boleh dikonversi otomatis ke 0. | **Terkonfirmasi** |
| **Nilai Negatif** | Durasi kerja bernilai negatif tidak wajar dan harus ditandai untuk review. | **Terkonfirmasi** |
| **Pembagian Nol** | Jika `Workload = 0`, perhitungan persentase reduksi tidak boleh dijalankan (mencegah *zero division*). | **Terkonfirmasi** |
| **Pengidentifikasi Baris** | `activity_id` dibaca langsung dari kolom sumber. Tidak ada rekonstruksi ID dari kolom lain. ID kosong/duplikat menghasilkan `REVIEW_REQUIRED`. | **Terkonfirmasi** |
| **Kelengkapan Kolom Wajib** | Daftar kolom yang wajib ada (*mandatory*) vs kolom yang boleh kosong (*optional*). | **Terkonfirmasi (M1)** |
| **Daftar Nilai Status** | Rentang nilai yang sah (*allowed enum*) untuk kolom `Automation/Manual`. | **Memerlukan Persetujuan** |

### 1.2 Taksonomi Severity Validasi

Untuk mencegah penetapan threshold bisnis sepihak, severity dibagi berdasarkan kelayakan teknis:

* **ERROR (Kegagalan Input Teknis):**
  * Tipe data tidak valid / tidak dapat diubah menjadi numerik (misal: teks `"abc"` pada kolom `Workload`).
  * Nilai kosong (*null*) pada `Workload` atau `Workload after`.
  * *Perilaku:* Menahan kalkulasi turunan untuk baris tersebut. Baris tetap dimasukkan ke Enriched CSV dengan status kegagalan, dan tidak membatalkan pemrosesan baris lain.
* **WARNING (Peringatan Anomali / Butuh Konfirmasi Manusia):**
  * `Workload < 0` atau `Workload after < 0` (durasi negatif).
  * `Workload after > Workload` (estimasi waktu pasca-otomasi lebih tinggi dari awal).
  * `Workload == 0` (kalkulasi menit dapat diproses, persentase reduksi tidak terdefinisi).
  * *Perilaku:* Perhitungan aritmatika tetap dicatat atau dialihkan ke fallback yang aman, dan baris diberi penanda (*flag*) review.
* **INFO (Informasi Kontekstual):**
  * Baris dengan status manual tanpa estimasi otomasi (`Workload after` kosong atau sama dengan `Workload`).
  * Kolom catatan peluang otomasi kosong.
  * *Perilaku:* Dicatat dalam log pemrosesan tanpa memengaruhi status baris.

---

## 2. Enrichment Engine (Deterministik)

Komponen Enrichment Engine memproses data assessment secara deterministik murni menggunakan formula matematika dan aturan berbasis kode.

### 2.1 Perilaku Rumus & Nilai Khusus

1. **`Workload Saved Est. (Min/Month)`**
   * Formula: $\text{Workload} - \text{Workload after}$
   * Jika salah satu input kosong atau tidak valid: Output berupa `None` / kosong (bukan 0).
   * Jika $\text{Workload after} > \text{Workload}$: Nilai matematis negatif tetap dihitung (misal: $-30$), dan status baris ditandai khusus.
2. **`Workload Reduction Est. (%)`**
   * Formula: $\left(\frac{\text{Workload} - \text{Workload after}}{\text{Workload}}\right) \times 100$
   * Syarat kalkulasi: Hanya dihitung jika $\text{Workload} > 0$ dan kedua input valid numerik.
   * Jika $\text{Workload} = 0$: Output berupa `None` / kosong.
   * Jika $\text{Workload} < 0$: Output berupa `None` / kosong.
3. **`Annualized Workload Saved Est. (Min/Year)`**
   * Formula: $\text{monthly saved} \times 12$
   * Asumsi: Pola penghematan bulanan berlangsung tetap sepanjang tahun.
   * Jika penghematan bulanan bernilai `None`: Output berupa `None` / kosong.

### 2.2 Usulan Enum `Workload Calculation Status`

Status ini **murni teknis/matematis** dan independen dari status bukti:

| Enum Status [USULAN] | Kondisi Pemicu | Kategori |
|---|---|---|
| `CALCULATED` | $\text{Workload} > 0$, $\text{Workload after} \le \text{Workload}$, kedua input numerik valid positif. | Sukses |
| `NEGATIVE_SAVINGS` | $\text{Workload after} > \text{Workload}$. Penghematan bulanan bernilai negatif; butuh konfirmasi. | Review |
| `ZERO_WORKLOAD` | $\text{Workload} = 0$. Penghematan menit dihitung ($0$), persentase reduksi tidak dapat dihitung. | Review |
| `NEGATIVE_INPUT` | $\text{Workload} < 0$ atau $\text{Workload after} < 0$. Input tidak lazim. | Review |
| `MISSING_INPUT` | `Workload` atau `Workload after` bernilai kosong / null. | Gagal Hitung |
| `INVALID_INPUT` | Format data korup / non-numerik sehingga kalkulasi tidak dapat dijalankan. | Gagal Hitung |

### 2.3 Pemisahan dari Status Bukti (`Workload Evidence Status`)

* Status kalkulasi mencerminkan *validitas aritmatika data*.
* Status bukti mencerminkan *ketersediaan dokumen / justifikasi pendukung* dari angka assessment tersebut.
* **Status Aturan:** Belum ada kriteria bukti yang disepakati dalam dokumen context.
* **Usulan Penanganan V1:** Kolom `Workload Evidence Status` diisi nilai default `UNVERIFIED` atau `NOT_EVALUATED` hingga kriteria atau kolom bukti pada dataset dikonfirmasi oleh pemilik proses.

### 2.4 Aturan Kolom `Workload Validation Notes`

Kolom teks deterministik yang menjelaskan alasan mengapa status kalkulasi tertentu disematkan.
* Contoh untuk `NEGATIVE_SAVINGS`: `"Workload after (90) exceeds Workload (60)"`
* Contoh untuk `ZERO_WORKLOAD`: `"Initial workload is 0; percentage reduction undefined"`
* Contoh untuk `MISSING_INPUT`: `"Missing value on Workload after"`
* Contoh untuk `CALCULATED`: `""` (atau `"Valid"`)

---

## 3. Change Detection Engine (Milestone 2)

Komponen Change Detection bertugas membandingkan data run aktif dengan run acuan terdahulu (*baseline run*) secara efisien dan deterministik.

### 3.1 Data Flow Change Detection

```text
[Current Source CSV] (Read-Only)      [Previous Baseline Run Directory]
          │                                           │
          ├─────────────────────────┐                 ▼
          │                         │        [baseline run_summary.json /
          ▼                         ▼         baseline enriched_assessment.csv]
┌────────────────────────┐  ┌────────────────────────┐        │
│ 1. Read activity_id    │  │ 2. Compute Content Hash│        │
│    Directly            │  │    (SHA-256)           │        │
└────────────────────────┘  └────────────────────────┘        │
          │                             │                     │
          ▼                             ▼                     │
┌────────────────────────────────────────────────────┐        │
│ 3. Row Identity Gate & Validation                  │        │
│    - If activity_id missing/empty ->               │        │
│      CLASSIFIED: REVIEW_REQUIRED                   │        │
│    - If duplicate activity_id in run ->            │        │
│      CLASSIFIED: REVIEW_REQUIRED                   │        │
└────────────────────────────────────────────────────┘        │
          │                                                   │
          ▼ (Hanya baris dengan activity_id valid & unik)     │
┌─────────────────────────────────────────────────────────────┼────────┐
│ 4. Delta Comparator vs Baseline                             ▼        │
│    - Match ID + Match Hash   -> UNCHANGED (Inherit AI Findings)      │
│    - Match ID + Diff Hash    -> MODIFIED  (Route to AI Queue)        │
│    - New ID                  -> ADDED     (Route to AI Queue)        │
│    - ID in Baseline, missing -> DELETED   (Log only, no AI)          │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 5. Generate change_log.json & Delta Sets for Downstream Pipeline     │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 Aturan Identitas & Validasi `activity_id`

1. **Identifier Tunggal Resmi:** Kolom `activity_id` adalah satu-satunya kolom yang dibaca dan dibandingkan oleh Change Detection.
2. **Tanpa Rekonstruksi ID:** Sistem dilarang membentuk, mengonkatensasi, atau menghitung ID dari kolom lain (aturan `APPS + ACTIVITY NAME` ditiadakan dari Change Detection).
3. **Pemisahan Penerbitan ID Awal:** Mekanisme penomoran awal atau injeksi `activity_id` ke dalam dataset mentah berada di luar lingkup Change Detection. Change Detection murni sebagai *read-only consumer*.
4. **Penanganan ID Kosong:** Baris dengan `activity_id` bernilai `None`, kosong, atau spasi diklasifikasikan sebagai `REVIEW_REQUIRED` (alasan: `EMPTY_ACTIVITY_ID`).
5. **Penanganan ID Duplikat:** Jika dalam satu file run terdapat lebih dari satu baris dengan `activity_id` yang sama, seluruh baris tersebut diklasifikasikan sebagai `REVIEW_REQUIRED` (alasan: `DUPLICATE_ACTIVITY_ID`).
6. **Imutabilitas Sumber:** File CSV sumber tidak pernah diubah atau ditambahkan kolom secara in-place.

### 3.3 Data Model Change Detection

```typescript
// Status klasifikasi delta baris
enum ChangeClassification {
  UNCHANGED = "UNCHANGED",
  MODIFIED = "MODIFIED",
  ADDED = "ADDED",
  DELETED = "DELETED",
  REVIEW_REQUIRED = "REVIEW_REQUIRED"
}

// Alasan anomali identitas baris
enum ReviewRequiredReason {
  EMPTY_ACTIVITY_ID = "EMPTY_ACTIVITY_ID",
  DUPLICATE_ACTIVITY_ID = "DUPLICATE_ACTIVITY_ID",
  AMBIGUOUS_MATCH = "AMBIGUOUS_MATCH"
}

// Rekaman perubahan per baris
interface RowChangeRecord {
  activity_id: string;
  source_row_index: number;
  classification: ChangeClassification;
  reason?: ReviewRequiredReason;
  content_hash: string;
  modified_fields?: string[];
  previous_content_hash?: string;
}

// Kontrak dokumen change_log.json
interface ChangeLog {
  run_id: string;
  baseline_run_id: string;
  generated_at_utc: string;
  summary_counts: {
    total_current_rows: number;
    unchanged: number;
    modified: number;
    added: number;
    deleted: number;
    review_required: number;
  };
  changes: RowChangeRecord[];
}
```

---

## 4. AI Assessment Reviewer

AI Reviewer bekerja setelah pipeline deterministik selesai. AI bertugas melakukan evaluasi kualitatif dan komparatif tanpa mengubah data numerik atau menimpa source CSV.

### 4.1 Tiga Fokus Review

1. **Fokus 1: Data Quality Review**
   * Menemukan kejanggalan semantik pada deskripsi aktivitas, inkonsistensi penulisan nama tools, atau kombinasi nilai yang tidak lazim.
   * Menandai baris yang memerlukan konfirmasi manusia sebelum assessment disahkan.
2. **Fokus 2: Assessment Consistency Review**
   * Mengelompokkan aktivitas serupa (misal: aktivitas restart service sejenis lintas server/aplikasi).
   * Membandingkan perbedaan klasifikasi `Automation/Manual`, estimasi durasi `Workload`, atau pilihan `Tools Automation`.
   * *Prinsip:* Perbedaan bukan vonis kesalahan, melainkan kandidat peninjauan (*review candidate*).
3. **Fokus 3: Automation Opportunity Review**
   * Mendeteksi kontradiksi positif antara catatan peluang (*opportunity notes*) dengan status aktual (misal: catatan menyebut `"Self Healing via AION"` tetapi status masih `"Not Automate"`).
   * Membedakan peluang yang didukung bukti nyata dari sekadar ide/hipotesis awal.

### 4.2 Kontrak Struktur Temuan AI

Setiap temuan dalam AI Feedback Report wajib memenuhi atribut berikut:

```typescript
interface AIFinding {
  finding_id: string;             // Format: FND-XXXX (misal: FND-0001)
  row_index: number;              // Nomor baris pada file sumber (1-indexed)
  source_row_index: number;       // Nomor baris pada file sumber (1-indexed)
  activity_id?: string;           // Identifier unik aktivitas sumber (jika tersedia)
  activity_ref: string;           // Nama atau identifier aktivitas sumber
  application: string;            // Nama aplikasi terkait
  focus_area: "DATA_QUALITY" | "ASSESSMENT_CONSISTENCY" | "AUTOMATION_OPPORTUNITY";
  confidence_level: "HIGH" | "MEDIUM" | "LOW"; // Berdasarkan kejelasan aturan pembanding
  evidence: Record<string, any>;  // Kutipan nilai kolom aktual dari source/enriched data
  reasoning: string;              // Penjelasan logis mengapa baris ini ditandai
  recommendation: string;         // Rekomendasi tindakan spesifik bagi analis
  action_by?: "L0" | "L1" | "L2"; // Penanggung jawab follow-up (Q42–Q44)
}
```

### 4.3 Integrasi Business Rules Baseline (Q14, Q18, Q29–Q35, Q42–Q44)

AI Reviewer mengintegrasikan aturan konsistensi bisnis yang bersumber dari `Workload_Enrichment_Tanya_Jawab_Q1-Q51.md`:

1. **Audit Aturan Pemetaan Target (Q14 & Q18):**
   * *Target Mapping yang Sah:*
     * `Improvement Category: "Automation"` $\to$ `Category Notes: "Already Automation"`
     * `Improvement Category: "As Is"` $\to$ `Category Notes: "To Be Automated"`
     * `Improvement Category: "Dismantled"` $\to$ `Category Notes: "Dismantled"`
   * *Deteksi Inkonsistensi:* Jika kombinasi menyimpang (misal: `Improvement Category: "Automation"` tetapi `Category Notes: "To Be Automated"` atau sebaliknya), AI Reviewer menerbitkan finding `ASSESSMENT_CONSISTENCY` (Confidence: `HIGH`, `action_by: "L1"`).
   * *Aturan Mutlak Imutabilitas (Q18):* Dilarang mengoreksi otomatis (*auto-correct*) nilai sel sumber. Temuan hanya disajikan sebagai penanda review bagi L1. Koreksi final adalah wewenang L1 di Milestone 5 (`New Improvement Category Fixed`, Q19).

2. **Audit Status Solusi & Tools Automation (Q29–Q35):**
   * *Not Yet Solution (Q29–Q31):* Jika baris berstatus `To Be Automated` namun kolom `Tools Automation` kosong atau belum ditemukan tools-nya, tandai sebagai kandidat `Not Yet Solution`. Berikan rekomendasi konfirmasi kelayakan dengan L2 atau pencarian tools alternatif (`action_by: "L2"`).
   * *Already Automation (Q33–Q35):* Jika baris berstatus `Already Automation`, verifikasi bahwa tools sudah dibuat atau tersedia. Tools yang sudah dibuat tetap berstatus `Already Automation` meskipun belum pernah terpicu atau pernah mengalami kegagalan operasional (`action_by: "L1"`).

3. **Penetapan Penanggung Jawab Tindak Lanjut (`action_by` per Q42–Q44):**
   * `L0`: Aktivitas terkait penanganan operasional rutin atau monitoring pasca-otomasi.
   * `L1`: Pemilik utama assessment, koreksi data quality, dan alignment kategori improvement (default untuk sebagian besar temuan).
   * `L2`: Dukungan teknis mendalam, analisis kelayakan bot/skrip otomasi baru, investigasi tools untuk `Not Yet Solution`, atau automasi lintas sistem/API.

---

## 5. Output Contract & 5 Standard Artifacts Guarantee

Setiap eksekusi pipeline yang berhasil (baik standalone maupun menggunakan `--prev-run`) dijamin menghasilkan **5 Artefak Standar** secara atomik dan konsisten di dalam folder `runs/YYYYMMDD_HHMMSS/`:

1. **`enriched_assessment.csv` (Output A):**
   * Format: RFC 4180 compliant CSV (UTF-8).
   * Baris: 1-ke-1 persis sama dengan Source CSV (~1.000 baris, tanpa kehilangan atau duplikasi baris).
   * Kolom: Semua kolom asli + 6 kolom turunan deterministik:
     1. `Workload Saved Est. (Min/Month)` *(Float / Empty)*
     2. `Workload Reduction Est. (%)` *(Float / Empty)*
     3. `Workload Calculation Status` *(Enum String)*
     4. `Workload Evidence Status` *(Enum String)*
     5. `Workload Validation Notes` *(String)*
     6. `Annualized Workload Saved Est. (Min/Year)` *(Float / Empty)*

2. **`run_summary.json` (Output B):**
   * Metadata eksekusi lengkap: `run_id`, `generated_at_utc`, mode (`mock`/`live`), `source_csv_hash` (SHA-256).
   * Statistik pemrosesan: total baris, rincian status kalkulasi, rincian status bukti.
   * Ringkasan temuan AI: total findings, unique rows, rincian per `focus_area`, inherited vs new findings, dan model yang digunakan.

3. **`change_log.json` (Output C):**
   * Audit jejak komparasi delta terhadap baseline (`baseline_run_id`).
   * Jika dijalankan dengan `--prev-run`: mencatat klasifikasi `UNCHANGED`, `MODIFIED`, `ADDED`, `DELETED`, dan `REVIEW_REQUIRED` beserta modified fields.
   * Jika dijalankan tanpa `--prev-run` (initial run / standalone): seluruh baris dengan `activity_id` valid dicatat sebagai initial baseline (`ADDED` dengan `baseline_run_id: null`), dan baris anomali dicatat sebagai `REVIEW_REQUIRED`. Hal ini menjamin kontrak 5 file selalu terpenuhi secara seragam untuk konsumsi downstream M5.

4. **`feedback_report.jsonl` (Output D):**
   * Format mesin (JSON Lines, UTF-8). Setiap baris merepresentasikan 1 objek `AIFinding` lengkap dengan `activity_id`, `source_row_index`, `action_by`, `evidence`, `reasoning`, dan `recommendation`.

5. **`feedback_report.md` (Output E):**
   * Laporan manusia terstruktur: Executive Summary, distribusi temuan, dan katalog temuan yang dikelompokkan berdasarkan Aplikasi dan Fokus Area, dilengkapi rekomendasi penugasan tindak lanjut (`Action by`).

### 5.1 Mekanisme Pemrosesan Batch (~1.000 Baris)

Untuk menangani ~1.000 baris secara efisien, aman, dan terkendali:

```
[Source CSV] (Read-Only)
     │
     ▼
[Tahap 1: Ingestion & Validation] (Lokal / Fail-fast skema)
     │
     ▼
[Tahap 2: Enrichment Engine] (Lokal / Deterministik 100%)
     │
     ├────────────────────────────────────────┐
     ▼                                        ▼
[Tahap 3: Change Detection]         [Tahap 4: Grouping & Batching]
(Komparasi SHA-256 via activity_id) (15-30 baris per grup App+Type)
     │                                        │
     ▼                                        ▼
[change_log.json]                   [Tahap 5: AI Reviewer]
                                    - Inherit feedback UNCHANGED
                                    - Review ADDED & MODIFIED
                                    - Business Rules Q14, Q29-35, Q42-44
                                              │
                                              ▼
[Tahap 6: Atomic Output Generator] ───────────┘
├── enriched_assessment.csv
├── run_summary.json
├── change_log.json
├── feedback_report.jsonl
└── feedback_report.md
```

* **Penanganan Error / Isolasi Kegagalan:** Kegagalan kalkulasi atau review pada baris ke-$k$ tidak boleh menghentikan proses baris lainnya. Baris anomali diisolasi ke `REVIEW_REQUIRED`.
* **Efisiensi Token & Kecepatan:** Kalkulasi aritmatika 100% deterministik lokal. AI Reviewer hanya memproses delta baris `ADDED` dan `MODIFIED` dalam batch terstruktur.

---

## 6. Acceptance Criteria dan Test Cases (Sintetis)

> [!NOTE]
> Semua test case di bawah ini adalah data sintetis ilustratif untuk pengujian logika teknis, bukan kutipan dari dataset riil.

### 6.1 Test Cases Enrichment Engine (Milestone 1)

| ID Test | Skenario | Input Sintetis | Expected Output & Status |
|---|---|---|---|
| **TC-DET-01** | Kondisi Normal Positif | `Workload: 100`, `Workload after: 20` | `Saved: 80`, `Reduction: 80.0%`, `Annualized: 960`, `Status: CALCULATED` |
| **TC-DET-02** | Data Kosong (Missing After) | `Workload: 100`, `Workload after: ""` | `Saved: None`, `Reduction: None`, `Annualized: None`, `Status: MISSING_INPUT`, `Notes: "Missing value on Workload after"` |
| **TC-DET-03** | Workload Bernilai Nol | `Workload: 0`, `Workload after: 0` | `Saved: 0`, `Reduction: None`, `Annualized: 0`, `Status: ZERO_WORKLOAD`, `Notes: "Initial workload is 0; percentage reduction undefined"` |
| **TC-DET-04** | Input Bernilai Negatif | `Workload: -45`, `Workload after: 15` | `Saved: None`, `Reduction: None`, `Status: NEGATIVE_INPUT`, `Notes: "Workload cannot be negative"` |
| **TC-DET-05** | Penghematan Negatif | `Workload: 60`, `Workload after: 90` | `Saved: -30`, `Reduction: -50.0%`, `Annualized: -360`, `Status: NEGATIVE_SAVINGS`, `Notes: "Workload after (90) exceeds Workload (60)"` |
| **TC-DET-06** | Format Non-Numerik | `Workload: "N/A"`, `Workload after: 20` | `Saved: None`, `Reduction: None`, `Status: INVALID_INPUT`, `Notes: "Cannot parse Workload as numeric"` |

### 6.2 Test Cases Change Detection Engine (Milestone 2)

| ID Test | Skenario | Input Baseline vs Run Aktif | Expected Classification & Action |
|---|---|---|---|
| **TC-CD-01** | Baris Tidak Berubah (*Unchanged*) | Baseline: `activity_id="ACT-001"`, Workload: 100, Hash: `H1`<br>Aktif: `activity_id="ACT-001"`, Workload: 100, Hash: `H1` | **Status:** `UNCHANGED`<br>**Tindakan:** Mewarisi temuan AI baseline; tidak masuk antrian prompt AI. |
| **TC-CD-02** | Nilai Atribut Berubah (*Modified*) | Baseline: `activity_id="ACT-002"`, Workload: 100, Hash: `H2`<br>Aktif: `activity_id="ACT-002"`, Workload: 60, Hash: `H2_NEW` | **Status:** `MODIFIED`<br>**Tindakan:** Masuk antrian AI Reviewer; perubahan dicatat di `change_log.json`. |
| **TC-CD-03** | Aktivitas Baru Ditambahkan (*Added*) | Baseline: tidak ada `activity_id="ACT-003"`<br>Aktif: `activity_id="ACT-003"` hadir | **Status:** `ADDED`<br>**Tindakan:** Masuk antrian AI Reviewer; dicatat sebagai baris baru di `change_log.json`. |
| **TC-CD-04** | Aktivitas Dihapus (*Deleted*) | Baseline: `activity_id="ACT-004"` hadir<br>Aktif: `activity_id="ACT-004"` tidak ditemukan | **Status:** `DELETED`<br>**Tindakan:** Dicatat di `change_log.json`; tidak dikirim ke AI Reviewer. |
| **TC-CD-05** | Nilai `activity_id` Kosong | Aktif: baris ke-12 memiliki `activity_id=""` atau null | **Status:** `REVIEW_REQUIRED`<br>**Alasan:** `EMPTY_ACTIVITY_ID`<br>**Tindakan:** Diisolasi di `change_log.json`; tidak menebak ID; tidak dikirim ke AI. |
| **TC-CD-06** | Nilai `activity_id` Duplikat | Aktif: baris ke-4 dan ke-9 keduanya memiliki `activity_id="ACT-005"` | **Status:** `REVIEW_REQUIRED`<br>**Alasan:** `DUPLICATE_ACTIVITY_ID`<br>**Tindakan:** Seluruh baris duplikat diisolasi di `change_log.json`; tidak dikirim ke AI. |

### 6.3 Test Cases AI Assessment Reviewer (Milestone 3)

| ID Test | Skenario | Data Uji Sintetis | Expected AI Finding |
|---|---|---|---|
| **TC-AI-01** | Inkonsistensi Dua Aktivitas Serupa | **Baris A:** Act: *"Restart Service NGINX"*, App: *"Portal A"*, Status: `"Automate"`, Workload: 15.<br>**Baris B:** Act: *"Restart Service Apache"*, App: *"Portal A"*, Status: `"Not Automate"`, Workload: 120. | **Fokus:** `ASSESSMENT_CONSISTENCY`<br>**Temuan:** Status dan durasi berbeda mencolok pada aktivitas restart web service pada aplikasi yang sama; disarankan alignment review. |
| **TC-AI-02** | Peluang Automation Teridentifikasi | Act: *"Daily Log Clean"*, Status: `"Not Automate"`, Notes: `"Can be automated via cron script"`, Workload: 180. | **Fokus:** `AUTOMATION_OPPORTUNITY`<br>**Temuan:** Terdapat catatan eksplisit peluang skrip otomasi pada aktivitas rutin berdurasi tinggi berstatus manual. |
| **TC-AI-03** | Anomali Kualitas Data | Act: *"DB Backup"*, Status: `"Automate"`, `Workload after`: bernilai sama persis dengan `Workload` (300). | **Fokus:** `DATA_QUALITY`<br>**Temuan:** Aktivitas dinyatakan otomatis, namun estimasi beban kerja tidak mengalami penurunan sama sekali. |

### 6.4 Test Cases Pipeline Hardening & Business Rules (Milestone 4)

| ID Test | Skenario | Data Uji Sintetis | Expected AI Finding / Perilaku Pipeline |
|---|---|---|---|
| **TC-M4-01** | Inkonsistensi Mapping Q14 (Automation vs To Be) | `Improvement Category: "Automation"`, `Category Notes: "To Be Automated"` | **Fokus:** `ASSESSMENT_CONSISTENCY`<br>**Confidence:** `HIGH`<br>**Action by:** `L1`<br>**Temuan:** Deviasi dari aturan target mapping Q14; disarankan verifikasi apakah tool sudah dibuat (`Already Automation`) atau kategori sebenarnya adalah `As Is`. Source CSV tidak diubah. |
| **TC-M4-02** | Inkonsistensi Mapping Q14 (As Is vs Already) | `Improvement Category: "As Is"`, `Category Notes: "Already Automation"` | **Fokus:** `ASSESSMENT_CONSISTENCY`<br>**Confidence:** `HIGH`<br>**Action by:** `L1`<br>**Temuan:** Deviasi target mapping Q14. Jika tools sudah ada, kategori seharusnya `Automation`. Source CSV tidak diubah. |
| **TC-M4-03** | Inkonsistensi Mapping Q14 (Dismantled) | `Improvement Category: "Dismantled"`, `Category Notes: "Already Automation"` | **Fokus:** `ASSESSMENT_CONSISTENCY`<br>**Confidence:** `HIGH`<br>**Action by:** `L1`<br>**Temuan:** Deviasi target mapping Q14. Aktivitas berstatus `Dismantled` tidak boleh dipetakan ke `Already Automation`. |
| **TC-M4-04** | Validasi Q14 Target Mapping Sah | `Improvement Category: "Automation"`, `Category Notes: "Already Automation"`<br>`Improvement Category: "As Is"`, `Category Notes: "To Be Automated"`<br>`Improvement Category: "Dismantled"`, `Category Notes: "Dismantled"` | **Hasil:** Lolos validasi tanpa temuan deviasi mapping Q14. |
| **TC-M4-05** | Audit Q29–31 (Not Yet Solution) | `Improvement Category: "As Is"`, `Category Notes: "To Be Automated"`, `Tools Automation: ""` | **Fokus:** `AUTOMATION_OPPORTUNITY`<br>**Confidence:** `MEDIUM`<br>**Action by:** `L2`<br>**Temuan:** Rencana otomasi belum memiliki tools yang terdefinisi; ditandai sebagai kandidat `Not Yet Solution` untuk dikonfirmasi dengan L2 atau mencari tools alternatif. |
| **TC-M4-06** | Tagging Action by (L0 vs L1 vs L2) | - Temuan Data Quality / Mapping Q14 $\to$ `action_by: "L1"`<br>- Temuan Not Yet Solution / Solusi Teknis $\to$ `action_by: "L2"`<br>- Temuan Operasional Rutin $\to$ `action_by: "L0"` | **Hasil:** Setiap item temuan pada `feedback_report.jsonl` dan `feedback_report.md` memiliki atribut `action_by` yang valid dan terdefinisi. |
| **TC-M4-07** | E2E CLI Run Tanpa `--prev-run` (Initial Run) | Eksekusi CLI: `py run_harness.py --input sample.csv --mode mock` | **Hasil:** Seluruh 5 file artefak terbit lengkap di folder `runs/YYYYMMDD_HHMMSS/` (`enriched_assessment.csv`, `run_summary.json`, `change_log.json`, `feedback_report.jsonl`, `feedback_report.md`). |
| **TC-M4-08** | E2E CLI Run Dengan `--prev-run` (Chained Run) | Eksekusi CLI dengan `--prev-run runs/<baseline>/` | **Hasil:** Seluruh 5 artefak terbit lengkap. Change log mencatat delta perbandingan, temuan baris `UNCHANGED` diwariskan, dan baris `MODIFIED`/`ADDED` direview ulang. |
| **TC-M4-09** | Imutabilitas Source CSV & Baseline | Verifikasi hash SHA-256 file source CSV dan baseline sebelum dan sesudah eksekusi pipeline lengkap. | **Hasil:** Hash SHA-256 bernilai 100% identik. Tidak ada operasi mutasi in-place pada input. |

### 6.5 Kriteria Penerimaan Milestone 4 (Acceptance Criteria M4)

Pipeline V1 / Milestone 4 dinyatakan memenuhi **Definition of Done (DoD)** jika:

- [x] **AC-M4-01 (Rule Mapping Q14):** AI Reviewer mendeteksi deviasi target pemetaan kategori (`Automation` $\to$ `Already Automation`, `As Is` $\to$ `To Be Automated`, `Dismantled` $\to$ `Dismantled`) sebagai finding `ASSESSMENT_CONSISTENCY` (Confidence: `HIGH`, `action_by: "L1"`). Source CSV tidak dimutasi.
- [x] **AC-M4-02 (Not Yet Solution Q29–31):** Aktivitas `To Be Automated` tanpa tools terisi ditandai sebagai finding `AUTOMATION_OPPORTUNITY` berkategori `Not Yet Solution` (`action_by: "L2"`).
- [x] **AC-M4-03 (Action by Tagging Q42–44):** Setiap finding pada `AIFinding` (`feedback_report.jsonl` dan `feedback_report.md`) memuat atribut `action_by` (`L0`, `L1`, atau `L2`).
- [x] **AC-M4-04 (5 Artefak Standar Konsisten):** Eksekusi CLI `--input` (dengan atau tanpa `--prev-run`) secara atomik menghasilkan 5 file artefak standar yang valid dan lengkap.
- [x] **AC-M4-05 (Zero Regression & Coverage $\ge 90\%$):** 100% test suite pytest lulus dengan line coverage keseluruhan $\ge 90\%$ (hasil aktual: 112/112 lulus, coverage 97%).
- [x] **AC-M4-06 (Imutabilitas Total):** File CSV input dan direktori run baseline terbukti 100% tidak berubah (SHA-256 identik).

---

## 7. Milestone 5 — Operational Delivery & Assessment Workspace (6 Modul MVP)

Komponen Milestone 5 mentransformasikan hasil Core Engine V1 menjadi antarmuka visual operasional interaktif bagi Tim L1 AGIT dan Manajemen, mengimplementasikan 6 Modul MVP (Q50) dan pembagian otorisasi pengguna (Q51), serta menyelaraskan alur kerja dengan arsitektur operasional perusahaan:
- **SharePoint Excel (`SOP L1 AGIT.xlsx`, sheet `Breakdown Activity`)**: *Operational Source of Truth*.
- **Power Automate**: Trigger, ekstraksi data, dan sinkronisasi kembali (*orchestration*).
- **Workload Enrichment Engine**: Pemrosesan deterministik, validasi, deteksi perubahan, dan AI assessment review.
- **Dashboard**: Assessment Workspace (L1) dan Monitoring (Management).

### 7.1 Prinsip Arsitektur Operasional & Zero-Bloat Workspace

Sesuai prinsip *Ponytail* (YAGNI) dan batasan lingkup tanpa database server:
1. **Operational Source of Truth (SharePoint Excel):** Data operasional hidup di workbook `SOP L1 AGIT.xlsx` pada sheet `Breakdown Activity` (35 kolom `A:AI`, formula lookup ke `List App,BA,Topology` dan `All SOP`).
2. **Dual-Mode Data Ingestion Contract:**
   - **Mode Operasional (Primary):** Engine menerima payload ekstraksi dari Power Automate (file JSON terstruktur atau snapshot Excel) yang memetakan kolom-kolom `Breakdown Activity`.
   - **Mode Fallback & Test (Secondary):** Engine tetap mempertahankan pembaca CSV RFC 4180 (`harness/csv_reader.py`) sebagai test harness otomatis dan fallback luring.
3. **Self-Contained Single-Page Application (SPA):** Diterbitkan secara otomatis sebagai `dashboard.html` di dalam folder `runs/YYYYMMDD_HHMMSS/` pada setiap eksekusi pipeline yang sukses.
4. **Offline-First & Zero External Dependency:** Berjalan 100% secara lokal pada peramban modern tanpa membutuhkan koneksi internet, CDN eksternal, atau framework JavaScript pihak ketiga yang berat.
5. **Data Kontrak Terpadu:** Mengonsumsi langsung data dari ke-5 artefak standar (`enriched_assessment.csv`, `run_summary.json`, `change_log.json`, `feedback_report.jsonl`, `feedback_report.md`).
6. **Opsional Local Server:** Mendukung flag `--serve` pada CLI (`run_harness.py --serve [run_dir]`) menggunakan modul bawaan `http.server` untuk kebutuhan presentasi bersama atau integrasi lokal.

### 7.2 Implementasi 6 Modul MVP (Q50) & Alur Operasional

Antarmuka workspace mengorganisasikan 6 modul utama yang dapat diakses secara tabbed:

1. **Modul 1: Assessment Workspace (L1)**
   * Menampilkan data tabel lengkap seluruh baris aktivitas (~1.000 baris) dengan kemampuan pencarian teks, filter berdasarkan `Aplikasi`, `Tipe Aktivitas`, `Calculation Status`, dan `Action by`.
   * Menampilkan badge status kalkulasi dan metrik penghematan deterministik secara jelas.
   * Pada mode L1, menyediakan kontrol pengeditan cepat untuk `Improvement Category`, `Category Notes`, dan `Action by`.
   * Melacak modifikasi pengguna (*dirty tracking*) secara lokal agar siap diekspor sebagai payload sinkronisasi.

2. **Modul 2: Monitoring Dashboard (Management)**
   * Menampilkan Kartu Metrik Utama (KPI): Total Aktivitas, Total Workload Saved (Menit/Bulan), Estimasi Rata-rata Reduksi (%), dan Annualized Workload Saved (Menit/Tahun).
   * Visualisasi distribusi status kalkulasi dan status perbaikan (`Automation`, `As Is`, `Dismantled`).
   * Fitur *drill-down*: Mengklik salah satu metrik langsung memfilter tabel aktivitas terkait tanpa meninggalkan dashboard.

3. **Modul 3: Export & SharePoint Sync (Egress Operasional)**
   * **SharePoint Sync Payload (JSON):** Mengekspor baris-baris yang telah dimodifikasi oleh L1 dalam format delta terstruktur (`activity_id`, `Improvement Category`, `Category Notes`, `Action by`, `New Improvement Category Fixed`) yang siap dikonsumsi alur Power Automate untuk memperbarui SharePoint Excel tanpa merusak formula lookup `A:AI`.
   * **Download Enriched CSV:** Tombol unduh langsung (*one-click download*) untuk mengunduh dataset enriched RFC 4180 terbaru langsung dari peramban untuk kebutuhan backup/analisis lokal.

4. **Modul 4: Generate Assessment Report**
   * Tampilan laporan komprehensif siap cetak/simpan (Print / PDF Ready) yang menyajikan Ringkasan Eksekutif, statistik efisiensi per aplikasi, dan katalog temuan terpenting.

5. **Modul 5: Quality Review**
   * Panel khusus untuk meninjau dan menyelesaikan anomali kualitas data (`DATA_QUALITY`), inkonsistensi target mapping Q14 (`ASSESSMENT_CONSISTENCY`), dan baris berstatus `REVIEW_REQUIRED`.
   * Menyediakan rekomendasi resolusi terarah dan opsi penetapan `New Improvement Category Fixed` bagi L1 yang otomatis terintegrasi ke payload sinkronisasi.

6. **Modul 6: Follow-up Management**
   * Panel koordinasi tindak lanjut yang mengelompokkan aktivitas berdasarkan `Action by` (`L0`, `L1`, `L2`).
   * Memfasilitasi pelacakan konfirmasi dukungan teknis L2 untuk aktivitas `Not Yet Solution` dan pelacakan implementasi bot/skrip otomasi.

### 7.3 Model Otorisasi Pengguna (Q51)

Antarmuka menyediakan *Role Switcher* eksplisit:
* **Peran L1 (Workspace & Edit):**
  * Hak edit penuh pada assessment, `Improvement Category`, `Category Notes`, `Quality Review`, dan penugasan `Follow-up`.
  * Tombol aksi simpan dan ekspor sinkronisasi SharePoint aktif.
* **Peran Management (Read-Only):**
  * Hak akses murni peninjauan (Summary + drill-down ke rincian aktivitas).
  * Seluruh kontrol pengeditan, dropdown pilihan, dan input teks otomatis dinonaktifkan (*disabled/hidden*) untuk mencegah perubahan data yang tidak disengaja.

### 7.4 Kriteria Penerimaan Milestone 5 (Acceptance Criteria M5)

- [x] **AC-M5-01 (6 Modul MVP Terpadu):** Antarmuka `dashboard.html` memuat dan menyediakan navigasi fungsional ke seluruh 6 modul MVP: Assessment Workspace, Monitoring Dashboard, Export & SharePoint Sync, Generate Report, Quality Review, dan Follow-up Management.
- [x] **AC-M5-02 (Pembagian Otorisasi L1 vs Management):** Mode L1 mengizinkan pengeditan field `Improvement Category`, `Category Notes`, `Action by`, dan resolusi Quality Review; Mode Management mengunci antarmuka menjadi murni *read-only* tanpa kemampuan mutasi (Q51).
- [x] **AC-M5-03 (Quality Review & Isolation):** Modul Quality Review menampilkan seluruh temuan anomali data, inkonsistensi target mapping Q14, dan baris `REVIEW_REQUIRED` secara terpisah dengan saran resolusi terstruktur.
- [x] **AC-M5-04 (Follow-up Koordinasi L0/L1/L2):** Modul Follow-up Management menyajikan pengelompokan aktivitas berdasarkan penanggung jawab (`Action by`) dengan status tindak lanjut.
- [x] **AC-M5-05 (Export & SharePoint Sync Payload):** Menyediakan ekspor delta payload terstruktur untuk Power Automate sync ke SharePoint Excel, serta pengunduhan CSV RFC 4180 valid dengan imutabilitas file sumber 100% terjaga.
- [x] **AC-M5-06 (Operational Data Ingestion Contract):** Pipeline mendukung ingestion data operasional (JSON payload Power Automate / Excel export) dengan tetap mempertahankan ingestion CSV sebagai fallback dan test harness.

---

## 8. Open Questions & Catatan Unresolved Items (Q1–Q51)

Sesuai prinsip SDD dan catatan resmi `Workload_Enrichment_Tanya_Jawab_Q1-Q51.md` Bagian G & I, hal-hal berikut **dicatat secara eksplisit sebagai unresolved/deferred** tanpa menghambat pekerjaan yang tidak bergantung padanya:

1. **Format Representasi Gabungan dalam Satu Kolom (Q31, Q.G.4):**
   * *Status:* Belum diputuskan oleh bisnis.
   * *Penanganan M4:* Di M4, sistem tidak menggabungkan string ke dalam source CSV. Keberadaan kondisi `Not Yet Solution` dilaporkan secara terstruktur via `feedback_report.jsonl` dan `feedback_report.md` tanpa memaksakan konvensi penulisan sel Excel.
2. **Detail Komponen dan Layout Dashboard (Q.G.5):**
   * *Status:* Ditunda ke Milestone 5 (Horizon 2).
   * *Penanganan M4:* M4 berfokus 100% pada *Core Engine* (headless CLI dan kelima artefak data kontrak). Rincian visualisasi UI dipersiapkan pada tahap spesifikasi M5.
3. **Hak Komentar / Feedback Management (Q51, Q.I):**
   * *Status:* Belum ditetapkan.
   * *Penanganan M4 & M5:* Diputuskan bahwa Management memiliki hak *Read-Only* (Summary + drill-down ke detail baris). Tidak ada asumsi hak edit atau komentar tambahan yang ditambahkan.
4. **Alur Status Operasional dari Awal hingga `Done` (Q.G.1):**
   * *Status:* Diskip sementara oleh bisnis.
   * *Penanganan M4:* Menggunakan kriteria bisnis Q9: sebuah aktivitas dianggap selesai dinilai oleh L1 jika L1 memiliki dasar yang cukup dan telah menetapkan keputusan kategori improvement.
5. **Formula Workload Saving Excel (Q41, Q.G.7):**
   * *Status:* Terkunci sesuai artefak formal proyek.
   * *Penanganan M4:* Menggunakan formula deterministik yang telah disahkan pada PRD Section 4.2 dan diimplementasikan pada Milestone 1 (Workload saved = Workload - Workload after; reduction % = (saved / workload) * 100).
6. **Provider / Kredensial AI Live:**
   * *Status:* Offline mock mode adalah default resmi. Egress API live membutuhkan `GEMINI_API_KEY` dan security approval enterprise.


