# Kasus Penggunaan 2: Modernisasi Kode Legacy

> **Durasi:** ~60 menit  
> **Tujuan:** Memigrasikan aplikasi legacy menggunakan Mode Perencanaan, sub-agen kustom, skill, dan checkpointing. Mempelajari cara menguraikan basis kode yang besar dengan aman.  
> **PRD Latihan:** [Modernisasi .NET](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_dotnet_modernization.md) · [Peningkatan Java](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_java_upgrade.md)
>
> *Terakhir diperbarui: 2026-05-05 · [Sumber diverifikasi terhadap repositori gemini-cli](https://github.com/google-gemini/gemini-cli)*

---
## 2.1 — Mode Perencanaan: Riset Aman (15 menit)

### Masuk ke Mode Perencanaan

Mode Perencanaan adalah riset hanya-baca. Agen menganalisis basis kode Anda, mengusulkan perubahan, tetapi **tidak memodifikasi apa pun** sampai Anda menyetujuinya.

```
/plan
```

> CLI menunjukkan bahwa Anda berada di Mode Perencanaan. Agen kehilangan akses ke alat penulisan — ia hanya dapat membaca file, menelusuri web, dan berpikir.

### Menganalisis Basis Kode

```
Analyze this codebase for a migration to a modern architecture. 
Identify:
1. Key dependencies and their versions
2. Architectural patterns currently in use
3. Areas of technical debt
4. Migration risks and complexity hotspots
```

> **Apa yang terjadi:** Agen membaca proyek — package.json, file sumber, konfigurasi — dan membangun model mental. Ia mengeksplorasi basis kode Anda sesuai permintaan menggunakan alat seperti `read_file`, `glob`, dan `grep_search` untuk melacak setiap dependensi, pola, dan anti-pola.

### Meninjau Rencana

Agen menghasilkan rencana migrasi terstruktur. Tinjau dengan cermat:

```
Propose a step-by-step plan to modernize the authentication system 
from session-based to JWT with refresh tokens. Include:
- Files that need to change
- Order of operations
- Risk assessment for each step
- Rollback strategy
```

### Pengeditan Rencana Kolaboratif

Buka editor eksternal untuk menyempurnakan rencana:

```
Ctrl+G
```

Ini membuka `$EDITOR` Anda (atau editor bawaan) di mana Anda dapat memodifikasi rencana secara langsung. Agen melihat editan Anda dan menyesuaikan pendekatannya.

### Keluar dari Mode Perencanaan

```
/plan
```

Beralih kembali ke mode normal. Sekarang agen dapat mengeksekusi rencana yang disetujui.

---
## 2.2 — Perutean dan Pengarahan Model (10 menit)

### Perutean Model Otomatis

Gemini CLI dapat secara otomatis memilih di antara model-model berdasarkan kompleksitas tugas:

| Jenis Tugas | Model Tipikal | Alasan |
|---|---|---|
| Perencanaan, analisis arsitektur | **Gemini Pro** | Penalaran kompleks, analisis bentuk panjang |
| Pembuatan kode, pengeditan file | **Gemini Flash** | Eksekusi cepat, biaya lebih rendah |
| Kueri sederhana, pemeriksaan status | **Gemini Flash** | Dioptimalkan untuk kecepatan |

> Perutean ini bersifat heuristik, bukan deterministik — CLI mengevaluasi kompleksitas prompt dan memilihnya dengan sesuai. Anda dapat menimpanya dengan `/model` untuk memilih model tertentu. Lihat [Perutean Model](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/model-routing.md) untuk detailnya.

### Pengarahan Model 🔬

Selama eksekusi, Anda dapat mengarahkan agen di tengah proses:

```
# While the agent is working on a migration step:
Actually, skip the database migration for now. Focus on the API 
layer first — we need the endpoints working before we touch the schema.
```

> **Pengarahan model** memungkinkan Anda mengoreksi arah tanpa harus memulai dari awal. Agen menyesuaikan rencananya berdasarkan input Anda dan melanjutkan dari arah yang baru.

### Periksa Model Mana yang Aktif

```
/stats
```

Menampilkan model saat ini, penggunaan token, dan status caching.

---
## 2.3 — Rekayasa Konteks untuk Migrasi (10 menit)

Proyek migrasi adalah tempat di mana rekayasa konteks memberikan keuntungan terbesar. Basis kode legacy penuh dengan pengetahuan implisit — pola arsitektur, penggunaan API yang sudah usang, rantai dependensi tersembunyi — yang tidak tertulis di mana pun. Agen perlu menginternalisasi ini sebelum dapat mengubah apa pun dengan aman.

Ada dua pendekatan: **manual** (Anda menulis GEMINI.md) dan **didorong oleh agen** (agen menulisnya untuk Anda). Keduanya menghasilkan artefak yang sama, tetapi pendekatan yang didorong oleh agen sering kali memunculkan hal-hal yang mungkin Anda lewatkan.

### Didorong oleh Agen: Orientasi Mandiri dengan @codebase_investigator

Pola paling kuat untuk migrasi adalah meminta agen **menyelidiki basis kode dan menulis GEMINI.md-nya sendiri**. Ini adalah pola "orientasi mandiri agen" — ini mencerminkan apa yang dilakukan oleh insinyur senior saat bergabung dengan proyek baru, tetapi pada kecepatan mesin.

**Langkah 1 — Selidiki:**

```
@codebase_investigator Analyze this entire codebase. Map:
1. Framework versions, build system, and dependency tree
2. Architectural patterns (MVC, data access layers, security config)
3. All javax.* imports that will need jakarta.* migration
4. Configuration files and property sources
5. Test frameworks and coverage patterns
Report any migration risks or complexity hotspots.
```

> **Apa yang terjadi:** Sub-agen `@codebase_investigator` membaca setiap file, melacak impor, memetakan hierarki kelas, dan membangun gambaran lengkap — semuanya dalam mode hanya-baca. Ia tidak pernah memodifikasi apa pun.

**Langkah 2 — Hasilkan konteks:**

```
Based on your codebase analysis, write a GEMINI.md that:
1. Documents what you found (current state: Boot 2.6, Java 8, javax.*)
2. Defines the target state (Boot 3.3, Java 21, jakarta.*)
3. Lists migration rules (one module at a time, preserve API contracts)
4. Encodes testing standards (every phase must pass mvn clean verify)
5. Flags the specific risks you identified

Write this file to the project root as GEMINI.md.
```

**Langkah 3 — Tinjau dan perbaiki:**

Agen menghasilkan GEMINI.md yang didasarkan pada apa yang sebenarnya ditemukannya di dalam kode — bukan tebakan. Tinjau, tambahkan konvensi spesifik tim apa pun, dan setujui. Mulai dari titik ini dan seterusnya, setiap perintah migrasi yang dieksekusi oleh agen dipandu oleh konteks ini.

> **Mengapa ini berhasil:** Agen menulis instruksi untuk dirinya sendiri. GEMINI.md yang dihasilkannya menjadi pagar pengaman untuk pekerjaannya sendiri selanjutnya. Ini adalah loop yang memperkuat diri sendiri: konteks yang lebih baik → perubahan kode yang lebih baik → agen mempelajari lebih banyak pola → konteks meningkat lebih jauh (melalui Auto Memory).

> **Lihat praktiknya:** [Java Upgrade PRD](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_java_upgrade.md) menggunakan pola ini sebagai Fase 0 — agen harus melakukan orientasi mandiri sebelum menyentuh kode migrasi apa pun.

### Manual: Menulis Standar Migrasi Secara Langsung

Untuk tim dengan standar yang sudah mapan, tulis GEMINI.md sendiri:

```markdown
# Migration Standards

## Target Architecture
- Framework: .NET 8 (or modern equivalent)
- Hosting: Cloud Run (containerized)
- Database: Cloud SQL with Entity Framework Core
- Auth: JWT with Google Identity Platform
- Config: appsettings.json (not web.config)

## Migration Rules
- Migrate one module at a time — never refactor everything at once
- Every migrated endpoint must have unit tests before moving on
- Preserve existing API contracts — no breaking changes to consumers
- Document every decision in a MIGRATION.md changelog
```

### Sintaks Impor @file

Untuk proyek besar, pisahkan GEMINI.md menjadi file-file modular:

```markdown
# GEMINI.md
@./docs/architecture.md
@./docs/coding-standards.md
@./docs/migration-checklist.md
```

> **Mengapa impor penting:** Satu GEMINI.md bisa menjadi tidak praktis untuk proyek perusahaan. Impor memungkinkan Anda mengatur konteks ke dalam dokumen terfokus yang lebih mudah dipelihara dan ditinjau. Lihat [referensi GEMINI.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md) untuk sintaks lengkap.

### Memori untuk Pola Migrasi

Saat agen menemukan pola selama migrasi, agen menyimpannya:

```
/memory show
```

Anda juga dapat mengajarinya secara eksplisit:

```
/memory add "When migrating Entity Framework 6 to EF Core, always 
check for .edmx files and replace them with code-first models. 
The database-first approach is deprecated in EF Core."
```

> **Siklus hidup rekayasa konteks:** Alur kerja migrasi terbaik menggabungkan ketiganya: GEMINI.md yang dihasilkan agen (konteks awal), impor @file (standar modular), dan Auto Memory (pola yang dipelajari selama eksekusi). Masing-masing saling memperkuat.

---
## 2.4 — Sub-agen: Mendelegasikan Pekerjaan Khusus (15 menit)

### Sub-agen Bawaan

Gemini CLI mencakup sub-agen bawaan untuk tugas-tugas umum:

```
@codebase_investigator Map the relationships between all controllers 
in the backend/ directory. Show which models each controller depends 
on and which routes call each controller.
```

> **@codebase_investigator** adalah agen hanya baca yang memetakan hubungan kode, melacak rantai panggilan, dan mengidentifikasi pola arsitektur. Agen ini tidak pernah memodifikasi file.

### Sub-agen Kustom

Buat pemindai keamanan untuk migrasi Anda:

```bash
cat .gemini/agents/security-scanner.md
```

Sub-agen pemindai keamanan (dari [`samples/agents/security-scanner.md`](../../samples/agents/security-scanner.md)):
- Memiliki prompt sistem yang difokuskan untuk analisis keamanan
- Dapat dibatasi pada alat-alat tertentu
- Menggunakan model tertentu (Anda dapat menetapkan Flash untuk kecepatan atau Pro untuk kedalaman)

### Menggunakan Sub-agen Kustom

```
@security-scanner Review the authentication middleware for OWASP 
Top 10 vulnerabilities. Check for:
1. Injection attacks (SQL, NoSQL)
2. Broken authentication
3. Sensitive data exposure
4. Missing rate limiting
```

### Isolasi Alat Sub-agen

Setiap sub-agen dapat memiliki daftar izin alatnya sendiri:

```markdown
# .gemini/agents/security-scanner.md
---
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - list_directory
  - google_web_search
# No write_file, no run_shell_command — this agent is read-only
---

You are a security analyst. Your job is to find vulnerabilities...
```

> **Nilai perusahaan:** Pemindai keamanan dapat membaca kode dan mencari CVE, tetapi tidak pernah dapat memodifikasi file atau menjalankan perintah. Isolasi alat adalah pertahanan mendalam.

---
## 2.5 — Skill: Keahlian yang Dapat Digunakan Kembali (5 mnt)

### Lihat Skill yang Tersedia

```
/skills list
```

Skill adalah kumpulan instruksi yang dapat digunakan kembali yang diaktifkan oleh agen saat relevan:

### Cara Kerja Skill

1. **Aktivasi otomatis:** Agen membaca deskripsi skill dan mengaktifkan yang relevan berdasarkan prompt Anda
2. **Aktivasi manual:** Anda dapat memaksakan penggunaan skill dengan namanya
3. **Persistensi:** Skill bertahan di seluruh sesi — pelajari sekali, gunakan di mana saja

### Memori Otomatis 🔬

Memori Otomatis mengekstrak pola dari sesi Anda dan menyimpannya ke GEMINI.md:

```
/memory show
```

> **Eksperimental:** Memori Otomatis memerlukan `experimental.autoMemory` untuk diaktifkan di `settings.json`. Lihat [Dokumentasi Memori Otomatis](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/auto-memory.md). Saat diaktifkan, agen mungkin menyimpan otomatis pola seperti: "Saat memigrasikan middleware Express.js, periksa ketidakcocokan `req.query` vs `req.params`."

---
## 2.6 — Checkpoint dan Git Worktree (5 menit)

### Checkpoint

Checkpoint secara otomatis menyimpan status file yang dimodifikasi sebelum perubahan, memungkinkan Anda untuk mengembalikannya jika terjadi kesalahan. Untuk mengaktifkannya, tambahkan ke `settings.json` Anda:

```json
{
  "general": {
    "checkpointing": {
      "enabled": true
    }
  }
}
```

Saat diaktifkan, gunakan `/restore` untuk kembali ke checkpoint sebelumnya:

```
/restore
```

> **Checkpoint bersifat ringan** — mereka melacak perubahan file, bukan riwayat git lengkap. Lihat [Dokumentasi checkpoint](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/checkpointing.md) untuk detailnya.

### Git Worktree 🔬

Untuk pekerjaan migrasi paralel, gunakan Git worktree:

```
# Create a worktree for the auth migration
git worktree add ../proshop-auth-migration feature/auth-migration
cd ../proshop-auth-migration
gemini
```

> **Mengapa worktree?** Anda dapat memiliki kode asli di satu terminal dan kode yang dimigrasikan di terminal lain. Jalankan pengujian pada keduanya secara bersamaan. Bandingkan pendekatan tanpa berpindah cabang.

---
## Latihan Praktik

Buka **PRD Modernisasi .NET** atau **PRD Peningkatan Java** dan kerjakan migrasi tersebut. Pilih pendekatan Anda:

### Pendekatan A: Mengutamakan Conductor (Rencana → Konteks → Eksekusi)

Mulailah dengan perencanaan terstruktur dan biarkan rencana tersebut mendorong pembuatan konteks:

1. Masuk ke **Mode Perencanaan** (`/plan`) → analisis basis kode target secara read-only
2. Gunakan **Conductor** untuk membuat rencana migrasi bertahap yang sesuai dengan fase-fase PRD
3. Tulis sebuah **GEMINI.md** yang mengodekan standar migrasi dan rencana yang disetujui
4. Gunakan **@codebase_investigator** untuk memetakan dependensi dan memvalidasi rencana tersebut
5. Buat sebuah **checkpoint** sebelum memulai
6. Keluar dari Mode Perencanaan → mulai migrasi, satu fase pada satu waktu
7. Gunakan **pengarahan model** untuk mengoreksi arah sesuai kebutuhan
8. Setelah setiap fase, jalankan `mvn clean verify` dan pemindaian keamanan (lihat di bawah)
9. Tinjau apa yang dipelajari **Auto Memory** dari sesi tersebut

### Pendekatan B: Orientasi Mandiri (Investigasi → Konteks → Rencana → Eksekusi)

Biarkan agen membangun pemahamannya sendiri terlebih dahulu, lalu buat rencana dari apa yang ditemukannya:

1. Gunakan **@codebase_investigator** untuk menganalisis basis kode target dan memetakan dependensi
2. Minta agen **menulis sebuah GEMINI.md** berdasarkan analisisnya (orientasi mandiri agen)
3. Tinjau dan perbaiki konteks yang dihasilkan — tambahkan standar spesifik tim
4. Masuk ke **Mode Perencanaan** → biarkan **Conductor** membuat rencana migrasi bertahap yang diinformasikan oleh GEMINI.md
5. Buat sebuah **checkpoint** sebelum memulai
6. Mulai migrasi — gunakan **pengarahan model** untuk mengoreksi arah sesuai kebutuhan
7. Setelah setiap fase, jalankan `mvn clean verify` dan pemindaian keamanan (lihat di bawah)
8. Tinjau apa yang dipelajari **Auto Memory** dari sesi tersebut

> **Pendekatan mana?** Pendekatan A berfungsi dengan baik ketika Anda sudah mengetahui basis kode dan ingin memimpin dengan struktur. Pendekatan B berfungsi lebih baik dengan kode legacy yang tidak dikenal — agen sering kali memunculkan risiko migrasi yang akan terlewatkan oleh rencana yang ditulis manusia. Coba keduanya dan bandingkan kualitas rencana yang dihasilkan.

> **Pemindaian keamanan pasca-migrasi:** Setelah memodernisasi kode legacy, jalankan [Security Extension](https://github.com/gemini-cli-extensions/security) resmi untuk menangkap kerentanan yang muncul selama migrasi. Instal dengan `gemini extensions install https://github.com/gemini-cli-extensions/security`, lalu jalankan `/security:analyze` untuk memindai perubahan Anda. Lihat [Ekosistem Ekstensi — Latihan 4](extensions-ecosystem.md) untuk detail lengkapnya.

---
## Ringkasan: Apa yang Anda Pelajari

| Fitur | Apa yang Dilakukannya |
|---|---|
| **Mode Perencanaan** | Riset hanya-baca — analisis sebelum memodifikasi |
| **Perutean model** | Pemilihan otomatis Pro (perencanaan) → Flash (pengkodean) |
| **Pengarahan model** | Mengoreksi arah agen di tengah proses |
| **Orientasi mandiri agen** | Agen menyelidiki basis kode dan menulis GEMINI.md-nya sendiri |
| **Sintaks @ import** | GEMINI.md modular untuk proyek besar |
| **@codebase_investigator** | Sub-agen analisis basis kode hanya-baca |
| **Sub-agen kustom** | Agen khusus dengan isolasi alat |
| **Skill** | Kumpulan instruksi yang dapat digunakan kembali dan aktif secara otomatis |
| **Memori Otomatis** | Agen mempelajari pola dari sesi |
| **Checkpointing** | Simpan/pulihkan status otomatis sebelum perubahan berisiko (aktifkan di settings.json) |
| **Git Worktree** | Cabang paralel untuk pekerjaan simultan |
| **Ekstensi Keamanan** | Pemindaian kerentanan pasca-migrasi dengan `/security:analyze` |

---
## Langkah Selanjutnya

→ Lanjutkan ke **[Kasus Penggunaan 3: Orkestrasi DevOps Agentic](devops-orchestration.md)**

→ Untuk pengguna tingkat lanjut: **[Pola Lanjutan](advanced-patterns.md)** — keterampilan prompt, loop verifikasi, dan pengembangan paralel
