# Gemini CLI 치트시트

> 이 워크숍에서 다룬 모든 내용에 대한 빠른 참조입니다.

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
| `Tab` | 제안된 편집 수락 |
| `Shift+Tab` | 옵션 순환 |
| `Ctrl+X` | 다중 줄 편집기 |
| `Ctrl+C` | 현재 작업 취소 |
| `↑` / `↓` | 프롬프트 기록 탐색 |

---
## 슬래시 명령어

| 명령어 | 설명 |
|---|---|
| `/plan` | 플랜 모드 전환 (읽기 전용 조사) |
| `/stats` | 토큰 사용량 및 모델 정보 표시 |
| `/clear` | 컨텍스트 지우기 및 새로 시작 |
| `/tools` | 사용 가능한 도구 목록 |
| `/resume` | 이전 세션 재개 |
| `/rewind` | 이전 상태로 롤백 |
| `/checkpoint` | 현재 상태 저장 |
| `/restore` | 체크포인트에서 복원 |
| `/memory show` | 저장된 메모리 표시 |
| `/memory add "..."` | 메모리 추가 |
| `/hooks panel` | 훅 실행 상태 표시 |
| `/skills list` | 사용 가능한 스킬 목록 |
| `/extensions list` | 설치된 확장 프로그램 목록 |
| `/sandbox status` | 샌드박스 모드 확인 |
| `/commands` | 사용자 지정 명령어 목록 |

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
@import ./docs/coding-standards.md
@import ./docs/architecture.md
```

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
model: gemini-2.5-flash
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
## 훅

### settings.json 훅 설정
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
SessionStart → BeforeModel → AfterModel → BeforeTool → AfterTool → AfterAgent → SessionEnd
```

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
