# Product Requirements Document (PRD): SOP L1 AGIT Agent Harness (V1)

> **Document Status:** APPROVED BASELINE V1  
> **Target Release:** V1  
> **Authors:** Product Discovery & Grilling Team (Antigravity & Process Owner)  
> **Base Reference:** [SOP_L1_AGIT_Agent_Harness_Project_Context.md](file:///c:/Users/rahma/OneDrive/Documents/workload_enrichment/SOP_L1_AGIT_Agent_Harness_Project_Context.md), [SOP_L1_AGIT_Agent_Harness_Specification.md](file:///c:/Users/rahma/OneDrive/Documents/workload_enrichment/SOP_L1_AGIT_Agent_Harness_Specification.md)

---

## 1. Executive Summary & Problem Statement

### 1.1 Background
Operasional L1 AGIT memiliki sekitar 1.000 baris penilaian (*assessment*) beban kerja aktivitas SOP yang mencakup berbagai aplikasi, sistem operasi, dan alat manajemen infrastruktur. Penilaian ini rentan terhadap kesalahan input numerik, inkonsistensi durasi antar-aktivitas serupa, serta peluang otomasi yang belum terevaluasi secara seragam.

### 1.2 Objective
Membangun *Agent Harness V1* berbasis Python lokal yang:
1. Menjalankan validasi skema dan kalkulasi metrik penghematan beban kerja (*workload enrichment*) secara **deterministik 100%**.
2. Menyediakan **AI Assessment Reviewer** terpisah untuk mengevaluasi kualitas data, konsistensi penilaian, dan peluang otomasi tanpa mengubah hasil hitungan matematis.
3. Mendukung **Change Detection & Delta Review** saat analis mengunggah ulang CSV revisi.
4. Menjaga kepatuhan privasi data enterprise melalui **sanitasi lokal** dan mode **offline mocking** sebagai default.

---

## 2. Core Architectural Principles

```text
[Source Assessment CSV] (Read-Only)
          │
          ▼
┌────────────────────────────────────────┐
│ 1. Schema Gate & Ingestion             │
│    Fail-fast jika kolom wajib hilang   │
└────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────┐
│ 2. Deterministic Validation &          │
│    Enrichment Engine                   │
│    - Kalkulasi Workload & Reduction    │
│    - Evaluasi Calculation Status       │
│    - Evaluasi Evidence Status          │
└────────────────────────────────────────┘
          │
          ├────────────────────────────────────────────────┐
          ▼                                                ▼
┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
│ Enriched CSV (1:1 baris sumber)        │       │ 3. Change Detection Engine             │
│ + 6 Kolom Turunan                      │       │    Hash Baris vs Run Sebelumnya:       │
└────────────────────────────────────────┘       │    - UNCHANGED                         │
                                                 │    - MODIFIED / ADDED                  │
                                                 │    - DELETED                           │
                                                 └────────────────────────────────────────┘
                                                           │
                                                           ▼ (Hanya MODIFIED & ADDED)
                                                 ┌────────────────────────────────────────┐
                                                 │ 4. Deterministic Grouping              │
                                                 │    Application + Activity Type         │
                                                 │    (Batch: 15-30 baris)                │
                                                 └────────────────────────────────────────┘
                                                           │
                                                           ▼
                                                 ┌────────────────────────────────────────┐
                                                 │ 5. Local Data Sanitization             │
                                                 │    Masking IP, Host, Kredensial        │
                                                 └────────────────────────────────────────┘
                                                           │
                                                           ▼
                                                 ┌────────────────────────────────────────┐
                                                 │ 6. AI Assessment Reviewer              │
                                                 │    (Mocking Default / Gemini API)      │
                                                 │    - Data Quality                      │
                                                 │    - Assessment Consistency            │
                                                 │    - Automation Opportunity            │
                                                 └────────────────────────────────────────┘
                                                           │
                                                           ▼
                                                 ┌────────────────────────────────────────┐
                                                 │ 7. Feedback Aggregator                 │
                                                 │    - feedback_report.jsonl             │
                                                 │    - feedback_report.md                │
                                                 │    - change_log.json                   │
                                                 │    - run_summary.json                  │
                                                 └────────────────────────────────────────┘
```

1. **Strict Pipeline Separation:** Perhitungan numerik dan validasi format tidak boleh diserahkan ke AI. AI Reviewer bersifat *read-only qualitative advisory*.
2. **Read-Only Source Integrity:** Source CSV tidak pernah ditimpa, diubah namanya, atau dimodifikasi isinya.
3. **No Hidden State / Database-Free (Ponytail):** Tidak menggunakan database server atau SQLite. State antar-run dikelola mandiri via folder artefak berbasis waktu (`runs/YYYYMMDD_HHMMSS/`).
4. **Data Privacy First:** Sanitasi data sensitif dijalankan secara lokal sebelum payload keluar dari mesin. Mode `mock` adalah default operasional.

---

## 3. Data Ingestion & Identity Specification

### 3.1 Identitas Baris (Row Identity Specification)
* **Identifier Sistem Utama:** Kolom `activity_id` adalah identifier resmi yang digunakan sistem untuk melacak aktivitas antar-run.
* **Perilaku Change Detection:**
  * Change Detection **hanya membaca dan membandingkan** nilai pada kolom `activity_id`.
  * Sistem **dilarang membentuk, menghitung, atau merekonstruksi** ID dari kombinasi kolom lain (aturan penggabungan `APPS + ACTIVITY NAME` ditiadakan dari Change Detection).
* **Validasi Integritas ID & Penanganan Anomali:**
  * Jika nilai `activity_id` kosong (*null*, *blank*, atau spasi): baris diklasifikasikan sebagai `REVIEW_REQUIRED` (alasan: `EMPTY_ACTIVITY_ID`).
  * Jika nilai `activity_id` duplikat dalam run yang sama: seluruh baris yang bersangkutan diklasifikasikan sebagai `REVIEW_REQUIRED` (alasan: `DUPLICATE_ACTIVITY_ID`).
  * Sistem dilarang menebak atau mengasumsikan identitas baris yang mengalami anomali ID.
* **Pemisahan Penerbitan ID (ID Issuance):**
  * Mekanisme penerbitan awal atau migrasi ID dipisahkan secara tegas di luar tanggung jawab Change Detection. Change Detection bersifat *read-only consumer* terhadap `activity_id`.
* **Peran `source_row_index`:**
  * `source_row_index` (1-indexed) dipertahankan murni sebagai metadata pelacakan posisi baris lokal pada run aktif (misalnya untuk navigasi file atau pesan log), bukan sebagai kunci pembanding antar-versi.
* **Imutabilitas Sumber:** Source CSV tetap bersifat *read-only* 100% dan tidak pernah dimodifikasi.

### 3.2 Ingestion & Schema Gate (Fail-Fast)
Sebelum kalkulasi dimulai, harness memvalidasi keberadaan kolom esensial pada header CSV:
* Kolom beban kerja: `Workload`, `Workload after` (atau alias sesuai Data Dictionary).
* Kolom identitas & konteks: `ACTIVITY NAME`, `APPS` (atau `Application`), `TYPE ACTIVITY`.
* Kolom tautan & catatan: `Link Confluence`, `Link Wiki`, `Additional Notes`.

Jika kolom wajib tidak ditemukan, proses dihentikan seketika (*fail-fast*) dengan pesan kesalahan jelas tanpa membuat folder run parsial.

---

## 4. Deterministic Validation & Enrichment Engine

### 4.1 Logika Nilai Khusus
* Nilai kosong (*null*, *blank*, *NaN*) **bukan nol** dan dilarang dikonversi otomatis ke 0.
* Format numerik harus di-parse dengan aman. Jika parsing gagal, nilai dialihkan ke `None` dan ditandai error.

### 4.2 Formula Matematika
1. **`Workload Saved Est. (Min/Month)`**
   $$\text{Workload Saved} = \text{Workload} - \text{Workload after}$$
   * Syarat: Kedua input valid numerik. Jika salah satu `None`, output `None`.
2. **`Workload Reduction Est. (%)`**
   $$\text{Workload Reduction} = \left(\frac{\text{Workload} - \text{Workload after}}{\text{Workload}}\right) \times 100$$
   * Syarat: Dihitung **hanya jika** $\text{Workload} > 0$ dan kedua input valid. Jika $\text{Workload} \le 0$, output `None`.
3. **`Annualized Workload Saved Est. (Min/Year)`**
   $$\text{Annualized Saved} = \text{Workload Saved} \times 12$$
   * Syarat: Dihitung jika $\text{Workload Saved}$ bukan `None`.

### 4.3 Hirarki Evaluasi `Workload Calculation Status`
Jika beberapa kondisi anomali terjadi secara bersamaan pada satu baris, status ditetapkan secara deterministik mengikuti urutan prioritas tertinggi:

| Prioritas | Status Enum | Kondisi Logika Pemicu | Sifat |
|:---:|---|---|---|
| **1** | `INVALID_INPUT` | Input tidak dapat di-parse sebagai angka (misal teks korup `"N/A"`). | Gagal Hitung |
| **2** | `MISSING_INPUT` | Salah satu atau kedua kolom `Workload` / `Workload after` kosong (*null*). | Gagal Hitung |
| **3** | `NEGATIVE_INPUT` | $\text{Workload} < 0$ atau $\text{Workload after} < 0$. | Anomali / Review |
| **4** | `ZERO_WORKLOAD` | $\text{Workload} = 0$. $\text{Workload Saved}$ tetap dihitung; persentase reduksi `None`. | Review |
| **5** | `NEGATIVE_SAVINGS` | $\text{Workload after} > \text{Workload}$. Penghematan bulanan bernilai minus. | Review |
| **6** | `CALCULATED` | $\text{Workload} > 0$, $\text{Workload after} \ge 0$, $\text{Workload after} \le \text{Workload}$. | Sukses Normal |

### 4.4 Aturan `Workload Evidence Status`
Murni mencatat ketersediaan fisik tautan pendukung, bukan mengesahkan validitas nilai:
* `LINK_PROVIDED`: Jika `Link Confluence` terisi ATAU `Link Wiki` terisi (minimal salah satu).
* `NO_LINK_ATTACHED`: Jika kedua kolom tautan kosong.
* *Catatan:* Kolom `Confirmation Tower/L2` diperlakukan sebagai metadata persetujuan terpisah, bukan bukti tautan.

### 4.5 Kolom Tambahan Enriched CSV
Enriched CSV mempertahankan seluruh kolom sumber asli, ditambah 6 kolom turunan pada posisi akhir:
1. `Workload Saved Est. (Min/Month)` *(Float / Empty)*
2. `Workload Reduction Est. (%)` *(Float / Empty)*
3. `Workload Calculation Status` *(Enum String)*
4. `Workload Evidence Status` *(Enum String)*
5. `Workload Validation Notes` *(String penjelasan alasan status)*
6. `Annualized Workload Saved Est. (Min/Year)` *(Float / Empty)*

---

## 5. Change Detection & Reassessment Engine

### 5.1 Siklus Re-upload Antar-Run
Saat analis mengunggah file CSV baru dan menyertakan flag `--prev-run <path_folder>`:
1. **Deterministik Full:** Pipeline deterministik tetap memproses 100% baris CSV baru untuk memastikan data enriched selalu terhitung mutakhir.
2. **Pencocokan Baris & Content Hashing:**
   * Change Detection membaca nilai `activity_id` langsung dari setiap baris data sumber (tanpa rekonstruksi atau kalkulasi dari kolom lain).
   * Nilai `activity_id` divalidasi keunikan dan keberadaannya:
     - Jika `activity_id` kosong/hilang, baris langsung diklasifikasikan sebagai `REVIEW_REQUIRED`.
     - Jika `activity_id` ditemukan duplikat dalam run yang sama, seluruh baris bertabrakan diklasifikasikan sebagai `REVIEW_REQUIRED`.
   * Untuk baris dengan `activity_id` valid dan unik, sistem menghitung content hash deterministik (SHA-256) berdasarkan gabungan terurut kolom-kolom sumber data.
3. **Klasifikasi Delta Baris:**
   * `UNCHANGED`: Nilai `activity_id` cocok dengan baseline run sebelumnya, dan content hash baris 100% identik.
   * `MODIFIED`: Nilai `activity_id` cocok dengan baseline run sebelumnya, tetapi content hash berbeda (terjadi perubahan nilai pada satu atau lebih kolom).
   * `ADDED`: Nilai `activity_id` ada pada run aktif tetapi tidak ditemukan pada baseline run sebelumnya.
   * `DELETED`: Nilai `activity_id` ada pada baseline run sebelumnya tetapi tidak ditemukan lagi pada run aktif.
   * `REVIEW_REQUIRED`: Baris dengan `activity_id` kosong, duplikat, atau kondisi integritas ambigu lainnya.
4. **Pewarisan Feedback AI & Delegasi:**
   * Baris `UNCHANGED` langsung mewarisi temuan AI dari run sebelumnya tanpa memanggil model AI ulang.
   * Baris `MODIFIED` dan `ADDED` dikirim ke antrian AI Reviewer.
   * Baris `DELETED` tidak dikirim ke AI, dicatat ke dalam `change_log.json`.
   * Baris `REVIEW_REQUIRED` diisolasi ke dalam `change_log.json` untuk peninjauan manusia dan tidak dikirim ke AI Reviewer otomatis.
   * Jika konfigurasi prompt AI atau versi model berubah, seluruh feedback lama ditandai berpotensi kedaluwarsa (*stale*) dan dievaluasi ulang.

---

## 6. AI Assessment Reviewer

### 6.1 Tiga Fokus Penilaian
1. **Data Quality Review:**
   * Kejanggalan semantik dalam deskripsi aktivitas.
   * Kontradiksi logis (contoh: status `"Automate"`, tetapi `Workload after` bernilai sama dengan `Workload`).
2. **Assessment Consistency Review:**
   * Membandingkan aktivitas serupa dalam kelompok yang sama.
   * Menandai anomali perbedaan durasi drastis atau status otomasi yang berlawanan pada aplikasi yang sama.
   * *Prinsip:* AI menandai sebagai kandidat peninjauan (*review candidate*), bukan vonis kesalahan.
3. **Automation Opportunity Review:**
   * Mendeteksi catatan deskriptif yang mengindikasikan peluang otomasi (contoh: kata kunci *auto-restart*, *cron script*, *self-healing*) pada aktivitas berstatus manual atau berdurasi tinggi.

### 6.2 Grouping & Batching Deterministik
* **Kunci Pengelompokan:** Kolom `APPS` + `TYPE ACTIVITY` (atau kombinasi kolom resmi dari Data Dictionary).
* **Ukuran Batch:** 15–30 baris per batch prompt untuk menjaga ketajaman perbandingan konsistensi dan efisiensi token.
* **Kelompok Tunggal (1 baris):** Hanya diproses untuk *Data Quality* dan *Automation Opportunity*; lewati evaluasi konsistensi komparatif.
* **Kelompok Heterogen:** Jika aktivitas dalam kelompok terlalu beragam, AI diinstruksikan untuk menyatakan konteks perbandingan tidak memadai dan dilarang memaksakan temuan konsistensi.

### 6.3 Taksonomi Confidence Temuan
Tingkat keyakinan mencerminkan kekuatan bukti data sumber, bukan level urgensi atau risiko bisnis:
* `HIGH`: Terdapat kontradiksi atau ketidaksesuaian eksplisit yang didukung langsung oleh data sumber.
* `MEDIUM`: Terdapat indikasi yang membutuhkan konfirmasi analis.
* `LOW`: Saran atau peluang eksplorasi awal.

### 6.4 Struktur Temuan AI (Kontrak JSONL)
Setiap temuan wajib memiliki referensi bukti kolom sumber:
```json
{
  "finding_id": "FND-0001",
  "source_row_index": 42,
  "activity_ref": "Restart Service Redis - offdeckpdb1",
  "application": "AdServer",
  "focus_area": "AUTOMATION_OPPORTUNITY",
  "confidence_level": "HIGH",
  "evidence": {
    "Status": "Not Automate",
    "Additional Notes": "Auto Restart / Self Healing via AION"
  },
  "reasoning": "Catatan aktivitas menyebutkan potensi auto-restart via AION, namun status assessment masih Not Automate.",
  "recommendation": "Konfirmasi ke tim technical lead apakah otomasi via AION layak diimplementasikan pada server ini."
}
```

---

## 7. Keamanan, Privasi, & Tata Kelola Model

1. **Penyedia Model:** Google Gemini API melalui *environment variable* `GEMINI_API_KEY` (dilarang keras menyimpan kunci di source code atau file konfigurasi repositori).
2. **Status Pengiriman Eksternal:** *Subject to security approval*. Pengiriman data ke API eksternal hanya boleh diaktifkan setelah ada izin resmi kebijakan keamanan enterprise.
3. **Sanitasi Data Lokal Otomatis:**
   * Dilakukan sebelum payload dikirim ke AI Reviewer.
   * Deteksi dan masking pola IPv4/IPv6 (misal `10.12.3.4` $\to$ `[IP_MASKED]`).
   * Deteksi dan masking pola kredensial, token, sandi, dan secret pada kolom catatan.
   * Aturan masking yang dapat dikonfigurasi (*configurable rules*) untuk hostname internal, path basis data sensitif, URL internal, dan alamat email.
   * Nama server dan aplikasi teknis dipertahankan hanya jika diizinkan kebijakan dan dibutuhkan untuk analisis konsistensi.
4. **Mocking Engine (Default):**
   * Mode default eksekusi adalah `--mode mock`.
   * Menghasilkan evaluasi heuristik berbasis aturan sintetis lokal tanpa koneksi jaringan sama sekali, memastikan pipeline dapat diverifikasi penuh di lingkungan offline/terisolasi.

---

## 8. Output Contract & Struktur File

Setiap eksekusi sukses menghasilkan folder terisolasi: `runs/YYYYMMDD_HHMMSS/` yang berisi 5 artefak:

### 8.1 `enriched_assessment.csv`
* File CSV standar RFC 4180 (UTF-8).
* Jumlah baris persis 1:1 dengan Source CSV.
* Memuat seluruh kolom asli ditambah 6 kolom turunan deterministik.

### 8.2 `feedback_report.jsonl`
* Format JSON Lines.
* Satu baris per temuan AI, terstruktur sesuai kontrak data untuk keterbacaan sistem/analisis lanjutan.

### 8.3 `feedback_report.md`
Dokumen kerja terstruktur bagi analis manusia:
1. **Ringkasan Eksekutif:**
   * Total baris diproses.
   * Jumlah baris unik yang memiliki temuan (bukan sekadar hitungan total temuan).
   * Distribusi temuan per fokus area (`DATA_QUALITY`, `ASSESSMENT_CONSISTENCY`, `AUTOMATION_OPPORTUNITY`).
   * Total estimasi penghematan beban kerja yang berstatus perlu peninjauan (dihitung 100% dari kolom deterministik; AI dilarang mengagregasi sendiri).
2. **Pengelompokan Temuan:**
   * Hierarki: `Application` $\to$ Area Fokus.
   * Jika kolom aplikasi kosong: dikelompokkan ke `APPLICATION_NOT_SPECIFIED`.
3. **Format Temuan Individual:**
   * Nomor baris sumber (`source_row_index`), nama aktivitas, kutipan bukti kolom sumber, alasan AI, tingkat keyakinan (`HIGH`/`MEDIUM`/`LOW`), dan checklist tindakan verifikasi analis.

### 8.4 `change_log.json`
* Rekap audit perbandingan run terhadap versi sebelumnya:
  * Jumlah baris `UNCHANGED`, `MODIFIED`, `ADDED`, `DELETED`, dan `REVIEW_REQUIRED`.
  * Daftar baris yang mengalami modifikasi dan atribut yang berubah.
  * Daftar baris berstatus `REVIEW_REQUIRED` beserta alasan kegagalan identitas (misal: `EMPTY_ACTIVITY_ID`, `DUPLICATE_ACTIVITY_ID`).
  * Pemetaan `activity_id` ke klasifikasi delta dan keterlacakan `source_row_index`.

### 8.5 `run_summary.json`
* Metadata teknis eksekusi: timestamp mulai dan selesai, hash SHA-256 dari source CSV, path input, mode operasi (`mock`/`live`), versi prompt, dan status keberhasilan pipeline.

---

## 9. User Workflow & CLI Specification

### 9.1 Perintah Eksekusi
```bash
py run_harness.py --input <path_to_source_csv> [--prev-run <path_to_previous_run_dir>] [--mode mock|live]
```

### 9.2 Penjelasan Parameter
* `--input` *(wajib)*: Path ke file CSV penilaian sumber.
* `--prev-run` *(opsional)*: Path direktori folder run terdahulu untuk mengaktifkan Change Detection dan AI Delta Review. Jika tidak diberikan, run dianggap sebagai *initial baseline run*.
* `--mode` *(opsional, default: `mock`)*:
  * `mock`: Menjalankan pipeline tanpa koneksi LLM eksternal.
  * `live`: Memanggil Gemini API (hanya dapat dijalankan jika API key valid dan kebijakan keamanan terpenuhi).

### 9.3 Penanganan Kegagalan & Isolasi Error
* **Tingkat File:** Gagal di detik pertama jika file tidak ada atau format header korup (*fail-fast*).
* **Tingkat Baris:** Kegagalan kalkulasi numerik pada satu baris tidak boleh menghentikan proses baris lainnya (*row-level error isolation*). Baris error ditandai dengan status kalkulasi yang sesuai dan dicatat dalam log run.

---

## 10. Acceptance Criteria (V1)

SOP L1 AGIT Agent Harness V1 dinyatakan memenuhi syarat rilis jika:
1. **Integritas Sumber:** Source CSV tidak mengalami perubahan timestamp, isi, atau hash file setelah seluruh proses selesai.
2. **Integritas Baris Enriched CSV:** Jumlah baris Enriched CSV persis sama dengan file sumber (tanpa baris yang hilang atau berganda).
3. **Akurasi Deterministik:** Seluruh skenario pengujian kalkulasi (normal, nilai kosong, durasi nol, durasi negatif, penghematan minus, data non-numerik) lolos uji sesuai hirarki status.
4. **Pencatatan Bukti:** Kolom `Workload Evidence Status` tepat mencatat `LINK_PROVIDED` atau `NO_LINK_ATTACHED`.
5. **Change Detection:** Pada skenario re-upload, Change Detection murni membaca `activity_id` (tanpa rekonstruksi ID dari kolom lain), mengidentifikasi baris ID kosong/duplikat sebagai `REVIEW_REQUIRED`, baris `UNCHANGED` mewarisi feedback lama, baris `DELETED` dicatat di log, dan hanya baris `MODIFIED`/`ADDED` yang dievaluasi ulang oleh AI.
6. **Keterlacakan Temuan AI:** Setiap temuan pada `feedback_report.jsonl` dan `feedback_report.md` memiliki referensi `source_row_index` dan kutipan bukti kolom sumber yang valid.
7. **Privasi & Keamanan:** Pengujian di mode default `mock` berjalan 100% sukses tanpa koneksi internet; deteksi IP/kredensial lokal berhasil memaskir data uji sensitif.
8. **Struktur Artefak:** Setiap run sukses menghasilkan 5 artefak lengkap pada direktori `runs/YYYYMMDD_HHMMSS/`.

