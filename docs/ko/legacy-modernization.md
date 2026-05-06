# 사용 사례 2: 레거시 코드 현대화

> **소요 시간:** 약 60분  
> **목표:** 플랜 모드, 사용자 지정 서브에이전트, 스킬 및 체크포인트를 사용하여 레거시 애플리케이션을 마이그레이션합니다. 거대한 코드베이스를 안전하게 분해하는 방법을 배웁니다.  
> **실습 PRD:** [.NET 현대화](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_dotnet_modernization.md) · [Java 업그레이드](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_java_upgrade.md)
>
> *최종 업데이트: 2026-05-05 · [gemini-cli 저장소에 대해 검증된 소스](https://github.com/google-gemini/gemini-cli)*

---
## 2.1 — 플랜 모드: 안전한 리서치 (15분)

### 플랜 모드 진입

플랜 모드는 읽기 전용 리서치입니다. 에이전트는 코드베이스를 분석하고 변경 사항을 제안하지만, 사용자가 승인할 때까지 **아무것도 수정하지 않습니다**.

```
/plan
```

> CLI는 현재 플랜 모드에 있음을 나타냅니다. 에이전트는 쓰기 도구에 대한 액세스 권한을 잃게 되며, 오직 파일을 읽고, 웹을 검색하고, 생각하는 것만 가능합니다.

### 코드베이스 분석

```
Analyze this codebase for a migration to a modern architecture. 
Identify:
1. Key dependencies and their versions
2. Architectural patterns currently in use
3. Areas of technical debt
4. Migration risks and complexity hotspots
```

> **진행 상황:** 에이전트가 프로젝트(package.json, 소스 파일, 구성)를 읽고 멘탈 모델을 구축합니다. `read_file`, `glob`, `grep_search`와 같은 도구를 사용하여 필요에 따라 코드베이스를 탐색하고 모든 종속성, 패턴 및 안티 패턴을 추적합니다.

### 계획 검토

에이전트가 구조화된 마이그레이션 계획을 생성합니다. 주의 깊게 검토하세요:

```
Propose a step-by-step plan to modernize the authentication system 
from session-based to JWT with refresh tokens. Include:
- Files that need to change
- Order of operations
- Risk assessment for each step
- Rollback strategy
```

### 협업을 통한 계획 편집

외부 편집기를 열어 계획을 구체화합니다:

```
Ctrl+G
```

그러면 `$EDITOR`(또는 내장 편집기)가 열리고 계획을 직접 수정할 수 있습니다. 에이전트는 사용자의 편집 내용을 확인하고 접근 방식을 조정합니다.

### 플랜 모드 종료

```
/plan
```

일반 모드로 다시 전환합니다. 이제 에이전트가 승인된 계획을 실행할 수 있습니다.

---
## 2.2 — 모델 라우팅 및 모델 스티어링 (10분)

### 자동 모델 라우팅

Gemini CLI는 작업 복잡도에 따라 모델을 자동으로 선택할 수 있습니다:

| 작업 유형 | 일반적인 모델 | 이유 |
|---|---|---|
| 계획 수립, 아키텍처 분석 | **Gemini Pro** | 복잡한 추론, 장문 분석 |
| 코드 생성, 파일 편집 | **Gemini Flash** | 빠른 실행, 저렴한 비용 |
| 단순 쿼리, 상태 확인 | **Gemini Flash** | 속도 최적화 |

> 이 라우팅은 결정론적이지 않고 휴리스틱 기반입니다. CLI는 프롬프트 복잡도를 평가하여 그에 맞게 선택합니다. `/model`을 사용하여 특정 모델을 선택하도록 재정의할 수 있습니다. 자세한 내용은 [모델 라우팅](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/model-routing.md)을 참조하세요.

### 모델 스티어링 🔬

실행 도중에 에이전트의 방향을 조정할 수 있습니다:

```
# While the agent is working on a migration step:
Actually, skip the database migration for now. Focus on the API 
layer first — we need the endpoints working before we touch the schema.
```

> **모델 스티어링**을 사용하면 처음부터 다시 시작하지 않고도 경로를 수정할 수 있습니다. 에이전트는 사용자의 입력에 따라 계획을 조정하고 새로운 방향으로 계속 진행합니다.

### 활성화된 모델 확인

```
/stats
```

현재 모델, 토큰 사용량 및 캐싱 상태를 보여줍니다.

---
## 2.3 — 마이그레이션을 위한 컨텍스트 엔지니어링 (10분)

마이그레이션 프로젝트는 컨텍스트 엔지니어링이 가장 큰 효과를 발휘하는 곳입니다. 레거시 코드베이스는 아키텍처 패턴, 더 이상 사용되지 않는 API 사용, 숨겨진 종속성 체인 등 어디에도 기록되어 있지 않은 암묵적인 지식으로 가득 차 있습니다. 에이전트가 안전하게 변경 작업을 수행하려면 먼저 이를 내재화해야 합니다.

여기에는 두 가지 접근 방식이 있습니다. **수동** 방식(사용자가 직접 GEMINI.md를 작성)과 **에이전트 주도** 방식(에이전트가 대신 작성)입니다. 두 방식 모두 동일한 결과물을 생성하지만, 에이전트 주도 방식은 종종 사용자가 놓칠 수 있는 부분들을 찾아냅니다.

### 에이전트 주도: @codebase_investigator를 활용한 셀프 온보딩

마이그레이션에 있어 가장 강력한 패턴은 에이전트가 **코드베이스를 조사하고 자체적으로 GEMINI.md를 작성**하도록 하는 것입니다. 이것이 "에이전트 셀프 온보딩" 패턴으로, 시니어 엔지니어가 새 프로젝트에 합류할 때 하는 일을 기계의 속도로 수행하는 것과 같습니다.

**1단계 — 조사:**

```
@codebase_investigator Analyze this entire codebase. Map:
1. Framework versions, build system, and dependency tree
2. Architectural patterns (MVC, data access layers, security config)
3. All javax.* imports that will need jakarta.* migration
4. Configuration files and property sources
5. Test frameworks and coverage patterns
Report any migration risks or complexity hotspots.
```

> **진행 상황:** `@codebase_investigator` 서브에이전트가 모든 파일을 읽고, 가져오기(import)를 추적하고, 클래스 계층 구조를 매핑하여 전체적인 그림을 구성합니다. 이 모든 과정은 읽기 전용 모드로 진행됩니다. 어떤 것도 수정하지 않습니다.

**2단계 — 컨텍스트 생성:**

```
Based on your codebase analysis, write a GEMINI.md that:
1. Documents what you found (current state: Boot 2.6, Java 8, javax.*)
2. Defines the target state (Boot 3.3, Java 21, jakarta.*)
3. Lists migration rules (one module at a time, preserve API contracts)
4. Encodes testing standards (every phase must pass mvn clean verify)
5. Flags the specific risks you identified

Write this file to the project root as GEMINI.md.
```

**3단계 — 검토 및 개선:**

에이전트는 추측이 아닌 코드에서 실제로 발견한 내용을 바탕으로 GEMINI.md를 생성합니다. 이를 검토하고, 팀 고유의 규칙을 추가한 후 승인하세요. 이 시점부터 에이전트가 실행하는 모든 마이그레이션 명령은 이 컨텍스트의 안내를 받습니다.

> **이 방식이 효과적인 이유:** 에이전트가 스스로를 위한 지침을 작성하기 때문입니다. 에이전트가 생성한 GEMINI.md는 이후 자체 작업에 대한 가드레일이 됩니다. 이는 자기 강화 루프(self-reinforcing loop)입니다. 더 나은 컨텍스트 → 더 나은 코드 변경 → 에이전트가 더 많은 패턴을 학습 → 컨텍스트가 더욱 개선됨(자동 메모리를 통해).

> **실제 적용 사례 보기:** [Java Upgrade PRD](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_java_upgrade.md)는 이 패턴을 0단계(Phase 0)로 사용합니다. 에이전트는 마이그레이션 코드를 건드리기 전에 반드시 셀프 온보딩을 수행해야 합니다.

### 수동: 마이그레이션 표준 직접 작성

확립된 표준이 있는 팀의 경우, 직접 GEMINI.md를 작성하세요:

```markdown
# Migration Standards

## Target Architecture
- Framework: .NET 8 (or modern equivalent)
- Hosting: Cloud Run (containerized)
- Database: Cloud SQL with Entity Framework Core
- Auth: JWT with Google Identity Platform
- Config: appsettings.json (not web.config)

## Migration Rules
- Migrate one module at a time — never refactor everything at once
- Every migrated endpoint must have unit tests before moving on
- Preserve existing API contracts — no breaking changes to consumers
- Document every decision in a MIGRATION.md changelog
```

### @file 가져오기 구문

대규모 프로젝트의 경우, GEMINI.md를 모듈식 파일로 분할하세요:

```markdown
# GEMINI.md
@./docs/architecture.md
@./docs/coding-standards.md
@./docs/migration-checklist.md
```

> **가져오기가 중요한 이유:** 엔터프라이즈 프로젝트에서는 단일 GEMINI.md가 다루기 힘들어질 수 있습니다. 가져오기를 사용하면 유지 관리 및 검토가 더 쉬운 집중된 문서로 컨텍스트를 구성할 수 있습니다. 전체 구문은 [GEMINI.md 참조](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md)를 확인하세요.

### 마이그레이션 패턴을 위한 메모리

에이전트가 마이그레이션 중에 패턴을 발견하면 이를 저장합니다:

```
/memory show
```

또한 명시적으로 가르칠 수도 있습니다:

```
/memory add "When migrating Entity Framework 6 to EF Core, always 
check for .edmx files and replace them with code-first models. 
The database-first approach is deprecated in EF Core."
```

> **컨텍스트 엔지니어링 수명 주기:** 최고의 마이그레이션 워크플로우는 에이전트가 생성한 GEMINI.md(초기 컨텍스트), @file 가져오기(모듈식 표준), 자동 메모리(실행 중 학습된 패턴) 이 세 가지를 모두 결합합니다. 각각은 서로를 강화합니다.

---
## 2.4 — 서브에이전트: 전문화된 작업 위임 (15분)

### 내장 서브에이전트

Gemini CLI에는 일반적인 작업을 위한 내장 서브에이전트가 포함되어 있습니다:

```
@codebase_investigator Map the relationships between all controllers 
in the backend/ directory. Show which models each controller depends 
on and which routes call each controller.
```

> **@codebase_investigator**는 코드 관계를 매핑하고, 호출 체인을 추적하며, 아키텍처 패턴을 식별하는 읽기 전용 에이전트입니다. 이 에이전트는 절대 파일을 수정하지 않습니다.

### 사용자 정의 서브에이전트

마이그레이션을 위한 보안 스캐너를 생성합니다:

```bash
cat .gemini/agents/security-scanner.md
```

보안 스캐너 서브에이전트([`samples/agents/security-scanner.md`](../../samples/agents/security-scanner.md)에서 제공):
- 보안 분석에 집중된 시스템 프롬프트를 가지고 있습니다.
- 특정 도구로 제한될 수 있습니다.
- 특정 모델을 사용합니다 (속도를 위해 Flash를 할당하거나 깊이를 위해 Pro를 할당할 수 있습니다).

### 사용자 정의 서브에이전트 사용

```
@security-scanner Review the authentication middleware for OWASP 
Top 10 vulnerabilities. Check for:
1. Injection attacks (SQL, NoSQL)
2. Broken authentication
3. Sensitive data exposure
4. Missing rate limiting
```

### 서브에이전트 도구 격리

각 서브에이전트는 자체 도구 허용 목록을 가질 수 있습니다:

```markdown
# .gemini/agents/security-scanner.md
---
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - list_directory
  - google_web_search
# No write_file, no run_shell_command — this agent is read-only
---

You are a security analyst. Your job is to find vulnerabilities...
```

> **엔터프라이즈 가치:** 보안 스캐너는 코드를 읽고 CVE를 검색할 수 있지만, 파일을 수정하거나 명령을 실행할 수는 없습니다. 도구 격리는 심층 방어(defense-in-depth)입니다.

---
## 2.5 — 스킬: 재사용 가능한 전문 지식 (5분)

### 사용 가능한 스킬 보기

```
/skills list
```

스킬은 관련성이 있을 때 에이전트가 활성화하는 재사용 가능한 명령어 세트입니다:

### 스킬 작동 방식

1. **자동 활성화:** 에이전트는 스킬 설명을 읽고 프롬프트를 기반으로 관련 스킬을 활성화합니다.
2. **수동 활성화:** 스킬 이름을 사용하여 강제로 스킬을 활성화할 수 있습니다.
3. **지속성:** 스킬은 세션 간에 유지됩니다. 한 번 배우면 어디서든 사용할 수 있습니다.

### 자동 메모리 🔬

자동 메모리는 세션에서 패턴을 추출하여 GEMINI.md에 저장합니다:

```
/memory show
```

> **실험적 기능:** 자동 메모리를 사용하려면 `settings.json`에서 `experimental.autoMemory`를 활성화해야 합니다. [Auto Memory docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/auto-memory.md)를 참조하세요. 활성화되면 에이전트가 다음과 같은 패턴을 자동 저장할 수 있습니다: "Express.js 미들웨어를 마이그레이션할 때 `req.query`와 `req.params`의 불일치를 확인하세요."

---
## 2.6 — 체크포인트 및 Git 워크트리 (5분)

### 체크포인트

체크포인트는 변경 전 수정된 파일의 상태를 자동으로 저장하여, 문제가 발생했을 때 되돌릴 수 있게 해줍니다. 이를 활성화하려면 `settings.json`에 다음을 추가하세요:

```json
{
  "general": {
    "checkpointing": {
      "enabled": true
    }
  }
}
```

활성화된 경우, 이전 체크포인트로 되돌리려면 `/restore`를 사용하세요:

```
/restore
```

> **체크포인트는 가볍습니다** — 전체 git 히스토리가 아닌 파일 변경 사항만 추적합니다. 자세한 내용은 [체크포인트 문서](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/checkpointing.md)를 참조하세요.

### Git 워크트리 🔬

병렬 마이그레이션 작업을 위해 Git 워크트리를 사용하세요:

```
# Create a worktree for the auth migration
git worktree add ../proshop-auth-migration feature/auth-migration
cd ../proshop-auth-migration
gemini
```

> **왜 워크트리를 사용하나요?** 한 터미널에는 원본 코드를, 다른 터미널에는 마이그레이션된 코드를 둘 수 있습니다. 두 코드에서 동시에 테스트를 실행할 수 있습니다. 브랜치를 전환하지 않고도 접근 방식을 비교할 수 있습니다.

---
## 실습

**.NET Modernization PRD** 또는 **Java Upgrade PRD**를 열고 마이그레이션을 진행해 보세요. 다음 접근 방식 중 하나를 선택하세요:

### 접근 방식 A: Conductor 우선 (계획 → 컨텍스트 → 실행)

구조화된 계획으로 시작하여 계획이 컨텍스트 생성을 주도하도록 합니다:

1. **플랜 모드**(`/plan`) 진입 → 대상 코드베이스를 읽기 전용으로 분석합니다.
2. **Conductor**를 사용하여 PRD 단계와 일치하는 단계별 마이그레이션 계획을 생성합니다.
3. 마이그레이션 표준과 승인된 계획을 인코딩하는 **GEMINI.md**를 작성합니다.
4. **@codebase_investigator**를 사용하여 종속성을 매핑하고 계획을 검증합니다.
5. 시작하기 전에 **체크포인트**를 생성합니다.
6. 플랜 모드 종료 → 한 번에 한 단계씩 마이그레이션을 시작합니다.
7. 필요에 따라 **모델 스티어링**을 사용하여 방향을 수정합니다.
8. 각 단계가 끝난 후 `mvn clean verify` 및 보안 스캔을 실행합니다(아래 참조).
9. **Auto Memory**가 세션에서 학습한 내용을 검토합니다.

### 접근 방식 B: 셀프 온보딩 (조사 → 컨텍스트 → 계획 → 실행)

에이전트가 먼저 자체적인 이해를 구축하도록 한 다음, 발견한 내용을 바탕으로 계획을 세웁니다:

1. **@codebase_investigator**를 사용하여 대상 코드베이스를 분석하고 종속성을 매핑합니다.
2. 에이전트가 분석을 기반으로 **GEMINI.md를 작성**하도록 합니다(에이전트 셀프 온보딩).
3. 생성된 컨텍스트를 검토하고 구체화합니다 — 팀별 표준을 추가합니다.
4. **플랜 모드** 진입 → **Conductor**가 GEMINI.md를 바탕으로 단계별 마이그레이션 계획을 생성하도록 합니다.
5. 시작하기 전에 **체크포인트**를 생성합니다.
6. 마이그레이션을 시작합니다 — 필요에 따라 **모델 스티어링**을 사용하여 방향을 수정합니다.
7. 각 단계가 끝난 후 `mvn clean verify` 및 보안 스캔을 실행합니다(아래 참조).
8. **Auto Memory**가 세션에서 학습한 내용을 검토합니다.

> **어떤 접근 방식을 선택해야 할까요?** 접근 방식 A는 이미 코드베이스를 알고 있고 구조를 주도하고자 할 때 잘 작동합니다. 접근 방식 B는 익숙하지 않은 레거시 코드에 더 적합합니다. 에이전트는 사람이 작성한 계획에서는 놓칠 수 있는 마이그레이션 위험을 종종 발견합니다. 두 가지를 모두 시도해 보고 결과 계획의 품질을 비교해 보세요.

> **마이그레이션 후 보안 스캔:** 레거시 코드를 현대화한 후, 공식 [보안 확장 프로그램](https://github.com/gemini-cli-extensions/security)을 실행하여 마이그레이션 중에 도입된 취약점을 찾아내세요. `gemini extensions install https://github.com/gemini-cli-extensions/security`로 설치한 다음, `/security:analyze`를 실행하여 변경 사항을 스캔합니다. 자세한 내용은 [확장 프로그램 생태계 — 실습 4](extensions-ecosystem.md)를 참조하세요.

---
## 요약: 학습한 내용

| 기능 | 설명 |
|---|---|
| **플랜 모드** | 읽기 전용 조사 — 수정 전 분석 |
| **모델 라우팅** | 자동 Pro (계획) → Flash (코딩) 선택 |
| **모델 스티어링** | 진행 중인 에이전트의 방향 수정 |
| **에이전트 셀프 온보딩** | 에이전트가 코드베이스를 조사하고 자체 GEMINI.md 작성 |
| **@ import 구문** | 대규모 프로젝트를 위한 모듈식 GEMINI.md |
| **@codebase_investigator** | 읽기 전용 코드베이스 분석 서브에이전트 |
| **맞춤형 서브에이전트** | 도구 격리가 적용된 특화된 에이전트 |
| **스킬** | 자동으로 활성화되는 재사용 가능한 명령어 세트 |
| **자동 메모리** | 에이전트가 세션에서 패턴을 학습 |
| **체크포인트** | 위험한 변경 전 자동 상태 저장/복원 (settings.json에서 활성화) |
| **Git 워크트리** | 동시 작업을 위한 병렬 브랜치 |
| **보안 확장 프로그램** | `/security:analyze`를 사용한 마이그레이션 후 취약점 스캔 |

---
## 다음 단계

→ **[사용 사례 3: 에이전트 기반 DevOps 오케스트레이션](devops-orchestration.md)**으로 계속

→ 파워 유저를 위한: **[고급 패턴](advanced-patterns.md)** — 프롬프트 작성 기술, 검증 루프 및 병렬 개발
