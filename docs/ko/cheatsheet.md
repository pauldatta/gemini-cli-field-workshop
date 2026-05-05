# Gemini CLI 치트시트

> 이 워크숍에서 다룬 모든 내용에 대한 빠른 참조입니다.
>
> *최종 업데이트: 2026-05-05 · [gemini-cli 저장소 기준 검증됨](https://github.com/google-gemini/gemini-cli)*

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
| `Ctrl+X` | 여러 줄 편집기 |
| `Ctrl+C` | 현재 작업 취소 |
| `↑` / `↓` | 프롬프트 기록 탐색 |

---

## 슬래시 명령어

| 명령어 | 설명 |
|---|---|
| `/plan` | 플랜 모드 전환 (읽기 전용 조사) |
| `/stats` | 토큰 사용량 및 모델 정보 표시 |
| `/clear` | 컨텍스트 지우기 및 새로 시작 |
| `/tools` | 사용 가능한 도구 목록 표시 |
| `/resume` | 이전 세션 재개 |
| `/rewind` | 이전 상태로 롤백 |
| `/restore` | 체크포인트에서 복원 ([체크포인팅 활성화](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/checkpointing.md) 필요) |
| `/memory show` | 저장된 메모리 표시 |
| `/memory add "..."` | 메모리 추가 |
| `/hooks panel` | 훅 실행 상태 표시 |
| `/skills list` | 사용 가능한 스킬 목록 표시 |
| `/extensions list` | 설치된 확장 프로그램 목록 표시 |
| `/commands` | 사용자 지정 명령어 목록 표시 |

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

### Import 구문
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
# 시크릿 읽기 차단
[[rule]]
toolName = "read_file"
argsPattern = '"file_path":".*\.env"'
decision = "deny"
priority = 100
deny_message = "Reading .env files is not allowed."

# 테스트 실행 허용
[[rule]]
toolName = "run_shell_command"
commandPrefix = "npm test"
decision = "allow"
priority = 50

# 기본값: 사용자에게 확인
[[rule]]
toolName = "*"
decision = "ask_user"
priority = 1
```

> 전체 스키마는 [정책 엔진 레퍼런스](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md)를, 실용적인 안내는 [정책 엔진으로 Gemini CLI 보안 강화하기](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy)를 참조하세요.

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

> 전체 이벤트 라이프사이클은 [훅 레퍼런스](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/index.md)를 참조하세요.

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

직접 게시하기: GitHub 저장소에 `gemini-cli-extension` 토픽을 추가하고 릴리스에 태그를 지정하세요.
