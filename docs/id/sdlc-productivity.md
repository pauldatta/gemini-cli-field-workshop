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

Mulailah dengan sesuatu yang membuktikan bahwa agen dapat membaca basis kode Anda:

```
What is the tech stack of this project? List the main frameworks, 
database, and authentication mechanism.
```

> **Apa yang terjadi:** Agen membaca `package.json`, memindai struktur direktori, dan memetakan arsitektur. Gemini CLI menjelajahi basis kode Anda sesuai permintaan — membaca file, mencari pola, dan melacak dependensi menggunakan alat seperti `read_file`, `glob`, dan `grep_search` sesuai kebutuhan.

### Jelajahi Alat

```
/tools
```

Ini menunjukkan setiap alat yang dapat digunakan agen: operasi file, perintah shell, pencarian web, dan server MCP apa pun yang telah Anda konfigurasikan.

### Pintasan Utama

| Pintasan | Tindakan |
|---|---|
| `Tab` | Terima saran pengeditan |
| `Shift+Tab` | Beralih antar mode persetujuan |
| `Ctrl+G` | Buka editor eksternal (edit prompt atau rencana) |
| `Ctrl+C` | Batalkan operasi saat ini |
| `/stats` | Tampilkan penggunaan token untuk sesi ini |
| `/clear` | Bersihkan konteks dan mulai dari awal |

---
## 1.2 — Rekayasa Konteks dengan GEMINI.md (15 menit)

### Hierarki Konteks

Gemini CLI membaca file `GEMINI.md` pada berbagai tingkat, masing-masing menambahkan konteks yang lebih spesifik:

![Hierarki Konteks GEMINI.md](../assets/context-hierarchy.png)

> **Penemuan konteks JIT:** Agen hanya memuat file GEMINI.md yang relevan dengan file yang sedang dikerjakannya. Jika ia sedang mengedit `backend/controllers/productController.js`, ia memuat GEMINI.md proyek DAN GEMINI.md backend — tetapi bukan yang frontend.

### Memeriksa GEMINI.md Proyek

```bash
cat GEMINI.md
```

File ini (disalin dari [`samples/gemini-md/project-gemini.md`](../../samples/gemini-md/project-gemini.md) selama pengaturan) mendefinisikan:
- Aturan arsitektur (rute → pengontrol → model)
- Anti-pola (tanpa callback, tanpa kredensial yang di-hardcode)
- Standar pengujian

### Menguji Penegakan Konteks

Minta agen untuk melanggar aturan dan lihat apakah ia mengoreksi dirinya sendiri:

```
Add a new GET endpoint to fetch featured products. 
Put the database query logic directly in the route file.
```

> **Diharapkan:** Agen harus mengenali bahwa ini melanggar aturan GEMINI.md ("Tidak ada logika bisnis dalam file rute") dan sebagai gantinya membuat endpoint di pengontrol, dengan rute tipis yang mendelegasikan.

> **Menegakkan Aturan:** Meskipun `GEMINI.md` memberikan panduan yang kuat (Rekayasa Prompt), AI masih dapat sesekali berhalusinasi atau membuat kesalahan selama refaktor yang kompleks. Untuk membangun alur kerja yang benar-benar kuat, Anda harus memasangkan aturan berbasis prompt ini dengan linter deterministik (seperti `dependency-cruiser`) menggunakan CI/CD atau [Gemini CLI Hooks](https://geminicli.com/docs/hooks/). Lihat [Penegakan Deterministik](advanced-patterns.md#deterministic-enforcement) di panduan Pola Lanjutan untuk mengetahui cara mengaturnya.

### Menambahkan Konteks Backend

```bash
cat backend/GEMINI.md
```

Ini menambahkan aturan khusus backend tentang penanganan kesalahan, pola async, dan keamanan.

### Memori: Pengetahuan Persisten

Agen dapat mengingat hal-hal di seluruh sesi:

```
/memory show
```

Tambahkan pengetahuan khusus proyek:

```
/memory add "The ProShop app uses port 5000 for the backend API 
and port 3000 for the React dev server. MongoDB runs on default 
port 27017. Test database is 'proshop_test'."
```

Agen juga dapat menyimpan memori itu sendiri menggunakan alat `save_memory` — baik saat Anda secara eksplisit memintanya untuk mengingat sesuatu, atau secara otomatis jika Anda mengaktifkan `experimental.autoMemory` di [settings.json](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/auto-memory.md).

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
## 1.3 — Conductor: Build yang Mengutamakan Konteks (15 mnt)

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

> **Wawasan utama:** File-file ini sekarang menjadi sumber kebenaran (source of truth) untuk proyek Anda. File-file tersebut adalah Markdown, berada di repo Anda, di-commit dan ditinjau seperti kode lainnya. Saat Anda kembali besok — atau menyerahkan proyek ini kepada rekan kerja — AI akan melanjutkan tepat di mana Anda tinggalkan. Statusnya ada di dalam file, bukan di memori.

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

> **Lihat rencananya.** Rencana ini dipecah menjadi beberapa fase dengan tugas dan kotak centang tertentu. Fase 1: skema database. Fase 2: endpoint API. Fase 3: komponen frontend. Fase 4: pengujian. Agen mengikuti rencana ini secara berurutan, mencentang tugas saat berjalan.

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

Ekstensi memaketkan skill, sub-agen, hook, kebijakan, dan server MCP menjadi unit-unit yang dapat diinstal:

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
- Membaca repositori, isu, dan PR
- Membuat isu dan komentar
- Membuka pull request

### Mencoba Prompt yang Terhubung

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

> **Nilai perusahaan:** Sub-agen `db-analyst` mendapatkan akses BigQuery hanya-baca. Ia dapat melakukan kueri dan membuat daftar tabel, tetapi tidak akan pernah bisa menghapus data. Isolasi alat adalah tata kelola di tingkat agen.

---
## 1.5 — Tata Kelola dan Mesin Kebijakan (10 menit)

### Mesin Kebijakan

Kebijakan adalah pagar pengaman sebagai kode (guardrails-as-code) yang ditulis dalam TOML:

```bash
cat .gemini/policies/team-guardrails.toml
```

### Aturan Kebijakan dalam Praktik

Contoh kebijakan:
- **Menolak** pembacaan file `.env`, `.ssh`, dan kredensial
- **Menolak** perintah shell yang merusak (`rm -rf`, `curl`)
- **Mengizinkan** agen implementer untuk menjalankan `npm test` dan `npm run lint`
- **Mengatur default** untuk hal lainnya ke `ask_user` (memerlukan persetujuan manusia)

### Uji Kebijakan

```
Read the contents of the .env file in this project.
```

> **Diharapkan:** Agen harus diblokir oleh mesin kebijakan. Anda akan melihat pesan penolakan yang menjelaskan alasannya.

### Sistem Kebijakan 5 Tingkat

Kebijakan menurun dalam urutan prioritas:

```
Default → Extension → Workspace → User → Admin (highest)
```

Kebijakan admin (ditetapkan pada tingkat sistem) mengesampingkan semua hal lainnya. Ini adalah cara perusahaan menegakkan pagar pengaman di seluruh organisasi.

> **Catatan:** Tingkat Workspace saat ini dinonaktifkan di sumber CLI. Lihat [Referensi Mesin Kebijakan](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md) untuk status tingkat terbaru.

### Hook dalam Praktik

Hook yang dikonfigurasi di `settings.json` sudah aktif:

1. **SessionStart → session-context**: Menyuntikkan nama cabang dan jumlah file dirty Anda pada awal sesi ini
2. **BeforeTool → secret-scanner**: Mengawasi setiap penulisan file untuk mencari kredensial yang di-hardcode
3. **BeforeTool → git-context**: Menyuntikkan riwayat git terbaru sebelum modifikasi file
4. **AfterTool → test-nudge**: Mengingatkan agen untuk mempertimbangkan menjalankan pengujian

Periksa status hook:

```
/hooks panel
```

> **Filosofi desain:** Hook ini adalah penyuntik konteks dan pengarah model yang ringan — bukan pelari pengujian yang berat. Mereka menambahkan latensi total <200ms dan meningkatkan kualitas keputusan agen tanpa membebani sistem.

### Konfigurasi Enterprise

Untuk pembatasan alat di seluruh organisasi, gunakan [Mesin Kebijakan](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md) dengan kebijakan TOML tingkat admin. Untuk panduan praktis, lihat [Amankan Gemini CLI dengan Mesin Kebijakan](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy).

**Kebijakan tingkat admin** (disebarkan melalui MDM ke `/etc/gemini-cli/policies/`) menegakkan keamanan di seluruh organisasi yang tidak dapat dikesampingkan oleh pengembang individu:

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

> **Memeriksa kebijakan aktif:** Gunakan `/policies list` di CLI untuk melihat semua aturan yang mengatur sesi Anda, termasuk keputusannya, tingkat prioritas, dan file sumber.

Untuk penegakan autentikasi enterprise, gunakan `security.auth.enforcedType` di `settings.json` tingkat sistem (lihat [Panduan Enterprise](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md)).

### Sandbox

Gemini CLI mendukung [eksekusi sandbox](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/sandbox.md):
- **Sandbox Docker**: Menjalankan perintah shell dalam wadah (container) yang terisolasi
- **Sandbox macOS**: Menggunakan sandbox macOS untuk membatasi akses sistem file

```bash
# Launch with sandboxing enabled
gemini --sandbox
```

---
## 1.6 — Manajemen Sesi (5 menit)

### Lanjutkan Sesi Sebelumnya

```
/resume
```

Menampilkan daftar sesi terbaru. Pilih salah satu untuk melanjutkan dari tempat Anda terakhir kali berhenti.

### Mundur ke Status Sebelumnya

```
/rewind
```

Menampilkan linimasa perubahan dalam sesi saat ini. Pilih sebuah titik untuk kembali ke keadaan tersebut.

### Perintah Kustom

```
/commands
```

Menampilkan perintah kustom yang tersedia. Anda dapat menentukan perintah Anda sendiri di `.gemini/commands/`.

---
## Ringkasan: Apa yang Telah Anda Pelajari

| Fitur | Apa yang Dilakukannya |
|---|---|
| **Hierarki GEMINI.md** | Mengenkode konvensi proyek di setiap tingkat — agen mengikutinya secara otomatis |
| **Penemuan konteks JIT** | Hanya memuat file konteks yang relevan untuk tugas saat ini |
| **Memori** | Mempertahankan pengetahuan di seluruh sesi |
| **Conductor** | Pengembangan berbasis spesifikasi dengan rencana yang persisten dan pelacakan kemajuan |
| **Ekstensi** | Paket skill, agen, hook, dan kebijakan yang dapat diinstal |
| **Server MCP** | Terhubung ke alat eksternal (GitHub, BigQuery, Jira) |
| **Mesin kebijakan** | Pagar pengaman sebagai kode dalam TOML — deny, allow, atau ask_user |
| **Hook** | Injeksi konteks yang ringan dan pengarahan model pada peristiwa siklus hidup agen |
| **Sandboxing** | Eksekusi terisolasi untuk lingkungan yang tidak tepercaya |

---
## 1.7 — Agen Kustom untuk SDLC Penuh (20 mnt)

> **Untuk pengguna mahir dan peserta yang kembali.** Bagian ini melampaui pembuatan kode untuk mencakup **siklus hidup pengembangan perangkat lunak penuh** — ulasan, dokumentasi, kepatuhan, dan manajemen rilis. Setiap agen dapat digunakan secara independen. Mulailah dari titik mana pun.

### Agen Bawaan

Gemini CLI dilengkapi dengan agen default yang dapat Anda gunakan segera. Daftarkan dengan:

```
/agents
```

| Agen | Tujuan | Kapan Digunakan |
|---|---|---|
| **`generalist`** | Agen umum dengan akses alat penuh | Tugas bervolume tinggi atau intensif giliran |
| **`codebase_investigator`** | Pemetaan arsitektur & analisis dependensi | "Petakan bagaimana alur autentikasi melalui aplikasi ini" |
| **`cli_help`** | Pakar dokumentasi Gemini CLI | "Bagaimana cara mengonfigurasi isolasi alat MCP?" |

Gunakan sintaks `@agent` untuk mendelegasikan secara eksplisit:

```
@codebase_investigator Map the complete data flow from the React 
product page through Redux, to the Express API, to the MongoDB model.
```

> **Mengapa ini penting:** Penyelidik beroperasi dalam mode hanya-baca dengan konteks terfokus. Ia tidak akan secara tidak sengaja memodifikasi file saat memetakan arsitektur Anda. Agen utama kemudian menggunakan peta tersebut untuk merencanakan implementasi.

---

### Membangun Agen Kustom

Agen kustom adalah file Markdown dengan frontmatter YAML, yang diletakkan ke dalam `.gemini/agents/`. Setiap agen mendapatkan:

- Sebuah **nama** yang Anda panggil dengan `@agent-name`
- Sebuah **deskripsi** yang digunakan CLI untuk perutean otomatis
- Sebuah **daftar izin alat** yang mengontrol apa yang dapat diakses oleh agen
- Sebuah **prompt sistem** yang mendefinisikan keahlian dan format outputnya

> **Prinsip desain utama:** Pisahkan pemikir dari pelaku. Agen hanya-baca untuk penelitian dan ulasan. Agen akses-tulis untuk implementasi. Jangan pernah mencampuradukkan investigasi dan mutasi dalam konteks yang sama.

Contoh-contoh di bawah ini menunjukkan bahwa Gemini CLI bukan sekadar pembuat kode — ini adalah **platform SDLC penuh** yang mencakup ulasan, dokumentasi, kepatuhan, dan manajemen rilis.

---

### Agen 1: Peninjau PR

Agen hanya-baca yang meninjau perubahan kode untuk kualitas, bug, dan pelanggaran gaya.

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

**Cobalah:**

```
@pr-reviewer Review all files changed in the last commit
```

> **Otomatiskan di CI/CD:** Untuk ulasan PR otomatis pada setiap pull request, gunakan GitHub Action resmi [`google-github-actions/run-gemini-cli`](https://github.com/google-github-actions/run-gemini-cli). Instal dari CLI dengan `/setup-github` — ini mengonfigurasi file alur kerja, penangan pengiriman (dispatch handler), dan triase masalah secara otomatis. Lihat [`samples/cicd/gemini-pr-review.yml`](../../samples/cicd/gemini-pr-review.yml) untuk contoh yang berfungsi.

---

### Agen 2: Penulis Dokumen

Menghasilkan dokumentasi API, README, dan komentar kode dari kode sumber. Hanya-baca — ia tidak akan pernah dapat memodifikasi file Anda.

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

**Cobalah:**

```
@doc-writer Generate API documentation for all endpoints in backend/routes/
```

> **Nilai loop luar:** Ini menggantikan berjam-jam pekerjaan dokumentasi manual. Jalankan setelah setiap sprint untuk menjaga dokumen tetap mutakhir.

---

### Agen 3: Analisis Keamanan (Ekstensi Resmi)

Daripada membangun pemeriksa kepatuhan kustom, instal **[Security Extension](https://github.com/gemini-cli-extensions/security) resmi** — sebuah ekstensi yang dikelola Google dengan mesin SAST penuh, pemindaian dependensi melalui [OSV-Scanner](https://github.com/google/osv-scanner), dan performa yang telah diuji tolak ukurnya (presisi 90%, perolehan 93% terhadap CVE nyata).

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
- Paparan PII dalam log dan respons API
- Masalah keamanan LLM (injeksi prompt, penggunaan alat yang tidak aman)

**Pindai dependensi untuk CVE yang diketahui:**

```
/security:scan-deps
```

Ini menggunakan [OSV-Scanner](https://github.com/google/osv-scanner) untuk merujuk silang dependensi Anda terhadap [osv.dev](https://osv.dev), basis data kerentanan sumber terbuka milik Google.

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

**Cobalah:**

```
@release-notes-drafter Write release notes for the last 10 commits
```

> **Nilai loop luar:** Catatan rilis adalah salah satu tugas SDLC yang paling ditakuti. Agen ini membaca riwayat git DAN perubahan kode aktual untuk menghasilkan catatan yang masuk akal bagi manajer produk.

---

### Menggabungkan Agen: Pipeline Penuh

Kekuatan sebenarnya adalah menggabungkan agen ke dalam sebuah alur kerja. Setiap agen mendapatkan **konteks yang segar dan terfokus** — tidak ada satu agen pun yang mengakumulasi riwayat percakapan penuh:

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

> **Mengapa ini berhasil:** Setiap langkah dimulai dengan konteks bersih yang terfokus pada pekerjaan spesifiknya. Penyelidik tidak membawa detail implementasi. Peninjau tidak membawa gangguan investigasi. Ini adalah prinsip di balik setiap alur kerja AI berkinerja tinggi.

---

### Melangkah Lebih Dalam

Untuk teknik lanjutan tambahan — disiplin prompt, loop verifikasi, rekayasa konteks, dan pengembangan paralel — lihat halaman **[Pola Lanjutan](advanced-patterns.md)**:

- [Keahlian Prompt: Tujuan vs. Instruksi](advanced-patterns.md#prompting-craft-goals-vs-instructions)
- [Disiplin Konteks](advanced-patterns.md#context-discipline)
- [Loop Verifikasi](advanced-patterns.md#verification-loops)
- [Pengembangan Paralel dengan Worktree](advanced-patterns.md#parallel-development-with-worktrees)
- [Orkestrasi Multi-Agen](advanced-patterns.md#multi-agent-orchestration)

---
## Bagian 2 — Loop Luar: Melampaui Penulisan Kode

> **Durasi:** ~20 menit (kecepatan mandiri)
> **Prasyarat:** Selesaikan Bagian 1 di atas. Keakraban dengan agen kustom (§1.5) dan Conductor (§1.4) akan sangat membantu.

Latihan di atas berfokus pada **loop dalam** — menulis, menguji, dan meninjau kode. Namun agen juga dapat menangani **loop luar** — alur kerja yang mengelilingi kode: keputusan arsitektur, orientasi pengembang, audit dependensi, dan otomatisasi pipeline CI.

Pada Bagian 1, Anda telah membangun blok bangunan: sub-agen untuk peran khusus, Conductor untuk pengembangan berbasis spesifikasi, dan pemeriksa kepatuhan untuk penegakan kebijakan. Bagian 2 menunjukkan cara mempromosikan pola-pola ini ke dalam alur kerja loop luar.

---

### 2.1 — Pembuat ADR dengan Pengembangan Berbasis Sub-agen

Architecture Decision Records (ADR) menangkap *mengapa* sebuah pilihan teknis dibuat. Menulisnya secara manual cukup membosankan sehingga tim sering kali melewatkannya sama sekali. Dengan metodologi pengembangan berbasis sub-agen (SDD) dari [ekstensi superpowers](extensions-ecosystem.md#exercise-1-superpowers--methodology-as-extension), Anda dapat menghasilkan ADR secara otomatis dari perubahan kode.

**Pengaturan:**

```bash
# Install superpowers if you haven't already
gemini extensions install https://github.com/obra/superpowers
```

**Buat agen ADR:**

Buat `.gemini/agents/adr-writer.md`:

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

**Gunakan:**

Lakukan perubahan kode (tambahkan fitur, ubah pola arsitektur), lalu:

```
@adr-writer Generate an ADR for the changes on this branch
```

**Dengan tinjauan dua tahap SDD:**

```
Use subagent-driven development to generate an ADR for my current branch 
changes. The first subagent should draft the ADR. The second should review 
it for completeness — does it explain the *why*, not just the *what*?
```

> **Mengapa ini penting:** ADR adalah salah satu artefak paling berharga yang dapat dihasilkan oleh sebuah tim — dan salah satu yang paling diabaikan. Sebuah agen yang menghasilkan draf ADR dari setiap PR mengurangi hambatan dari "menulis dokumen" menjadi "meninjau dokumen." Tim yang mengadopsi pola ini membangun sejarah arsitektur secara otomatis.

---

### 2.2 — Agen Orientasi Pengembang

Pengembang baru menghabiskan waktu berhari-hari untuk memetakan basis kode sebelum mereka dapat berkontribusi. Agen orientasi melakukan pemetaan ini dalam hitungan menit.

**Buat agen:**

Buat `.gemini/agents/onboarding-guide.md`:

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

**Coba:**

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

> **Wawasan utama:** Bandingkan ini dengan membaca README dan berharap itu mutakhir. Agen melacak jalur kode yang sebenarnya, bukan dokumentasi yang mungkin telah menyimpang. Ini adalah pola `@codebase_investigator` dari Bagian 1 (§1.5) — tetapi dikhususkan untuk pertanyaan orientasi dan dipertahankan sebagai agen yang dapat digunakan kembali.

---

### 2.3 — Analisis Keamanan dalam Pipeline CI

Pada Bagian 1, Anda menginstal [Ekstensi Keamanan](https://github.com/gemini-cli-extensions/security) untuk analisis lokal. Langkah selanjutnya adalah mempromosikannya ke dalam CI — analisis keamanan otomatis pada setiap pull request.

#### Pola: Ekstensi Keamanan di GitHub Actions

Ekstensi Keamanan dilengkapi dengan alur kerja GitHub Actions yang siap pakai. Salin secara langsung:

```bash
# Copy the extension's CI workflow into your repo
cp $(gemini extensions path security)/.github/workflows/gemini-review.yml \
  .github/workflows/security-review.yml
```

Atau rujuk [templat alur kerja resmi](https://github.com/gemini-cli-extensions/security/blob/main/.github/workflows/gemini-review.yml) dan tambahkan secara manual. Alur kerja tersebut:

1. Menginstal Ekstensi Keamanan ke dalam runner CI
2. Menjalankan `/security:analyze` pada diff PR
3. Menjalankan `/security:scan-deps` untuk kerentanan dependensi
4. Memposting temuan sebagai komentar PR

**Mengapa Ekstensi Keamanan mengalahkan prompt yang ditulis tangan:**

| Prompt Audit Tulisan Tangan | Ekstensi Keamanan |
|---|---|
| Prompt bentuk bebas — hasil bervariasi setiap kali dijalankan | Mesin SAST dua tahap terstruktur dengan metodologi yang konsisten |
| Tidak ada taksonomi kerentanan | 7 kategori, 20+ jenis kerentanan, rubrik tingkat keparahan (Kritis/Tinggi/Sedang/Rendah) |
| Tidak ada pemindaian dependensi | OSV-Scanner terintegrasi terhadap basis data kerentanan Google |
| Tidak ada alur kerja remediasi | Pembuatan PoC bawaan dan skill penambalan otomatis |
| Tidak ada daftar izin (allowlisting) | `.gemini_security/vuln_allowlist.txt` persisten untuk risiko yang diterima |

> **Ini adalah pola CI dari slide 18** tetapi menggunakan ekstensi tingkat produksi yang telah di-benchmark (presisi 90%, recall 93%) alih-alih prompt yang ditulis tangan. Perintah `/security:analyze` yang sama yang Anda jalankan secara lokal di §1.7 sekarang berjalan secara otomatis pada setiap PR.

---

### Menghubungkan Titik-titik

Bagian 1 memberi Anda blok bangunan: sub-agen, Conductor, mesin kebijakan, hook. Bagian 2 menunjukkan cara mempromosikan pola-pola ini ke dalam loop luar:

| Blok Bangunan (Bagian 1) | Aplikasi Loop Luar (Bagian 2) |
|---|---|
| Sub-agen kustom (§1.5) | Penulis ADR, panduan orientasi |
| Ekstensi Keamanan (§1.7) | Pipeline analisis keamanan CI |
| Conductor spesifikasi-ke-kode (§1.4) | Pipeline PRD → ADR → implementasi |
| Mode headless (direferensikan di UC3) | Otomatisasi GitHub Action |

Polanya selalu sama: **bangun secara lokal → validasi → promosikan ke CI/CD → skalakan ke seluruh organisasi.** Agen yang membantu satu pengembang menjadi otomatisasi yang membantu seluruh tim.

---
## Ringkasan: Apa yang Telah Anda Pelajari

| Fitur | Apa yang Dilakukannya |
|---|---|
| **Hierarki GEMINI.md** | Mengkodekan konvensi proyek di setiap tingkat — agen mengikutinya secara otomatis |
| **Penemuan konteks JIT** | Hanya memuat file konteks yang relevan untuk tugas saat ini |
| **Memori** | Mempertahankan pengetahuan di seluruh sesi |
| **Conductor** | Pengembangan berbasis spesifikasi dengan rencana persisten dan pelacakan kemajuan |
| **Ekstensi** | Paket skill, agen, hook, dan kebijakan yang dapat diinstal |
| **Server MCP** | Terhubung ke alat eksternal (GitHub, BigQuery, Jira) |
| **Mesin kebijakan** | Pagar pengaman sebagai kode dalam TOML — deny, allow, atau ask_user |
| **Hook** | Injeksi konteks yang ringan dan pengarahan model pada peristiwa siklus hidup agen |
| **Sandboxing** | Eksekusi terisolasi untuk lingkungan yang tidak tepercaya |
| **Agen kustom** | Agen khusus untuk peninjauan, dokumentasi, catatan rilis — bukan hanya pengkodean |
| **Ekstensi Keamanan** | SAST resmi + pemindaian dependensi dengan pembuatan PoC dan penambalan otomatis |
| **Agen bawaan** | `generalist`, `codebase_investigator`, `cli_help` — pendelegasian tanpa pengaturan |
| **Pembuatan ADR** | Catatan keputusan arsitektur (architecture decision records) yang digerakkan oleh sub-agen dari git diff |
| **Agen onboarding** | Pemetaan basis kode untuk pengembang baru — melacak jalur kode yang sebenarnya |
| **Pipeline keamanan CI** | Ekstensi Keamanan di GitHub Actions untuk analisis kerentanan otomatis |

---
## Langkah Selanjutnya

→ Lanjutkan ke **[Kasus Penggunaan 2: Modernisasi Kode Legacy](legacy-modernization.md)**

→ Jelajahi ekosistem ekstensi: **[Ekosistem Ekstensi](extensions-ecosystem.md)** — penemuan, instalasi, pembuatan, dan pola perusahaan

→ Untuk pengguna mahir: **[Pola Lanjutan](advanced-patterns.md)** — keahlian prompting, loop verifikasi, rekayasa konteks, dan pengembangan paralel
