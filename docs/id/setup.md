# Pengaturan Lingkungan

> Selesaikan ini sebelum memulai kasus penggunaan apa pun. Membutuhkan waktu sekitar 15 menit.
>
> *Terakhir diperbarui: 2026-05-05 · [Sumber diverifikasi terhadap repositori gemini-cli](https://github.com/google-gemini/gemini-cli)*

---
## Persyaratan Sistem

| Komponen       | Minimum  | Direkomendasikan                                                   |
| -------------- | -------- | ------------------------------------------------------------------ |
| **Node.js**    | v18.0.0  | v20+ (LTS)                                                         |
| **npm**        | v9+      | v10+                                                               |
| **Git**        | v2.30+   | v2.40+                                                             |
| **Terminal**   | Apa saja | iTerm2 (macOS), Windows Terminal, atau terintegrasi dengan VS Code |
| **Ruang Disk** | 500MB    | 1GB (termasuk aplikasi demo + node_modules)                        |
| **jq**         | Opsional | Diperlukan untuk contoh hook                                       |

---
## Langkah 1: Kloning Workshop

```bash
git clone https://github.com/pauldatta/gemini-cli-field-workshop.git
cd gemini-cli-field-workshop
```

---
## Langkah 2: Jalankan Skrip Pengaturan

Skrip pengaturan menangani semuanya — instalasi Gemini CLI, checkout aplikasi demo, dan konfigurasi:

```bash
chmod +x setup.sh
./setup.sh
```

**Apa yang dilakukannya:**

1. Memverifikasi bahwa Node.js, npm, dan Git telah terinstal
2. Menginstal/memperbarui Gemini CLI secara global (`npm install -g @google/gemini-cli`)
3. Menginisialisasi submodul `demo-app/` (ProShop v2) dan menjalankan `npm install`
4. Menyalin konfigurasi sampel ke dalam aplikasi demo:
   - Hierarki konteks `GEMINI.md`
   - Skrip hook (pemindai rahasia, pengujian otomatis, pencatat sesi, penjaga jalur)
   - Aturan mesin kebijakan
   - Definisi sub-agen kustom
5. Memverifikasi autentikasi Gemini CLI

---
## Langkah 3: Autentikasi

### Opsi A: Akun Google Pribadi (Tier Gratis)

Terbaik untuk lokakarya dan evaluasi. Tidak memerlukan proyek GCP.

```bash
cd demo-app
gemini
# Follow the browser-based OAuth flow
```

> **Batas tier gratis:** Tier Google AI pribadi memiliki batas harian yang besar yang cocok untuk penggunaan lokakarya. Lihat [Kuota dan harga](https://geminicli.com/docs/resources/quota-and-pricing/).

### Opsi B: Vertex AI (Enterprise)

Untuk produksi dan penerapan enterprise. Memerlukan proyek GCP dengan penagihan.

```bash
# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Authenticate
gcloud auth application-default login
```

Gemini CLI akan mendeteksi kredensial Vertex AI secara otomatis. Untuk autentikasi yang diberlakukan enterprise, lihat [Panduan Enterprise](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md).

---
## Langkah 4: Verifikasi Instalasi

```bash
# Check Gemini CLI version
gemini --version

# Quick test (should respond instantly)
gemini -p "Say 'Workshop ready!' in exactly two words."

# Verify the demo app is set up
ls demo-app/GEMINI.md          # Should exist
ls demo-app/.gemini/hooks/     # Should contain 4 hook scripts
ls demo-app/.gemini/policies/  # Should contain team-guardrails.toml
```

---
## Pemecahan Masalah

| Masalah                                     | Solusi                                                                                                                                                                      |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `npm install -g` gagal dengan `EACCES`      | Gunakan `sudo npm install -g @google/gemini-cli` atau perbaiki izin npm: [dokumentasi npm](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally) |
| `gemini: command not found` setelah instalasi | Mulai ulang terminal Anda atau jalankan `source ~/.bashrc` / `source ~/.zshrc`                                                                                                           |
| Alur OAuth tidak membuka browser           | Salin URL dari terminal dan buka secara manual                                                                                                                           |
| `git submodule update` gagal              | Jalankan `git submodule init && git submodule update --recursive`                                                                                                                  |
| `npm install` aplikasi demo gagal              | Periksa versi Node.js (`node --version`). ProShop v2 membutuhkan Node 18+.                                                                                                       |
| Kesalahan batas permintaan (rate limit) selama lokakarya         | Beralih ke autentikasi Vertex AI, atau tunggu 60 detik dan coba lagi                                                                                              |
| hook tidak dieksekusi                       | Jalankan `chmod +x demo-app/.gemini/hooks/*.sh`                                                                                                                                    |
| `jq: command not found`                   | Instal jq: `brew install jq` (macOS) atau `apt install jq` (Linux)                                                                                                             |

---
## Pengaturan Manual (jika setup.sh gagal)

Jika skrip pengaturan tidak berfungsi pada sistem Anda, jalankan langkah-langkah ini secara manual:

```bash
# 1. Install Gemini CLI
npm install -g @google/gemini-cli

# 2. Initialize demo app
git submodule add https://github.com/bradtraversy/proshop-v2.git demo-app
cd demo-app && npm install && cd ..

# 3. Copy configs
mkdir -p demo-app/.gemini/agents demo-app/.gemini/hooks demo-app/.gemini/policies
cp samples/config/settings.json demo-app/.gemini/settings.json
cp samples/config/policy.toml demo-app/.gemini/policies/team-guardrails.toml
cp samples/agents/security-scanner.md demo-app/.gemini/agents/
cp samples/hooks/*.sh demo-app/.gemini/hooks/
chmod +x demo-app/.gemini/hooks/*.sh
cp samples/gemini-md/project-gemini.md demo-app/GEMINI.md
mkdir -p demo-app/backend
cp samples/gemini-md/backend-gemini.md demo-app/backend/GEMINI.md

# 4. Authenticate
cd demo-app && gemini
```

---
## Langkah Selanjutnya

→ Mulai dengan **[Kasus Penggunaan 1: Peningkatan Produktivitas SDLC](sdlc-productivity.md)**
