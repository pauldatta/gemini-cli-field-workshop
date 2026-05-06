# Lembar Contekan Gemini CLI

> Referensi cepat untuk semua yang dibahas dalam lokakarya ini.
>
> *Terakhir diperbarui: 2026-05-05 · [Sumber diverifikasi terhadap repositori gemini-cli](https://github.com/google-gemini/gemini-cli)*

---
## Instalasi

```bash
npm install -g @google/gemini-cli
gemini                     # Launch interactive mode
gemini --version           # Check version
```

---
## Pintasan Keyboard

| Pintasan | Aksi |
|---|---|
| `Tab` | Terima saran pengeditan |
| `Shift+Tab` | Beralih antar opsi |
| `Ctrl+G` | Editor eksternal (edit prompt atau rencana) |
| `Ctrl+C` | Batalkan operasi saat ini |
| `↑` / `↓` | Navigasi riwayat prompt |

---
## Perintah Slash

| Perintah | Deskripsi |
|---|---|
| `/plan` | Alihkan Mode Perencanaan (penelitian hanya-baca) |
| `/stats` | Tampilkan penggunaan token dan info model |
| `/clear` | Bersihkan konteks dan mulai dari awal |
| `/tools` | Tampilkan daftar alat yang tersedia |
| `/resume` | Lanjutkan sesi sebelumnya |
| `/rewind` | Kembalikan ke keadaan sebelumnya |
| `/restore` | Pulihkan dari checkpoint (memerlukan [checkpoint diaktifkan](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/checkpointing.md)) |
| `/memory show` | Tampilkan memori yang disimpan |
| `/memory add "..."` | Tambahkan memori |
| `/hooks panel` | Tampilkan status eksekusi hook |
| `/skills list` | Tampilkan daftar skill yang tersedia |
| `/extensions list` | Tampilkan daftar ekstensi yang diinstal |
| `/commands` | Tampilkan daftar perintah kustom |

---
## Mode Headless

```bash
# Simple prompt
gemini -p "Explain this code"

# Structured output
gemini -p "List endpoints as JSON" --output-format json

# Pipe input
cat error.log | gemini -p "Diagnose this error"

# Pipe code
cat file.js | gemini -p "Review this code for bugs"
```

---
## Hierarki GEMINI.md

```
~/.gemini/GEMINI.md          # Global preferences
./GEMINI.md                  # Project conventions
./backend/GEMINI.md          # Subdirectory rules
./frontend/GEMINI.md         # Subdirectory rules
```

### Sintaks impor
```markdown
@./docs/coding-standards.md
@./docs/architecture.md
```

> Lihat [referensi GEMINI.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md) untuk sintaks lengkap.

---
## Sub-agen

```
# Built-in
@codebase_investigator Map the call chain for the login endpoint

# Custom (defined in .gemini/agents/)
@security-scanner Review auth middleware for vulnerabilities
```

### Definisi sub-agen (`.gemini/agents/my-agent.md`)
```markdown
---
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - list_directory
---
You are a specialist in...
```

---
## Ekstensi Conductor

```bash
# Install
gemini extensions install https://github.com/gemini-cli-extensions/conductor

# Set up project context
/conductor:setup prompt="Project description..."

# Create a feature track
/conductor:newTrack prompt="Feature description..."

# Implement the current track
/conductor:implement
```

---
## Mesin Kebijakan (TOML)

```toml
# Deny reading secrets
[[rule]]
toolName = "read_file"
argsPattern = '"file_path":".*\.env"'
decision = "deny"
priority = 100
deny_message = "Reading .env files is not allowed."

# Allow running tests
[[rule]]
toolName = "run_shell_command"
commandPrefix = "npm test"
decision = "allow"
priority = 50

# Default: ask human
[[rule]]
toolName = "*"
decision = "ask_user"
priority = 1
```

> Lihat [referensi Mesin Kebijakan](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md) untuk skema lengkapnya dan [Mengamankan Gemini CLI dengan Mesin Kebijakan](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy) untuk panduan praktis.

---
## Hooks

### Konfigurasi hook settings.json
```json
{
  "hooks": {
    "BeforeTool": [{
      "matcher": "write_file|replace",
      "hooks": [{
        "name": "my-hook",
        "type": "command",
        "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/my-hook.sh",
        "timeout": 3000
      }]
    }]
  }
}
```

### Templat skrip hook
```bash
#!/usr/bin/env bash
input=$(cat)
filepath=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Allow (default)
echo '{}'

# Deny with reason
echo '{"decision":"deny","reason":"Blocked because..."}'

# Inject context
echo '{"systemMessage":"Remember to..."}'
```

### Peristiwa hook
```
SessionStart → BeforeAgent → BeforeModel → BeforeToolSelection →
AfterModel → BeforeTool → AfterTool → AfterAgent → PreCompress →
Notification → SessionEnd
```

> Lihat [Referensi Hooks](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/index.md) untuk siklus hidup peristiwa yang lengkap.

---
## Server MCP

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_TOKEN"
      }
    }
  }
}
```

---
## GitHub Actions

```yaml
- uses: google-github-actions/run-gemini-cli@v1
  with:
    prompt: "Review this PR for code quality and security"
```

---
## Opsi Autentikasi

```bash
# Personal (free tier)
gemini   # OAuth flow

# Vertex AI (enterprise)
gcloud auth application-default login
# + configure .gemini/settings.json with auth.provider = "vertex-ai"
```

---
## Pola yang Berguna

```bash
# Smart commit
git diff --cached | gemini -p "Generate a conventional commit message"

# Code review
git diff main...HEAD | gemini -p "Review these changes"

# Generate docs
gemini -p "Generate JSDoc for all exports in backend/controllers/"

# Batch processing
for f in src/*.js; do gemini -p "Add TypeScript types" < "$f"; done
```

---
## Ekstensi

```bash
# Install from GitHub
gemini extensions install https://github.com/owner/repo

# Install a specific version
gemini extensions install https://github.com/owner/repo --ref v1.2.0

# List installed extensions
gemini extensions list
/extensions list   # from interactive mode

# Update all extensions
gemini extensions update --all

# Create from a template
gemini extensions new my-extension mcp-server

# Develop locally (symlink — changes reflected immediately)
gemini extensions link .

# Disable for this workspace only
gemini extensions disable my-extension --scope workspace
```

### Ekstensi Komunitas Terkemuka

```bash
# Conductor (spec-driven development) — already in UC1
gemini extensions install https://github.com/gemini-cli-extensions/conductor

# Superpowers (TDD, code review, subagent-driven development)
gemini extensions install https://github.com/obra/superpowers

# Oh-My-Gemini-CLI (multi-agent orchestration framework)
gemini extensions install https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli

# Google Workspace CLI (optional — requires Workspace auth)
gemini extensions install https://github.com/googleworkspace/cli
```

### Galeri

Jelajahi ekstensi komunitas: [geminicli.com/extensions/browse](https://geminicli.com/extensions/browse/)

Publikasikan milik Anda sendiri: Tambahkan topik `gemini-cli-extension` ke repo GitHub Anda + tag sebuah rilis.
