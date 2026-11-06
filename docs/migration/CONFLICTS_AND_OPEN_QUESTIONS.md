# WORKLENS — Conflicts and Open Questions Report

> **Tujuan:** Dokumentasi komprehensif seluruh konflik spesifikasi, inkonsistensi antara dokumen vs kode vs pengujian, dan pertanyaan terbuka yang memerlukan konfirmasi bisnis sebelum atau selama porting logic.

---

## 1. Identifikasi Konflik Antara Dokumen, Kode, dan Pengujian

### Konflik 1: Batasan Ruang Lingkup Web UI (Frontend)
- **Teks Dokumen Sumber (`AGENTS.md` Bagian 2):**
  > *"Scope Boundaries (Strictly Out of Scope for V1): No Web UI or frontend frameworks."*
- **Spesifikasi Sasaran WORKLENS:**
  > *"Target Arsitektur Frontend: React, TypeScript, Vite, Tailwind CSS."*
- **Bukti & Analisis:**
  Pada project legacy (`workload_enrichment`), harness awal beroperasi secara murni CLI/headless dengan laporan akhir diekspor ke file HTML statis tunggal (`ops_category_dashboard.html`). Di WORKLENS, frontend interaktif adalah sasaran utama platform.
- **Rekomendasi:**
  Adaptasikan `AGENTS.md` di WORKLENS untuk mencantumkan bahwa Web UI berbasis React + Tailwind adalah **IN SCOPE** untuk WORKLENS, sembari tetap mempertahankan batasan inti lainnya (tanpa database SQL eksternal, tanpa bypass validasi, logika deterministik terpisah dari AI).

---

### Konflik 2: Integrasi Sinkronisasi SharePoint / OneDrive
- **Teks Dokumen Sumber (`OPERATIONAL_INTEGRATION_GUIDE.md` & `harness/operational_sync.py`):**
  > Dokumen mendesain integrasi Power Automate, Office Scripts, dan Microsoft Graph API untuk sinkronisasi otomatis bolak-balik dengan SharePoint Online.
- **Mandat Proyek WORKLENS:**
  > *"Input utama melalui manual JSON upload. Tidak menggunakan OneDrive Desktop Sync atau Microsoft Graph API. Jangan memasukkan kembali fitur OneDrive Sync."*
- **Bukti & Analisis:**
  Modul `operational_sync.py` pada legacy project menangani deteksi token dan sync OneDrive lokal. Ini bertentangan langsung dengan prinsip arsitektur WORKLENS yang mengutamakan portabilitas lokal, kesederhanaan deployment, dan isolasi keamanan (YAGNI).
- **Rekomendasi:**
  Klasifikasikan `OPERATIONAL_INTEGRATION_GUIDE.md` dan modul sync sebagai **OBSOLETE**. Seluruh logika upload dan swapping dataset di WORKLENS dialihkan secara eksklusif ke REST API `/api/v1/upload` (Manual JSON/CSV Ingestion).

---

### Konflik 3: Status Bukti (`Workload Evidence Status`) — Dokumen vs Kode
- **Teks Dokumen Spesifikasi Awal (`Specification.md` Bagian 2.3):**
  > *"Kolom Workload Evidence Status diisi nilai default UNVERIFIED atau NOT_EVALUATED hingga kriteria atau kolom bukti pada dataset dikonfirmasi oleh pemilik proses."*
- **Implementasi Nyata & Pengujian Terkunci (`harness/enrichment.py` & `tests/test_enrichment.py`):**
  ```python
  class EvidenceStatus(str, Enum):
      LINK_PROVIDED = "LINK_PROVIDED"
      NO_LINK_ATTACHED = "NO_LINK_ATTACHED"
  ```
  Baris diberi status `LINK_PROVIDED` jika kolom `Link Confluence` atau `Link Wiki` memiliki nilai teks valid; selain itu bernilai `NO_LINK_ATTACHED`.
- **Bukti & Analisis:**
  Keputusan ini telah disahkan dan dikunci pada Milestone 1 Chunk 3. Kode pengujian menguji secara ketat nilai enum `LINK_PROVIDED` dan `NO_LINK_ATTACHED`.
- **Rekomendasi:**
  Pertahankan implementasi kode & pengujian existing (`LINK_PROVIDED` dan `NO_LINK_ATTACHED`) sebagai standar kanonikal di WORKLENS, dan perbarui catatan di `TECHNICAL_SPECIFICATION.md` bahwa usulan `UNVERIFIED` telah digantikan secara permanen oleh evaluasi ketersediaan tautan fisik.

---

### Konflik 4: Skema Nilai Diizinkan untuk Kolom `Automation/Manual`
- **Teks Dokumen Spesifikasi (`Specification.md` Bagian 1.1):**
  > *"Daftar Nilai Status: Rentang nilai yang sah (allowed enum) untuk kolom Automation/Manual -> Status Keputusan: Memerlukan Persetujuan."*
- **Implementasi Nyata (`harness/schema.py` & `harness/enrichment.py`):**
  Pipeline deterministik M1 **tidak memblokir** baris jika nilai `Automation/Manual` memiliki variasi teks (misal `"Auto"`, `"Manual"`, `"Automasi"`, `""`), karena kalkulasi matematika hanya bergantung pada angka `Workload` dan `Workload after`. Namun, pada M3 AI Reviewer (`ai_reviewer.py`), anomali konsistensi diperiksa terhadap kombinasi `Improvement Category` dan `Category Notes` (aturan Q14 & Q50).
- **Rekomendasi:**
  Jangan membatasi kolom `Automation/Manual` dengan filter rigid fail-fast pada tahap validasi skema input. Pertahankan pendekatan permisif pada M1, dan serahkan evaluasi inkonsistensi nilai ke AI Reviewer M3.

---

## 2. Pertanyaan Terbuka & Keputusan yang Membutuhkan Konfirmasi Bisnis

| No | Pertanyaan Terbuka / Keputusan | Opsi yang Tersedia | Dampak Teknis di WORKLENS | Rekomendasi Terpilih (Sesuai Ponytail) |
|:---:|:---|:---|:---|:---|
| **Q1** | **Scope Dataset Upload Multi-user vs Single-instance:** Apakah upload file assessment di Web UI diperlakukan sebagai dataset global aktif tunggal (shared across all viewers) atau per-session pengguna? | **A.** Single Active Dataset (Global singleton di memory server)<br/>**B.** Multi-session / Multi-tenant (Tiap sesi browser memiliki state terpisah) | Opsi B membutuhkan session management, cookie tokens, dan multi-instance store di memory. | **Pilih Opsi A (Single Active Dataset):** Selaras dengan arsitektur assessment batch internal L1 AGIT di mana satu tim menganalisis dataset acuan yang sama. |
| **Q2** | **Format Primer Upload Manual:** Apakah endpoint upload menerima file JSON terstruktur murni, CSV mentah, atau keduanya? | **A.** JSON murni<br/>**B.** Dual-mode (JSON primer, CSV dengan parsing otomatis) | Dual-mode membutuhkan parser header CSV dan JSON normalizer berdampingan. | **Pilih Opsi B (Dual-mode):** Mendukung fleksibilitas analis yang masih mengekspor dari Excel/CSV maupun sistem yang mengirim JSON. |
| **Q3** | **Retensi Riwayat Run (Pruning Policy):** Apakah folder timestamped `runs/YYYYMMDD_HHMMSS/` perlu dibatasi (misal simpan 30 run terakhir) untuk mencegah penumpukan disk? | **A.** Simpan tanpa batas (manual cleanup)<br/>**B.** Auto-prune (retensi N run terakhir) | Disk I/O kecil karena artefak run rata-rata < 5 MB. | **Pilih Opsi A untuk V1:** Tetap simpan seluruh run untuk kebutuhan audit immutabilitas; tambahkan auto-prune di Horizon 3 jika disk mulai terbebani. |

