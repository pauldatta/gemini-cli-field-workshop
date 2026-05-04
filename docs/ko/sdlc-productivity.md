# 사용 사례 1: SDLC 생산성 향상

> **소요 시간:** 약 60분  
> **목표:** 초기 설치부터 컨텍스트 엔지니어링, Conductor를 사용한 스펙 기반 개발, 그리고 거버넌스 가드레일에 이르기까지 엔터프라이즈급 개발자 워크플로우를 구축합니다.  
> **실습 PRD:** [제품 위시리스트 기능](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_sdlc_productivity.md)

---
## 1.1 — 첫 만남 (10분)

### Gemini CLI 설치

```bash
npm install -g @google/gemini-cli
```

### 실행 및 인증

```bash
cd demo-app
gemini
# Follow the OAuth flow in your browser
```

### 첫 번째 프롬프트

에이전트가 코드베이스를 읽을 수 있다는 것을 증명하는 것으로 시작해 보세요:

```
What is the tech stack of this project? List the main frameworks, 
database, and authentication mechanism.
```

> **무슨 일이 일어나고 있나요:** 에이전트가 `package.json`을 읽고, 디렉터리 구조를 스캔하며, 아키텍처를 매핑합니다. 열려 있는 파일로만 제한되는 도구들과 달리, Gemini CLI는 단일 세션에서 전체 코드베이스를 유지할 수 있습니다. 즉, 컨트롤러, 라우트, 모델 및 미들웨어가 어떻게 연결되는지 이해합니다.

### 도구 탐색

```
/tools
```

이것은 에이전트가 사용할 수 있는 모든 도구를 보여줍니다. 파일 작업, 셸 명령, 웹 검색 및 구성한 모든 MCP 서버가 포함됩니다.

### 주요 단축키

| 단축키 | 동작 |
|---|---|
| `Tab` | 제안된 편집 수락 |
| `Shift+Tab` | 편집 옵션 순환 |
| `Ctrl+X` | 여러 줄 편집기 열기 |
| `Ctrl+C` | 현재 작업 취소 |
| `/stats` | 이 세션의 토큰 사용량 표시 |
| `/clear` | 컨텍스트를 지우고 새로 시작 |

---
## 1.2 — GEMINI.md를 활용한 컨텍스트 엔지니어링 (15분)

### 컨텍스트 계층 구조

Gemini CLI는 여러 수준에서 `GEMINI.md` 파일을 읽으며, 각 수준마다 더 구체적인 컨텍스트를 추가합니다:

![GEMINI.md 컨텍스트 계층 구조](../assets/context-hierarchy.png)

> **JIT 컨텍스트 검색:** 에이전트는 현재 작업 중인 파일과 관련된 GEMINI.md 파일만 로드합니다. `backend/controllers/productController.js`를 편집하는 경우, 프로젝트 GEMINI.md와 백엔드 GEMINI.md를 로드하지만 프론트엔드 GEMINI.md는 로드하지 않습니다.

### 프로젝트 GEMINI.md 검토

```bash
cat GEMINI.md
```

이 파일(설정 중 [`samples/gemini-md/project-gemini.md`](../../samples/gemini-md/project-gemini.md)에서 복사됨)은 다음을 정의합니다:
- 아키텍처 규칙 (라우트 → 컨트롤러 → 모델)
- 안티 패턴 (콜백 금지, 하드코딩된 자격 증명 금지)
- 테스트 표준

### 컨텍스트 적용 테스트

에이전트에게 규칙을 위반하도록 요청하고 스스로 수정하는지 확인합니다:

```
Add a new GET endpoint to fetch featured products. 
Put the database query logic directly in the route file.
```

> **예상 결과:** 에이전트는 이것이 GEMINI.md 규칙("라우트 파일에 비즈니스 로직 금지")을 위반한다는 것을 인식하고, 대신 위임하는 얇은 라우트와 함께 컨트롤러에 엔드포인트를 생성해야 합니다.

### 백엔드 컨텍스트 추가

```bash
cat backend/GEMINI.md
```

이는 오류 처리, 비동기 패턴 및 보안에 대한 백엔드 전용 규칙을 추가합니다.

### 메모리: 영구적인 지식

에이전트는 세션 간에 정보를 기억할 수 있습니다:

```
/memory show
```

프로젝트별 지식 추가:

```
/memory add "The ProShop app uses port 5000 for the backend API 
and port 3000 for the React dev server. MongoDB runs on default 
port 27017. Test database is 'proshop_test'."
```

에이전트는 세션 중에 중요한 패턴을 발견하면 `save_memory` 도구를 사용하여 스스로 메모리를 저장할 수도 있습니다.

### .geminiignore 파일

에이전트가 볼 수 있는 것과 볼 수 없는 것을 제어합니다:

```bash
cat .geminiignore
# node_modules/
# .env
# *.log
# coverage/
```

> **이것이 중요한 이유:** `.geminiignore`가 없으면 에이전트는 `node_modules/`(수십만 개의 파일)를 읽는 데 컨텍스트 토큰을 낭비할 수 있습니다. 이 파일이 있으면 에이전트는 소스 코드에만 집중합니다.

---
## 1.3 — Conductor: 컨텍스트 우선 빌드 (15분)

### 왜 Conductor인가?

플랜 모드는 일회성 기능에 매우 유용합니다. 하지만 지속적인 사양, 단계별 구현 계획, 그리고 여러 세션에 걸친 진행 상황 추적이 필요한 며칠짜리 프로젝트의 경우 — 바로 Conductor가 필요합니다.

### Conductor 설치

```bash
gemini extensions install https://github.com/gemini-cli-extensions/conductor
```

확인:

```
/extensions list
```

### 프로젝트 컨텍스트 설정

```
/conductor:setup prompt="This is a MERN stack eCommerce app (ProShop). 
Express.js backend with MongoDB. React frontend with Redux Toolkit. 
Use clean architecture: routes register middleware and delegate to 
controllers. Controllers handle business logic. Models define schema. 
No business logic in route files."
```

### Conductor가 생성한 항목 검토

```bash
ls conductor/
# product.md  tech-stack.md  tracks/

cat conductor/product.md
cat conductor/tech-stack.md
```

> **핵심 인사이트:** 이 파일들은 이제 프로젝트의 진실의 원천입니다. 이 파일들은 마크다운(Markdown) 형식이며, 리포지토리에 존재하고, 다른 코드와 마찬가지로 커밋되고 검토됩니다. 내일 다시 돌아오거나 이 프로젝트를 동료에게 넘길 때 — AI는 여러분이 중단한 바로 그 지점부터 다시 시작합니다. 상태는 메모리가 아닌 파일에 존재합니다.

### 기능 트랙 생성

위시리스트 PRD를 기능 사양으로 사용합니다:

```
/conductor:newTrack prompt="Add a product wishlist feature. Users can 
add products to a personal wishlist from the product detail page. 
The wishlist is stored in MongoDB as an array of product references 
on the User model. Show a wishlist page with the ability to remove 
items or move them to the cart."
```

### 생성된 아티팩트 검토

```bash
# The specification
cat conductor/tracks/*/spec.md

# The implementation plan
cat conductor/tracks/*/plan.md
```

> **계획을 살펴보세요.** 특정 작업과 체크박스가 있는 여러 단계로 나뉘어 있습니다. 1단계: 데이터베이스 스키마. 2단계: API 엔드포인트. 3단계: 프론트엔드 컴포넌트. 4단계: 테스트. 에이전트는 이 계획을 순서대로 따르며 진행하면서 작업을 체크합니다.

> **접근 방식에 동의하지 않는 경우** — 예를 들어 REST 대신 GraphQL을 원한다면 — `plan.md`를 직접 편집하고 다시 실행하세요. 이 계획은 여러분과 에이전트 사이의 계약입니다.

### 구현 (시간이 허락하는 경우)

```
/conductor:implement
```

> **전체 코드베이스 인식:** 지금 에이전트는 여러분의 `GEMINI.md` 규칙, Conductor 제품 문서, 사양, 구현 계획, 그리고 전체 ProShop 코드베이스를 — 모두 동시에 컨텍스트에 유지하고 있습니다. 파일 분할이나 수동 컨텍스트 관리가 필요 없습니다. 에이전트는 모든 조각이 어떻게 연결되는지 파악합니다.

### 상태 확인

```
What's the current status on all active Conductor tracks?
```

---
## 1.4 — 확장 프로그램 및 MCP 서버 (10분)

### 확장 프로그램 개요

확장 프로그램은 스킬, 서브에이전트, 훅, 정책 및 MCP 서버를 설치 가능한 단위로 패키징합니다:

```
/extensions list
```

### MCP 서버: 외부 도구 연결

MCP(Model Context Protocol)는 Gemini CLI를 외부 데이터 소스 및 도구에 연결합니다:

```bash
# Check your MCP configuration
cat .gemini/settings.json
```

settings.json에는 GitHub MCP 서버가 포함되어 있습니다. `GITHUB_TOKEN`으로 구성되면 에이전트는 다음을 수행할 수 있습니다:
- 리포지토리, 이슈 및 PR 읽기
- 이슈 및 댓글 생성
- 풀 리퀘스트 열기

### 연결된 프롬프트 시도해보기

```
List the open issues in this repository using the GitHub MCP server.
```

### 서브에이전트를 위한 MCP 도구 격리

서브에이전트가 액세스할 수 있는 MCP 도구를 제한할 수 있습니다:

```json
{
  "mcpServers": {
    "bigquery": {
      "includeTools": ["query", "list_tables"],
      "excludeTools": ["delete_table", "drop_dataset"]
    }
  }
}
```

> **엔터프라이즈 가치:** `db-analyst` 서브에이전트는 읽기 전용 BigQuery 액세스 권한을 얻습니다. 테이블을 쿼리하고 나열할 수는 있지만 데이터를 삭제할 수는 없습니다. 도구 격리는 에이전트 수준의 거버넌스입니다.

---
## 1.5 — 거버넌스 및 정책 엔진 (10분)

### 정책 엔진

정책은 TOML로 작성된 코드형 가드레일(guardrails-as-code)입니다:

```bash
cat .gemini/policies/team-guardrails.toml
```

### 정책 규칙 실행

샘플 정책:
- `.env`, `.ssh` 및 자격 증명 파일 읽기를 **거부(Denies)**합니다.
- 파괴적인 셸 명령(`rm -rf`, `curl`)을 **거부(Denies)**합니다.
- 구현자(implementer) 에이전트가 `npm test` 및 `npm run lint`를 실행하도록 **허용(Allows)**합니다.
- 그 외의 모든 항목은 기본적으로 `ask_user`(사람의 승인 필요)로 **설정(Defaults)**합니다.

### 정책 테스트

```
Read the contents of the .env file in this project.
```

> **예상 결과:** 에이전트가 정책 엔진에 의해 차단되어야 합니다. 차단 이유를 설명하는 거부 메시지가 표시됩니다.

### 5계층 정책 시스템

정책은 우선순위에 따라 계단식으로 적용됩니다:

```
Default → Extension → Workspace → User → Admin (highest)
```

관리자 정책(시스템 수준에서 설정됨)은 다른 모든 것을 재정의합니다. 이는 기업이 조직 전체의 가드레일을 적용하는 방법입니다.

### 훅 실행

`settings.json`에 구성된 훅은 이미 활성화되어 있습니다:

1. **SessionStart → session-context**: 이 세션이 시작될 때 브랜치 이름과 변경된(dirty) 파일 수를 주입했습니다.
2. **BeforeTool → secret-scanner**: 하드코딩된 자격 증명이 있는지 모든 파일 쓰기를 감시합니다.
3. **BeforeTool → git-context**: 파일 수정 전에 최근 git 기록을 주입합니다.
4. **AfterTool → test-nudge**: 에이전트에게 테스트 실행을 고려하도록 상기시킵니다.

훅 상태 확인:

```
/hooks panel
```

> **설계 철학:** 이러한 훅은 무거운 테스트 실행기가 아니라 가벼운 컨텍스트 주입기이자 모델 스티어링 도구입니다. 총 지연 시간을 200ms 미만으로 추가하며 시스템에 부담을 주지 않으면서 에이전트의 의사 결정 품질을 향상시킵니다.

### 엔터프라이즈 구성

조직 전체 설정의 경우 관리자는 다음을 구성할 수 있습니다:

```json
{
  "tools": {
    "allowed": ["read_file", "write_file", "run_shell_command"],
    "blocked": ["web_fetch"]
  },
  "auth": {
    "required": true,
    "provider": "vertex-ai"
  }
}
```

### 샌드박스

Gemini CLI는 샌드박스 실행을 지원합니다:
- **Docker 샌드박스**: 격리된 컨테이너에서 셸 명령을 실행합니다.
- **macOS seatbelt**: macOS 샌드박스를 사용하여 파일 시스템 액세스를 제한합니다.

```
# Check current sandbox mode
/sandbox status
```

---
## 1.6 — 세션 관리 (5분)

### 이전 세션 재개

```
/resume
```

최근 세션 목록을 표시합니다. 중단한 부분부터 이어서 진행할 세션을 선택하세요.

### 이전 상태로 되감기

```
/rewind
```

현재 세션의 변경 사항 타임라인을 표시합니다. 롤백할 시점을 선택하세요.

### 사용자 정의 명령어

```
/commands
```

사용 가능한 사용자 정의 명령어를 표시합니다. `.gemini/commands/`에서 직접 정의할 수 있습니다.

---
## 요약: 배운 내용

| 기능 | 역할 |
|---|---|
| **GEMINI.md 계층 구조** | 모든 수준에서 프로젝트 규칙을 인코딩합니다 — 에이전트가 이를 자동으로 따릅니다 |
| **JIT 컨텍스트 검색** | 현재 작업과 관련된 컨텍스트 파일만 로드합니다 |
| **메모리** | 세션 간에 지식을 유지합니다 |
| **Conductor** | 영구적인 계획 및 진행 상황 추적을 통한 사양 주도 개발 |
| **확장 프로그램** | 스킬, 에이전트, 훅 및 정책의 설치 가능한 패키지 |
| **MCP 서버** | 외부 도구(GitHub, BigQuery, Jira)에 연결합니다 |
| **정책 엔진** | TOML의 코드형 가드레일(Guardrails-as-code) — deny, allow 또는 ask_user |
| **훅** | 에이전트 수명 주기 이벤트에서의 경량 컨텍스트 주입 및 모델 스티어링 |
| **샌드박싱** | 신뢰할 수 없는 환경을 위한 격리된 실행 |

---
## 1.7 — 전체 SDLC를 위한 맞춤형 에이전트 (20분)

> **파워 유저 및 재참여자를 위한 섹션입니다.** 이 섹션은 코드 생성을 넘어 리뷰, 문서화, 규정 준수 및 릴리스 관리를 포함하는 **전체 소프트웨어 개발 수명 주기(SDLC)**를 다룹니다. 각 에이전트는 독립적으로 사용할 수 있습니다. 어느 시점에서든 바로 시작해 보세요.

### 내장 에이전트

Gemini CLI는 즉시 사용할 수 있는 기본 에이전트와 함께 제공됩니다. 다음 명령어로 목록을 확인하세요:

```
/agents
```

| 에이전트 | 목적 | 사용 시기 |
|---|---|---|
| **`generalist`** | 모든 도구에 접근 가능한 범용 에이전트 | 대용량 또는 턴이 많이 필요한 작업 |
| **`codebase_investigator`** | 아키텍처 매핑 및 종속성 분석 | "이 앱에서 인증 흐름이 어떻게 되는지 매핑해 줘" |
| **`cli_help`** | Gemini CLI 문서 전문가 | "MCP 도구 격리를 어떻게 설정하나요?" |

`@agent` 구문을 사용하여 명시적으로 위임하세요:

```
@codebase_investigator Map the complete data flow from the React 
product page through Redux, to the Express API, to the MongoDB model.
```

> **이것이 중요한 이유:** investigator는 집중된 컨텍스트와 함께 읽기 전용 모드로 작동합니다. 아키텍처를 매핑하는 동안 실수로 파일을 수정하지 않습니다. 그런 다음 메인 에이전트가 해당 맵을 사용하여 구현을 계획합니다.

---

### 맞춤형 에이전트 구축

맞춤형 에이전트는 YAML 프런트매터가 포함된 마크다운 파일이며, `.gemini/agents/`에 저장됩니다. 각 에이전트는 다음을 갖습니다:

- `@agent-name`으로 호출하는 **이름**
- CLI가 자동 라우팅에 사용하는 **설명**
- 에이전트가 접근할 수 있는 대상을 제어하는 **도구 허용 목록**
- 전문 지식과 출력 형식을 정의하는 **시스템 프롬프트**

> **핵심 설계 원칙:** 생각하는 역할과 실행하는 역할을 분리하세요. 조사 및 리뷰에는 읽기 전용 에이전트를 사용합니다. 구현에는 쓰기 권한이 있는 에이전트를 사용합니다. 동일한 컨텍스트에서 조사와 변경을 절대 혼합하지 마세요.

아래 예제는 Gemini CLI가 단순한 코드 생성기가 아니라 리뷰, 문서화, 규정 준수 및 릴리스 관리를 포괄하는 **완전한 SDLC 플랫폼**임을 보여줍니다.

---

### 에이전트 1: PR 리뷰어

품질, 버그 및 스타일 위반에 대한 코드 변경 사항을 검토하는 읽기 전용 에이전트입니다.

```bash
cp samples/agents/pr-reviewer.md .gemini/agents/
```

```markdown
<!-- .gemini/agents/pr-reviewer.md -->
---
name: pr-reviewer
description: Review code changes for quality, bugs, and style violations.
model: gemini-3.1-pro-preview
tools:
  - read_file
  - glob
  - grep_search
  - run_shell_command
---

You are a senior engineer conducting a pull request review.

## Review Checklist
1. **Correctness**: Does the code do what it claims?
2. **Edge Cases**: What happens with empty inputs, nulls, boundary values?
3. **Style Consistency**: Does it match the project's existing patterns?
4. **Test Coverage**: Are there tests for happy path AND error cases?
5. **Security**: User input passed to DB queries unparameterized?

## Output Format
For each finding:
- **File:Line** — exact location
- **Severity** — Critical / Suggestion / Nit
- **Issue** — one-sentence description
- **Suggestion** — concrete code improvement

Keep feedback constructive. Acknowledge good patterns when you see them.
```

**직접 해보기:**

```
@pr-reviewer Review all files changed in the last commit
```

> **CI/CD에서 자동화하기:** 모든 풀 리퀘스트에 대한 자동화된 PR 리뷰를 위해 공식 [`google-github-actions/run-gemini-cli`](https://github.com/google-github-actions/run-gemini-cli) GitHub Action을 사용하세요. CLI에서 `/setup-github` 명령어로 설치하면 워크플로 파일, 디스패치 핸들러 및 이슈 분류를 자동으로 설정합니다. 작동하는 예제는 [`samples/cicd/gemini-pr-review.yml`](../../samples/cicd/gemini-pr-review.yml)을 참조하세요.

---

### 에이전트 2: 문서 작성자

소스 코드에서 API 문서, README 및 코드 주석을 생성합니다. 읽기 전용이므로 파일을 절대 수정할 수 없습니다.

```bash
cp samples/agents/doc-writer.md .gemini/agents/
```

```markdown
<!-- .gemini/agents/doc-writer.md -->
---
name: doc-writer
description: Generate API documentation and README sections from source code.
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - glob
  - grep_search
---

You are a technical writer generating documentation from source code.
- Read the actual source — never guess at API signatures
- Document: endpoint, method, auth, request body, response format
- Add usage examples with curl or fetch
- Flag undocumented endpoints or missing error handling
```

**직접 해보기:**

```
@doc-writer Generate API documentation for all endpoints in backend/routes/
```

> **아우터 루프 가치:** 이는 수 시간의 수동 문서화 작업을 대체합니다. 각 스프린트 후에 실행하여 문서를 최신 상태로 유지하세요.

---

### 에이전트 3: 규정 준수 검사기

라이선스 헤더, PII 노출, 하드코딩된 비밀 정보 및 정책 위반에 대해 코드를 감사합니다.

```bash
cp samples/agents/compliance-checker.md .gemini/agents/
```

```markdown
<!-- .gemini/agents/compliance-checker.md -->
---
name: compliance-checker
description: Audit code for compliance, PII exposure, and policy violations.
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - glob
  - grep_search
---

You are a compliance auditor. Scan for:
1. License headers — every source file needs one
2. PII exposure — emails, phone numbers, SSNs in code or logs
3. Hardcoded secrets — API keys, passwords, tokens
4. Logging hygiene — no user data in log statements

Report as: Category / Severity / File:Line / Finding / Remediation.
If clean, state "✅ PASS: [category]".
```

**직접 해보기:**

```
@compliance-checker Audit the entire backend/ directory
```

> **엔터프라이즈 가치:** 삼성의 평가는 특히 "콘텐츠 필터링 및 중앙 집중식 감사"를 테스트합니다. 이 에이전트는 해당 기능을 직접적으로 보여줍니다.

---

### 에이전트 4: 릴리스 노트 작성자

git 기록과 변경된 파일을 읽어 이해관계자 친화적인 구조화된 릴리스 노트를 생성합니다.

```bash
cp samples/agents/release-notes-drafter.md .gemini/agents/
```

```markdown
<!-- .gemini/agents/release-notes-drafter.md -->
---
name: release-notes-drafter
description: Generate release notes from git history and source changes.
model: gemini-3.1-flash-lite-preview
tools:
  - run_shell_command
  - read_file
  - glob
  - grep_search
---

You are a release engineer. Process:
1. Run `git log --oneline -20` for recent commits
2. Group by: Features, Bug Fixes, Breaking Changes, Dependencies
3. Read changed files to understand actual impact
4. Write user-facing descriptions, not developer jargon
```

**직접 해보기:**

```
@release-notes-drafter Write release notes for the last 10 commits
```

> **아우터 루프 가치:** 릴리스 노트는 SDLC 작업 중 가장 꺼려지는 작업 중 하나입니다. 이 에이전트는 git 기록과 실제 코드 변경 사항을 모두 읽어 프로덕트 매니저가 이해할 수 있는 노트를 생성합니다.

---

### 에이전트 결합: 전체 파이프라인

진정한 강력함은 에이전트들을 워크플로로 결합하는 데 있습니다. 각 에이전트는 **새롭고 집중된 컨텍스트**를 얻으며, 단일 에이전트가 전체 대화 기록을 축적하지 않습니다:

```
# Step 1: Investigate (read-only, fresh context)
@codebase_investigator Map the authentication flow in this application

# Step 2: Implement (write access, fresh context)
Add a "forgot password" endpoint following the patterns described above

# Step 3: Review (read-only, fresh context)
@pr-reviewer Review the forgot-password implementation

# Step 4: Document (read-only, fresh context)
@doc-writer Update the API docs with the new endpoint

# Step 5: Audit (read-only, fresh context)
@compliance-checker Check the new code for hardcoded secrets or PII
```

> **이것이 효과적인 이유:** 각 단계는 특정 작업에 집중된 깨끗한 컨텍스트로 시작합니다. investigator는 구현 세부 정보를 전달하지 않습니다. reviewer는 조사 과정의 노이즈를 전달하지 않습니다. 이것이 모든 고성능 AI 워크플로의 이면에 있는 원칙입니다.

---

### 더 깊이 알아보기

프롬프트 원칙, 검증 루프, 컨텍스트 엔지니어링 및 병렬 개발과 같은 추가적인 고급 기술에 대해서는 **[고급 패턴](advanced-patterns.md)** 페이지를 참조하세요:

- [프롬프트 기술: 목표 대 지침](advanced-patterns.md#prompting-craft-goals-vs-instructions)
- [컨텍스트 원칙](advanced-patterns.md#context-discipline)
- [검증 루프](advanced-patterns.md#verification-loops)
- [워크트리를 활용한 병렬 개발](advanced-patterns.md#parallel-development-with-worktrees)
- [다중 에이전트 오케스트레이션](advanced-patterns.md#multi-agent-orchestration)

---
## 요약: 배운 내용

| 기능 | 역할 |
|---|---|
| **GEMINI.md 계층 구조** | 모든 수준에서 프로젝트 규칙을 인코딩합니다 — 에이전트가 이를 자동으로 따릅니다 |
| **JIT 컨텍스트 검색** | 현재 작업과 관련된 컨텍스트 파일만 로드합니다 |
| **메모리** | 세션 간에 지식을 유지합니다 |
| **Conductor** | 영구적인 계획 및 진행률 추적을 통한 사양 주도 개발 |
| **확장 프로그램** | 스킬, 에이전트, 훅 및 정책의 설치 가능한 패키지 |
| **MCP 서버** | 외부 도구(GitHub, BigQuery, Jira)에 연결합니다 |
| **정책 엔진** | TOML로 작성된 코드형 가드레일 — deny, allow 또는 ask_user |
| **훅** | 에이전트 수명 주기 이벤트에서의 경량 컨텍스트 주입 및 모델 스티어링 |
| **샌드박싱** | 신뢰할 수 없는 환경을 위한 격리된 실행 |
| **사용자 지정 에이전트** | 단순한 코딩이 아닌 리뷰, 문서, 규정 준수, 릴리스 노트를 위한 특화된 에이전트 |
| **내장 에이전트** | `generalist`, `codebase_investigator`, `cli_help` — 설정 없는 위임 |

---
## 다음 단계

→ 계속해서 **[사용 사례 2: 레거시 코드 현대화](legacy-modernization.md)**로 이동하세요.

→ 파워 유저를 위한: **[고급 패턴](advanced-patterns.md)** — 프롬프트 작성 기술, 검증 루프, 컨텍스트 엔지니어링 및 병렬 개발