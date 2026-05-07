# Workshop Gemini CLI

> **Pemberdayaan langsung untuk pengembang enterprise** — kuasai pengkodean agentic, modernisasi legacy, dan otomatisasi DevOps dengan eksplorasi berbantuan alat dari Gemini CLI, Mode Perencanaan, dan sistem agen yang dapat diperluas.
>
> *Terakhir diperbarui: 2026-05-05 · [Sumber diverifikasi terhadap repositori gemini-cli](https://github.com/google-gemini/gemini-cli)*

**🌐 Bahasa:** [English](/) · [한국어](/ko/) · Bahasa Indonesia · [简体中文](/zh/)

---
## Alur Workshop

Workshop ini disusun sebagai **3 kasus penggunaan progresif**. Masing-masing berdiri sendiri tetapi dibangun di atas keterampilan dari yang sebelumnya:

![Alur Workshop](../assets/workshop-flow.png)

**Mengapa urutan ini:** Kasus Penggunaan 1 membangun keterampilan dasar (instalasi, rekayasa konteks, tata kelola). Kasus Penggunaan 2 menambahkan perencanaan dan pendelegasian. Kasus Penggunaan 3 menghadirkan otomatisasi dan CI/CD sebagai puncaknya. Masing-masing dibangun di atas yang sebelumnya.

---
## Prasyarat

| Persyaratan | Detail |
|---|---|
| **Node.js** | v18+ ([nodejs.org](https://nodejs.org)) |
| **npm** | Disertakan dengan Node.js |
| **Git** | v2.30+ ([git-scm.com](https://git-scm.com)) |
| **Terminal** | Terminal modern apa pun (iTerm2, Windows Terminal, terintegrasi dengan VS Code) |
| **Akun Google** | Akun Google pribadi (tingkat gratis) atau kredensial Vertex AI (perusahaan) |
| **jq** | Untuk contoh hook ([jqlang.github.io/jq](https://jqlang.github.io/jq/download/)) |

---
## Mulai Cepat

```bash
# Clone the workshop repo
git clone https://github.com/pauldatta/gemini-cli-field-workshop.git
cd gemini-cli-field-workshop

# Run the setup script (installs CLI, sets up demo app, copies configs)
./setup.sh

# Start the workshop
cd demo-app && gemini
```

Kemudian buka situs lokakarya: **[pauldatta.github.io/gemini-cli-field-workshop](https://pauldatta.github.io/gemini-cli-field-workshop/)**

---
## Sekilas Kasus Penggunaan

### [1. Peningkatan Produktivitas SDLC](sdlc-productivity.md)
Bangun alur kerja pengembang tingkat perusahaan dari instalasi pertama melalui rekayasa konteks, pengembangan berbasis spesifikasi dengan Conductor, dan pagar pengaman tata kelola. Fondasi untuk semua hal lainnya.

### [2. Modernisasi Kode Legacy](legacy-modernization.md)
Migrasikan aplikasi .NET Framework 4.8 legacy ke .NET 8 di Cloud Run menggunakan Mode Perencanaan, sub-agen kustom, skill, dan checkpointing. Pelajari cara menguraikan basis kode yang sangat besar dengan aman.

### [3. Orkestrasi DevOps Agentic](devops-orchestration.md)
Bangun otomatisasi CI/CD yang mendiagnosis kegagalan pipeline, membuat perbaikan, mengirimkan PR, dan memberi tahu tim — semuanya dari mode headless, hook, dan GitHub Actions.

---
## Aplikasi Demo

Workshop ini menggunakan **[ProShop v2](https://github.com/bradtraversy/proshop-v2)** — sebuah aplikasi eCommerce MERN full-stack (Express.js + MongoDB + React + Redux Toolkit). Aplikasi ini disertakan sebagai submodul git di dalam `demo-app/`.

---
## Alat Bonus

> **[gemini-cli-scanner](https://github.com/pauldatta/gemini-cli-scanner)** — Sebuah alat TUI yang memindai instalasi Gemini CLI lokal Anda dan menghasilkan laporan kematangan. Jalankan setelah lokakarya untuk mengaudit adopsi skill peserta, pola penggunaan alat, dan kualitas konfigurasi — sebuah aktivitas penutup yang bagus yang membuat kemajuan pembelajaran menjadi terlihat.

---
## Sumber Daya

| Sumber Daya | Tautan |
|---|---|
| Dokumentasi Gemini CLI | [geminicli.com/docs](https://geminicli.com/docs/) |
| Gemini CLI GitHub | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) |
| Lembar Contekan CLI | [geminicli.com/docs/cli/cli-reference](https://geminicli.com/docs/cli/cli-reference/) |
| Registri Ekstensi | [github.com/gemini-cli-extensions](https://github.com/gemini-cli-extensions) |
| Server MCP | [geminicli.com/docs/tools/mcp-server](https://geminicli.com/docs/tools/mcp-server/) |
