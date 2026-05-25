# M09 — Panduan Migrasi: Gemini CLI → Antigravity CLI

**Durasi:** 30 menit  
**Audiens:** Semua  
**Prasyarat:** M01 (Kontak Pertama)  
**Tujuan:** Memahami transisi 18 Juni 2026, memigrasikan semua konfigurasi yang ada, dan memutuskan jalur yang tepat ke depan untuk tim Anda.

> **⚠️ Sensitif Waktu:** Gemini CLI berhenti melayani pengguna gratis, Google AI Pro, dan Google AI Ultra pada **18 Juni 2026**. Modul ini memandu setiap langkah migrasi sehingga tim Anda tidak terbangun dengan alur kerja yang rusak.

---
## Latar Belakang: Mengapa Ini Terjadi

Ketika Google merilis Gemini CLI pada tahun 2025, tujuannya adalah untuk membawa Gemini langsung ke dalam terminal. Setelah lebih dari 100.000 bintang GitHub, 6.000 pull request yang digabungkan, dan jutaan pengguna, tim mempelajari sesuatu yang penting: pengembang kini membutuhkan **beberapa agen yang berkomunikasi satu sama lain**, berbagi backend terpadu dengan sisa alur kerja mereka.

Kebutuhan arsitektur tersebut mendorong konsolidasi. **Antigravity CLI** (`agy`) adalah hasilnya — pengalaman terminal berbasis Go yang mengutamakan agen, yang berbagi harness yang sama dengan aplikasi desktop Antigravity 2.0. Setiap peningkatan inti pada mesin agen secara otomatis berlaku di mana saja.

Perubahan utama dari Gemini CLI:

| Dimensi | Gemini CLI | Antigravity CLI |
|:---|:---|:---|
| **Bahasa** | Node.js / TypeScript | Go (cold start lebih cepat) |
| **Nama berkas biner** | `gemini` | `agy` |
| **Lisensi** | Apache 2.0 (sumber terbuka) | Sumber tertutup |
| **Multi-agen** | Sub-agen (sesi tunggal) | Asinkronus, orkestrasi latar belakang |
| **Sinkronisasi desktop** | Tidak ada | Harness bersama dengan Antigravity 2.0 |
| **Jalur skill** | `.gemini/skills/` | `.agents/skills/` |
| **Format plugin** | Ekstensi di `settings.json` | Plugin Antigravity (`plugin.json`) |
| **Konfigurasi MCP** | Inline di `settings.json` | `mcp_config.json` terpisah |
| **Berkas konteks** | `GEMINI.md` | `GEMINI.md` **atau** `AGENTS.md` (keduanya berfungsi) |

**Referensi:**
- [Pengumuman Google I/O (19 Mei 2026)](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
- [Dokumentasi migrasi resmi](https://antigravity.google/docs/gcli-migration)
- [Panduan migrasi komunitas](https://avinashsangle.com/blog/gemini-cli-to-antigravity-cli-guide)

---
## 9.1 — Siapa yang Terdampak? (5 menit)

**Tunjukkan matriks dampak:**

| Tingkat | Status pada 18 Juni 2026 | Tindakan yang Disarankan |
|:---|:---|:---|
| **Gratis (Gemini Code Assist untuk individu)** | Akses diputus | Migrasi ke Antigravity CLI |
| **Google AI Pro ($19.99/bln)** | Akses ke Gemini CLI diputus | Tingkat Antigravity Pro diterapkan secara otomatis; periksa batas permintaan baru |
| **Google AI Ultra ($249.99/bln)** | Akses ke Gemini CLI diputus | Tingkat Antigravity Ultra (tanpa batas mingguan) diterapkan secara otomatis |
| **Gemini Code Assist Standard / Enterprise** | ✅ Tidak berubah | Migrasi opsional; Gemini CLI tetap berfungsi |
| **Gemini Code Assist untuk GitHub (dibayar melalui GCP)** | Instalasi yang ada tidak berubah; instalasi baru diblokir | Rencanakan migrasi sebelum pembaruan berikutnya |

> **Untuk peserta lokakarya di Standard/Enterprise:** Anda tidak dipaksa untuk melakukan migrasi. Antigravity CLI tersedia untuk Anda sekarang dan layak untuk dievaluasi, tetapi investasi Anda yang ada saat ini tetap terlindungi.

**Ada dua jalur jika Anda ingin mempertahankan berkas biner sumber terbuka Gemini CLI:**
1. Hubungkan **kunci API Gemini berbayar** (AI Studio atau Vertex AI) ke dalam berkas biner Gemini CLI Apache 2.0 — skill, hook, dan konfigurasi MCP Anda tidak memerlukan perubahan.
2. Tingkatkan ke **Gemini Code Assist Standard atau Enterprise** untuk jalur yang dikelola dan didukung.

> Catatan: Antigravity CLI adalah **sumber tertutup** — sebuah pemisahan yang disengaja dari model Apache 2.0 Gemini CLI. Jika portabilitas yang netral terhadap vendor, audit, atau hak *forking* penting di lingkungan Anda yang diatur, jalur kunci API berbayar mempertahankan properti tersebut.

---
## 9.2 — Instal Antigravity CLI (5 menit)

> **Praktik terbaik:** Biarkan kedua berkas biner (`gemini` dan `agy`) terinstal berdampingan selama masa transisi. Jalankan alur kerja melalui keduanya untuk memastikan kesetaraan sebelum beralih sepenuhnya.

### macOS dan Linux

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

Berkas biner akan ditempatkan di `~/.local/bin/agy`. Jika direktori tersebut tidak ada di `PATH` Anda:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

### Windows PowerShell

```powershell
irm https://antigravity.google/cli/install.ps1 | iex
```

### Windows CMD

```cmd
curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && install.cmd && del install.cmd
```

### Jalankan Pertama Kali & OAuth

```bash
agy
```

Ini akan membuka peramban bawaan Anda untuk Google OAuth. Masuk dengan **akun yang sama yang Anda gunakan untuk Gemini CLI** sehingga impor plugin mengambil ruang kerja yang benar. Pada mesin SSH jarak jauh, `agy` mendeteksi sesi dan mencetak URL otorisasi untuk dibuka secara lokal (sebuah peningkatan dari alur lama Gemini CLI).

**Verifikasi instalasi:**

```bash
agy --version
```

---
## 9.3 — Migrasi Plugin & Ekstensi (5 menit)

Ekstensi Gemini CLI menjadi plugin Antigravity CLI. Perintah import menangani sebagian besar proses ini secara otomatis.

### Langkah 1 — Impor Otomatis

```bash
agy plugin import gemini
```

Ini memindai direktori ekstensi Gemini CLI Anda dan mendaftarkan masing-masing sebagai plugin Antigravity. Plugin yang bergantung pada tema kustom akan dihapus temanya tanpa pemberitahuan — bangun ulang secara manual menggunakan format `plugin.json`.

### Langkah 2 — Verifikasi Plugin yang Diimpor

```bash
agy plugin list
```

### Langkah 3 — Pindahkan Skill Ruang Kerja

```bash
# Skills used to live here (per-workspace):
# .gemini/skills/

# They now live here:
# .agents/skills/

cp -r .gemini/skills/ .agents/skills/
```

Direktori skill global dimuat secara otomatis dari jalur baru. Tidak ada perubahan konten yang diperlukan pada berkas skill SKILL.md.

> **Berkas konteks lokakarya kompatibel ke belakang.** Baik `GEMINI.md` maupun `AGENTS.md` dibaca tanpa modifikasi. Anda tidak perlu mengganti nama atau memformat ulang berkas konteks proyek yang ada.

---
## 9.4 — Migrasi Konfigurasi server MCP (5 menit)

Konfigurasi server MCP berpindah dari `settings.json` inline ke `mcp_config.json` khusus, dan satu bidang diganti namanya.

### Sebelum (Gemini CLI `settings.json`)

```json
{
  "mcpServers": {
    "bigquery-mcp": {
      "command": "npx",
      "args": ["-y", "@google/bigquery-mcp-server"],
      "url": "http://localhost:3000"
    },
    "developer-knowledge": {
      "command": "npx",
      "args": ["-y", "@google/developer-knowledge-mcp"],
      "url": "http://localhost:3001"
    }
  }
}
```

### Sesudah (Antigravity CLI `mcp_config.json`)

```json
{
  "mcpServers": {
    "bigquery-mcp": {
      "command": "npx",
      "args": ["-y", "@google/bigquery-mcp-server"],
      "serverUrl": "http://localhost:3000"
    },
    "developer-knowledge": {
      "command": "npx",
      "args": ["-y", "@google/developer-knowledge-mcp"],
      "serverUrl": "http://localhost:3001"
    }
  }
}
```

**Satu-satunya perubahan adalah `url` → `serverUrl`.** Semua bidang lainnya tetap sama.

**Verifikasi server MCP dimuat:**

```bash
agy /mcp
```

---
## 9.5 — Memvalidasi Hook & Menjalankan End-to-End (5 menit)

Hook terus berfungsi di Antigravity CLI. Jalankan kembali alur kerja yang digerakkan oleh hook untuk mengonfirmasi bahwa hook `pre-tool-call` dan `stop` terpicu seperti yang diharapkan.

```bash
# Run a representative workflow you trust
agy "Analyze backend/controllers/orderController.js and summarize the error handling patterns"

# Compare to Gemini CLI output if you still have it running
gemini "Analyze backend/controllers/orderController.js and summarize the error handling patterns"
```

**Hal-hal yang berubah pada permukaan CLI (perhatian):**

| Gemini CLI | Antigravity CLI | Catatan |
|:---|:---|:---|
| `gemini --resume` | `agy --resume` | Semantik yang sama |
| `gemini -p "prompt"` | `agy -p "prompt"` | Mode headless utuh |
| `/tools` | `/tools` | Tidak berubah |
| `/rewind` | `/rewind` | Tidak berubah |
| `gemini skills` (perintah terminal) | Gunakan `/skills` di dalam `agy` | Perintah tingkat terminal dihapus |
| `--temperature`, `--top_k` | Tidak diekspos di permukaan CLI | Diatur melalui konfigurasi atau prompt |

---
## 9.6 — Batas Permintaan & Pengecekan Realitas Harga (5 menit)

> **Perhatian untuk pengguna paket gratis:** Paket gratis jauh lebih ketat dibandingkan paket gratis lama Gemini CLI.

| Tingkat | Gemini CLI (lama) | Antigravity CLI |
|:---|:---|:---|
| **Gratis** | ~1.000 permintaan/hari | Kuota mingguan; disegarkan setiap 5 jam hingga batas keras mingguan |
| **Pro ($19,99/bln)** | Batas harian yang wajar | Tingkat Antigravity Pro |
| **Ultra ($249,99/bln)** | Batas harian yang tinggi | Tidak ada batas mingguan |

Laporan komunitas (Diskusi GitHub #27274) menunjukkan bahwa batas mingguan paket gratis habis dalam **4–5 giliran obrolan** dengan jendela pengaturan ulang 166 jam. Rencanakan hal ini jika Anda menggunakan Antigravity CLI untuk latihan lokakarya.

**Rekomendasi praktis untuk penyampaian lokakarya:**
- Jika organisasi Anda memiliki lisensi Standar/Enterprise, lanjutkan menggunakan Gemini CLI untuk modul praktik langsung dan gunakan modul ini untuk mengarahkan tim pada jalur migrasi.
- Jika berjalan pada akun pribadi, gunakan tingkat Pro/Ultra berbayar atau siapkan cadangan yang didukung kunci API.

---
## 9.7 — Kerangka Keputusan: Bertahan, Migrasi, atau Beralih? (5 menit)

Gunakan pohon keputusan ini untuk merekomendasikan jalur yang tepat:

```
Are you on Gemini Code Assist Standard or Enterprise?
├── YES → Keep Gemini CLI. Evaluate Antigravity CLI in parallel.
│         No forced migration. Your access is unchanged.
└── NO → Continue below.

Do you need open-source auditability, forking rights, or vendor-neutral plumbing?
├── YES → Stay on Gemini CLI + paid Gemini API key (AI Studio or Vertex AI).
│         Apache 2.0 toolchain, zero migration required.
└── NO → Continue below.

Do you do heavy long-context refactors, CI agents, or MCP-intensive workflows?
├── YES → Evaluate Claude Code with Opus 4.6 (1M context, 77.2% SWE-bench).
│         Strongest open alternative for terminal-first coding.
└── NO → Migrate to Antigravity CLI.
         agy plugin import gemini covers 90% of the work.
```

---
## Aktivitas: Migrasi Langsung (jika waktu memungkinkan)

Jalankan daftar periksa migrasi terhadap repo lokakarya itu sendiri:

```bash
# 1. Install
curl -fsSL https://antigravity.google/cli/install.sh | bash

# 2. Authenticate
agy

# 3. Import plugins
agy plugin import gemini

# 4. Move skills
cp -r .gemini/skills/ .agents/skills/

# 5. Create mcp_config.json from existing settings.json
# (change url → serverUrl for each server entry)

# 6. Validate
agy /mcp
agy /skills

# 7. Run a known-good workflow
agy "Trace the request lifecycle for placing an order in the ProShop demo app"
```

---
## Poin-Poin Penting

- **Batas waktu:** 18 Juni 2026 untuk pengguna paket gratis, AI Pro, dan AI Ultra. Pengguna enterprise tidak terpengaruh.
- **Waktu migrasi:** 30–60 menit per ruang kerja dengan skill, hook, dan server MCP.
- **`GEMINI.md` langsung berfungsi.** Tanpa penggantian nama, tanpa pemformatan ulang.
- **Hal yang paling perlu diperhatikan:** Konfigurasi MCP dipindahkan ke `mcp_config.json` dengan `url` diubah namanya menjadi `serverUrl`.
- **Batas permintaan:** Aturan paket gratis jauh lebih ketat. Atur anggaran Anda dengan sesuai.
- **Tim enterprise:** Investasi Gemini CLI Anda saat ini terlindungi. Migrasi bersifat opsional.

---
## Referensi

- [Pengumuman resmi — Google Developers Blog](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
- [Dokumentasi migrasi resmi — antigravity.google](https://antigravity.google/docs/gcli-migration)
- [Panduan komunitas — Avinash Sangle](https://avinashsangle.com/blog/gemini-cli-to-antigravity-cli-guide)
- [Diskusi GitHub #27274 — Reaksi komunitas](https://github.com/google-gemini/gemini-cli/discussions/27274)
- [Unduhan Antigravity CLI](https://antigravity.google/download)
