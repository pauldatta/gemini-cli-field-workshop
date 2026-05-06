# 확장 프로그램 생태계

> **소요 시간:** 약 30분 (자기 주도 학습)
> **목표:** 확장 프로그램이 무엇인지 이해하고, 커뮤니티 확장 프로그램을 검색 및 설치하며, 조직이 지식과 도구를 배포하기 위해 어떻게 패키징하는지 알아봅니다.
> **사전 요구 사항:** 최소한 [사용 사례 1: SDLC 생산성 향상](sdlc-productivity.md)을 완료했거나 기본 사항에 익숙해야 합니다. `GEMINI.md`, 에이전트 및 스킬이 어떻게 작동하는지 이미 알고 있어야 합니다.
>
> *최종 업데이트: 2026-05-05 · [gemini-cli 저장소에 대해 검증된 소스](https://github.com/google-gemini/gemini-cli)*

---
## 확장 프로그램이란 무엇인가요?

[SDLC 생산성 향상](sdlc-productivity.md)에서 Conductor 확장 프로그램을 설치했습니다. [고급 패턴](advanced-patterns.md)에서는 agent-skills 팩을 설치했습니다. 두 가지 모두 동일한 방식인 `gemini extensions install <url>`로 설치되었는데, 이는 둘 다 **확장 프로그램**이기 때문입니다.

확장 프로그램은 여러 기능을 설치 가능한 단일 단위로 패키징합니다:

| 기능 | 설명 | 호출 주체 |
|---|---|---|
| **MCP 서버** | 모델에 새로운 도구와 데이터 소스를 노출합니다 | 모델 |
| **사용자 정의 명령어** | 복잡한 프롬프트나 셸 명령어를 위한 `/my-cmd` 단축키 | 사용자 |
| **컨텍스트 파일** (`GEMINI.md`) | 매 세션마다 로드되는 상시 지침 | CLI → 모델 |
| **에이전트 스킬** | 필요에 따라 활성화되는 특화된 워크플로우 (TDD, 코드 리뷰 등) | 모델 |
| **훅** | 수명 주기 인터셉터 — 도구 호출, 모델 응답, 세션 전/후 | CLI |
| **테마** | CLI UI 개인화를 위한 색상 정의 | 사용자 (`/theme`) |
| **정책 엔진** | 2단계 우선순위로 기여되는 안전 규칙 및 도구 제한 | CLI |

> **핵심 인사이트:** 여러분은 이미 두 개의 확장 프로그램을 사용해 보았습니다. 고급 패턴의 agent-skills 팩은 *주로* 스킬 확장 프로그램으로, 20개의 스킬과 7개의 슬래시 명령어를 제공합니다. Conductor는 주로 명령어 + MCP 서버 확장 프로그램입니다. 확장 프로그램은 유연한 컨테이너로서 위의 7가지 기능 중 어떤 조합이든 패키징할 수 있습니다.

### 매니페스트: `gemini-extension.json`

모든 확장 프로그램에는 매니페스트가 있습니다. 이는 확장 프로그램과 Gemini CLI 간의 계약입니다:

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "description": "What this extension does",
  "contextFileName": "GEMINI.md",
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${extensionPath}${/}server.js"],
      "cwd": "${extensionPath}"
    }
  },
  "excludeTools": ["run_shell_command(rm -rf)"],
  "settings": [
    {
      "name": "API Key",
      "envVar": "MY_API_KEY",
      "sensitive": true
    }
  ]
}
```

| 필드 | 목적 |
|---|---|
| `name` | 고유 식별자 — 디렉터리 이름과 일치해야 합니다 |
| `contextFileName` | 매 세션마다 이 파일을 컨텍스트에 로드합니다. 파일이 존재할 경우 기본값은 `GEMINI.md`입니다 |
| `mcpServers` | 시작할 MCP 서버 — `settings.json`과 동일한 형식입니다. 이식성을 위해 `${extensionPath}`를 사용하세요 |
| `excludeTools` | 특정 도구나 명령어를 차단합니다 (예: 셸을 통한 `rm -rf`) |
| `settings` | 사용자 구성 가능 값 — `sensitive: true`는 시스템 키체인에 저장합니다 |

### 확장 프로그램 vs. 스킬 vs. 에이전트 — 언제 무엇을 사용해야 할까

| | 확장 프로그램 | 스킬 (`SKILL.md`) | 에이전트 (`.gemini/agents/*.md`) |
|---|---|---|---|
| **범위** | 사용자/머신 간 공유됨 | 로컬 또는 확장 프로그램에 번들됨 | 로컬 프로젝트 |
| **설치 출처** | GitHub, 로컬 경로 | 확장 프로그램 또는 프로젝트의 일부 | 프로젝트 디렉터리 |
| **최적의 용도** | 배포 가능한 툴킷, 조직 표준, MCP 통합 | 단계별 워크플로우 (TDD, 보안 감사) | 특화된 페르소나 (리뷰어, 규정 준수 검사기) |
| **예시** | `oh-my-gemini-cli`, `agent-skills`, `conductor` | `subagent-driven-development`, `debugging` | `@pr-reviewer`, `@compliance-checker` |

---
## 탐색 및 설치

### 확장 프로그램 찾기

[확장 프로그램 갤러리](https://geminicli.com/extensions/browse/)는 공개된 확장 프로그램을 자동으로 색인합니다. `gemini-cli-extension` 토픽이 있는 모든 GitHub 저장소는 갤러리에 표시되며, 별도의 제출이 필요하지 않습니다.

### 설치

```bash
# Install from GitHub
gemini extensions install https://github.com/owner/repo

# Install a specific version (branch, tag, or commit)
gemini extensions install https://github.com/owner/repo --ref v1.2.0

# Enable auto-updates
gemini extensions install https://github.com/owner/repo --auto-update
```

### 설치된 확장 프로그램 관리

```bash
# List all installed extensions
gemini extensions list

# Or from within an interactive session
/extensions list

# Update a specific extension
gemini extensions update my-extension

# Update all extensions
gemini extensions update --all

# Disable an extension for this workspace only
gemini extensions disable my-extension --scope workspace

# Re-enable
gemini extensions enable my-extension --scope workspace

# Uninstall
gemini extensions uninstall my-extension
```

### Google 관리 확장 프로그램

Google은 보안, 데이터베이스, CI/CD 및 Google Cloud 서비스를 다루는 60개 이상의 확장 프로그램이 있는 공식 확장 프로그램 조직인 [**gemini-cli-extensions**](https://github.com/gemini-cli-extensions)를 유지 관리합니다:

| 확장 프로그램 | 주요 분야 | 추가되는 기능 |
|---|---|---|
| [**security**](https://github.com/gemini-cli-extensions/security) | 보안 분석 | 전체 SAST 엔진, OSV-Scanner를 통한 종속성 스캔, PoC 생성, 자동 패치. 90% 정밀도, 93% 재현율 |
| [**conductor**](https://github.com/gemini-cli-extensions/conductor) | 스펙 주도 개발 | 구조화된 계획, 구현 추적 및 컨텍스트 주도 개발 |
| [**workspace**](https://github.com/gemini-cli-extensions/workspace) | Google Workspace | 에이전트에 최적화된 JSON 출력을 제공하는 Gmail, Drive, Calendar, Sheets 통합 |
| [**cicd**](https://github.com/gemini-cli-extensions/cicd) | CI/CD | 파이프라인 생성, 워크플로우 디버깅 및 배포 자동화 |
| [**firebase**](https://github.com/gemini-cli-extensions/firebase) | Firebase | Firebase 프로젝트 관리, Firestore 쿼리 및 호스팅 배포 |
| [**bigquery-data-analytics**](https://github.com/gemini-cli-extensions/bigquery-data-analytics) | 데이터 분석 | 데이터 탐색, 쿼리 최적화 및 분석을 위한 BigQuery 스킬 |
| [**cloud-sql-***](https://github.com/gemini-cli-extensions) | 데이터베이스 | PostgreSQL, MySQL, SQL Server, AlloyDB, OracleDB를 위한 스킬 |
| [**vertex**](https://github.com/gemini-cli-extensions/vertex) | Vertex AI | 프롬프트 관리 및 Vertex AI 통합 |

다음 명령어로 설치할 수 있습니다:

```text
gemini extensions install https://github.com/gemini-cli-extensions/<name>
```

### 주목할 만한 커뮤니티 확장 프로그램

공식 생태계를 넘어, 커뮤니티는 점점 더 정교한 확장 프로그램을 구축해 왔습니다:

| 확장 프로그램 | 주요 분야 | 추가되는 기능 |
|---|---|---|
| [**oh-my-gemini-cli**](https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli) | 오케스트레이션 | 12개의 에이전트, 9개의 스킬, 43개의 슬래시 명령어, 수명 주기 훅. 승인 게이트가 있는 완전한 다중 에이전트 프레임워크 |
| [**superpowers**](https://github.com/obra/superpowers) | 방법론 | TDD, 디버깅, 코드 리뷰, 서브에이전트 주도 개발을 위한 14개의 스킬. 크로스 툴: Cursor 및 OpenCode에서도 작동 |
| [**gws (Google Workspace CLI)**](https://github.com/googleworkspace/cli) | Workspace 통합 | Gmail, Drive, Calendar, Sheets를 위한 동적 CLI. 에이전트에 최적화된 JSON 출력. Model Armor 통합 |

---
## 실습: 커뮤니티 확장 프로그램 설치 및 사용

여러분은 이미 **agent-skills** 팩(고급 패턴)과 **Conductor**(SDLC 생산성 향상)를 설치했습니다. 이제 공식 생태계를 넘어 커뮤니티에서 구축한 것들을 살펴보겠습니다.

### 연습 문제 1: Superpowers — 확장 프로그램으로서의 방법론

`superpowers` 확장 프로그램은 에이전트에게 단순히 무엇을 해야 할지뿐만 아니라 *어떻게 작업해야 하는지*를 가르칩니다. 이 확장 프로그램의 대표적인 기능은 **서브에이전트 주도 개발(SDD, Subagent-Driven Development)**로, 작업당 새로운 서브에이전트를 파견하고 2단계 검토를 거치는 공식적인 방법론입니다.

```bash
# Install
gemini extensions install https://github.com/obra/superpowers

# Verify — you should see superpowers in the list
/extensions list
```

**plan 스킬 시도해 보기:**

```
Write a plan for adding a "recently viewed products" feature to the ProShop app.
Use the $plan skill.
```

**서브에이전트 주도 개발 시도해 보기:**

```
I want to add a "recently viewed" sidebar widget. Use subagent-driven development 
to implement this — dispatch a subagent for each component and review each one.
```

SDD가 어떻게 작동하는지 살펴보세요:
1. 각 구성 요소(데이터 모델, API 엔드포인트, React 컴포넌트)에 대한 사양을 생성합니다.
2. 각 구성 요소에 대해 새로운 서브에이전트를 파견합니다. 작업 간에 컨텍스트가 섞이지 않습니다.
3. 각 서브에이전트의 출력을 사양 준수 여부, 그 다음 코드 품질의 2단계로 검토합니다.
4. 모든 발견 사항이 포함된 요약을 보고합니다.

> **핵심 요약:** 이를 가공되지 않은 "최근 본 사이드바 추가" 프롬프트와 비교해 보세요. SDD는 검토되고 검증된 코드를 생성합니다. 가공되지 않은 프롬프트는 수동으로 검토해야 하는 코드를 생성합니다. 이것이 바로 개발자와 개발 *프로세스*의 차이입니다.

**교차 도구 이식성:** Superpowers는 Cursor(`.cursor-plugin/`) 및 OpenCode(`.opencode/`)에서도 작동합니다. 동일한 `SKILL.md` 파일을 사용하지만 플러그인 매니페스트는 다릅니다. 스킬은 특정 공급업체에 종속되지 않습니다.

---

### 연습 문제 2: Oh-My-Gemini-CLI — 확장 프로그램으로서의 오케스트레이션

이 확장 프로그램은 승인 게이트가 있는 완전한 다중 에이전트 워크플로를 구현합니다. 이는 엔터프라이즈 팀에 필요한 일종의 거버넌스입니다.

```bash
# Install
gemini extensions install https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli
```

**의도 기반 워크플로 시도해 보기:**

```
/omg:intent Add user profile avatars to the ProShop application
```

어떤 일이 일어나는지 주목하세요:
- 에이전트가 즉시 코딩을 시작하지 않습니다. 범위, 제약 조건 및 허용 기준에 대해 질문하는 **소크라테스식 인터뷰**를 시작합니다.
- 범위를 확인한 후에야 `omg-planner` 에이전트가 구조화된 계획을 생성합니다.
- 계획은 구현을 위해 `omg-executor`로 전달됩니다.
- 구현 후, `omg-reviewer`가 품질 게이트 검사를 실행합니다.

**구조 엿보기:** 이 확장 프로그램은 7가지 확장 프로그램 기능을 모두 동시에 사용합니다:

```
oh-my-gemini-cli/
├── gemini-extension.json    # Manifest (contextFileName, MCP config)
├── GEMINI.md                # Always-on context → delegates to skills
├── context/omg-core.md      # Core behavioral rules
├── agents/                  # 12 sub-agents (architect, reviewer, debugger, etc.)
├── skills/                  # 9 deep-work procedures ($plan, $prd, $research, etc.)
├── commands/                # 43 TOML slash commands under /omg:* namespace
└── hooks/hooks.json         # BeforeModel (banner/router) + AfterAgent (auto-learn)
```

> **핵심 요약:** OMG는 "모든 것이 포함된(batteries-included)" 확장 프로그램이 어떤 모습인지 보여줍니다. 소크라테스식 인터뷰 게이트웨이는 에이전트가 모호한 요청에 대해 자동 실행하는 것을 방지하며, 이는 모든 엔터프라이즈에서 고려해야 할 패턴입니다.

---

### 연습 문제 3: Google Workspace CLI (선택 사항)

> **참고:** 이 연습 문제에는 Google Workspace(Gmail, Drive, Calendar)가 필요합니다. 조직에서 Workspace를 사용하지 않는 경우 이 부분을 건너뛰세요.

`gws` 확장 프로그램은 에이전트에게 Workspace API에 대한 직접적이고 구조화된 액세스를 제공합니다:

```bash
# Install as a Gemini extension
gemini extensions install https://github.com/googleworkspace/cli

# Authenticate (one-time setup)
gws auth setup
```

**받은편지함 분류 시도해 보기:**

```
Use gws to triage my inbox — show me unread emails grouped by priority
```

**스탠드업 보고서 시도해 보기:**

```
Use gws to generate a standup report from my calendar and recent email activity
```

`gws`는 에이전트 소비에 최적화된 구조화된 JSON을 출력합니다. 또한 에이전트가 처리하기 전에 API 응답을 Model Armor 템플릿을 통해 라우팅하는 `--sanitize`를 지원합니다.

---

### 연습 문제 4: 보안 확장 프로그램 — 프로덕션급 SAST

[보안 확장 프로그램](https://github.com/gemini-cli-extensions/security)은 Gemini CLI를 위한 Google의 공식 보안 분석 도구입니다. 수작업으로 만든 규정 준수 에이전트와 달리, 이 도구는 전체 SAST 엔진, 종속성 스캐너 및 벤치마크 결과를 함께 제공합니다.

```bash
# Install
gemini extensions install https://github.com/gemini-cli-extensions/security
```

**현재 변경 사항에 대해 보안 분석 실행하기:**

```
/security:analyze
```

이 확장 프로그램은 구조화된 2단계 분석을 실행합니다:
1. **정찰 단계(Reconnaissance pass)** — 취약점 분류 체계에 따라 변경된 모든 파일을 빠르게 스캔합니다.
2. **조사 단계(Investigation pass)** — 플래그가 지정된 패턴을 심층 분석하여 소스에서 싱크까지의 데이터 흐름을 추적합니다.

하드코딩된 비밀 정보, 인젝션 취약점(SQLi, XSS, SSRF, SSTI), 손상된 접근 제어, PII 노출, 취약한 암호화 및 LLM 안전 문제를 검사합니다.

**알려진 CVE에 대한 종속성 스캔하기:**

```
/security:scan-deps
```

이는 Google의 오픈소스 취약점 데이터베이스인 [osv.dev](https://osv.dev)에 대해 [OSV-Scanner](https://github.com/google/osv-scanner)를 사용합니다.

**범위 사용자 지정하기:**

```
/security:analyze Analyze all source code under the src/ folder. Skip docs and config files.
```

**주요 기능:**
- **PoC 생성** — 발견 사항을 검증하기 위한 개념 증명 스크립트를 생성합니다(`poc` 스킬).
- **자동 패치** — 확인된 취약점에 대한 수정 사항을 적용합니다(`security-patcher` 스킬).
- **허용 목록(Allowlisting)** — 수용된 위험을 `.gemini_security/vuln_allowlist.txt`에 유지합니다.
- **CI 통합** — 자동화된 PR 보안 검토를 위해 즉시 사용 가능한 [GitHub Actions 워크플로](https://github.com/gemini-cli-extensions/security/blob/main/.github/workflows/gemini-review.yml)를 제공합니다.

> **엔터프라이즈 가치:** 이는 [SDLC 생산성 향상 §1.7](sdlc-productivity.md) 및 [§2.3](sdlc-productivity.md)에서 참조된 것과 동일한 확장 프로그램입니다. 맞춤형 규정 준수 검사기 에이전트를 구축할 필요가 없으며, `gemini extensions install` 한 번으로 전체 팀에 프로덕션급 보안 파이프라인을 제공합니다.

---
## 나만의 확장 프로그램 만들기

### 템플릿에서 스캐폴딩하기

Gemini CLI는 7개의 내장 템플릿을 제공합니다:

```bash
# Create from a template
gemini extensions new my-extension mcp-server
gemini extensions new my-extension custom-commands
gemini extensions new my-extension exclude-tools
gemini extensions new my-extension hooks
gemini extensions new my-extension skills
gemini extensions new my-extension policies
gemini extensions new my-extension themes-example
```

### `link`를 사용하여 로컬에서 개발하기

재설치 없이 변경 사항을 테스트하려면 `link`를 사용하세요:

```bash
cd my-extension
npm install
gemini extensions link .
```

변경 사항은 Gemini CLI 세션을 다시 시작한 후 즉시 반영됩니다. 개발 중에는 다시 설치할 필요가 없습니다.

### 갤러리에 게시하기

게시는 자동으로 이루어지며 제출할 필요가 없습니다:

1. 루트에 유효한 `gemini-extension.json`이 있는 **공개 GitHub 저장소에 푸시합니다**
2. 저장소의 About 섹션에 **GitHub 주제** `gemini-cli-extension`을 **추가합니다**
3. **릴리스에 태그를 지정합니다** (예: `v1.0.0`)

갤러리 크롤러는 태그가 지정된 저장소를 매일 색인화합니다. 유효성 검사 후 확장 프로그램이 자동으로 표시됩니다.

### 연습: 미니 확장 프로그램 만들기

팀의 코드 리뷰 체크리스트를 위한 슬래시 명령어를 추가하는 간단한 확장 프로그램을 만듭니다:

```bash
# Scaffold
gemini extensions new team-review custom-commands
cd team-review

# Create the command
mkdir -p commands/team
cat > commands/team/review.toml << 'EOF'
prompt = """
Review the current changes using this checklist:
1. Does it follow our coding standards?
2. Are there any security issues (OWASP Top 10)?
3. Is error handling complete?
4. Are tests adequate?
5. Is the API contract backward-compatible?

Focus on findings, not praise. Be specific with file:line references.
"""
EOF

# Link for local development
gemini extensions link .
```

Gemini CLI를 다시 시작하고 `/team:review`를 실행하세요. 이제 사용자 지정 리뷰 체크리스트를 하나의 명령어로 실행할 수 있습니다.

---
## 엔터프라이즈를 위한 확장 프로그램 패턴

### 조직 지식 배포

엔터프라이즈 팀을 위한 가장 가치 있는 패턴: **조직의 지식을 확장 프로그램으로 패키징하는 것입니다.**

Confluence에서 썩어가는 온보딩 문서 대신, 에이전트에게 조직의 패턴을 가르치는 확장 프로그램을 배포하세요:

```
my-org-extension/
├── gemini-extension.json
├── GEMINI.md                # Org coding standards, always loaded
├── skills/
│   ├── security-review/     # OWASP checklist + your org's threat model
│   ├── api-design/          # Your API design guide, enforced at dev time
│   └── incident-response/   # Runbook for on-call engineers
├── commands/
│   ├── team/
│   │   ├── review.toml      # Team-specific code review checklist
│   │   └── deploy.toml      # Deploy workflow with org-specific gates
│   └── oncall/
│       └── triage.toml      # Incident triage workflow
├── agents/
│   └── compliance-checker.md  # Org compliance rules as a sub-agent
└── policies/
    └── safety.toml          # Tool restrictions (no force-push, no prod DB access)
```

**이점:**
- **버전 관리:** 확장 프로그램을 업데이트하면, 다음 `gemini extensions update` 시 모든 사람이 최신 표준을 얻게 됩니다.
- **분산 배포:** 첫날에 `gemini extensions install`을 실행하면, 신규 입사자가 조직의 전체 지식을 얻게 됩니다.
- **유지보수:** 단일 저장소, 단일 PR로 모든 개발자의 에이전트에 걸쳐 조직 표준을 업데이트합니다.
- **일관성:** 팀의 모든 에이전트가 동일한 규칙을 따르고, 동일한 체크리스트로 검토하며, 동일한 게이트로 배포합니다.

> **이것은 "위키 읽기" 온보딩 패턴을 대체합니다.** 개발자가 스타일 가이드를 찾아서 읽기를 바라는 대신, 에이전트가 이를 자동으로 강제합니다.

### 거버넌스 패턴

확장 프로그램은 **티어 2 우선순위**로 정책 규칙을 제공합니다. 이는 기본값보다 높고, 사용자/관리자 재정의보다 낮습니다:

```toml
# policies/safety.toml (contributed by your org extension)
[[rule]]
toolName = "run_shell_command"
commandRegex = ".*--force.*"
decision = "deny"
priority = 100
denyMessage = "Force operations are blocked by organization policy."
```

> **보안 모델:** 확장 프로그램 정책은 티어 2 우선순위에서 작동합니다. 사용자(티어 4) 및 관리자(티어 5) 정책이 항상 우선합니다. 즉, 확장 프로그램이 가드레일을 설정할 수 있지만, 필요할 때 사용자와 관리자가 이를 재정의할 수 있습니다. 전체 티어 세부 정보는 [정책 엔진](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md)을 참조하고, 실용적인 연습은 [정책 엔진으로 Gemini CLI 보호하기](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy)를 참조하세요.

**키체인 스토리지가 있는 설정:** 확장 프로그램은 시스템 키체인에 저장되는 설정을 정의할 수 있습니다:

```json
{
  "settings": [
    {
      "name": "Internal API Key",
      "envVar": "ORG_API_KEY",
      "sensitive": true
    }
  ]
}
```

`sensitive: true`로 표시된 값은 OS 키체인에 암호화되어 저장되며 CLI 출력에서는 난독화됩니다.

### 도구 간 이식성

`superpowers` 확장 프로그램은 핵심 엔터프라이즈 패턴을 보여줍니다. 동일한 `SKILL.md` 파일이 Gemini CLI, Cursor, OpenCode에서 모두 작동하며, 각각 고유한 플러그인 매니페스트 형식(`gemini-extension.json`, `.cursor-plugin/`, `.opencode/`)을 갖습니다. 이는 다음을 의미합니다:

- **스킬은 특정 공급업체에 종속되지 않습니다** — 도구별 설정이 아닌 방법론에 투자하세요.
- **서로 다른 편집기를 사용하는 팀**도 동일한 엔지니어링 표준을 공유합니다.
- **마이그레이션 위험이 낮습니다** — 도구를 변경한다는 것은 스킬을 다시 작성하는 것이 아니라 새로운 매니페스트를 작성하는 것을 의미합니다.

### 내부 레지스트리 패턴

비공개 확장 프로그램 생태계를 유지하는 조직의 경우:

1. **GitHub 조직** — 내부 조직을 생성합니다(예: `my-company-gemini-extensions`).
2. **토픽 태깅** — 비공개 규칙을 사용합니다(예: `internal-gemini-extension`).
3. **버전 고정** — 프로덕션 안정성을 위해 `--ref` 태그를 사용하여 설치합니다:
   ```bash
   gemini extensions install https://github.internal.com/org/my-ext --ref v2.1.0
   ```
4. **자동 업데이트** — 최신 버전이 가장 좋은 확장 프로그램(스타일 가이드)에는 `--auto-update`를 사용합니다.
5. **작업 공간 범위 지정** — 특정 프로젝트에 대해 조직 확장 프로그램을 비활성화합니다:
   ```bash
   gemini extensions disable org-standards --scope workspace
   ```

---
## 요약

| 개념 | 주요 내용 |
|---|---|
| **확장 프로그램 패키지 구성** | 7가지 기능: MCP 서버, 명령어, 컨텍스트, 스킬, 훅, 테마, 정책 |
| **Google 관리형** | [gemini-cli-extensions](https://github.com/gemini-cli-extensions)의 60개 이상 확장 프로그램 — 보안, 데이터베이스, CI/CD, Workspace |
| **설치** | `gemini extensions install <url>` — 단일 명령어 |
| **갤러리** | `gemini-cli-extension` GitHub 토픽을 통해 자동 색인됨 |
| **빌드** | 7가지 템플릿에서 `gemini extensions new` 사용, 로컬 개발을 위한 `link` |
| **엔터프라이즈 가치** | 조직 지식 패키징, 표준 적용, 설치 명령어를 통한 배포 |
| **보안** | SAST 및 종속성 스캐닝이 포함된 공식 보안 확장 프로그램. 티어 2의 확장 프로그램 정책. 키체인에 비밀 정보 저장 |
| **이식성** | 스킬은 Gemini CLI, Cursor 및 OpenCode 전반에서 작동함 |

---
## 다음 단계

→ **[사용 사례 1: SDLC 생산성 향상](sdlc-productivity.md)**으로 돌아가기 — 2부에서는 아우터 루프 에이전트(ADR, 온보딩, 종속성 감사)를 다룹니다.

→ **[고급 패턴](advanced-patterns.md)**으로 계속 진행하기 — 프롬프트 작성 기술, 컨텍스트 엔지니어링, 에이전트 스킬 설치
