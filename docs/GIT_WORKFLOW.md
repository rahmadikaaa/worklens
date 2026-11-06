# Git Workflow & Recovery Guide — SOP L1 AGIT Agent Harness

Dokumen ini menjadi standar operasional version control untuk repository `sop-l1-agit-agent-harness` guna menjaga stabilitas kode, ketertelusuran riwayat, dan keamanan data.

---

## 1. Branch Strategy

Strategi branching dirancang sederhana dan pragmatis:

```
[main] (versi stabil / production baseline)
  │
  └── [develop] (integrasi development)
        │
        ├── [feature/parser-engine]
        ├── [feature/gemini-enricher]
        └── [feature/audit-validator]
```

### Aturan Branch:
1. **`main`**:
   - Khusus versi stabil dan teruji yang sesuai baseline PRD & Spesifikasi.
   - **Dilarang keras melakukan commit atau development langsung di `main`**.
2. **`develop`**:
   - Cabang integrasi aktif seluruh fitur sebelum masuk ke `main`.
3. **`feature/<feature-name>`**:
   - Cabang kerja untuk implementasi modul/fitur spesifik (dibuat dari `develop`).
   - Format penamaan: `feature/<nama-fitur-kebab-case>` (contoh: `feature/excel-parser`, `feature/batch-enricher`).
   - Setelah fitur selesai diuji, digabungkan kembali ke `develop`.

---

## 2. Standar Commit Message

Gunakan konvensi *Conventional Commits*:
- `feat:` Penambahan fitur baru (misal: `feat: add lookup mapping engine for activity breakdown`)
- `fix:` Perbaikan bug / logic issue (misal: `fix: handle null values in timestamp column`)
- `chore:` Pemeliharaan, dependensi, atau konfigurasi (misal: `chore: establish initial project baseline`)
- `docs:` Pembaruan dokumentasi (misal: `docs: update git workflow recovery steps`)
- `test:` Penambahan atau perbaikan unit test / fixtures

---

## 3. Recovery Workflow (Penanganan Perubahan & Rollback)

### A. Melihat Perubahan & Riwayat
- **Melihat status file:**
  ```bash
  git status
  ```
- **Melihat diff perubahan yang belum di-stage:**
  ```bash
  git diff
  ```
- **Melihat diff file yang sudah di-stage:**
  ```bash
  git diff --staged
  ```
- **Melihat riwayat commit secara ringkas:**
  ```bash
  git log --oneline --graph --decorate
  ```

### B. Membatalkan Perubahan yang Belum Di-commit
- **Membatalkan perubahan pada file tertentu di working directory:**
  ```bash
  git restore <nama_file>
  ```
- **Unstage file dari staging area (tetap menyimpan perubahannya di working tree):**
  ```bash
  git restore --staged <nama_file>
  ```

### C. Membatalkan Commit dengan Aman (`git revert`)
Gunakan `git revert` untuk membatalkan commit lama dengan membuat commit baru yang membalikkan perubahannya tanpa merusak riwayat git:
```bash
# Membatalkan commit tertentu secara aman
git revert <commit-hash>
```

> [!CAUTION]
> **Larangan Perintah Destruktif Tanpa Persetujuan Eksplisit:**
> - Jangan jalankan `git reset --hard` karena menghapus perubahan yang belum di-commit secara permanen.
> - Jangan jalankan `git clean -fd` tanpa verifikasi daftar file yang akan terhapus.
> - Jangan jalankan force push (`git push --force`) ke branch bersama (`main` / `develop`).

---

## 4. Rekomendasi Setup Remote GitHub

1. **Pembuatan Repository di GitHub:**
   - Nama repositori: `sop-l1-agit-agent-harness`
   - Visibilitas: **Private**
   - Jangan inisialisasi dengan README / .gitignore / License bawaan GitHub (karena sudah ada di lokal).

2. **Menghubungkan Remote Lokal ke GitHub:**
   ```bash
   # Ganti <username-atau-org> dengan akun GitHub Anda
   git remote add origin https://github.com/<username-atau-org>/sop-l1-agit-agent-harness.git
   ```

3. **Push Baseline ke Remote (Setelah Mendapat Persetujuan):**
   ```bash
   git branch -M main
   git push -u origin main
   git checkout -b develop
   git push -u origin develop
   ```
