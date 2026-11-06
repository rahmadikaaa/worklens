# SOP L1 AGIT Agent Harness — Project Context

> **Purpose:** Dokumen konteks untuk membangun AI Assessment Reviewer V1 di Antigravity.
>
> **Status:** Draft hasil konsolidasi percakapan. Konfirmasi terhadap file project dan aturan bisnis tetap wajib sebelum implementasi.

## 1. Tujuan Project

Membangun Agent Harness untuk mereview assessment aktivitas dan automation SOP L1 AGIT, termasuk pemrosesan data berjumlah besar (sekitar 1.000 baris assessment).

Reviewer harus membantu:
1. Memeriksa kualitas data.
2. Menemukan potensi inkonsistensi antar-assessment aktivitas serupa.
3. Mengidentifikasi peluang automation atau perbaikan assessment.
4. Menghasilkan temuan yang dapat ditelusuri, disertai bukti, alasan, dan rekomendasi tindak lanjut.

## 2. Arsitektur yang Disepakati

```text
CSV Assessment (Read-Only)
      │
      ▼
Data Validation & Schema Gate
      │
      ▼
+-----------------------------------+
| 3A. Enrichment Engine (M1)        |
| Deterministik                     |
| Menghitung 6 metrik turunan       |
+-----------------------------------+
      │
      ├─────────────────────────────────────────┐
      ▼                                         ▼
+-----------------------------------+     +-----------------------------------+
| Output Enriched CSV               |     | 3B. Change Detection Engine (M2)  |
| 1:1 baris sumber                  |     | - Baca activity_id langsung       |
+-----------------------------------+     | - Content Hash (SHA-256)          |
                                          | - Delta: UNCHANGED, MODIFIED,     |
                                          |   ADDED, DELETED, REVIEW_REQUIRED |
                                          +-----------------------------------+
                                                        │
                                                        ▼ (Hanya MODIFIED & ADDED)
                                          +-----------------------------------+
                                          | 3C. AI Assessment Reviewer (M3)   |
                                          | AI-assisted (Mock/Gemini)         |
                                          | - Data Quality                    |
                                          | - Assessment Consistency          |
                                          | - Automation Opportunity          |
                                          +-----------------------------------+
                                                        │
                                                        ▼
                                          +-----------------------------------+
                                          | Output Tambahan                   |
                                          | 1. change_log.json                |
                                          | 2. feedback_report.jsonl          |
                                          | 3. feedback_report.md             |
                                          | 4. run_summary.json               |
                                          +-----------------------------------+
```

### Perbedaan Enrichment dan AI Feedback

| Enrichment Engine | AI Feedback |
|---|---|
| Menghasilkan kolom atau metrik baru | Menjelaskan temuan dan saran |
| Menggunakan rumus dan aturan teruji | Menggunakan analisis AI berdasarkan data dan aturan yang tersedia |v
| Contoh: estimasi penghematan 90 menit/bulan | Contoh: estimasi perlu ditinjau karena dasar nilai `Workload after` belum jelas |

**Prinsip:** AI tidak menggantikan enrichment deterministik. AI boleh menandai metrik untuk ditinjau, tetapi tidak boleh diam-diam mengubah hasil hitungan atau data sumber.

## 3. Input dan Output

### Input
- CSV assessment.
- Data Dictionary / definisi kolom yang tersedia.
- Kode dan output Enrichment Engine V1 yang sudah ada, jika tersedia di workspace.

### Output A — Enriched CSV

Output mempertahankan data sumber dan menambahkan metrik/kolom turunan yang relevan, antara lain:

- `Workload Saved Est. (Min/Month)`
- `Workload Reduction Est. (%)`
- `Workload Calculation Status`
- `Workload Evidence Status`
- `Workload Validation Notes`
- `Annualized Workload Saved Est. (Min/Year)`

Jangan menganggap daftar kolom ini harus selalu ditambahkan ulang. Periksa implementasi yang sudah ada untuk menghindari duplikasi.

### Output B — AI Feedback Report

Feedback disimpan terpisah dari CSV sumber/enriched CSV. Setiap temuan sebaiknya memiliki:
- Identitas baris/aktivitas yang dapat ditelusuri.
- Kategori temuan.
- Bukti dari kolom/data sumber.
- Penjelasan alasan.
- Rekomendasi tindak lanjut.
- Tingkat kepastian atau status review, bila dapat ditentukan dengan aturan yang jelas.

Pisahkan fakta terverifikasi, dugaan/indikasi, dan rekomendasi AI.

## 4. Tiga Fokus AI Assessment Reviewer

### 4.1 Data Quality
Periksa antara lain:
- Nilai kosong pada field yang diperlukan.
- Format atau tipe data tidak valid.
- Nilai numerik yang tidak masuk akal atau melanggar aturan yang sudah disepakati.
- Inkonsistensi perhitungan workload.
- Nilai yang memerlukan konfirmasi manusia.

Nilai kosong tidak otomatis dianggap nol. Jangan mengarang aturan validasi untuk kolom yang definisinya belum dikonfirmasi.

### 4.2 Assessment Consistency
- Kelompokkan atau bandingkan aktivitas yang berpotensi serupa.
- Cari perbedaan klasifikasi, status, durasi, atau keputusan assessment yang patut ditinjau.
- Gunakan kolom seperti nama aktivitas, aplikasi, tipe aktivitas, tools, dan status hanya setelah memeriksa definisi dan kualitas datanya.
- Jelaskan mengapa dua aktivitas dianggap sebanding dan tunjukkan bukti pembanding.
- Perbedaan bukan otomatis kesalahan; hasilnya adalah kandidat review jika aturan bisnis belum menetapkan bahwa keduanya harus sama.

### 4.3 Automation Opportunity
- Identifikasi aktivitas yang mungkin bisa diotomasi atau diperbaiki.
- Gunakan data aktivitas, workload, tools, status, dan catatan yang benar-benar tersedia.
- Bedakan peluang yang didukung bukti dari hipotesis yang perlu dikonfirmasi.
- Jangan menyimpulkan bahwa aktivitas pasti bisa diotomasi hanya karena workload tinggi atau ada kata tertentu dalam deskripsi.
- Jangan menetapkan prioritas atau ambang skor tanpa persetujuan.

## 5. Enrichment Engine: Aturan yang Sudah Diketahui

Definisi yang sudah dikonfirmasi:
- `Workload`: total workload bulanan, satuan menit.
- `Workload after`: estimasi workload setelah automation, satuan menit; bukan pengukuran aktual.
- `Automation/Manual`: menunjukkan apakah aktivitas otomatis atau masih manual, sesuai nilai pada dataset; aturan klasifikasi rinci perlu mengikuti definisi project.
- `Tools Automation`: kategori/metode seperti GUI, Web, OS, DB; lebih dari satu kategori bisa berlaku.
- `Application / Tool Name`: nama aplikasi/tools; lebih dari satu nilai dapat tercantum.

Rumus:
- `Workload Saved Est. (Min/Month) = Workload - Workload after`
- `Workload Reduction Est. (%) = ((Workload - Workload after) / Workload) * 100`, hanya jika `Workload > 0` dan nilai yang diperlukan valid.
- `Annualized Workload Saved Est. (Min/Year) = monthly saved * 12`, dengan asumsi pola bulanan tetap.

Penanganan:
- Nilai kosong bukan nol.
- Nilai negatif perlu ditandai untuk ditinjau.
- Jika `Workload after > Workload`, hasil penghematan negatif perlu ditinjau; jangan langsung menyimpulkan automation gagal.
- Jika `Workload = 0`, persentase reduction tidak dapat dihitung.
- Hasil merupakan estimasi, bukan actual savings.
- Jangan menambahkan impact band tanpa threshold yang disetujui.

## 6. Contoh Kasus dari Percakapan

Contoh aktivitas: **Restart Redis Service - offdeckpdb1**.

Informasi yang terlihat pada contoh:
- Aplikasi: AdServer.
- Tipe aktivitas: Incident Handling.
- Catatan peluang: `Auto Restart / Self Healing via AION (need further assessment)`.
- Status automation pada baris contoh: `Not Automate`.
- Kategori notes terlihat sebagai `OS`.

Interpretasi awal yang aman:
- Aktivitas ini dapat ditandai sebagai **kandidat untuk ditinjau** karena catatan menyebut peluang auto-restart/self-healing sementara status menunjukkan `Not Automate`.
- Ini bukan bukti bahwa assessment salah atau bahwa automation pasti layak dilakukan.
- Reviewer perlu menampilkan bukti dan meminta validasi manusia.

## 7. Batch Processing / Looping

Dataset sekitar 1.000 baris dapat diproses melalui loop/batch:
1. Baca dan validasi seluruh baris.
2. Jalankan enrichment deterministik.
3. Jalankan review AI per baris atau per batch sesuai kebutuhan.
4. Untuk consistency review, bandingkan aktivitas serupa lintas baris, bukan hanya menilai tiap baris secara terpisah.
5. Gabungkan feedback menjadi laporan terpisah.
6. Catat kegagalan per baris/batch agar satu kegagalan tidak menghentikan seluruh proses, jika desain runner mendukungnya.

Jangan mengirim semua baris ke AI sekaligus tanpa mempertimbangkan batas token, biaya, privasi, dan kualitas hasil. Gunakan AI hanya untuk tugas interpretatif; validasi dan rumus deterministik tetap di kode.

Contoh alur ilustratif, bukan implementasi siap pakai:

```python
for activity in assessment_data:
    validation = validate_activity(activity)
    enrichment = calculate_enrichment(activity)
    feedback = review_assessment(activity, enrichment)
    save_feedback(activity, validation, enrichment, feedback)
```

Untuk perbandingan aktivitas serupa, dibutuhkan tahap lintas-baris/kelompok tambahan; jangan menganggap contoh loop sederhana di atas sudah menyelesaikan consistency review.

## 8. Prinsip Implementasi

- Lakukan discovery sebelum mengubah file.
- Baca source CSV, Data Dictionary, kode, test, dan output yang sudah tersedia.
- Pertahankan source CSV; jangan menimpa file asli.
- Jangan mengganti Enrichment Engine V1 tanpa alasan teknis dan persetujuan.
- Pisahkan validasi deterministik, enrichment, dan feedback AI.
- Jangan mengarang definisi kolom, aturan bisnis, threshold, atau hasil review.
- Gunakan pemrosesan batch bila diperlukan.
- Buat test untuk perhitungan, validasi, batch processing, dan format output.
- Catat asumsi, error, dan keterbatasan.
- Hindari overengineering; tidak perlu menambah UI, database, multi-agent, atau integrasi API sebelum kebutuhan V1 terbukti.
- Jika model AI/API belum tersedia, jelaskan keterbatasan dan jangan mengklaim AI review telah dijalankan. Implementasi rule-based boleh disiapkan secara eksplisit sebagai fallback, tetapi jangan menyebutnya AI review sesungguhnya.

## 9. Rencana Kerja di Antigravity

### Checkpoint 1 — Discovery
Agent memeriksa:
- File dan struktur project.
- Source CSV dan Data Dictionary.
- Enrichment Engine V1 dan cara menjalankannya.
- Existing tests dan output.
- Definisi yang sudah diketahui vs belum dikonfirmasi.
- Gap yang menghalangi implementasi AI Reviewer.

**Output:** ringkasan temuan dan daftar pertanyaan terbatas. Jangan mengubah kode atau data pada tahap ini.

### Checkpoint 2 — Specification
Buat atau perbarui:
- Glossary.
- Business rules dan daftar asumsi.
- Architecture/workflow.
- Format feedback report.
- Acceptance criteria.
- Rencana test.

Review dokumen sebelum implementasi.

### Checkpoint 3 — Implementation Plan
Tentukan file yang akan dibuat/diubah, dependensi, alur batch, penanganan error, model AI yang digunakan (jika ada), serta batasan privasi dan biaya.

Jangan menambahkan framework/API baru tanpa alasan.

### Checkpoint 4 — Deterministic Pipeline
Pastikan data validation dan enrichment bekerja, teruji, dan tidak mengubah source file.

### Checkpoint 5 — AI Assessment Reviewer
Implementasikan tiga fokus:
1. Data Quality.
2. Assessment Consistency.
3. Automation Opportunity.

Semua feedback harus dapat ditelusuri ke bukti dan tidak boleh mengubah data secara otomatis.

### Checkpoint 6 — End-to-End Verification
Jalankan test dan simulasi pada dataset yang sesuai. Verifikasi:
- Jumlah baris input dan output.
- Tidak ada duplikasi atau kehilangan baris tanpa penjelasan.
- Rumus enrichment benar.
- Feedback terhubung ke aktivitas yang tepat.
- Kegagalan batch dicatat.
- Source CSV tetap tidak berubah.
- Batasan AI dan status pengujian dilaporkan secara jujur.

## 10. Acceptance Criteria V1

V1 dapat dianggap siap diuji jika:
- Semua baris input diproses atau kegagalannya tercatat jelas.
- Source CSV tidak berubah.
- Enriched CSV memuat metrik turunan yang benar tanpa kolom duplikat.
- Feedback report terpisah dari CSV.
- Tiga fokus review terwakili.
- Temuan berisi bukti dan alasan yang dapat ditelusuri.
- Hasil tidak mengarang definisi atau threshold yang belum disetujui.
- Test lulus dan hasilnya dilaporkan.
- Jelas apakah review benar-benar menggunakan model AI atau hanya aturan deterministik.

## 11. Instruksi Pembuka untuk Antigravity

Mulai dengan **Discovery saja**.

1. Inspeksi file project yang benar-benar tersedia di workspace.
2. Identifikasi Enrichment Engine V1, source CSV, Data Dictionary, tests, dan output.
3. Laporkan arsitektur yang ada dibandingkan arsitektur target di dokumen ini.
4. Pisahkan fakta yang ditemukan, asumsi, dan hal yang perlu dikonfirmasi.
5. Berikan rencana tahap berikutnya.

**Jangan langsung coding, jangan mengubah source CSV, dan jangan mengklaim file atau komponen ada sebelum memeriksanya.**
