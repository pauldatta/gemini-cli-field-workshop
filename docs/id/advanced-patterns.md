# Pola Lanjutan

> **Durasi:** ~45 menit (mandiri)  
> **Tujuan:** Menguasai disiplin prompt, loop verifikasi, rekayasa konteks, dan pengembangan paralel. Teknik-teknik ini berfungsi dengan alur kerja Gemini CLI apa pun.  
> **Prasyarat:** Menyelesaikan setidaknya [Kasus Penggunaan 1: Produktivitas SDLC](sdlc-productivity.md) atau sudah familier dengan dasar-dasarnya.
>
> *Terakhir diperbarui: 2026-05-05 · [Sumber diverifikasi terhadap repositori gemini-cli](https://github.com/google-gemini/gemini-cli)*

---
## Seni Prompting: Tujuan vs. Instruksi

Peningkatan tunggal terbesar yang dapat Anda lakukan pada kualitas keluaran AI adalah mengubah **cara Anda bertanya**.

### Masalah

Sebagian besar pengembang memberikan instruksi langkah demi langkah:

```
Create a wishlist model with userId and productId fields.
Then create a controller with addToWishlist and getWishlist functions.
Then add routes at /api/wishlist.
Then create a Redux slice.
Then create the WishlistScreen component.
```

Hal ini memaksa agen ke jalur tertentu — bahkan jika ada pendekatan yang lebih baik. Agen tidak dapat menolak, memunculkan tradeoff, atau beradaptasi.

### Solusi: Tujuan Deklaratif dengan Kriteria Keberhasilan

```
Add a product wishlist feature. When you're done:
1. A logged-in user can add/remove products from their wishlist
2. The wishlist persists across sessions (stored in MongoDB)
3. There's a /wishlist page accessible from the navbar
4. All existing tests still pass (npm test)
5. The code follows the conventions in GEMINI.md

Say "WISHLIST_COMPLETE" when all criteria are verified.
```

### Mengapa Ini Berhasil

| Imperatif (❌) | Deklaratif (✅) |
|---|---|
| Menentukan detail implementasi | Menjelaskan hasil yang diinginkan |
| Agen tidak dapat menolak atau menyarankan alternatif | Agen memilih pendekatan terbaik untuk basis kode |
| Tidak ada verifikasi — Anda harus memeriksanya secara manual | Loop verifikasi bawaan melalui kriteria keberhasilan |
| Satu jalur yang kaku | Agen beradaptasi dengan apa yang ditemukannya |

> **Wawasan utama:** "Jangan beri tahu apa yang harus dilakukan — berikan kriteria keberhasilan dan biarkan ia berjalan." Agen sangat pandai melakukan perulangan hingga memenuhi tujuan tertentu. Kriteria yang lemah ("buat agar berfungsi") membutuhkan bimbingan terus-menerus. Kriteria yang kuat memungkinkannya berjalan secara mandiri.

### Latihan

Cobalah kedua pendekatan pada tugas yang sama dengan ProShop. Bandingkan:
1. Berapa banyak giliran yang dibutuhkan masing-masing?
2. Apakah versi deklaratif menemukan pendekatan yang lebih baik?
3. Mana yang menghasilkan kode yang lebih bersih?

---
## Disiplin Konteks

Setiap token di dalam jendela konteks agen membuat respons berikutnya menjadi sedikit kurang fokus. Konteks adalah sebuah anggaran — kelola seperti memori pada perangkat yang terbatas.

### Gejala Kelebihan Beban Konteks

- Agen mulai mengulangi dirinya sendiri
- Halusinasi meningkat (merujuk pada file yang tidak ada)
- Kualitas output menurun secara nyata setelah 15-20 giliran
- Agen "lupa" instruksi sebelumnya

### Perangkat Alat

#### 1. Reset Strategis

Ketika kualitas output menurun:

```
/clear
```

Ini mereset konteks percakapan sambil menjaga GEMINI.md, memori, dan status file tetap utuh. Agen memulai ulang dengan segar tetapi dengan semua pengetahuan proyek Anda.

#### 2. Simpan Sebelum Anda Membersihkan

```
/memory add "The ProShop codebase uses a repository pattern for 
data access. All MongoDB queries go through model methods, never 
directly in controllers. Express middleware chain: cors → 
cookieParser → authMiddleware → routes."
```

Memori bertahan di seluruh sesi dan reset `/clear`. Simpan penemuan penting sebelum membersihkan.

#### 3. Pemindahan Konteks

Pindahkan spesifikasi besar keluar dari percakapan dan ke dalam file:

```bash
# Instead of pasting a long spec into chat:
echo "Your detailed spec..." > feature-spec.md

# Then reference it in your prompt with @:
# "Read @./feature-spec.md and implement it"
```

Atau tambahkan sebagai impor di GEMINI.md Anda untuk konteks yang persisten:

```markdown
# GEMINI.md
@./feature-spec.md
```

> Lihat [referensi GEMINI.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md) untuk sintaks impor.

#### 4. Isolasi melalui Delegasi Agen

Setiap agen kustom mendapatkan jendela konteksnya sendiri. Gunakan ini secara strategis:

```
# Bad: one agent doing everything (context bloat)
"Research the auth system, then refactor it, then write tests, then review"

# Good: isolated phases (each gets clean context)
@codebase_investigator Map the auth system
Now refactor based on the investigator's findings
@pr-reviewer Review the refactored auth code
```

### Latihan

1. Mulai sesi dan bangun tiga fitur secara berurutan (sengaja menumpuk konteks)
2. Perhatikan penurunan kualitas sekitar giliran 15-20
3. Jalankan `/memory add` untuk menyimpan fakta-fakta kunci
4. Jalankan `/clear` — amati peningkatan kualitas secara langsung
5. Minta agen untuk melanjutkan dari tempat ia tinggalkan — ia melanjutkannya melalui memori + status file

---
## Loop Verifikasi

Cara paling andal untuk mendapatkan kode yang benar dari sebuah agen adalah dengan memberikannya **loop umpan balik** — sebuah cara untuk memeriksa pekerjaannya sendiri dan memperbaiki kesalahan secara otomatis.

### Pola

```
Add product ratings to ProShop. When you're done:
1. Users can rate products 1-5 stars
2. Average rating displays on the product page
3. Only authenticated users can rate
4. A user can only rate a product once
5. All existing tests pass AND new tests cover the rating logic

Run `npm test` after each change. Fix any failures before moving on.
Say "RATINGS_COMPLETE" when all 5 criteria are verified.
```

### Mengapa Janji Penyelesaian Berhasil

Frasa "katakan X jika sudah selesai" memberikan agen:

1. **Titik henti yang jelas** — ia tahu kapan harus berhenti bekerja
2. **Insentif verifikasi mandiri** — ia memeriksa pekerjaannya sebelum menyatakan selesai
3. **Pemulihan iteratif** — jika pengujian gagal, ia memperbaiki dan menjalankan ulang daripada bertanya kepada Anda

### Mengotomatiskan Loop

Untuk tugas-tugas besar, Anda dapat mengotomatiskan loop umpan balik menggunakan hook. Sebuah hook `AfterAgent` memeriksa apakah janji penyelesaian muncul di output. Jika tidak, ia akan mereset percakapan (mempertahankan perubahan file) dan menjalankan ulang dengan prompt asli + basis kode yang telah ditingkatkan:

```json
{
  "hooks": {
    "AfterAgent": [{
      "type": "command",
      "command": "python3 check_completion.py",
      "description": "Checks for completion promise and resets if not met"
    }]
  }
}
```

> **Keamanan:** Selalu konfigurasikan pembatasan alat saat menjalankan loop otonom. Blokir operasi destruktif (`git push --force`, `rm -rf`) di `settings.json` atau `policy.toml` Anda.

### Latihan

Beri agen tugas refactoring dengan kriteria keberhasilan yang eksplisit dan janji penyelesaian. Perhatikan ia beriterasi melalui kegagalan pengujian hingga mencapai hijau.

---
## Pengembangan Paralel dengan worktree

Jalankan beberapa sesi Gemini CLI secara bersamaan di cabang yang berbeda — masing-masing dalam isolasi penuh.

### Masalah

Anda hanya dapat melakukan checkout pada satu cabang pada satu waktu. Jika Anda ingin mengerjakan sebuah fitur, perbaikan bug, dan refactor secara bersamaan dengan agen yang terpisah, mereka akan bertabrakan.

### Solusi

```bash
# Terminal 1: Feature work
gemini --worktree feature-wishlist

# Terminal 2: Bug fix
gemini --worktree fix-cart-rounding

# Terminal 3: Documentation
gemini --worktree update-api-docs
```

Setiap agen bekerja di direktorinya sendiri, di cabangnya sendiri, dengan konteksnya sendiri. Tidak ada konflik.

### Alur Kerja

| Fase | Tindakan |
|---|---|
| **Isolasi** | Buat satu worktree per tugas/agen |
| **Konfigurasi** | Setiap worktree mendapatkan port server dev-nya sendiri untuk menghindari konflik |
| **Eksekusi** | Luncurkan sesi Gemini CLI yang terpisah — setiap agen bekerja secara independen |
| **Tinjauan** | Setiap agen melakukan commit ke cabangnya di dalam worktree-nya |
| **Integrasi** | Gabungkan cabang kembali ke `main` melalui PR |
| **Pembersihan** | `git worktree remove <path>` + `git worktree prune` |

> **Perlakukan worktree sebagai sesuatu yang sekali pakai.** Mereka dioptimalkan untuk durasi satu tugas tunggal. Hapus setelah digabungkan.

### Latihan

Buka dua jendela terminal. Gunakan worktree untuk:
1. Menambahkan fitur wishlist di salah satunya
2. Memperbaiki perhitungan total keranjang di yang lainnya

Kedua agen bekerja secara bersamaan. Tidak ada yang melihat perubahan satu sama lain. Gabungkan keduanya melalui PR.

---
## Orkestrasi Multi-Agen

Untuk tim yang mengelola puluhan agen di berbagai proyek, alat orkestrasi menyediakan isolasi, observabilitas, dan penskalaan tingkat perusahaan.

### Scion (Google Cloud Platform)

**[Scion](https://github.com/GoogleCloudPlatform/scion)** adalah orkestrator multi-agen eksperimental yang menjalankan agen sebagai proses yang terisolasi dan bersamaan — masing-masing di dalam kontainernya sendiri.

```bash
# Install
go install github.com/GoogleCloudPlatform/scion/cmd/scion@latest

# Start parallel agents with specialized roles
scion start reviewer "Review all open PRs for security issues" --attach
scion start implementer "Implement the wishlist feature" --attach
scion start tester "Write integration tests for the order API" --attach

# Manage
scion list                              # See all running agents
scion message reviewer "Focus on auth"  # Send instructions
scion attach implementer                # Watch an agent work
```

| Konsep | Deskripsi |
|---|---|
| **Agen** | Proses dalam kontainer yang menjalankan Gemini CLI |
| **Grove** | Namespace proyek — biasanya 1:1 dengan repo git |
| **Template** | Cetak biru agen: prompt sistem + skill + izin alat |
| **Runtime** | Docker, Podman, Apple Container, atau Kubernetes |

> **Kapan menggunakan Scion:** Tim dengan 5+ tugas agen yang berjalan bersamaan, proyek yang membutuhkan isolasi ketat antar agen, atau organisasi yang menskalakan pengembangan yang dikelola AI di berbagai repositori.

---
## Pola Konstitusi Rekayasa

Jika Anda harus memberi tahu agen hal yang sama dua kali, itu harus berada di dalam sebuah file.

### Apa yang Ada di dalam Konstitusi

Sebuah `GEMINI.md` yang disusun dengan baik menyandikan standar rekayasa tim Anda sehingga agen mengikutinya secara otomatis:

```markdown
# GEMINI.md

## Coding Standards
- All MongoDB queries go through model methods — never directly in controllers
- Use asyncHandler wrapper for all route handlers
- Error responses use the errorMiddleware pattern
- API responses are JSON with consistent field naming (camelCase)

## Behavioral Rules
- Surface assumptions before implementing — ask if multiple interpretations exist
- Prefer minimal changes over broad refactors
- Every changed line must trace to the original request
- Run tests after every file modification
- Never modify files outside the scope of the current task
```

### Latihan

1. Tulis sebuah GEMINI.md dengan 5 aturan untuk ProShop
2. Minta agen untuk menambahkan fitur **tanpa** file tersebut — perhatikan outputnya
3. Minta hal yang sama **dengan** file tersebut
4. Bandingkan: Apakah agen mengikuti konvensi? Apakah ia menanyakan pertanyaan klarifikasi yang sebelumnya dilewati?

---
## Penegakan Deterministik

Sebuah `GEMINI.md` sangat baik untuk *memandu* agen, tetapi tidak dapat menjamin kepatuhan 100%. Agen dapat berhalusinasi dengan pola yang salah selama refaktor kompleks — mengimpor model secara langsung di file rute meskipun konstitusi Anda melarangnya.

Solusinya: pasangkan panduan berbasis prompt dengan **pagar pengaman deterministik** — batasan keras yang menangkap pelanggaran secara mekanis.

### Pagar Pengaman Input vs. Output

| Lapisan | Kapan | Contoh |
|---|---|---|
| **Input** (pra-pembuatan) | Sebelum agen melihat konteks | `.geminiignore` membatasi akses file; `GEMINI.md` menetapkan ekspektasi arsitektur |
| **Output** (pasca-pembuatan) | Setelah pembuatan, sebelum penggabungan | Linter menegakkan batasan; pemindai mendeteksi rahasia yang bocor; test suite memverifikasi perilaku |

Pagar pengaman input mengurangi kesalahan. Pagar pengaman output *menangkapnya*.

### Pola: "AI Mengusulkan, CI Menentukan"

Alih-alih mengandalkan LLM untuk mengawasi dirinya sendiri, gunakan alat rekayasa tradisional untuk menegakkan aturan:

1. **Panduan** (`GEMINI.md`) — memberi tahu agen cara menulis kode dengan benar sejak awal.
2. **Penjaga** (linter, analisis statis) — menangkap pelanggaran secara deterministik.
3. **Loop** — jika penjaga gagal, kesalahan diumpankan kembali ke agen melalui [hook `AfterAgent`](https://www.geminicli.com/docs/hooks/), memaksanya untuk mengoreksi diri. Ini adalah pola [Loop Verifikasi](#verification-loops) yang sama, yang diotomatisasi.

### Penegakan dalam Praktik

Alat apa pun yang keluar dengan nilai non-zero dapat berfungsi sebagai pagar pengaman. Hubungkan ke CI, hook `pre-commit` Git, atau event `AfterAgent` dari Gemini CLI:

| Penegak | Apa yang Ditangkapnya |
|---|---|
| **ESLint / Ruff** | Kompleksitas kode, pelanggaran gaya, API yang dilarang |
| **gitleaks** | Kunci API yang di-hardcode, kredensial dalam sumber |
| **dependency-cruiser** | Impor lintas lapisan ilegal (batasan arsitektur) |
| **Test suite kustom** | Regresi perilaku |

#### Contoh: Menegakkan Batasan Lapisan dengan `dependency-cruiser`

Jika aturan `GEMINI.md` Anda menyatakan "Tidak boleh ada logika bisnis di file rute", tegakkan secara deterministik dengan [dependency-cruiser](https://github.com/sverweij/dependency-cruiser):

```javascript
// .dependency-cruiser.js
module.exports = {
  forbidden: [
    {
      name: 'no-business-logic-in-routes',
      comment: 'Routes should only delegate to controllers. Never import models directly.',
      severity: 'error',
      from: { path: '^src/routes/' },
      to: { path: '^src/models/' }
    }
  ]
};
```

Buat skrip hook yang menjalankan linter dan mengembalikan JSON terstruktur saat gagal:

```bash
#!/usr/bin/env bash
# .gemini/hooks/check-architecture.sh
input=$(cat)  # Read hook input from stdin (required)

output=$(npx depcruise src --config .dependency-cruiser.js 2>&1)
if [ $? -ne 0 ]; then
  # Return a denial — AfterAgent treats this as a retry prompt
  jq -n --arg msg "$output" '{
    "decision": "deny",
    "reason": ("Architecture violation detected. Fix the illegal import:\n" + $msg)
  }'
else
  echo '{"decision": "allow"}'
fi
```

> **Cara kerja percobaan ulang `AfterAgent`:** Saat hook mengembalikan `decision: "deny"`, Gemini CLI menolak respons agen dan mengirimkan teks `reason` kembali ke agen sebagai prompt baru. Agen kemudian mencoba memperbaiki pelanggaran secara otomatis. Lihat [Referensi Hook](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md) untuk skema lengkapnya.

Daftarkan skrip di pengaturan Anda menggunakan skema konfigurasi hook standar:

**`.gemini/settings.json`**

```json
{
  "hooks": {
    "AfterAgent": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/check-architecture.sh",
            "name": "architecture-guard",
            "description": "Enforces layer boundaries via dependency-cruiser after each agent turn"
          }
        ]
      }
    ]
  }
}
```

Sekarang, jika agen membuat impor ilegal, hook menolak respons dan mengumpankan kesalahan linter kembali sebagai prompt percobaan ulang — agen memperbaiki pelanggarannya sendiri.

### Latihan

1. Dalam sebuah proyek, buat file rute yang mengimpor model database secara langsung
2. Konfigurasikan `dependency-cruiser` (atau aturan ESLint kustom) untuk memblokir pola ini
3. Daftarkan sebagai hook `AfterAgent` menggunakan konfigurasi di atas
4. Minta agen untuk "Menambahkan endpoint baru ke rute" — amati apakah agen menyalin pola yang buruk tersebut
5. Jika ya, perhatikan hook menolak respons dan agen mengoreksi diri

---
## Pengembangan Berbasis Skill

Skill adalah file instruksi terstruktur dan dapat digunakan kembali (`SKILL.md`) yang menyandikan alur kerja insinyur senior secara langsung ke dalam agen. Tidak seperti prompt mentah, setiap skill mencakup proses langkah demi langkah, tabel anti-rasionalisasi (alasan umum yang mungkin digunakan agen untuk melewati langkah, dengan sanggahan yang didokumentasikan), tanda bahaya, dan gerbang verifikasi.

### Mengapa Skill Mengungguli Prompt Mentah

| Prompt Mentah | Skill Terstruktur |
|---|---|
| "Tulis pengujian untuk ini" | Mengaktifkan alur kerja Red-Green-Refactor dengan target piramida pengujian (80/15/5) |
| "Tinjau kode ini" | Menjalankan tinjauan lima sumbu dengan label tingkat keparahan (Nit/Opsional/FYI) dan norma ukuran perubahan |
| "Buat ini aman" | Memicu daftar periksa OWASP Top 10 dengan sistem batas tiga tingkat |
| Tidak ada kriteria penghentian | Gerbang verifikasi bawaan — agen harus menghasilkan bukti sebelum melanjutkan |

### Menginstal Skill Komunitas

Paket [agent-skills](https://github.com/addyosmani/agent-skills) menyediakan 20 skill tingkat produksi yang mencakup seluruh SDLC. Instal dengan satu perintah:

```bash
# Install from GitHub (auto-discovers all SKILL.md files)
gemini skills install https://github.com/addyosmani/agent-skills.git --path skills

# Verify installation
/skills list
```

Setelah diinstal, skill aktif sesuai permintaan saat agen mengenali tugas yang cocok. Membangun UI? Skill `frontend-ui-engineering` aktif secara otomatis. Men-debug kegagalan pengujian? `debugging-and-error-recovery` akan bekerja.

### Perintah Slash SDLC

Paket skill menyediakan 7 perintah slash di bawah `.gemini/commands/` yang memetakan ke siklus hidup pengembangan:

| Perintah | Fase | Apa yang Dilakukannya |
|---|---|---|
| `/spec` | Tentukan | Tulis PRD terstruktur sebelum menulis kode |
| `/planning` | Rencanakan | Pecah pekerjaan menjadi tugas-tugas kecil yang dapat diverifikasi dengan kriteria penerimaan |
| `/build` | Bangun | Implementasikan tugas berikutnya sebagai irisan vertikal tipis |
| `/test` | Verifikasi | Jalankan alur kerja TDD — red, green, refactor |
| `/review` | Tinjau | Tinjauan kode lima sumbu dengan label tingkat keparahan |
| `/code-simplify` | Tinjau | Kurangi kompleksitas tanpa mengubah perilaku (Chesterton's Fence) |
| `/ship` | Kirim | Daftar periksa pra-peluncuran melalui penyebaran (fan-out) persona paralel |

> **Catatan:** Gunakan `/planning` alih-alih `/plan` — `/plan` berkonflik dengan perintah Mode Perencanaan bawaan Gemini CLI.

### Skill vs GEMINI.md

Keduanya memengaruhi perilaku agen, tetapi melayani tujuan yang berbeda:

| | Skill | GEMINI.md |
|---|---|---|
| **Dimuat** | Sesuai permintaan, saat tugas cocok | Setiap prompt, selalu |
| **Biaya token** | Minimal hingga diaktifkan | Overhead konstan |
| **Terbaik untuk** | Alur kerja spesifik fase (TDD, tinjauan keamanan, pengiriman) | Konvensi proyek yang selalu aktif (tumpukan teknologi, standar pengkodean) |

**Aturan praktis:** Jika Anda ingin ini aktif untuk *setiap* prompt, letakkan di GEMINI.md. Jika spesifik untuk fase tertentu, instal sebagai skill.

### Latihan

1. Instal paket agent-skills ke dalam ruang kerja ProShop Anda
2. Jalankan `/spec` — tulis spesifikasi untuk fitur "perbandingan produk"
3. Jalankan `/build` — implementasikan irisan pertama secara bertahap
4. Jalankan `/test` — perhatikan alur kerja TDD menerapkan red-green-refactor
5. Bandingkan: Bagaimana alur kerja terstruktur berbeda dari prompt mentah "tambahkan fitur perbandingan"?

---
## Server MCP Terkelola Google

Google menyediakan **50+ server MCP terkelola** yang memberikan agen Anda akses langsung dan terkelola ke layanan Google Cloud, aplikasi Workspace, dan alat pengembang — tidak memerlukan instalasi server lokal.

### Mengapa MCP Terkelola?

| Perhatian | Bagaimana MCP Terkelola Menyelesaikannya |
|---|---|
| **Keamanan** | Kebijakan IAM Deny untuk kontrol akses tingkat alat; Model Armor untuk pertahanan injeksi prompt |
| **Penemuan** | Agent Registry — direktori terpadu untuk menemukan dan mengelola server MCP |
| **Observabilitas** | OTel Tracing + Cloud Audit Logs untuk forensik tindakan penuh |
| **Interoperabilitas** | Berfungsi dengan Gemini CLI, Claude Code, Cursor, VS Code, LangChain, ADK, CrewAI |

### Developer Knowledge MCP

[Server MCP Developer Knowledge](https://developers.google.com/knowledge/mcp) mendasarkan agen Anda pada dokumentasi resmi Google — Firebase, Cloud, Android, Maps, dan lainnya. Daripada menghalusinasi tanda tangan API, agen menanyakan korpus dokumentasi langsung.

**Instalasi satu baris (autentikasi kunci API):**

```bash
gemini mcp add -t http \
  -H "X-Goog-Api-Key: YOUR_API_KEY" \
  google-developer-knowledge \
  https://developerknowledge.googleapis.com/mcp --scope user
```

**Atau melalui `settings.json` (autentikasi ADC untuk perusahaan):**

```json
{
  "mcpServers": {
    "google-developer-knowledge": {
      "httpUrl": "https://developerknowledge.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": {
        "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
      },
      "timeout": 30000,
      "headers": {
        "X-goog-user-project": "YOUR_PROJECT_ID"
      }
    }
  }
}
```

**Alat yang tersedia:**

| Alat | Tujuan |
|---|---|
| `search_documents` | Temukan potongan dokumentasi yang relevan untuk sebuah kueri |
| `get_documents` | Ambil konten halaman penuh untuk dokumen tertentu |
| `answer_query` | Dapatkan jawaban yang disintesis dan berdasar dari korpus dokumentasi |

### Server MCP Bernilai Tinggi Berdasarkan Kategori

| Kategori | Server | Contoh Kasus Penggunaan |
|---|---|---|
| **Dokumen Pengembang** | Developer Knowledge API | "Bagaimana cara mengonfigurasi penskalaan otomatis Cloud Run?" → jawaban dengan kutipan sumber |
| **Data & Analitik** | BigQuery, Spanner, Firestore, AlloyDB | Kueri data produksi langsung dari konteks agen |
| **Infrastruktur** | Cloud Run, GKE, Compute Engine | Sediakan, skalakan, dan kelola infrastruktur melalui bahasa alami |
| **Produktivitas** | Gmail, Drive, Calendar, Chat | Ringkas utas, buat draf dokumen, kelola undangan |
| **Keamanan** | Security Operations, Model Armor | Selidiki ancaman, blokir injeksi prompt secara real-time |

> **Tata Kelola:** Gunakan [kebijakan IAM Deny](https://docs.cloud.google.com/mcp/control-mcp-use-iam#deny-all-mcp-tool-use) untuk membatasi alat MCP mana yang dapat dipanggil oleh agen. Gabungkan dengan [Model Armor](https://docs.cloud.google.com/model-armor/model-armor-mcp-google-cloud-integration) untuk bertahan dari injeksi prompt tidak langsung dan eksfiltrasi data.

### Latihan

1. Dapatkan kunci API Developer Knowledge dari proyek Google Cloud Anda
2. Tambahkan server MCP Developer Knowledge ke konfigurasi Gemini CLI Anda menggunakan perintah satu baris di atas
3. Tanyakan kepada agen: *"Bagaimana cara men-deploy layanan Cloud Run dengan domain kustom?"*
4. Verifikasi: Apakah respons mengutip dokumentasi resmi? Bandingkan dengan jawaban tanpa server MCP yang terhubung

---
## Membangun Agen dengan agents-cli

[`agents-cli`](https://github.com/google/agents-cli) adalah sebuah CLI dan paket skill yang mengajarkan agen pengkodean Anda cara membangun, mengevaluasi, dan men-deploy agen di [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform) milik Google. Ini bukan pengganti untuk Gemini CLI — ini adalah alat *untuk* agen pengkodean.

### Pengaturan Cepat

```bash
# Install CLI + skills into all detected coding agents
uvx google-agents-cli setup

# Or install just the skills (your coding agent handles the rest)
npx skills add google/agents-cli
```

> **Prasyarat:** Python 3.11+, [uv](https://docs.astral.sh/uv/getting-started/installation/), dan Node.js. Lihat `setup.sh` untuk catatan lingkungan.

### Alur Kerja Inti

| Perintah | Apa yang Dilakukannya |
|---|---|
| `agents-cli scaffold <name>` | Membuat proyek agen ADK baru dengan struktur praktik terbaik |
| `agents-cli scaffold enhance` | Menambahkan deployment, CI/CD, atau RAG ke proyek agen yang ada |
| `agents-cli eval run` | Menjalankan evaluasi agen (LLM-as-judge, penilaian lintasan) |
| `agents-cli deploy` | Men-deploy ke Google Cloud (Agent Runtime, Cloud Run, atau GKE) |
| `agents-cli publish gemini-enterprise` | Mendaftarkan agen dengan Gemini Enterprise |

### Skill yang Diinstal

Saat Anda menjalankan `agents-cli setup`, ini menginstal 7 skill ke dalam agen pengkodean Anda:

| Skill | Apa yang Dipelajari Agen Pengkodean Anda |
|---|---|
| `google-agents-cli-workflow` | Siklus hidup pengembangan, aturan pelestarian kode, pemilihan model |
| `google-agents-cli-adk-code` | API Python ADK — agen, alat, orkestrasi, callback, status |
| `google-agents-cli-scaffold` | Scaffolding proyek — `create`, `enhance`, `upgrade` |
| `google-agents-cli-eval` | Metodologi evaluasi — metrik, evalset, LLM-as-judge |
| `google-agents-cli-deploy` | Deployment — Agent Runtime, Cloud Run, GKE, CI/CD, rahasia |
| `google-agents-cli-publish` | Pendaftaran Gemini Enterprise |
| `google-agents-cli-observability` | Cloud Trace, logging, integrasi pihak ketiga |

### Kapan Menggunakan agents-cli vs ADK Mentah

| Skenario | Alat |
|---|---|
| Membangun agen dari awal dengan praktik terbaik | `agents-cli scaffold` |
| Menambahkan RAG atau deployment ke agen yang sudah ada | `agents-cli scaffold enhance` |
| Mengevaluasi kualitas agen dengan metrik terstruktur | `agents-cli eval run` |
| Men-deploy secara manual dengan kontrol penuh | `adk deploy` secara langsung |
| Menulis kode ADK tanpa scaffolding | ADK Mentah + agen pengkodean Anda |

### Latihan

1. Instal agents-cli: `uvx google-agents-cli setup`
2. Scaffold agen baru: `agents-cli scaffold my-review-bot`
3. Buka proyek yang di-scaffold di Gemini CLI dan tanyakan: *"Tingkatkan agen ini dengan kemampuan RAG menggunakan Cloud Storage"*
4. Jalankan evaluasi: `agents-cli eval run`
5. Amati bagaimana skill yang diinstal memandu Gemini CLI melalui pola khusus ADK yang sebelumnya tidak diketahuinya

---
## Bacaan Lebih Lanjut

| Sumber Daya | Deskripsi |
|---|---|
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 20 skill rekayasa tingkat produksi untuk agen pengodean |
| [google/agents-cli](https://github.com/google/agents-cli) | CLI + skill untuk membangun agen ADK di Google Cloud |
| [Developer Knowledge MCP](https://developers.google.com/knowledge/mcp) | Mendasarkan agen pada dokumentasi pengembang resmi Google |
| [Server MCP yang Dikelola Google](https://cloud.google.com/blog/products/ai-machine-learning/google-managed-mcp-servers-are-available-for-everyone) | 50+ server MCP perusahaan (Cloud Blog) |
| [Produk MCP yang Didukung](https://docs.cloud.google.com/mcp/supported-products) | Katalog lengkap server MCP yang dikelola Google |
| [GoogleCloudPlatform/scion](https://github.com/GoogleCloudPlatform/scion) | Orkestrasi multi-agen untuk tim |
| [pauldatta/gemini-cli-field-workshop](https://github.com/pauldatta/gemini-cli-field-workshop) | Repositori sumber lokakarya ini |
| [Dokumentasi Gemini CLI](https://geminicli.com) | Dokumentasi resmi |

---
## Langkah Selanjutnya

→ Kembali ke **[Kasus Penggunaan 1: Produktivitas SDLC](sdlc-productivity.md)** untuk fitur-fitur inti

→ Lanjutkan ke **[Kasus Penggunaan 2: Modernisasi Kode Legacy](legacy-modernization.md)** untuk alur kerja brownfield
