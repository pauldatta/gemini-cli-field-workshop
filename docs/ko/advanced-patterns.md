# 고급 패턴

> **소요 시간:** 약 45분 (자기 주도)  
> **목표:** 프롬프팅 규율, 검증 루프, 컨텍스트 엔지니어링 및 병렬 개발을 마스터합니다. 이러한 기술은 모든 Gemini CLI 워크플로우에서 작동합니다.  
> **사전 요구 사항:** 최소한 [사용 사례 1: SDLC 생산성](sdlc-productivity.md)을 완료했거나 기본 사항에 익숙해야 합니다.

---
## 프롬프트 작성 기술: 목표 vs. 지시사항

AI 출력 품질을 개선할 수 있는 가장 큰 방법은 **질문하는 방식**을 바꾸는 것입니다.

### 문제점

대부분의 개발자는 단계별 지시사항을 제공합니다:

```
Create a wishlist model with userId and productId fields.
Then create a controller with addToWishlist and getWishlist functions.
Then add routes at /api/wishlist.
Then create a Redux slice.
Then create the WishlistScreen component.
```

이는 더 나은 접근 방식이 존재하더라도 에이전트가 특정 경로를 따르도록 강제합니다. 에이전트는 이의를 제기하거나, 장단점을 드러내거나, 적응할 수 없습니다.

### 해결책: 성공 기준을 갖춘 선언적 목표

```
Add a product wishlist feature. When you're done:
1. A logged-in user can add/remove products from their wishlist
2. The wishlist persists across sessions (stored in MongoDB)
3. There's a /wishlist page accessible from the navbar
4. All existing tests still pass (npm test)
5. The code follows the conventions in GEMINI.md

Say "WISHLIST_COMPLETE" when all criteria are verified.
```

### 이것이 효과적인 이유

| 명령형 (❌) | 선언적 (✅) |
|---|---|
| 구현 세부 사항을 규정함 | 원하는 결과를 설명함 |
| 에이전트가 이의를 제기하거나 대안을 제시할 수 없음 | 에이전트가 코드베이스에 가장 적합한 접근 방식을 선택함 |
| 검증 없음 — 수동으로 확인해야 함 | 성공 기준을 통한 내장된 검증 루프 |
| 하나의 경직된 경로 | 에이전트가 발견한 내용에 적응함 |

> **핵심 인사이트:** "무엇을 해야 할지 지시하지 말고, 성공 기준을 제시하고 지켜보세요." 에이전트는 특정 목표를 달성할 때까지 루프를 반복하는 데 매우 뛰어납니다. 약한 기준("작동하게 만드세요")은 지속적인 개입이 필요합니다. 강력한 기준은 에이전트가 독립적으로 실행되도록 합니다.

### 연습 문제

ProShop을 사용하여 동일한 작업에 두 가지 접근 방식을 모두 시도해 보세요. 다음을 비교해 보세요:
1. 각각 몇 번의 턴이 걸렸나요?
2. 선언적 버전이 더 나은 접근 방식을 찾았나요?
3. 어느 쪽이 더 깔끔한 코드를 생성했나요?

---
## 컨텍스트 규율

에이전트의 컨텍스트 윈도우에 있는 모든 토큰은 다음 응답의 초점을 약간 흐리게 만듭니다. 컨텍스트는 예산입니다. 제한된 기기의 메모리처럼 관리하세요.

### 컨텍스트 과부하의 증상

- 에이전트가 같은 말을 반복하기 시작함
- 환각(존재하지 않는 파일 참조)이 증가함
- 15-20턴 이후 출력 품질이 눈에 띄게 떨어짐
- 에이전트가 이전 지시사항을 "잊어버림"

### 툴킷

#### 1. 전략적 초기화

출력 품질이 저하될 때:

```
/clear
```

이것은 GEMINI.md, 메모리, 파일 상태를 그대로 유지하면서 대화형 컨텍스트를 초기화합니다. 에이전트는 프로젝트에 대한 모든 지식을 가진 상태로 새롭게 다시 시작합니다.

#### 2. 지우기 전에 저장하기

```
/memory add "The ProShop codebase uses a repository pattern for 
data access. All MongoDB queries go through model methods, never 
directly in controllers. Express middleware chain: cors → 
cookieParser → authMiddleware → routes."
```

메모리는 세션과 `/clear` 초기화 후에도 유지됩니다. 지우기 전에 중요한 발견 사항을 저장하세요.

#### 3. 컨텍스트 오프로딩

대규모 사양(spec)은 대화에서 빼내어 파일로 이동하세요:

```bash
# Instead of pasting a long spec into chat:
echo "Your detailed spec..." > .gemini/context/feature-spec.md

# Then reference it:
# "Read the spec in .gemini/context/feature-spec.md and implement it"
```

에이전트는 컨텍스트 파일을 온디맨드(JIT)로 로드합니다. 즉, 필요할 때까지 토큰을 소비하지 않습니다.

#### 4. 에이전트 위임을 통한 격리

각 맞춤형 에이전트는 고유한 컨텍스트 윈도우를 갖습니다. 이를 전략적으로 사용하세요:

```
# Bad: one agent doing everything (context bloat)
"Research the auth system, then refactor it, then write tests, then review"

# Good: isolated phases (each gets clean context)
@codebase_investigator Map the auth system
Now refactor based on the investigator's findings
@pr-reviewer Review the refactored auth code
```

### 연습 문제

1. 세션을 시작하고 세 가지 기능을 순차적으로 구축합니다(의도적으로 컨텍스트를 축적함).
2. 15-20턴 부근에서 품질 저하를 관찰합니다.
3. `/memory add`를 실행하여 핵심 사실을 저장합니다.
4. `/clear`를 실행하고 즉각적인 품질 향상을 관찰합니다.
5. 에이전트에게 중단된 부분부터 계속하라고 요청합니다. 메모리와 파일 상태를 통해 작업을 이어갑니다.

---
## 검증 루프

에이전트에서 올바른 코드를 얻는 가장 확실한 방법은 **피드백 루프**를 제공하는 것입니다. 이는 에이전트가 스스로 작업을 확인하고 실수를 자동으로 수정할 수 있는 방법입니다.

### 패턴

```
Add product ratings to ProShop. When you're done:
1. Users can rate products 1-5 stars
2. Average rating displays on the product page
3. Only authenticated users can rate
4. A user can only rate a product once
5. All existing tests pass AND new tests cover the rating logic

Run `npm test` after each change. Fix any failures before moving on.
Say "RATINGS_COMPLETE" when all 5 criteria are verified.
```

### 완료 약속이 작동하는 이유

"완료되면 X라고 말하세요"라는 문구는 에이전트에게 다음을 제공합니다:

1. **명확한 중지 지점** — 언제 작업을 멈춰야 할지 알게 됩니다.
2. **자체 검증 동기 부여** — 완료를 선언하기 전에 자신의 작업을 확인합니다.
3. **반복적인 복구** — 테스트가 실패하면 사용자에게 묻는 대신 수정하고 다시 실행합니다.

### 루프 자동화

대규모 작업의 경우 훅을 사용하여 피드백 루프를 자동화할 수 있습니다. `AfterAgent` 훅은 출력에 완료 약속이 나타났는지 확인합니다. 나타나지 않았다면 대화를 초기화하고(파일 변경 사항은 유지) 원본 프롬프트와 개선된 코드베이스로 다시 실행합니다:

```json
{
  "hooks": {
    "AfterAgent": [{
      "type": "command",
      "command": "python3 check_completion.py",
      "description": "Checks for completion promise and resets if not met"
    }]
  }
}
```

> **안전:** 자율 루프를 실행할 때는 항상 도구 제한을 구성하세요. `settings.json` 또는 `policy.toml`에서 파괴적인 작업(`git push --force`, `rm -rf`)을 차단하세요.

### 연습 문제

에이전트에게 명시적인 성공 기준과 완료 약속이 포함된 리팩토링 작업을 부여하세요. 테스트 실패를 반복하며 통과(green) 상태에 도달할 때까지 지켜보세요.

---
## 워크트리를 활용한 병렬 개발

서로 다른 브랜치에서 여러 Gemini CLI 세션을 동시에 실행하세요. 각 세션은 완전히 격리된 상태로 실행됩니다.

### 문제점

한 번에 하나의 브랜치만 체크아웃할 수 있습니다. 별도의 에이전트를 사용하여 기능 개발, 버그 수정, 리팩토링을 동시에 작업하려는 경우 충돌이 발생합니다.

### 해결책

```bash
# Terminal 1: Feature work
gemini --worktree feature-wishlist

# Terminal 2: Bug fix
gemini --worktree fix-cart-rounding

# Terminal 3: Documentation
gemini --worktree update-api-docs
```

각 에이전트는 자체 디렉터리, 자체 브랜치, 자체 컨텍스트에서 작업합니다. 충돌이 발생하지 않습니다.

### 워크플로우

| 단계 | 작업 |
|---|---|
| **격리 (Isolate)** | 작업/에이전트당 하나의 워크트리 생성 |
| **구성 (Configure)** | 충돌을 방지하기 위해 각 워크트리에 고유한 개발 서버 포트 할당 |
| **실행 (Execute)** | 별도의 Gemini CLI 세션 시작 — 각 에이전트가 독립적으로 작업 |
| **검토 (Review)** | 각 에이전트가 워크트리 내의 자체 브랜치에 커밋 |
| **통합 (Integrate)** | PR을 통해 브랜치를 `main`으로 다시 병합 |
| **정리 (Cleanup)** | `git worktree remove <path>` + `git worktree prune` |

> **워크트리는 일회용으로 취급하세요.** 단일 작업 기간에 맞춰 최적화되어 있습니다. 병합 후에는 제거하세요.

### 실습

두 개의 터미널 창을 엽니다. 워크트리를 사용하여 다음을 수행하세요:
1. 한 창에서는 위시리스트 기능 추가
2. 다른 창에서는 장바구니 총액 계산 오류 수정

두 에이전트가 동시에 작업합니다. 서로의 변경 사항을 볼 수 없습니다. PR을 통해 두 작업을 모두 병합하세요.

---
## 다중 에이전트 오케스트레이션

여러 프로젝트에 걸쳐 수십 개의 에이전트를 관리하는 팀을 위해, 오케스트레이션 도구는 엔터프라이즈급 격리, 관찰 가능성 및 확장을 제공합니다.

### Scion (Google Cloud Platform)

**[Scion](https://github.com/GoogleCloudPlatform/scion)**은 에이전트를 격리된 동시 프로세스로 실행하는 실험적인 다중 에이전트 오케스트레이터로, 각각 자체 컨테이너에서 실행됩니다.

```bash
# Install
go install github.com/GoogleCloudPlatform/scion/cmd/scion@latest

# Start parallel agents with specialized roles
scion start reviewer "Review all open PRs for security issues" --attach
scion start implementer "Implement the wishlist feature" --attach
scion start tester "Write integration tests for the order API" --attach

# Manage
scion list                              # See all running agents
scion message reviewer "Focus on auth"  # Send instructions
scion attach implementer                # Watch an agent work
```

| 개념 | 설명 |
|---|---|
| **에이전트** | Gemini CLI를 실행하는 컨테이너화된 프로세스 |
| **Grove** | 프로젝트 네임스페이스 — 일반적으로 git 저장소와 1:1로 매핑됨 |
| **템플릿** | 에이전트 청사진: 시스템 프롬프트 + 스킬 + 도구 권한 |
| **런타임** | Docker, Podman, Apple Container 또는 Kubernetes |

> **Scion 사용 시기:** 5개 이상의 동시 에이전트 작업이 있는 팀, 에이전트 간의 엄격한 격리가 필요한 프로젝트, 또는 여러 저장소에 걸쳐 AI 관리 개발을 확장하는 조직.

---
## 엔지니어링 규약 패턴

에이전트에게 같은 내용을 두 번 말해야 한다면, 해당 내용은 파일에 저장되어야 합니다.

### 규약에 포함되는 내용

잘 작성된 `GEMINI.md`는 팀의 엔지니어링 표준을 인코딩하여 에이전트가 이를 자동으로 따르도록 합니다:

```markdown
# GEMINI.md

## Coding Standards
- All MongoDB queries go through model methods — never directly in controllers
- Use asyncHandler wrapper for all route handlers
- Error responses use the errorMiddleware pattern
- API responses are JSON with consistent field naming (camelCase)

## Behavioral Rules
- Surface assumptions before implementing — ask if multiple interpretations exist
- Prefer minimal changes over broad refactors
- Every changed line must trace to the original request
- Run tests after every file modification
- Never modify files outside the scope of the current task
```

### 연습 문제

1. ProShop을 위한 5가지 규칙이 포함된 GEMINI.md를 작성하세요.
2. 파일 **없이** 에이전트에게 기능 추가를 요청하고 — 출력을 확인하세요.
3. 파일과 **함께** 동일한 내용을 요청하세요.
4. 비교: 에이전트가 규칙을 따랐나요? 이전에 건너뛰었던 명확한 질문을 했나요?

---
## 스킬 기반 개발

스킬은 시니어 엔지니어의 워크플로우를 에이전트에 직접 인코딩하는 구조화되고 재사용 가능한 지침 파일(`SKILL.md`)입니다. 단순한 프롬프트와 달리, 각 스킬에는 단계별 프로세스, 합리화 방지 테이블(에이전트가 단계를 건너뛰기 위해 사용할 수 있는 일반적인 변명과 문서화된 반박), 위험 신호(red flags) 및 검증 게이트가 포함되어 있습니다.

### 스킬이 단순한 프롬프트보다 나은 이유

| 단순한 프롬프트 | 구조화된 스킬 |
|---|---|
| "이것에 대한 테스트 작성해 줘" | 테스트 피라미드 목표(80/15/5)와 함께 Red-Green-Refactor 워크플로우를 활성화합니다. |
| "이 코드 리뷰해 줘" | 심각도 레이블(Nit/Optional/FYI) 및 변경 규모 기준을 포함한 5축 리뷰를 실행합니다. |
| "이것을 안전하게 만들어 줘" | 3계층 경계 시스템과 함께 OWASP Top 10 체크리스트를 트리거합니다. |
| 중지 기준 없음 | 내장된 검증 게이트 — 에이전트는 다음으로 넘어가기 전에 증거를 제시해야 합니다. |

### 커뮤니티 스킬 설치

[agent-skills](https://github.com/addyosmani/agent-skills) 팩은 전체 SDLC를 다루는 20개의 프로덕션 수준 스킬을 제공합니다. 다음 명령어 하나로 설치하세요:

```bash
# Install from GitHub (auto-discovers all SKILL.md files)
gemini skills install https://github.com/addyosmani/agent-skills.git --path skills

# Verify installation
/skills list
```

설치가 완료되면, 에이전트가 일치하는 작업을 인식할 때 스킬이 온디맨드로 활성화됩니다. UI를 구축하시나요? `frontend-ui-engineering` 스킬이 자동으로 활성화됩니다. 테스트 실패를 디버깅하시나요? `debugging-and-error-recovery`가 작동합니다.

### SDLC 슬래시 명령어

스킬 팩은 개발 수명 주기에 매핑되는 7개의 슬래시 명령어를 `.gemini/commands/` 아래에 제공합니다:

| 명령어 | 단계 | 기능 |
|---|---|---|
| `/spec` | 정의 | 코드를 작성하기 전에 구조화된 PRD를 작성합니다. |
| `/planning` | 계획 | 작업을 수용 기준이 있는 작고 검증 가능한 작업으로 나눕니다. |
| `/build` | 빌드 | 다음 작업을 얇은 수직 슬라이스로 구현합니다. |
| `/test` | 검증 | TDD 워크플로우(red, green, refactor)를 실행합니다. |
| `/review` | 리뷰 | 심각도 레이블이 있는 5축 코드 리뷰를 실행합니다. |
| `/code-simplify` | 리뷰 | 동작을 변경하지 않고 복잡성을 줄입니다(체스터턴의 울타리). |
| `/ship` | 배포 | 병렬 페르소나 팬아웃을 통한 출시 전 체크리스트를 실행합니다. |

> **참고:** `/plan` 대신 `/planning`을 사용하세요. `/plan`은 Gemini CLI에 내장된 플랜 모드 명령어와 충돌합니다.

### 스킬 vs GEMINI.md

둘 다 에이전트 동작에 영향을 미치지만, 서로 다른 목적을 수행합니다:

| | 스킬 | GEMINI.md |
|---|---|---|
| **로드 방식** | 작업이 일치할 때 온디맨드로 | 항상 모든 프롬프트에서 |
| **토큰 비용** | 활성화될 때까지 최소화됨 | 지속적인 오버헤드 |
| **최적의 용도** | 특정 단계의 워크플로우(TDD, 보안 리뷰, 배포) | 항상 켜져 있는 프로젝트 규칙(기술 스택, 코딩 표준) |

**경험 법칙:** *모든* 프롬프트에서 활성화되기를 원한다면 GEMINI.md에 넣으세요. 특정 단계에만 해당한다면 스킬로 설치하세요.

### 연습 문제

1. ProShop 작업 공간에 agent-skills 팩을 설치합니다.
2. `/spec`을 실행합니다 — "제품 비교" 기능에 대한 사양을 작성합니다.
3. `/build`를 실행합니다 — 첫 번째 슬라이스를 점진적으로 구현합니다.
4. `/test`를 실행합니다 — TDD 워크플로우가 red-green-refactor를 강제하는지 관찰합니다.
5. 비교: 구조화된 워크플로우가 단순한 "비교 기능 추가해 줘" 프롬프트와 어떻게 다른가요?

---
## Google 관리형 MCP 서버

Google은 에이전트가 로컬 서버 설치 없이 Google Cloud 서비스, Workspace 앱 및 개발자 도구에 직접적이고 통제된 방식으로 액세스할 수 있도록 **50개 이상의 관리형 MCP 서버**를 제공합니다.

### 관리형 MCP를 사용하는 이유

| 고려 사항 | 관리형 MCP의 해결 방법 |
|---|---|
| **보안** | 도구 수준의 액세스 제어를 위한 IAM 거부 정책; 프롬프트 인젝션 방어를 위한 Model Armor |
| **검색** | Agent Registry — MCP 서버를 찾고 관리하기 위한 통합 디렉터리 |
| **관측성** | 전체 작업 포렌식을 위한 OTel Tracing + Cloud Audit Logs |
| **상호 운용성** | Gemini CLI, Claude Code, Cursor, VS Code, LangChain, ADK, CrewAI와 연동 |

### Developer Knowledge MCP

[Developer Knowledge MCP 서버](https://developers.google.com/knowledge/mcp)는 에이전트가 Firebase, Cloud, Android, Maps 등 공식 Google 문서에 기반하도록 합니다. 에이전트는 API 서명을 환각(hallucinate)하는 대신 실시간 문서 코퍼스를 쿼리합니다.

**한 줄 설치 (API 키 인증):**

```bash
gemini mcp add -t http \
  -H "X-Goog-Api-Key: YOUR_API_KEY" \
  google-developer-knowledge \
  https://developerknowledge.googleapis.com/mcp --scope user
```

**또는 `settings.json`을 통해 (엔터프라이즈용 ADC 인증):**

```json
{
  "mcpServers": {
    "google-developer-knowledge": {
      "httpUrl": "https://developerknowledge.googleapis.com/mcp",
      "authProviderType": "google_credentials",
      "oauth": {
        "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
      },
      "timeout": 30000,
      "headers": {
        "X-goog-user-project": "YOUR_PROJECT_ID"
      }
    }
  }
}
```

**사용 가능한 도구:**

| 도구 | 목적 |
|---|---|
| `search_documents` | 쿼리와 관련된 문서 청크 찾기 |
| `get_documents` | 특정 문서의 전체 페이지 콘텐츠 검색 |
| `answer_query` | 문서 코퍼스에서 합성되고 근거 있는 답변 얻기 |

### 카테고리별 고가치 MCP 서버

| 카테고리 | 서버 | 예시 사용 사례 |
|---|---|---|
| **개발자 문서** | Developer Knowledge API | "Cloud Run 자동 확장을 어떻게 구성하나요?" → 출처가 인용된 답변 |
| **데이터 및 분석** | BigQuery, Spanner, Firestore, AlloyDB | 에이전트 컨텍스트에서 직접 프로덕션 데이터 쿼리 |
| **인프라** | Cloud Run, GKE, Compute Engine | 자연어를 통해 인프라 프로비저닝, 확장 및 관리 |
| **생산성** | Gmail, Drive, Calendar, Chat | 스레드 요약, 문서 초안 작성, 초대 관리 |
| **보안** | Security Operations, Model Armor | 위협 조사, 실시간으로 프롬프트 인젝션 차단 |

> **거버넌스:** 에이전트가 호출할 수 있는 MCP 도구를 제한하려면 [IAM 거부 정책](https://docs.cloud.google.com/mcp/control-mcp-use-iam#deny-all-mcp-tool-use)을 사용하세요. 간접적인 프롬프트 인젝션 및 데이터 유출을 방어하려면 [Model Armor](https://docs.cloud.google.com/model-armor/model-armor-mcp-google-cloud-integration)와 결합하세요.

### 연습 문제

1. Google Cloud 프로젝트에서 Developer Knowledge API 키를 가져옵니다.
2. 위의 한 줄 명령어를 사용하여 Gemini CLI 구성에 Developer Knowledge MCP 서버를 추가합니다.
3. 에이전트에게 질문합니다: *"사용자 지정 도메인으로 Cloud Run 서비스를 배포하려면 어떻게 해야 하나요?"*
4. 확인: 응답이 공식 문서를 인용하나요? MCP 서버가 연결되지 않은 상태의 답변과 비교해 보세요.

---
## agents-cli를 사용한 에이전트 구축

[`agents-cli`](https://github.com/google/agents-cli)는 코딩 에이전트에게 Google의 [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform)에서 에이전트를 구축, 평가 및 배포하는 방법을 가르치는 CLI 및 스킬 팩입니다. 이것은 Gemini CLI를 대체하는 것이 아닙니다. 코딩 에이전트를 *위한* 도구입니다.

### 빠른 설정

```bash
# Install CLI + skills into all detected coding agents
uvx google-agents-cli setup

# Or install just the skills (your coding agent handles the rest)
npx skills add google/agents-cli
```

> **사전 요구 사항:** Python 3.11 이상, [uv](https://docs.astral.sh/uv/getting-started/installation/) 및 Node.js. 환경에 대한 참고 사항은 `setup.sh`를 참조하세요.

### 핵심 워크플로우

| 명령어 | 기능 |
|---|---|
| `agents-cli scaffold <name>` | 모범 사례 구조를 갖춘 새로운 ADK 에이전트 프로젝트 생성 |
| `agents-cli scaffold enhance` | 기존 에이전트 프로젝트에 배포, CI/CD 또는 RAG 추가 |
| `agents-cli eval run` | 에이전트 평가 실행 (LLM-as-judge, 궤적 채점) |
| `agents-cli deploy` | Google Cloud에 배포 (Agent Runtime, Cloud Run 또는 GKE) |
| `agents-cli publish gemini-enterprise` | Gemini Enterprise에 에이전트 등록 |

### 설치되는 스킬

`agents-cli setup`을 실행하면 코딩 에이전트에 7가지 스킬이 설치됩니다:

| 스킬 | 코딩 에이전트가 학습하는 내용 |
|---|---|
| `google-agents-cli-workflow` | 개발 수명 주기, 코드 보존 규칙, 모델 선택 |
| `google-agents-cli-adk-code` | ADK Python API — 에이전트, 도구, 오케스트레이션, 콜백, 상태 |
| `google-agents-cli-scaffold` | 프로젝트 스캐폴딩 — `create`, `enhance`, `upgrade` |
| `google-agents-cli-eval` | 평가 방법론 — 지표, 평가 세트(evalsets), LLM-as-judge |
| `google-agents-cli-deploy` | 배포 — Agent Runtime, Cloud Run, GKE, CI/CD, 보안 비밀(secrets) |
| `google-agents-cli-publish` | Gemini Enterprise 등록 |
| `google-agents-cli-observability` | Cloud Trace, 로깅, 서드파티 통합 |

### agents-cli와 Raw ADK 사용 시기 비교

| 시나리오 | 도구 |
|---|---|
| 모범 사례를 적용하여 처음부터 에이전트 구축 | `agents-cli scaffold` |
| 기존 에이전트에 RAG 또는 배포 추가 | `agents-cli scaffold enhance` |
| 구조화된 지표로 에이전트 품질 평가 | `agents-cli eval run` |
| 모든 권한을 가지고 수동으로 배포 | 직접 `adk deploy` 사용 |
| 스캐폴딩 없이 ADK 코드 작성 | Raw ADK + 코딩 에이전트 |

### 연습 문제

1. agents-cli 설치: `uvx google-agents-cli setup`
2. 새 에이전트 스캐폴딩: `agents-cli scaffold my-review-bot`
3. 스캐폴딩된 프로젝트를 Gemini CLI에서 열고 다음과 같이 질문합니다: *"Cloud Storage를 사용하여 이 에이전트에 RAG 기능을 추가해 줘"*
4. 평가 실행: `agents-cli eval run`
5. 설치된 스킬이 어떻게 Gemini CLI를 안내하여 원래라면 알지 못했을 ADK 특정 패턴을 사용하도록 하는지 관찰합니다.

---
## 추가 자료

| 리소스 | 설명 |
|---|---|
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 코딩 에이전트를 위한 20가지 프로덕션 수준의 엔지니어링 스킬 |
| [google/agents-cli](https://github.com/google/agents-cli) | Google Cloud에서 ADK 에이전트를 구축하기 위한 CLI + 스킬 |
| [Developer Knowledge MCP](https://developers.google.com/knowledge/mcp) | 공식 Google 개발자 문서를 기반으로 에이전트 그라운딩 |
| [Google Managed MCP Servers](https://cloud.google.com/blog/products/ai-machine-learning/google-managed-mcp-servers-are-available-for-everyone) | 50개 이상의 엔터프라이즈 MCP 서버 (Cloud 블로그) |
| [Supported MCP Products](https://docs.cloud.google.com/mcp/supported-products) | Google 관리형 MCP 서버의 전체 카탈로그 |
| [GoogleCloudPlatform/scion](https://github.com/GoogleCloudPlatform/scion) | 팀을 위한 멀티 에이전트 오케스트레이션 |
| [pauldatta/gemini-cli-field-workshop](https://github.com/pauldatta/gemini-cli-field-workshop) | 이 워크샵의 소스 저장소 |
| [Gemini CLI 문서](https://geminicli.com) | 공식 문서 |

---
## 다음 단계

→ 핵심 기능을 확인하려면 **[사용 사례 1: SDLC 생산성](sdlc-productivity.md)**으로 돌아가기

→ 브라운필드 워크플로우를 확인하려면 **[사용 사례 2: 레거시 코드 현대화](legacy-modernization.md)**로 계속 진행하기