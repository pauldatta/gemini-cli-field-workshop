# Gemini CLI 치트시트

> 이 워크숍에서 다룬 모든 내용에 대한 빠른 참조 가이드입니다.
>
> *마지막 업데이트: 2026-05-05 · [gemini-cli 저장소에 대해 검증된 소스](https://github.com/google-gemini/gemini-cli)*

---
## 설치

```bash
npm install -g @google/gemini-cli
gemini                     # Launch interactive mode
gemini --version           # Check version
```

---
## 키보드 단축키

| 단축키 | 동작 |
|---|---|
| `Tab` | 제안된 수정 사항 수락 |
| `Shift+Tab` | 옵션 순환 |
| `Ctrl+G` | 외부 편집기 (프롬프트 또는 플랜 편집) |
| `Ctrl+C` | 현재 작업 취소 |
| `↑` / `↓` | 프롬프트 기록 탐색 |

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
| ~~`/memory add "..."`~~ | ~~Add a memory~~ — **removed in v0.41.1**, use natural language instead: *"Remember that..."* ([details](../../CHANGELOG.md)) |
| `/hooks panel` | Show hook execution status |
| `/skills list` | List available skills |
| `/extensions list` | List installed extensions |
| `/commands` | List custom commands |

---


## 헤드리스 모드

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
## GEMINI.md 계층 구조

```
~/.gemini/GEMINI.md          # Global preferences
./GEMINI.md                  # Project conventions
./backend/GEMINI.md          # Subdirectory rules
./frontend/GEMINI.md         # Subdirectory rules
```

### 가져오기 구문
```markdown
@./docs/coding-standards.md
@./docs/architecture.md
```

> 전체 구문은 [GEMINI.md 레퍼런스](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md)를 참조하세요.

---
## 서브에이전트

```
# Built-in
@codebase_investigator Map the call chain for the login endpoint

# Custom (defined in .gemini/agents/)
@security-scanner Review auth middleware for vulnerabilities
```

### 서브에이전트 정의 (`.gemini/agents/my-agent.md`)
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
## Conductor 확장 프로그램

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
## 정책 엔진 (TOML)

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

> 전체 스키마에 대해서는 [정책 엔진 참조](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md)를 참조하고, 실용적인 연습에 대해서는 [정책 엔진으로 Gemini CLI 보호하기](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy)를 참조하세요.

---
## 훅

### Settings.json 훅 설정
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

### 훅 스크립트 템플릿
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

### 훅 이벤트
```
SessionStart → BeforeAgent → BeforeModel → BeforeToolSelection →
AfterModel → BeforeTool → AfterTool → AfterAgent → PreCompress →
Notification → SessionEnd
```

> 전체 이벤트 수명 주기는 [훅 참조](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/index.md)를 확인하세요.

---
## MCP 서버

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
## 인증 옵션

```bash
# Personal (free tier)
gemini   # OAuth flow

# Vertex AI (enterprise)
gcloud auth application-default login
# + configure .gemini/settings.json with auth.provider = "vertex-ai"
```

---
## 유용한 패턴

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
## 확장 프로그램

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

### 주목할 만한 커뮤니티 확장 프로그램

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

### 갤러리

커뮤니티 확장 프로그램 찾아보기: [geminicli.com/extensions/browse](https://geminicli.com/extensions/browse/)

직접 게시하기: GitHub 저장소에 `gemini-cli-extension` 주제를 추가하고 릴리스를 태그하세요.
