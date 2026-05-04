# Gemini CLI Cheatsheet

> Quick reference for everything covered in this workshop.

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
| `Ctrl+X` | Multi-line editor |
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
| `/checkpoint` | Save current state |
| `/restore` | Restore from a checkpoint |
| `/memory show` | Show saved memories |
| `/memory add "..."` | Add a memory |
| `/hooks panel` | Show hook execution status |
| `/skills list` | List available skills |
| `/extensions list` | List installed extensions |
| `/sandbox status` | Check sandbox mode |
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
@import ./docs/coding-standards.md
@import ./docs/architecture.md
```

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
model: gemini-2.5-flash
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
[[rules]]
agent = "*"
tool = "read_file"
action = "deny"
when = { path_matches = ".*\\.env.*" }

# Allow specific agent to run tests
[[rules]]
agent = "implementer"
tool = "run_shell_command"
action = "allow"
when = { command_starts_with = "npm test" }

# Default: ask human
[[rules]]
agent = "*"
tool = "*"
action = "ask_user"
```

---

## Hooks

### Settings.json hook config
```json
{
  "hooks": {
    "BeforeTool": [{
      "matcher": "write_file|replace_in_file",
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
SessionStart → BeforeModel → AfterModel → BeforeTool → AfterTool → AfterAgent → SessionEnd
```

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
