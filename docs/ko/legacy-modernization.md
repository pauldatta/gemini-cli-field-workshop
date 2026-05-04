# 사용 사례 2: 레거시 코드 현대화

> **소요 시간:** 약 60분  
> **목표:** 플랜 모드, 맞춤형 서브에이전트, 스킬 및 체크포인트를 사용하여 레거시 애플리케이션을 마이그레이션합니다. 방대한 코드베이스를 안전하게 분해하는 방법을 배웁니다.  
> **실습 PRD:** [.NET 현대화](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_dotnet_modernization.md) · [Java 업그레이드](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_java_upgrade.md)

---
## 2.1 — 플랜 모드: 안전한 조사 (15분)

### 플랜 모드 진입

플랜 모드는 읽기 전용 조사입니다. 에이전트는 코드베이스를 분석하고 변경 사항을 제안하지만, 사용자가 승인할 때까지 **아무것도 수정하지 않습니다**.

```
/plan
```

> 프롬프트 표시기가 변경되어 플랜 모드에 있음을 보여줍니다. 에이전트는 쓰기 도구에 대한 접근 권한을 잃으며, 파일을 읽고, 웹을 검색하고, 생각하는 것만 가능합니다.

### 코드베이스 분석

```
Analyze this codebase for a migration to a modern architecture. 
Identify:
1. Key dependencies and their versions
2. Architectural patterns currently in use
3. Areas of technical debt
4. Migration risks and complexity hotspots
```

> **진행 상황:** 에이전트가 package.json, 소스 파일, 구성 등 전체 프로젝트를 읽고 멘탈 모델을 구축합니다. 모든 종속성, 모든 패턴, 모든 안티 패턴 등 전체 아키텍처를 동시에 컨텍스트에 유지할 수 있습니다.

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

### 협업 계획 편집

여러 줄 편집기를 열어 계획을 구체화합니다:

```
Ctrl+X
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

Gemini CLI는 작업 복잡도에 따라 모델 간에 자동으로 라우팅합니다:

| 작업 유형 | 사용된 모델 | 이유 |
|---|---|---|
| 계획 수립, 아키텍처 분석 | **Gemini Pro** | 복잡한 추론, 장문 분석 |
| 코드 생성, 파일 편집 | **Gemini Flash** | 빠른 실행, 낮은 비용 |
| 단순 쿼리, 상태 확인 | **Gemini Flash** | 속도 최적화 |

> 이를 구성할 필요는 없습니다. 자동으로 수행됩니다. 에이전트가 각 단계에 맞는 적절한 모델을 선택합니다.

### 모델 스티어링 🔬

실행 도중에 에이전트를 스티어링할 수 있습니다:

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

### 마이그레이션 표준 설정

대상 아키텍처를 인코딩하는 GEMINI.md를 생성합니다:

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

### @ Import 구문

대규모 프로젝트의 경우, GEMINI.md를 모듈식 파일로 분할합니다:

```markdown
# GEMINI.md
@import ./docs/architecture.md
@import ./docs/coding-standards.md
@import ./docs/migration-checklist.md
```

> **Import가 중요한 이유:** 엔터프라이즈 프로젝트의 경우 단일 GEMINI.md는 다루기 힘들어질 수 있습니다. Import를 사용하면 유지 관리 및 검토가 더 쉬운 집중된 문서로 컨텍스트를 구성할 수 있습니다.

### 마이그레이션 패턴을 위한 메모리

에이전트가 마이그레이션 중에 패턴을 발견하면 이를 저장합니다:

```
/memory show
```

명시적으로 가르칠 수도 있습니다:

```
/memory add "When migrating Entity Framework 6 to EF Core, always 
check for .edmx files and replace them with code-first models. 
The database-first approach is deprecated in EF Core."
```

---
## 2.4 — 서브에이전트: 전문화된 작업 위임 (15분)

### 내장 서브에이전트

Gemini CLI는 일반적인 작업을 위한 내장 서브에이전트를 포함하고 있습니다:

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
- 보안 분석에 초점을 맞춘 시스템 프롬프트를 가집니다.
- 특정 도구로 제한될 수 있습니다.
- 특정 모델을 사용합니다(속도를 위해 Flash를, 깊이를 위해 Pro를 할당할 수 있습니다).

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
model: gemini-2.5-flash
tools:
  - read_file
  - list_directory
  - web_search
# No write_file, no run_shell_command — this agent is read-only
---

You are a security analyst. Your job is to find vulnerabilities...
```

> **엔터프라이즈 가치:** 보안 스캐너는 코드를 읽고 CVE를 검색할 수 있지만, 절대 파일을 수정하거나 명령을 실행할 수 없습니다. 도구 격리는 심층 방어(defense-in-depth)입니다.

---
## 2.5 — 스킬: 재사용 가능한 전문 지식 (5분)

### 사용 가능한 스킬 보기

```
/skills list
```

스킬은 관련성이 있을 때 에이전트가 활성화하는 재사용 가능한 명령 세트입니다:

### 스킬 작동 방식

1. **자동 활성화:** 에이전트가 스킬 설명을 읽고 프롬프트를 기반으로 관련 스킬을 활성화합니다.
2. **수동 활성화:** 이름으로 스킬을 강제 적용할 수 있습니다.
3. **지속성:** 스킬은 세션 간에 유지됩니다 — 한 번 배우면 어디서나 사용할 수 있습니다.

### 자동 메모리 🔬

자동 메모리는 세션에서 스킬을 자동으로 추출합니다:

```
/memory show
```

> 마이그레이션을 완료한 후 에이전트는 다음과 같이 자동 저장할 수 있습니다: "Express.js 미들웨어를 마이그레이션할 때 `req.query`와 `req.params`의 불일치를 확인하세요 — 이전 API는 쿼리 문자열을 사용했고, 새 API는 경로 매개변수를 사용합니다."

---
## 2.6 — 체크포인트 및 Git 워크트리 (5분)

### 체크포인트

위험한 변경을 수행하기 전에 체크포인트를 저장하세요:

```
/checkpoint
```

이렇게 하면 수정된 모든 파일의 현재 상태가 저장됩니다. 문제가 발생할 경우:

```
/restore
```

> **체크포인트는 가볍습니다** — 전체 git 기록이 아닌 파일 변경 사항만 추적합니다. 여러 파일을 리팩터링하기 전에 자유롭게 사용하세요.

### Git 워크트리 🔬

병렬 마이그레이션 작업을 위해 Git 워크트리를 사용하세요:

```
# Create a worktree for the auth migration
git worktree add ../proshop-auth-migration feature/auth-migration
cd ../proshop-auth-migration
gemini
```

> **왜 워크트리를 사용하나요?** 한 터미널에는 원본 코드를, 다른 터미널에는 마이그레이션된 코드를 둘 수 있습니다. 두 코드에서 동시에 테스트를 실행하세요. 브랜치를 전환하지 않고도 접근 방식을 비교할 수 있습니다.

---
## 실습 연습

**.NET 현대화 PRD** 또는 **Java 업그레이드 PRD**를 열고 마이그레이션을 진행합니다:

1. **플랜 모드** 진입 → 대상 코드베이스 분석
2. 마이그레이션 표준을 포함한 **GEMINI.md** 생성
3. **Conductor**를 사용하여 단계별 마이그레이션 계획 생성
4. **@codebase_investigator**를 사용하여 종속성 매핑
5. 시작하기 전에 **체크포인트** 생성
6. 마이그레이션 시작 — 필요에 따라 **모델 스티어링**을 사용하여 방향 수정
7. 각 단계가 끝난 후 **@security-scanner**로 확인
8. 세션에서 **Auto Memory**가 학습한 내용 검토

---
## 요약: 배운 내용

| 기능 | 설명 |
|---|---|
| **플랜 모드** | 읽기 전용 조사 — 수정 전 분석 |
| **모델 라우팅** | 자동 Pro (계획) → Flash (코딩) 선택 |
| **모델 스티어링** | 진행 중인 에이전트의 방향 수정 |
| **@ import 구문** | 대규모 프로젝트를 위한 모듈식 GEMINI.md |
| **@codebase_investigator** | 읽기 전용 코드베이스 분석 서브에이전트 |
| **사용자 지정 서브에이전트** | 도구 격리가 적용된 특화된 에이전트 |
| **스킬** | 자동 활성화되는 재사용 가능한 명령어 세트 |
| **자동 메모리** | 세션에서 패턴을 학습하는 에이전트 |
| **체크포인트** | 위험한 변경 전 상태 저장/복원 |
| **git 워크트리** | 동시 작업을 위한 병렬 브랜치 |

---
## 다음 단계

→ **[사용 사례 3: 에이전트 기반 DevOps 오케스트레이션](devops-orchestration.md)**(으)로 계속

→ 파워 유저를 위한: **[고급 패턴](advanced-patterns.md)** — 프롬프팅 기술, 검증 루프 및 병렬 개발