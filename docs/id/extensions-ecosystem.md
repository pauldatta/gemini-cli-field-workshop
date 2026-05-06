# Ekosistem Ekstensi

> **Durasi:** ~30 menit (kecepatan mandiri)
> **Tujuan:** Memahami apa itu ekstensi, menemukan dan menginstal ekstensi komunitas, dan mempelajari bagaimana organisasi memaketkan pengetahuan dan alat untuk didistribusikan.
> **Prasyarat:** Menyelesaikan setidaknya [Kasus Penggunaan 1: Produktivitas SDLC](sdlc-productivity.md) atau sudah terbiasa dengan dasar-dasarnya. Anda seharusnya sudah mengetahui bagaimana `GEMINI.md`, agen, dan skill bekerja.
>
> *Terakhir diperbarui: 2026-05-05 · [Sumber diverifikasi terhadap repositori gemini-cli](https://github.com/google-gemini/gemini-cli)*

---
## Apa Itu Ekstensi?

Di [Produktivitas SDLC](sdlc-productivity.md) Anda menginstal ekstensi Conductor. Di [Pola Lanjutan](advanced-patterns.md) Anda menginstal paket agent-skills. Keduanya diinstal dengan cara yang sama — `gemini extensions install <url>` — karena keduanya adalah **ekstensi**.

Ekstensi memaketkan berbagai kemampuan ke dalam satu unit yang dapat diinstal:

| Fitur | Apa Itu | Dipanggil Oleh |
|---|---|---|
| **Server MCP** | Mengekspos alat dan sumber data baru ke model | Model |
| **Perintah Kustom** | Pintasan `/my-cmd` untuk prompt kompleks atau perintah shell | Pengguna |
| **File Konteks** (`GEMINI.md`) | Instruksi yang selalu aktif yang dimuat setiap sesi | CLI → Model |
| **Skill Agen** | Alur kerja khusus yang diaktifkan sesuai permintaan (TDD, tinjauan kode, dll.) | Model |
| **Hook** | Interseptor siklus hidup — sebelum/sesudah panggilan alat, respons model, sesi | CLI |
| **Tema** | Definisi warna untuk personalisasi UI CLI | Pengguna (`/theme`) |
| **Mesin Kebijakan** | Aturan keselamatan dan pembatasan alat yang dikontribusikan pada prioritas tingkat 2 | CLI |

> **Wawasan utama:** Anda telah menggunakan dua ekstensi. Paket agent-skills dari Pola Lanjutan *terutama* merupakan ekstensi skill — ini menyumbangkan 20 skill dan 7 perintah garis miring (slash commands). Conductor *terutama* merupakan ekstensi perintah + server MCP. Ekstensi adalah wadah yang fleksibel — mereka dapat memaketkan kombinasi apa pun dari 7 fitur di atas.

### Manifes: `gemini-extension.json`

Setiap ekstensi memilikinya. Ini adalah kontrak antara ekstensi dan Gemini CLI:

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "description": "What this extension does",
  "contextFileName": "GEMINI.md",
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${extensionPath}${/}server.js"],
      "cwd": "${extensionPath}"
    }
  },
  "excludeTools": ["run_shell_command(rm -rf)"],
  "settings": [
    {
      "name": "API Key",
      "envVar": "MY_API_KEY",
      "sensitive": true
    }
  ]
}
```

| Bidang | Tujuan |
|---|---|
| `name` | Pengidentifikasi unik — harus cocok dengan nama direktori |
| `contextFileName` | Memuat file ini ke dalam konteks setiap sesi. Default ke `GEMINI.md` jika ada |
| `mcpServers` | Server MCP yang akan dimulai — format yang sama dengan `settings.json`. Gunakan `${extensionPath}` untuk portabilitas |
| `excludeTools` | Memblokir alat atau perintah tertentu (misalnya, `rm -rf` melalui shell) |
| `settings` | Nilai yang dapat dikonfigurasi pengguna — `sensitive: true` menyimpannya di keychain sistem |

### Ekstensi vs. Skill vs. Agen — Kapan Menggunakan Apa

| | Ekstensi | Skill (`SKILL.md`) | Agen (`.gemini/agents/*.md`) |
|---|---|---|---|
| **Cakupan** | Dibagikan di seluruh pengguna/mesin | Lokal atau dibundel dalam ekstensi | Proyek lokal |
| **Diinstal dari** | GitHub, jalur lokal | Bagian dari ekstensi atau proyek | Direktori proyek |
| **Terbaik untuk** | Toolkit yang dapat didistribusikan, standar organisasi, integrasi MCP | Alur kerja spesifik fase (TDD, audit keamanan) | Persona khusus (peninjau, pemeriksa kepatuhan) |
| **Contoh** | `oh-my-gemini-cli`, `agent-skills`, `conductor` | `subagent-driven-development`, `debugging` | `@pr-reviewer`, `@compliance-checker` |

---
## Penemuan & Instalasi

### Menemukan Ekstensi

[Galeri Ekstensi](https://geminicli.com/extensions/browse/) secara otomatis mengindeks ekstensi publik. Repositori GitHub apa pun dengan topik `gemini-cli-extension` akan muncul di galeri — tidak perlu pengajuan.

### Menginstal

```bash
# Install from GitHub
gemini extensions install https://github.com/owner/repo

# Install a specific version (branch, tag, or commit)
gemini extensions install https://github.com/owner/repo --ref v1.2.0

# Enable auto-updates
gemini extensions install https://github.com/owner/repo --auto-update
```

### Mengelola Ekstensi yang Terinstal

```bash
# List all installed extensions
gemini extensions list

# Or from within an interactive session
/extensions list

# Update a specific extension
gemini extensions update my-extension

# Update all extensions
gemini extensions update --all

# Disable an extension for this workspace only
gemini extensions disable my-extension --scope workspace

# Re-enable
gemini extensions enable my-extension --scope workspace

# Uninstall
gemini extensions uninstall my-extension
```

### Ekstensi yang Dikelola Google

Google memelihara organisasi ekstensi resmi di [**gemini-cli-extensions**](https://github.com/gemini-cli-extensions) dengan lebih dari 60 ekstensi yang mencakup keamanan, basis data, CI/CD, dan layanan Google Cloud:

| Ekstensi | Fokus | Apa yang Ditambahkan |
|---|---|---|
| [**security**](https://github.com/gemini-cli-extensions/security) | Analisis keamanan | Mesin SAST penuh, pemindaian dependensi melalui OSV-Scanner, pembuatan PoC, penambalan otomatis. Presisi 90%, perolehan (recall) 93% |
| [**conductor**](https://github.com/gemini-cli-extensions/conductor) | Pengembangan berbasis spesifikasi | Perencanaan terstruktur, pelacakan implementasi, dan pengembangan berbasis konteks |
| [**workspace**](https://github.com/gemini-cli-extensions/workspace) | Google Workspace | Integrasi Gmail, Drive, Calendar, Sheets dengan output JSON yang dioptimalkan untuk agen |
| [**cicd**](https://github.com/gemini-cli-extensions/cicd) | CI/CD | Pembuatan pipeline, debugging alur kerja, dan otomatisasi penerapan |
| [**firebase**](https://github.com/gemini-cli-extensions/firebase) | Firebase | Manajemen proyek Firebase, kueri Firestore, dan penerapan hosting |
| [**bigquery-data-analytics**](https://github.com/gemini-cli-extensions/bigquery-data-analytics) | Analitik data | skill BigQuery untuk eksplorasi data, optimasi kueri, dan analitik |
| [**cloud-sql-***](https://github.com/gemini-cli-extensions) | Basis data | skill untuk PostgreSQL, MySQL, SQL Server, AlloyDB, OracleDB |
| [**vertex**](https://github.com/gemini-cli-extensions/vertex) | Vertex AI | Manajemen prompt dan integrasi Vertex AI |

Instal salah satu dari ekstensi tersebut dengan:

```text
gemini extensions install https://github.com/gemini-cli-extensions/<name>
```

### Ekstensi Komunitas yang Terkemuka

Di luar ekosistem resmi, komunitas telah membangun ekstensi yang semakin canggih:

| Ekstensi | Fokus | Apa yang Ditambahkan |
|---|---|---|
| [**oh-my-gemini-cli**](https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli) | Orkestrasi | 12 agen, 9 skill, 43 perintah garis miring (slash commands), hook siklus hidup. Kerangka kerja multi-agen penuh dengan gerbang persetujuan |
| [**superpowers**](https://github.com/obra/superpowers) | Metodologi | 14 skill untuk TDD, debugging, tinjauan kode, pengembangan yang digerakkan oleh sub-agen. Lintas alat: juga berfungsi di Cursor dan OpenCode |
| [**gws (Google Workspace CLI)**](https://github.com/googleworkspace/cli) | Integrasi Workspace | CLI dinamis untuk Gmail, Drive, Calendar, Sheets. Output JSON yang dioptimalkan untuk agen. Integrasi Model Armor |

---
## Praktik Langsung: Instal & Gunakan Ekstensi Komunitas

Anda telah menginstal paket **agent-skills** (Pola Lanjutan) dan **Conductor** (Produktivitas SDLC). Sekarang mari kita jelajahi apa yang telah dibangun oleh komunitas di luar ekosistem resmi.

### Latihan 1: Superpowers — Metodologi sebagai Ekstensi

Ekstensi `superpowers` mengajarkan agen Anda *cara bekerja*, bukan hanya apa yang harus dilakukan. Fitur andalannya adalah **Subagent-Driven Development (SDD)** — sebuah metodologi formal untuk mengirimkan sub-agen baru per tugas dengan tinjauan dua tahap.

```bash
# Install
gemini extensions install https://github.com/obra/superpowers

# Verify — you should see superpowers in the list
/extensions list
```

**Coba skill plan:**

```
Write a plan for adding a "recently viewed products" feature to the ProShop app.
Use the $plan skill.
```

**Coba Subagent-Driven Development:**

```
I want to add a "recently viewed" sidebar widget. Use subagent-driven development 
to implement this — dispatch a subagent for each component and review each one.
```

Perhatikan bagaimana SDD:
1. Membuat spesifikasi untuk setiap komponen (model data, endpoint API, komponen React)
2. Mengirimkan sub-agen baru untuk masing-masing — tidak ada kebocoran konteks antar tugas
3. Meninjau output setiap sub-agen dalam dua tahap: kepatuhan spesifikasi, lalu kualitas kode
4. Melaporkan ringkasan dengan semua temuan

> **Poin penting:** Bandingkan ini dengan prompt mentah "tambahkan bilah sisi yang baru dilihat". SDD menghasilkan kode yang telah ditinjau dan divalidasi. prompt mentah menghasilkan kode yang harus Anda tinjau secara manual. Inilah perbedaan antara seorang pengembang dan sebuah *proses* pengembangan.

**Portabilitas lintas alat:** Superpowers juga berfungsi di Cursor (`.cursor-plugin/`) dan OpenCode (`.opencode/`). File `SKILL.md` yang sama, manifes plugin yang berbeda. skill tidak terkunci pada vendor tertentu.

---

### Latihan 2: Oh-My-Gemini-CLI — Orkestrasi sebagai Ekstensi

Ekstensi ini mengimplementasikan alur kerja multi-agen yang lengkap dengan gerbang persetujuan — jenis tata kelola yang dibutuhkan oleh tim perusahaan.

```bash
# Install
gemini extensions install https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli
```

**Coba alur kerja berbasis niat (intent-driven):**

```
/omg:intent Add user profile avatars to the ProShop application
```

Perhatikan apa yang terjadi:
- agen tidak langsung mulai membuat kode. Ia meluncurkan **wawancara Sokrates** — menanyakan tentang ruang lingkup, batasan, dan kriteria penerimaan
- Hanya setelah Anda mengonfirmasi ruang lingkup, agen `omg-planner` membuat rencana terstruktur
- Rencana tersebut diserahkan kepada `omg-executor` untuk diimplementasikan
- Setelah implementasi, `omg-reviewer` menjalankan pemeriksaan gerbang kualitas

**Intipan anatomi:** Ekstensi ini menggunakan ketujuh fitur ekstensi secara bersamaan:

```
oh-my-gemini-cli/
├── gemini-extension.json    # Manifest (contextFileName, MCP config)
├── GEMINI.md                # Always-on context → delegates to skills
├── context/omg-core.md      # Core behavioral rules
├── agents/                  # 12 sub-agents (architect, reviewer, debugger, etc.)
├── skills/                  # 9 deep-work procedures ($plan, $prd, $research, etc.)
├── commands/                # 43 TOML slash commands under /omg:* namespace
└── hooks/hooks.json         # BeforeModel (banner/router) + AfterAgent (auto-learn)
```

> **Poin penting:** OMG menunjukkan seperti apa ekstensi yang "siap pakai" (batteries-included). Gerbang wawancara Sokrates mencegah agen mengeksekusi otomatis pada permintaan yang ambigu — sebuah pola yang harus dipertimbangkan oleh setiap perusahaan.

---

### Latihan 3: Google Workspace CLI (Opsional)

> **Catatan:** Latihan ini memerlukan Google Workspace (Gmail, Drive, Calendar). Lewati ini jika organisasi Anda tidak menggunakan Workspace.

Ekstensi `gws` memberi agen Anda akses langsung dan terstruktur ke API Workspace:

```bash
# Install as a Gemini extension
gemini extensions install https://github.com/googleworkspace/cli

# Authenticate (one-time setup)
gws auth setup
```

**Coba triase kotak masuk:**

```
Use gws to triage my inbox — show me unread emails grouped by priority
```

**Coba laporan standup:**

```
Use gws to generate a standup report from my calendar and recent email activity
```

`gws` menghasilkan JSON terstruktur yang dioptimalkan untuk konsumsi agen. Ini juga mendukung `--sanitize` untuk merutekan respons API melalui templat Model Armor sebelum agen memprosesnya.

---

### Latihan 4: Ekstensi Keamanan — SAST Tingkat Produksi

[Ekstensi Keamanan](https://github.com/gemini-cli-extensions/security) adalah alat analisis keamanan resmi Google untuk Gemini CLI. Tidak seperti agen kepatuhan buatan sendiri, ia dilengkapi dengan mesin SAST penuh, pemindai dependensi, dan hasil yang di-benchmark.

```bash
# Install
gemini extensions install https://github.com/gemini-cli-extensions/security
```

**Jalankan analisis keamanan pada perubahan Anda saat ini:**

```
/security:analyze
```

Ekstensi ini menjalankan analisis dua tahap yang terstruktur:
1. **Tahap pengintaian (Reconnaissance)** — pemindaian cepat terhadap semua file yang diubah berdasarkan taksonomi kerentanannya
2. **Tahap investigasi** — penyelidikan mendalam ke dalam pola yang ditandai, melacak aliran data dari sumber ke tujuan (sink)

Ini memeriksa rahasia yang di-hardcode, kerentanan injeksi (SQLi, XSS, SSRF, SSTI), kontrol akses yang rusak, paparan PII, kriptografi yang lemah, dan masalah keamanan LLM.

**Pindai dependensi untuk CVE yang diketahui:**

```
/security:scan-deps
```

Ini menggunakan [OSV-Scanner](https://github.com/google/osv-scanner) terhadap [osv.dev](https://osv.dev) — basis data kerentanan sumber terbuka Google.

**Sesuaikan ruang lingkup:**

```
/security:analyze Analyze all source code under the src/ folder. Skip docs and config files.
```

**Kemampuan utama:**
- **Pembuatan PoC** — menghasilkan skrip proof-of-concept untuk memvalidasi temuan (skill `poc`)
- **Penambalan otomatis (Auto-patching)** — menerapkan perbaikan untuk kerentanan yang dikonfirmasi (skill `security-patcher`)
- **Daftar izin (Allowlisting)** — mempertahankan risiko yang diterima di `.gemini_security/vuln_allowlist.txt`
- **Integrasi CI** — menyediakan [alur kerja GitHub Actions](https://github.com/gemini-cli-extensions/security/blob/main/.github/workflows/gemini-review.yml) yang siap pakai untuk tinjauan keamanan PR otomatis

> **Nilai perusahaan:** Ini adalah ekstensi yang sama yang dirujuk dalam [Produktivitas SDLC §1.7](sdlc-productivity.md) dan [§2.3](sdlc-productivity.md). Ini menggantikan kebutuhan untuk membangun agen pemeriksa kepatuhan kustom — satu `gemini extensions install` memberi seluruh tim Anda pipeline keamanan tingkat produksi.

---
## Membangun Ekstensi Anda Sendiri

### Scaffold dari Templat

Gemini CLI menyediakan 7 templat bawaan:

```bash
# Create from a template
gemini extensions new my-extension mcp-server
gemini extensions new my-extension custom-commands
gemini extensions new my-extension exclude-tools
gemini extensions new my-extension hooks
gemini extensions new my-extension skills
gemini extensions new my-extension policies
gemini extensions new my-extension themes-example
```

### Mengembangkan Secara Lokal dengan `link`

Gunakan `link` untuk menguji perubahan tanpa menginstal ulang:

```bash
cd my-extension
npm install
gemini extensions link .
```

Perubahan akan langsung terlihat setelah memulai ulang sesi Gemini CLI Anda. Tidak perlu menginstal ulang selama pengembangan.

### Memublikasikan ke Galeri

Publikasi bersifat otomatis — tidak perlu pengajuan:

1. **Push ke repo GitHub publik** dengan `gemini-extension.json` yang valid di root
2. **Tambahkan topik GitHub** `gemini-cli-extension` ke bagian About repo Anda
3. **Beri tag pada rilis** (misalnya, `v1.0.0`)

Crawler galeri mengindeks repo yang diberi tag setiap hari. Ekstensi Anda akan muncul secara otomatis setelah validasi.

### Latihan: Membangun Ekstensi Mini

Buat ekstensi sederhana yang menambahkan slash command untuk daftar periksa tinjauan kode tim Anda:

```bash
# Scaffold
gemini extensions new team-review custom-commands
cd team-review

# Create the command
mkdir -p commands/team
cat > commands/team/review.toml << 'EOF'
prompt = """
Review the current changes using this checklist:
1. Does it follow our coding standards?
2. Are there any security issues (OWASP Top 10)?
3. Is error handling complete?
4. Are tests adequate?
5. Is the API contract backward-compatible?

Focus on findings, not praise. Be specific with file:line references.
"""
EOF

# Link for local development
gemini extensions link .
```

Mulai ulang Gemini CLI dan jalankan `/team:review` — daftar periksa tinjauan kustom Anda sekarang menjadi tindakan satu perintah.

---
## Pola Ekstensi untuk Perusahaan

### Distribusi Pengetahuan Organisasi

Pola bernilai tertinggi untuk tim perusahaan: **kemas pengetahuan organisasi Anda sebagai sebuah ekstensi.**

Alih-alih dokumen orientasi yang membusuk di Confluence, kirimkan sebuah ekstensi yang mengajarkan agen pola organisasi Anda:

```
my-org-extension/
├── gemini-extension.json
├── GEMINI.md                # Org coding standards, always loaded
├── skills/
│   ├── security-review/     # OWASP checklist + your org's threat model
│   ├── api-design/          # Your API design guide, enforced at dev time
│   └── incident-response/   # Runbook for on-call engineers
├── commands/
│   ├── team/
│   │   ├── review.toml      # Team-specific code review checklist
│   │   └── deploy.toml      # Deploy workflow with org-specific gates
│   └── oncall/
│       └── triage.toml      # Incident triage workflow
├── agents/
│   └── compliance-checker.md  # Org compliance rules as a sub-agent
└── policies/
    └── safety.toml          # Tool restrictions (no force-push, no prod DB access)
```

**Manfaat:**
- **Memiliki Versi:** Perbarui ekstensi, semua orang mendapatkan standar terbaru pada `gemini extensions update` berikutnya
- **Terdistribusi:** `gemini extensions install` pada hari ke-1 — karyawan baru mendapatkan seluruh pengetahuan institusional Anda
- **Terpelihara:** Satu repo, satu PR untuk memperbarui standar organisasi di setiap agen pengembang
- **Konsisten:** Setiap agen di tim Anda mengikuti aturan yang sama, meninjau dengan daftar periksa yang sama, menerapkan dengan gerbang yang sama

> **Ini menggantikan pola orientasi "baca wiki".** Alih-alih berharap pengembang menemukan dan membaca panduan gaya Anda, agen menerapkannya secara otomatis.

### Pola Tata Kelola

Ekstensi menyumbangkan aturan kebijakan pada **prioritas tingkat 2** — lebih tinggi dari default, lebih rendah dari penimpaan pengguna/admin:

```toml
# policies/safety.toml (contributed by your org extension)
[[rule]]
toolName = "run_shell_command"
commandRegex = ".*--force.*"
decision = "deny"
priority = 100
denyMessage = "Force operations are blocked by organization policy."
```

> **Model keamanan:** Kebijakan ekstensi beroperasi pada prioritas tingkat 2. Kebijakan pengguna (tingkat 4) dan admin (tingkat 5) selalu diutamakan. Ini berarti sebuah ekstensi dapat menetapkan pagar pengaman, tetapi pengguna dan admin dapat menimpanya jika diperlukan. Lihat [Mesin Kebijakan](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md) untuk detail tingkat lengkap dan [Mengamankan Gemini CLI dengan Mesin Kebijakan](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy) untuk panduan praktis.

**Pengaturan dengan penyimpanan keychain:** Ekstensi dapat mendefinisikan pengaturan yang disimpan dalam keychain sistem:

```json
{
  "settings": [
    {
      "name": "Internal API Key",
      "envVar": "ORG_API_KEY",
      "sensitive": true
    }
  ]
}
```

Nilai yang ditandai `sensitive: true` disimpan terenkripsi di keychain OS dan disamarkan dalam keluaran CLI.

### Portabilitas Lintas Alat

Ekstensi `superpowers` mendemonstrasikan pola perusahaan utama: file `SKILL.md` yang sama berfungsi di Gemini CLI, Cursor, dan OpenCode — masing-masing dengan format manifes pluginnya sendiri (`gemini-extension.json`, `.cursor-plugin/`, `.opencode/`). Ini berarti:

- **Skill tidak terkunci oleh vendor** — berinvestasi dalam metodologi, bukan konfigurasi khusus alat
- **Tim yang menggunakan editor berbeda** berbagi standar rekayasa yang sama
- **Migrasi berisiko rendah** — beralih alat berarti menulis manifes baru, bukan menulis ulang skill

### Pola Registri Internal

Untuk organisasi yang memelihara ekosistem ekstensi privat:

1. **Organisasi GitHub** — Buat organisasi internal (misalnya, `my-company-gemini-extensions`)
2. **Penandaan topik** — Gunakan konvensi privat (misalnya, `internal-gemini-extension`)
3. **Penyematan versi** — Instal dengan tag `--ref` untuk stabilitas produksi:
   ```bash
   gemini extensions install https://github.internal.com/org/my-ext --ref v2.1.0
   ```
4. **Pembaruan otomatis** — Gunakan `--auto-update` untuk ekstensi di mana yang terbaru adalah yang terbaik (panduan gaya)
5. **Pencakupan ruang kerja** — Nonaktifkan ekstensi organisasi untuk proyek tertentu:
   ```bash
   gemini extensions disable org-standards --scope workspace
   ```

---
## Ringkasan

| Konsep | Poin Penting |
|---|---|
| **Apa yang dikemas ekstensi** | 7 fitur: server MCP, perintah, konteks, skill, hook, tema, kebijakan |
| **Dikelola Google** | 60+ ekstensi di [gemini-cli-extensions](https://github.com/gemini-cli-extensions) — keamanan, basis data, CI/CD, Workspace |
| **Instalasi** | `gemini extensions install <url>` — satu perintah |
| **Galeri** | Diindeks secara otomatis melalui topik GitHub `gemini-cli-extension` |
| **Membangun** | `gemini extensions new` dari 7 templat, `link` untuk pengembangan lokal |
| **Nilai perusahaan** | Mengemas pengetahuan organisasi, menegakkan standar, mendistribusikan melalui perintah instal |
| **Keamanan** | Ekstensi Keamanan Resmi dengan SAST + pemindaian dependensi. Kebijakan ekstensi di tingkat 2. Rahasia di keychain |
| **Portabilitas** | Skill berfungsi di seluruh Gemini CLI, Cursor, dan OpenCode |

---
## Langkah Selanjutnya

→ Kembali ke **[Kasus Penggunaan 1: Produktivitas SDLC](sdlc-productivity.md)** — Bagian 2 membahas agen loop luar (ADR, orientasi, audit dependensi)

→ Lanjutkan ke **[Pola Lanjutan](advanced-patterns.md)** — keahlian prompt, rekayasa konteks, dan instalasi skill agen
