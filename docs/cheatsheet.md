# Gemini CLI Cheatsheet

> Quick reference for everything covered in this workshop.
>
> *Last updated: 2026-05-05 · [Source verified against gemini-cli repository](https://github.com/google-gemini/gemini-cli)*

---

## Installation

```bash
npm install -g @google/gemini-cli
gemini                     # Launch interactive mode
gemini --version           # Check version
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Tab` | Accept suggested edit |
| `Shift+Tab` | Cycle through options |
| `Ctrl+G` | External editor (edit prompt or plan) |
| `Ctrl+C` | Cancel current operation |
| `↑` / `↓` | Navigate prompt history |

---

## Slash Commands

| Command | Description |
|---|---|
| `/plan` | Toggle Plan Mode (read-only research) |
| `/stats` | Show token usage and model info |
| `/clear` | Clear context and start fresh |
| `/tools` | List available tools |
| `/resume` | Resume a previous session |
| `/rewind` | Roll back to a previous state |
| `/restore` | Restore from a checkpoint (requires [checkpointing enabled](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/checkpointing.md)) |
| `/memory show` | Show saved memories |
| `/memory reload` | Reload memory from source files |
| `/memory list` | List all GEMINI.md files in use |
| `/memory inbox` | Review auto-extracted memory candidates (requires `experimental.autoMemory: true`) |
| ~~`/memory add "..."`~~ | ~~Add a memory~~ — **removed in v0.41.1**, use natural language instead: *"Remember that..."* ([details](../CHANGELOG.md)) |
| `/hooks panel` | Show hook execution status |
| `/skills list` | List available skills |
| `/extensions list` | List installed extensions |
| `/commands` | List custom commands |

---

## Headless Mode

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

## GEMINI.md Hierarchy

```
~/.gemini/GEMINI.md          # Global preferences
./GEMINI.md                  # Project conventions
./backend/GEMINI.md          # Subdirectory rules
./frontend/GEMINI.md         # Subdirectory rules
```

### Import syntax
```markdown
@./docs/coding-standards.md
@./docs/architecture.md
```

> See [GEMINI.md reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md) for full syntax.

---

## Subagents

```
# Built-in
@codebase_investigator Map the call chain for the login endpoint

# Custom (defined in .gemini/agents/)
@security-scanner Review auth middleware for vulnerabilities
```

### Subagent definition (`.gemini/agents/my-agent.md`)
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

## Conductor Extension

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

## Policy Engine (TOML)

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

> See [Policy Engine reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md) for the full schema and [Secure Gemini CLI with the Policy Engine](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy) for a practical walkthrough.

---

## Hooks

### Settings.json hook config
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

### Hook script template
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

### Hook events
```
SessionStart → BeforeAgent → BeforeModel → BeforeToolSelection →
AfterModel → BeforeTool → AfterTool → AfterAgent → PreCompress →
Notification → SessionEnd
```

> See [Hooks reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/index.md) for the complete event lifecycle.

---

## MCP Servers

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

## Auth Options

```bash
# Personal (free tier)
gemini   # OAuth flow

# Vertex AI (enterprise)
gcloud auth application-default login
# + configure .gemini/settings.json with auth.provider = "vertex-ai"
```

---

## Useful Patterns

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

## Extensions

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

### Notable Community Extensions

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

### Gallery

Browse community extensions: [geminicli.com/extensions/browse](https://geminicli.com/extensions/browse/)

Publish your own: Add `gemini-cli-extension` topic to your GitHub repo + tag a release.
