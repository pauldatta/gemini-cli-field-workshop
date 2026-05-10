# Kasus Penggunaan 1: Peningkatan Produktivitas SDLC

> **Durasi:** ~60 menit  
> **Tujuan:** Membangun alur kerja pengembang tingkat perusahaan dari instalasi pertama melalui rekayasa konteks, pengembangan berbasis spesifikasi dengan Conductor, dan pagar pengaman tata kelola.  
> **PRD Latihan:** [Fitur Wishlist Produk](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_sdlc_productivity.md)
>
> *Terakhir diperbarui: 2026-05-05 · [Sumber diverifikasi terhadap repositori gemini-cli](https://github.com/google-gemini/gemini-cli)*

---
## 1.1 — Kontak Pertama (10 menit)

### Instal Gemini CLI

```bash
npm install -g @google/gemini-cli
```

### Luncurkan dan Autentikasi

```bash
cd demo-app
gemini
# Follow the OAuth flow in your browser
```

### Prompt Pertama Anda

Mulailah dengan sesuatu yang membuktikan agen dapat membaca basis kode Anda:

```
What is the tech stack of this project? List the main frameworks, 
database, and authentication mechanism.
```

> **Apa yang terjadi:** Agen membaca `package.json`, memindai struktur direktori, dan memetakan arsitekturnya. Gemini CLI menjelajahi basis kode Anda sesuai permintaan — membaca file, mencari pola, dan melacak dependensi menggunakan alat seperti `read_file`, `glob`, dan `grep_search` sesuai kebutuhan.

### Jelajahi Alat

```
/tools
```

Ini menunjukkan setiap alat yang dapat digunakan agen: operasi file, perintah shell, pencarian web, dan server MCP apa pun yang telah Anda konfigurasikan.

### Pintasan Utama

| Pintasan | Tindakan |
|---|---|
| `Tab` | Terima saran pengeditan |
| `Shift+Tab` | Siklus melalui mode persetujuan |
| `Ctrl+G` | Buka editor eksternal (edit prompt atau rencana) |
| `Ctrl+C` | Batalkan operasi saat ini |
| `/stats` | Tampilkan penggunaan token untuk sesi ini |
| `/clear` | Bersihkan konteks dan mulai dari awal |

---
## 1.2 — Rekayasa Konteks dengan GEMINI.md (15 menit)

### Hierarki Konteks

Gemini CLI membaca file `GEMINI.md` di berbagai tingkat, masing-masing menambahkan konteks yang lebih spesifik:

![Hierarki Konteks GEMINI.md](../assets/context-hierarchy.png)

> **Penemuan konteks JIT:** Agen hanya memuat file GEMINI.md yang relevan dengan file yang sedang dikerjakannya. Jika sedang mengedit `backend/controllers/productController.js`, agen memuat GEMINI.md proyek DAN GEMINI.md backend — tetapi bukan yang frontend.

### Memeriksa GEMINI.md Proyek

```bash
cat GEMINI.md
```

File ini (disalin dari [`samples/gemini-md/project-gemini.md`](../../samples/gemini-md/project-gemini.md) selama pengaturan) mendefinisikan:
- Aturan arsitektur (routes → controllers → models)
- Anti-pola (tidak ada callback, tidak ada kredensial yang di-hardcode)
- Standar pengujian

### Menguji Penegakan Konteks

Minta agen untuk melanggar aturan dan lihat apakah ia mengoreksi dirinya sendiri:

```
Add a new GET endpoint to fetch featured products. 
Put the database query logic directly in the route file.
```

> **Diharapkan:** Agen harus mengenali bahwa ini melanggar aturan GEMINI.md ("Tidak boleh ada logika bisnis di file rute") dan sebagai gantinya membuat endpoint di pengontrol, dengan rute tipis yang mendelegasikan.

> **Menegakkan Aturan:** `GEMINI.md` memberikan panduan yang kuat, tetapi agen masih bisa membuat kesalahan selama refaktor yang kompleks. Pasangkan aturan berbasis prompt ini dengan linter deterministik (seperti `dependency-cruiser`) yang terhubung ke CI/CD atau [Gemini CLI Hooks](https://www.geminicli.com/docs/hooks/). Lihat [Penegakan Deterministik](advanced-patterns.md#deterministic-enforcement) di panduan Pola Lanjutan untuk pengaturan lengkapnya.

### Menambahkan Konteks Backend

```bash
cat backend/GEMINI.md
```

Ini menambahkan aturan khusus backend tentang penanganan kesalahan, pola async, dan keamanan.

### Memori: Pengetahuan Persisten

Agen dapat mengingat berbagai hal di seluruh sesi:

```
/memory show
```

Tambahkan pengetahuan khusus proyek dengan memberi tahu agen secara langsung:

```
Remember that the ProShop backend runs on port 5000, the React dev server 
on port 3000, MongoDB on port 27017, and the test database is 'proshop_test'.
```

Agen akan memperbarui file `GEMINI.md` Anda secara langsung menggunakan `write_file` atau `edit` — tidak diperlukan perintah garis miring (slash command).

> ⚠️ **Catatan:** `/memory add` telah dihapus di Gemini CLI v0.41.1 sebagai bagian dari pembaruan Memory V2. Alat `save_memory` yang mendasarinya tidak lagi didaftarkan secara default. Gunakan bahasa alami sebagai gantinya — hasilnya identik. Lihat [CHANGELOG.md](../../CHANGELOG.md) dan [upstream issue #26563](https://github.com/google-gemini/gemini-cli/issues/26563) untuk detailnya.

Agar agen menggali sesi sebelumnya secara otomatis dan mengusulkan pembaruan memori untuk Anda tinjau, aktifkan Auto Memory di `~/.gemini/settings.json`:

```json
{
  "experimental": {
    "autoMemory": true
  }
}
```

Kemudian gunakan `/memory inbox` untuk meninjau dan menyetujui fakta yang diekstraksi sebelum di-commit.

### File .geminiignore

Kendalikan apa yang dapat dan tidak dapat dilihat oleh agen:

```bash
cat .geminiignore
# node_modules/
# .env
# *.log
# coverage/
```

> **Mengapa ini penting:** Tanpa `.geminiignore`, agen mungkin membuang-buang token konteks untuk membaca `node_modules/` (ratusan ribu file). Dengannya, agen hanya berfokus pada kode sumber Anda.

---
## 1.3 — Conductor: Build yang Mengutamakan Konteks (15 menit)

### Mengapa Conductor?

Mode Perencanaan sangat bagus untuk fitur sekali pakai. Namun untuk proyek multi-hari di mana Anda memerlukan spesifikasi yang persisten, rencana implementasi bertahap, dan pelacakan kemajuan di seluruh sesi — itulah Conductor.

### Instal Conductor

```bash
gemini extensions install https://github.com/gemini-cli-extensions/conductor
```

Verifikasi:

```
/extensions list
```

### Siapkan Konteks Proyek

```
/conductor:setup prompt="This is a MERN stack eCommerce app (ProShop). 
Express.js backend with MongoDB. React frontend with Redux Toolkit. 
Use clean architecture: routes register middleware and delegate to 
controllers. Controllers handle business logic. Models define schema. 
No business logic in route files."
```

### Periksa Apa yang Dibuat Conductor

```bash
ls conductor/
# product.md  tech-stack.md  tracks/

cat conductor/product.md
cat conductor/tech-stack.md
```

> **Wawasan utama:** File-file ini sekarang menjadi sumber kebenaran untuk proyek Anda. File-file tersebut adalah Markdown, berada di repo Anda, di-commit dan ditinjau seperti kode lainnya. Saat Anda kembali besok — atau menyerahkan proyek ini kepada rekan kerja — AI akan melanjutkannya tepat di tempat Anda berhenti. Statusnya ada di dalam file, bukan di memori.

### Buat Jalur Fitur

Gunakan PRD wishlist sebagai spesifikasi fitur:

```
/conductor:newTrack prompt="Add a product wishlist feature. Users can 
add products to a personal wishlist from the product detail page. 
The wishlist is stored in MongoDB as an array of product references 
on the User model. Show a wishlist page with the ability to remove 
items or move them to the cart."
```

### Tinjau Artefak yang Dihasilkan

```bash
# The specification
cat conductor/tracks/*/spec.md

# The implementation plan
cat conductor/tracks/*/plan.md
```

> **Lihatlah rencananya.** Rencana tersebut dipecah menjadi beberapa fase dengan tugas dan kotak centang spesifik. Fase 1: skema database. Fase 2: endpoint API. Fase 3: komponen frontend. Fase 4: pengujian. Agen mengikuti rencana ini secara berurutan, mencentang tugas saat menyelesaikannya.

> **Jika Anda tidak setuju dengan pendekatannya** — katakanlah Anda menginginkan GraphQL alih-alih REST — edit `plan.md` secara langsung dan jalankan ulang. Rencana tersebut adalah kontrak antara Anda dan agen.

### Implementasikan (jika waktu memungkinkan)

```
/conductor:implement
```

> **Eksplorasi sesuai permintaan:** Agen menavigasi basis kode Anda melalui alat — membaca file, melacak impor, dan mereferensikan silang pola saat mengimplementasikan setiap langkah dari rencana. File konteks seperti `GEMINI.md` dan spesifikasi Conductor dimuat bersama file yang sedang dikerjakan secara aktif oleh agen.

### Periksa Status

```
What's the current status on all active Conductor tracks?
```

---
## 1.4 — Ekstensi dan Server MCP (10 menit)

### Gambaran Umum Ekstensi

Ekstensi mengemas skill, sub-agen, hook, kebijakan, dan server MCP ke dalam unit yang dapat diinstal:

```
/extensions list
```

### Server MCP: Menghubungkan Alat Eksternal

MCP (Model Context Protocol) menghubungkan Gemini CLI ke sumber data dan alat eksternal:

```bash
# Check your MCP configuration
cat .gemini/settings.json
```

settings.json menyertakan server MCP GitHub. Saat dikonfigurasi dengan `GITHUB_TOKEN`, agen dapat:
- Membaca repositori, issue, dan PR
- Membuat issue dan komentar
- Membuka pull request

### Coba Prompt yang Terhubung

```
List the open issues in this repository using the GitHub MCP server.
```

### Isolasi Alat MCP untuk Sub-agen

Anda dapat membatasi alat MCP mana yang dapat diakses oleh sub-agen:

```json
{
  "mcpServers": {
    "bigquery": {
      "includeTools": ["query", "list_tables"],
      "excludeTools": ["delete_table", "drop_dataset"]
    }
  }
}
```

> **Nilai perusahaan:** Sub-agen `db-analyst` mendapatkan akses BigQuery hanya-baca. Sub-agen ini dapat melakukan kueri dan membuat daftar tabel, tetapi tidak akan pernah bisa menghapus data. Isolasi alat adalah tata kelola pada tingkat agen.

---
## 1.5 — Tata Kelola dan Mesin Kebijakan (10 menit)

### Mesin Kebijakan

Kebijakan adalah pagar pengaman-sebagai-kode yang ditulis dalam TOML:

```bash
cat .gemini/policies/team-guardrails.toml
```

### Aturan Kebijakan Beraksi

Contoh kebijakan:
- **Menolak** pembacaan `.env`, `.ssh`, dan file kredensial
- **Menolak** perintah shell destruktif (`rm -rf`, `curl`)
- **Mengizinkan** agen implementer untuk menjalankan `npm test` dan `npm run lint`
- **Mengatur default** untuk hal lainnya ke `ask_user` (memerlukan persetujuan manusia)

### Uji Kebijakan

```
Read the contents of the .env file in this project.
```

> **Diharapkan:** Agen harus diblokir oleh mesin kebijakan. Anda akan melihat pesan penolakan yang menjelaskan alasannya.

### Sistem Kebijakan 5 Tingkat

Kebijakan diterapkan secara berjenjang dalam urutan prioritas:

```
Default → Extension → Workspace → User → Admin (highest)
```

Kebijakan admin (ditetapkan pada tingkat sistem) menimpa semua hal lainnya. Ini adalah cara perusahaan menerapkan pagar pengaman di seluruh organisasi.

> **Catatan:** Tingkat Workspace saat ini dinonaktifkan di sumber CLI. Lihat [Referensi Mesin Kebijakan](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md) untuk status tingkat terbaru.

### Hook Beraksi

Hook yang dikonfigurasi dalam `settings.json` sudah aktif:

1. **SessionStart → session-context**: Menyuntikkan nama cabang Anda dan jumlah file kotor (dirty file) pada awal sesi ini
2. **BeforeTool → secret-scanner**: Mengawasi setiap penulisan file untuk kredensial yang di-hardcode
3. **BeforeTool → git-context**: Menyuntikkan riwayat git terbaru sebelum modifikasi file
4. **AfterTool → test-nudge**: Mengingatkan agen untuk mempertimbangkan menjalankan pengujian

Periksa status hook:

```
/hooks panel
```

> **Filosofi desain:** Hook ini adalah penyuntik konteks dan pengarah model yang ringan — bukan pelari pengujian yang berat. Mereka menambahkan latensi total <200ms dan meningkatkan kualitas keputusan agen tanpa membebani sistem.

### Konfigurasi Enterprise

Untuk pembatasan alat di seluruh organisasi, gunakan [Mesin Kebijakan](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md) dengan kebijakan TOML tingkat admin. Untuk panduan praktis, lihat [Mengamankan Gemini CLI dengan Mesin Kebijakan](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy).

**Kebijakan tingkat admin** (diterapkan melalui MDM ke `/etc/gemini-cli/policies/`) menegakkan keamanan di seluruh organisasi yang tidak dapat ditimpa oleh pengembang individu:

```toml
# /etc/gemini-cli/policies/admin.toml

# Block network exfiltration tools
[[rule]]
toolName = "run_shell_command"
commandPrefix = ["curl", "wget", "nc", "netcat", "nmap", "ssh"]
decision = "deny"
priority = 900
deny_message = "Network commands are blocked to prevent data exfiltration."

# Block reading sensitive system files and secrets
[[rule]]
toolName = ["read_file", "grep_search", "glob"]
argsPattern = "(\\.env|/etc/shadow|/etc/passwd|\\.ssh/|\\.aws/)"
decision = "deny"
priority = 900
deny_message = "Access to system secrets and environment variables is prohibited."

# Block privilege escalation
[[rule]]
toolName = "run_shell_command"
commandPrefix = ["sudo", "su ", "chmod 777", "chown "]
decision = "deny"
priority = 950
deny_message = "Agents are not permitted to elevate privileges."
```

**Kebijakan tingkat Workspace** (di-check in ke repo Anda di `.gemini/policies/dev.toml`) menetapkan default tingkat tim:

```toml
# .gemini/policies/dev.toml

# Allow the CLI to read freely to build context
[[rule]]
toolName = ["read_file", "grep_search", "glob"]
decision = "allow"
priority = 100

# Auto-approve safe local commands
[[rule]]
toolName = "run_shell_command"
commandPrefix = ["npm test", "git diff"]
decision = "allow"
priority = 100

# Explicitly prompt for file modifications
[[rule]]
toolName = ["write_file", "replace"]
decision = "ask_user"
priority = 100

# Block destructive commands
[[rule]]
toolName = "run_shell_command"
commandRegex = "^rm -rf /"
decision = "deny"
priority = 999
deny_message = "Blocked by policy: Destructive root commands are prohibited."
```

> **Memeriksa kebijakan aktif:** Gunakan `/policies list` di CLI untuk melihat semua aturan yang mengatur sesi Anda, termasuk keputusannya, tingkat prioritas, dan file sumbernya.

Untuk penegakan autentikasi enterprise, gunakan `security.auth.enforcedType` di `settings.json` tingkat sistem (lihat [Panduan Enterprise](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md)).

### Sandboxing

Gemini CLI mendukung [eksekusi sandbox](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/sandbox.md):
- **Sandbox Docker**: Menjalankan perintah shell dalam kontainer yang terisolasi
- **Sandbox macOS**: Menggunakan sandboxing macOS untuk membatasi akses sistem file

```bash
# Launch with sandboxing enabled
gemini --sandbox
```

---
## 1.6 — Manajemen Sesi (5 menit)

### Melanjutkan Sesi Sebelumnya

```
/resume
```

Menampilkan daftar sesi terbaru. Pilih salah satu untuk melanjutkan dari tempat Anda terakhir berhenti.

### Kembali ke Status Sebelumnya

```
/rewind
```

Menampilkan linimasa perubahan di sesi saat ini. Pilih satu titik untuk kembali ke status tersebut.

### Perintah Kustom

```
/commands
```

Menampilkan perintah kustom yang tersedia. Anda dapat menentukan perintah Anda sendiri di `.gemini/commands/`.

---
## Ringkasan: Apa yang Anda Pelajari

| Fitur | Apa yang Dilakukannya |
|---|---|
| **Hierarki GEMINI.md** | Mengodekan konvensi proyek di setiap tingkat — agen mengikutinya secara otomatis |
| **Penemuan konteks JIT** | Hanya memuat file konteks yang relevan untuk tugas saat ini |
| **Memori** | Mempertahankan pengetahuan di seluruh sesi |
| **Conductor** | Pengembangan berbasis spesifikasi dengan rencana persisten dan pelacakan kemajuan |
| **Ekstensi** | Paket skill, agen, hook, dan kebijakan yang dapat diinstal |
| **Server MCP** | Terhubung ke alat eksternal (GitHub, BigQuery, Jira) |
| **Mesin kebijakan** | Pagar pengaman sebagai kode di TOML — deny, allow, atau ask_user |
| **Hook** | Injeksi konteks ringan dan pengarahan model pada peristiwa siklus hidup agen |
| **Sandboxing** | Eksekusi terisolasi untuk lingkungan yang tidak tepercaya |

---
## 1.7 — Agen Kustom untuk SDLC Penuh (20 menit)

> **Untuk pengguna mahir dan peserta yang kembali.** Bagian ini melampaui pembuatan kode untuk mencakup **siklus hidup pengembangan perangkat lunak penuh** — ulasan, dokumentasi, kepatuhan, dan manajemen rilis. Setiap agen dapat digunakan secara independen. Anda dapat mulai dari titik mana pun.

### Agen Bawaan

Gemini CLI dilengkapi dengan agen default yang dapat Anda gunakan segera. Daftarkan agen tersebut dengan:

```
/agents
```

| Agen | Tujuan | Kapan Digunakan |
|---|---|---|
| **`generalist`** | Agen umum dengan akses alat penuh | Tugas dengan volume tinggi atau yang membutuhkan banyak giliran |
| **`codebase_investigator`** | Pemetaan arsitektur & analisis dependensi | "Petakan bagaimana alur autentikasi di aplikasi ini" |
| **`cli_help`** | Pakar dokumentasi Gemini CLI | "Bagaimana cara mengonfigurasi isolasi alat MCP?" |

Gunakan sintaks `@agent` untuk mendelegasikan secara eksplisit:

```
@codebase_investigator Map the complete data flow from the React 
product page through Redux, to the Express API, to the MongoDB model.
```

> **Mengapa ini penting:** Investigator beroperasi dalam mode hanya-baca dengan konteks yang terfokus. Agen ini tidak akan secara tidak sengaja memodifikasi file saat memetakan arsitektur Anda. Agen utama kemudian menggunakan peta tersebut untuk merencanakan implementasi.

---

### Membangun Agen Kustom

Agen kustom adalah file Markdown dengan frontmatter YAML, yang diletakkan ke dalam `.gemini/agents/`. Setiap agen mendapatkan:

- Sebuah **nama** yang Anda panggil dengan `@agent-name`
- Sebuah **deskripsi** yang digunakan CLI untuk perutean otomatis
- Sebuah **daftar izin alat** yang mengontrol apa yang dapat diakses oleh agen
- Sebuah **prompt sistem** yang mendefinisikan keahlian dan format outputnya

> **Prinsip desain utama:** Pisahkan pemikir dari pelaku. Agen hanya-baca untuk penelitian dan ulasan. Agen dengan akses tulis untuk implementasi. Jangan pernah mencampuradukkan investigasi dan mutasi dalam konteks yang sama.

Contoh-contoh di bawah ini menunjukkan bahwa Gemini CLI bukan sekadar pembuat kode — ini adalah **platform SDLC penuh** yang mencakup ulasan, dokumentasi, kepatuhan, dan manajemen rilis.

---

### Agen 1: Peninjau PR

Agen hanya-baca yang meninjau perubahan kode untuk kualitas, bug, dan pelanggaran gaya penulisan.

```bash
cp samples/agents/pr-reviewer.md .gemini/agents/
```

```markdown
<!-- .gemini/agents/pr-reviewer.md -->
---
name: pr-reviewer
description: Review code changes for quality, bugs, and style violations.
model: gemini-3.1-pro-preview
tools:
  - read_file
  - glob
  - grep_search
  - run_shell_command
---

You are a senior engineer conducting a pull request review.

## Review Checklist
1. **Correctness**: Does the code do what it claims?
2. **Edge Cases**: What happens with empty inputs, nulls, boundary values?
3. **Style Consistency**: Does it match the project's existing patterns?
4. **Test Coverage**: Are there tests for happy path AND error cases?
5. **Security**: User input passed to DB queries unparameterized?

## Output Format
For each finding:
- **File:Line** — exact location
- **Severity** — Critical / Suggestion / Nit
- **Issue** — one-sentence description
- **Suggestion** — concrete code improvement

Keep feedback constructive. Acknowledge good patterns when you see them.
```

**Coba ini:**

```
@pr-reviewer Review all files changed in the last commit
```

> **Otomatiskan di CI/CD:** Untuk ulasan PR otomatis pada setiap pull request, gunakan GitHub Action resmi [`google-github-actions/run-gemini-cli`](https://github.com/google-github-actions/run-gemini-cli). Instal dari CLI dengan `/setup-github` — ini mengonfigurasi file alur kerja, penangan pengiriman (dispatch handler), dan triase masalah secara otomatis. Lihat [`samples/cicd/gemini-pr-review.yml`](../../samples/cicd/gemini-pr-review.yml) untuk contoh yang berfungsi.

---

### Agen 2: Penulis Dokumen

Menghasilkan dokumentasi API, README, dan komentar kode dari kode sumber. Hanya-baca — agen ini tidak akan pernah dapat memodifikasi file Anda.

```bash
cp samples/agents/doc-writer.md .gemini/agents/
```

```markdown
<!-- .gemini/agents/doc-writer.md -->
---
name: doc-writer
description: Generate API documentation and README sections from source code.
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - glob
  - grep_search
---

You are a technical writer generating documentation from source code.
- Read the actual source — never guess at API signatures
- Document: endpoint, method, auth, request body, response format
- Add usage examples with curl or fetch
- Flag undocumented endpoints or missing error handling
```

**Coba ini:**

```
@doc-writer Generate API documentation for all endpoints in backend/routes/
```

> **Nilai loop luar:** Ini menggantikan berjam-jam pekerjaan dokumentasi manual. Jalankan setelah setiap sprint untuk menjaga dokumen tetap mutakhir.

---

### Agen 3: Analisis Keamanan (Ekstensi Resmi)

Daripada membangun pemeriksa kepatuhan kustom, instal **[Ekstensi Keamanan](https://github.com/gemini-cli-extensions/security) resmi** — sebuah ekstensi yang dikelola Google dengan mesin SAST penuh, pemindaian dependensi melalui [OSV-Scanner](https://github.com/google/osv-scanner), dan performa yang telah diuji tolak ukurnya (presisi 90%, perolehan 93% terhadap CVE nyata).

```bash
# Install the Security Extension (requires Gemini CLI v0.4.0+)
gemini extensions install https://github.com/gemini-cli-extensions/security
```

**Analisis perubahan kode untuk kerentanan:**

```
/security:analyze
```

Ekstensi ini menjalankan analisis SAST dua tahap pada diff cabang Anda saat ini, memeriksa:
- Rahasia yang di-hardcode dan kunci API
- Injeksi SQL, XSS, SSRF, dan injeksi perintah
- Kontrol akses yang rusak dan bypass autentikasi
- Eksposur PII dalam log dan respons API
- Masalah keamanan LLM (injeksi prompt, penggunaan alat yang tidak aman)

**Pindai dependensi untuk CVE yang diketahui:**

```
/security:scan-deps
```

Ini menggunakan [OSV-Scanner](https://github.com/google/osv-scanner) untuk mereferensikan silang dependensi Anda terhadap [osv.dev](https://osv.dev), basis data kerentanan sumber terbuka milik Google.

**Sesuaikan cakupan:**

```
/security:analyze Analyze all the source code under the backend/ folder. Skip tests and config files.
```

> **Nilai perusahaan:** Ekstensi ini dilengkapi dengan skill untuk pembuatan PoC (`poc`), penambalan otomatis (`security-patcher`), dan daftar izin kerentanan. Ini siap produksi sejak awal — tidak perlu membangun agen kepatuhan kustom.

---

### Agen 4: Penyusun Catatan Rilis

Membaca riwayat git dan file yang diubah untuk menghasilkan catatan rilis yang terstruktur dan ramah pemangku kepentingan.

```bash
cp samples/agents/release-notes-drafter.md .gemini/agents/
```

```markdown
<!-- .gemini/agents/release-notes-drafter.md -->
---
name: release-notes-drafter
description: Generate release notes from git history and source changes.
model: gemini-3.1-flash-lite-preview
tools:
  - run_shell_command
  - read_file
  - glob
  - grep_search
---

You are a release engineer. Process:
1. Run `git log --oneline -20` for recent commits
2. Group by: Features, Bug Fixes, Breaking Changes, Dependencies
3. Read changed files to understand actual impact
4. Write user-facing descriptions, not developer jargon
```

**Coba ini:**

```
@release-notes-drafter Write release notes for the last 10 commits
```

> **Nilai loop luar:** Catatan rilis adalah salah satu tugas SDLC yang paling ditakuti. Agen ini membaca riwayat git DAN perubahan kode aktual untuk menghasilkan catatan yang masuk akal bagi manajer produk.

---

### Menggabungkan Agen: Pipeline Penuh

Kekuatan sebenarnya adalah menggabungkan agen ke dalam alur kerja. Setiap agen mendapatkan **konteks yang segar dan terfokus** — tidak ada satu agen pun yang mengakumulasi riwayat percakapan penuh:

```
# Step 1: Investigate (read-only, fresh context)
@codebase_investigator Map the authentication flow in this application

# Step 2: Implement (write access, fresh context)
Add a "forgot password" endpoint following the patterns described above

# Step 3: Review (read-only, fresh context)
@pr-reviewer Review the forgot-password implementation

# Step 4: Document (read-only, fresh context)
@doc-writer Update the API docs with the new endpoint

# Step 5: Audit (read-only, fresh context)
@compliance-checker Check the new code for hardcoded secrets or PII
```

> **Mengapa ini berhasil:** Setiap langkah dimulai dengan konteks bersih yang terfokus pada pekerjaan spesifiknya. Investigator tidak membawa detail implementasi. Peninjau tidak membawa kebisingan investigasi. Ini adalah prinsip di balik setiap alur kerja AI berkinerja tinggi.

---

### Mempelajari Lebih Dalam

Untuk teknik lanjutan tambahan — disiplin prompt, loop verifikasi, rekayasa konteks, dan pengembangan paralel — lihat halaman **[Pola Lanjutan](advanced-patterns.md)**:

- [Keahlian Prompt: Tujuan vs. Instruksi](advanced-patterns.md#prompting-craft-goals-vs-instructions)
- [Disiplin Konteks](advanced-patterns.md#context-discipline)
- [Loop Verifikasi](advanced-patterns.md#verification-loops)
- [Pengembangan Paralel dengan Worktree](advanced-patterns.md#parallel-development-with-worktrees)
- [Orkestrasi Multi-Agen](advanced-patterns.md#multi-agent-orchestration)

---
## Part 2 — Outer Loop: Beyond Code Writing

> **Duration:** ~20 minutes (self-paced)
> **Prerequisites:** Complete Part 1 above. Familiarity with custom agents (§1.5) and Conductor (§1.4) is helpful.

The exercises above focused on the **inner loop** — writing, testing, and reviewing code. But agents can also handle the **outer loop** — the workflows that surround code: architecture decisions, developer onboarding, dependency auditing, and CI pipeline automation.

In Part 1, you already built the building blocks: subagents for specialized roles, Conductor for spec-driven development, and a compliance checker for policy enforcement. Part 2 shows how to promote these patterns into outer loop workflows.

---

### 2.1 — ADR Generator with Subagent-Driven Development

Architecture Decision Records (ADRs) capture *why* a technical choice was made. Manually writing them is tedious enough that teams skip them entirely. With the subagent-driven development (SDD) methodology from the [superpowers extension](extensions-ecosystem.md#exercise-1-superpowers--methodology-as-extension), you can generate ADRs automatically from code changes.

**Setup:**

```bash
# Install superpowers if you haven't already
gemini extensions install https://github.com/obra/superpowers
```

**Create an ADR agent:**

Create `.gemini/agents/adr-writer.md`:

```markdown
---
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - list_directory
  - run_shell_command
---
You are an Architecture Decision Record (ADR) writer. When given a set 
of code changes:

1. Run `git diff main...HEAD` to understand what changed
2. Analyze the architectural significance — what decision was made?
3. Generate an ADR in this format:

## ADR-{number}: {title}

**Status:** Proposed
**Date:** {today}
**Context:** What problem or requirement drove this decision?
**Decision:** What was decided and why?
**Consequences:** What are the tradeoffs? What becomes easier? Harder?
**Alternatives Considered:** What other approaches were evaluated?

Focus on the *why*, not the *what*. The code shows *what* changed — 
the ADR explains *why* it was the right choice.
```

**Use it:**

Make a code change (add a feature, change an architecture pattern), then:

```
@adr-writer Generate an ADR for the changes on this branch
```

**With SDD two-stage review:**

```
Use subagent-driven development to generate an ADR for my current branch 
changes. The first subagent should draft the ADR. The second should review 
it for completeness — does it explain the *why*, not just the *what*?
```

> **Why this matters:** ADRs are one of the most valuable artifacts a team can produce — and one of the most neglected. An agent that generates a draft ADR from every PR reduces the barrier from "write a document" to "review a document." Teams that adopt this pattern build an architectural history automatically.

---

### 2.2 — Developer Onboarding Agent

New developers spend days mapping a codebase before they can contribute. An onboarding agent does this mapping in minutes.

**Create the agent:**

Create `.gemini/agents/onboarding-guide.md`:

```markdown
---
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - list_directory
  - grep_search
---
You are a codebase onboarding guide. When a new developer asks about 
this codebase, help them understand:

1. **Architecture:** What frameworks and patterns are used? 
   (Check package.json, project structure, GEMINI.md)
2. **Data flow:** How do requests move through the system? 
   (Trace from routes → controllers → models → database)
3. **Authentication:** How does auth work? 
   (Find auth middleware, token handling, session management)
4. **Testing:** How are tests organized? What's the testing strategy?
5. **Deployment:** How does the app get deployed? 
   (Check CI/CD configs, Dockerfiles, deployment scripts)

Always cite specific files and line numbers. Don't summarize — 
show the actual code paths.
```

**Try it:**

```
@onboarding-guide How does authentication work in this application?
```

```
@onboarding-guide What's the testing strategy? Show me an example test 
and explain the patterns I should follow.
```

```
@onboarding-guide I need to add a new API endpoint. Walk me through the 
pattern — which files do I create and in what order?
```

> **Key insight:** Compare this to reading the README and hoping it's up-to-date. The agent traces actual code paths, not documentation that may have drifted. This is the `@codebase_investigator` pattern from Part 1 (§1.5) — but specialized for onboarding questions and persisted as a reusable agent.

---

### 2.3 — Security Analysis in CI Pipelines

In Part 1, you installed the [Security Extension](https://github.com/gemini-cli-extensions/security) for local analysis. The next step is promoting it into CI — automated security analysis on every pull request.

#### The Pattern: Security Extension in GitHub Actions

The Security Extension ships with a ready-to-use GitHub Actions workflow. Copy it directly:

```bash
# Copy the extension's CI workflow into your repo
cp $(gemini extensions path security)/.github/workflows/gemini-review.yml \
  .github/workflows/security-review.yml
```

Or reference the [official workflow template](https://github.com/gemini-cli-extensions/security/blob/main/.github/workflows/gemini-review.yml) and add it manually. The workflow:

1. Installs the Security Extension into the CI runner
2. Runs `/security:analyze` on the PR diff
3. Runs `/security:scan-deps` for dependency vulnerabilities
4. Posts findings as PR comments

**Why the Security Extension beats hand-written prompts:**

| Hand-Written Audit Prompt | Security Extension |
|---|---|
| Free-form prompt — results vary per run | Structured two-pass SAST engine with consistent methodology |
| No vulnerability taxonomy | 7 categories, 20+ vuln types, severity rubric (Critical/High/Medium/Low) |
| No dependency scanning | Integrated OSV-Scanner against Google's vulnerability database |
| No remediation workflow | Built-in PoC generation and auto-patching skills |
| No allowlisting | Persistent `.gemini_security/vuln_allowlist.txt` for accepted risks |

> **This is the CI pattern from slide 18** but using a production-grade, benchmarked extension (90% precision, 93% recall) instead of a hand-written prompt. The same `/security:analyze` command you ran locally in §1.7 now runs automatically on every PR.

---

### Connecting the Dots

Part 1 gave you the building blocks: subagents, Conductor, policy engine, hooks. Part 2 showed how to promote these patterns into the outer loop:

| Building Block (Part 1) | Outer Loop Application (Part 2) |
|---|---|
| Custom subagent (§1.5) | ADR writer, onboarding guide |
| Security Extension (§1.7) | CI security analysis pipeline |
| Conductor spec-to-code (§1.4) | PRD → ADR → implementation pipeline |
| Headless mode (referenced in UC3) | GitHub Action automation |

The pattern is always the same: **build locally → validate → promote to CI/CD → scale across the org.** The agent that helps one developer becomes the automation that helps the entire team.

---
## Ringkasan: Apa yang Telah Anda Pelajari

| Fitur | Apa yang Dilakukannya |
|---|---|
| **Hierarki GEMINI.md** | Mengenkode konvensi proyek di setiap tingkat — agen mengikutinya secara otomatis |
| **Penemuan konteks JIT** | Hanya memuat file konteks yang relevan untuk tugas saat ini |
| **Memori** | Mempertahankan pengetahuan di seluruh sesi |
| **Conductor** | Pengembangan berbasis spesifikasi dengan rencana persisten dan pelacakan kemajuan |
| **Ekstensi** | Paket skill, agen, hook, dan kebijakan yang dapat diinstal |
| **Server MCP** | Terhubung ke alat eksternal (GitHub, BigQuery, Jira) |
| **Mesin kebijakan** | Pagar pengaman sebagai kode (guardrails-as-code) di TOML — deny, allow, atau ask_user |
| **Hook** | Injeksi konteks yang ringan dan pengarahan model pada peristiwa siklus hidup agen |
| **Sandboxing** | Eksekusi terisolasi untuk lingkungan yang tidak tepercaya |
| **Agen kustom** | Agen khusus untuk peninjauan, dokumentasi, catatan rilis — bukan hanya pengkodean |
| **Ekstensi Keamanan** | SAST resmi + pemindaian dependensi dengan pembuatan PoC dan penambalan otomatis |
| **Agen bawaan** | `generalist`, `codebase_investigator`, `cli_help` — pendelegasian tanpa pengaturan |
| **Pembuatan ADR** | Catatan keputusan arsitektur (ADR) yang digerakkan oleh sub-agen dari git diff |
| **Agen orientasi** | Pemetaan basis kode untuk pengembang baru — melacak jalur kode yang sebenarnya |
| **Pipeline keamanan CI** | Ekstensi Keamanan di GitHub Actions untuk analisis kerentanan otomatis |

---
## Langkah Selanjutnya

→ Lanjutkan ke **[Kasus Penggunaan 2: Modernisasi Kode Legacy](legacy-modernization.md)**

→ Jelajahi ekosistem ekstensi: **[Ekosistem Ekstensi](extensions-ecosystem.md)** — penemuan, instalasi, pembuatan, dan pola perusahaan

→ Untuk pengguna mahir: **[Pola Lanjutan](advanced-patterns.md)** — keahlian prompting, loop verifikasi, rekayasa konteks, dan pengembangan paralel
