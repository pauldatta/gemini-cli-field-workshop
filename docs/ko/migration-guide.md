# M09 — 마이그레이션 가이드: Gemini CLI → Antigravity CLI

**소요 시간:** 30분  
**대상:** 전체  
**사전 준비:** M01 (첫 만남)  
**목표:** 2026년 6월 18일 전환을 이해하고, 기존의 모든 구성을 마이그레이션하며, 팀에 맞는 올바른 진행 방향을 결정합니다.

> **⚠️ 시간 민감:** Gemini CLI는 **2026년 6월 18일**에 무료 플랜, Google AI Pro 및 Google AI Ultra 사용자에 대한 서비스를 중단합니다. 이 모듈은 팀이 워크플로우가 중단되는 상황을 겪지 않도록 모든 마이그레이션 단계를 안내합니다.

---
## 배경: 이러한 변화가 일어나는 이유

Google이 2025년에 Gemini CLI를 출시했을 때, 목표는 Gemini를 터미널로 직접 가져오는 것이었습니다. 100,000개 이상의 GitHub 별, 6,000개의 병합된 풀 리퀘스트, 그리고 수백만 명의 사용자를 거치면서 팀은 중요한 사실을 깨달았습니다. 이제 개발자들에게는 워크플로우의 나머지 부분과 통합된 백엔드를 공유하면서 **서로 통신하는 여러 에이전트**가 필요하다는 것입니다.

이러한 아키텍처적 요구가 통합을 이끌었습니다. 그 결과물이 바로 **Antigravity CLI**(`agy`)입니다. 이는 Antigravity 2.0 데스크톱 애플리케이션과 동일한 하네스를 공유하는 Go 기반의 에이전트 우선 터미널 경험입니다. 에이전트 엔진에 대한 모든 핵심 개선 사항은 모든 곳에 자동으로 적용됩니다.

Gemini CLI의 주요 변경 사항:

| 구분 | Gemini CLI | Antigravity CLI |
|:---|:---|:---|
| **언어** | Node.js / TypeScript | Go (더 빠른 콜드 스타트) |
| **바이너리 이름** | `gemini` | `agy` |
| **라이선스** | Apache 2.0 (오픈 소스) | 비공개 소스 |
| **멀티 에이전트** | 서브에이전트 (단일 세션) | 비동기, 백그라운드 오케스트레이션 |
| **데스크톱 동기화** | 없음 | Antigravity 2.0과 하네스 공유 |
| **스킬 경로** | `.gemini/skills/` | `.agents/skills/` |
| **플러그인 형식** | `settings.json`의 확장 프로그램 | Antigravity 플러그인 (`plugin.json`) |
| **MCP 설정** | `settings.json`에 인라인으로 포함 | 별도의 `mcp_config.json` |
| **컨텍스트 파일** | `GEMINI.md` | `GEMINI.md` **또는** `AGENTS.md` (둘 다 작동함) |

**참고 자료:**
- [Google I/O 발표 (2026년 5월 19일)](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
- [공식 마이그레이션 문서](https://antigravity.google/docs/gcli-migration)
- [커뮤니티 마이그레이션 가이드](https://avinashsangle.com/blog/gemini-cli-to-antigravity-cli-guide)

---
## 9.1 — 누가 영향을 받나요? (5분)

**영향 매트릭스 표시:**

| 플랜 | 2026년 6월 18일 기준 상태 | 권장 조치 |
|:---|:---|:---|
| **무료 플랜 (개인용 Gemini Code Assist)** | 지원 중단 | Antigravity CLI로 마이그레이션 |
| **Google AI Pro (월 $19.99)** | Gemini CLI 지원 중단 | Antigravity Pro 플랜 자동 적용, 새로운 요청 제한 확인 |
| **Google AI Ultra (월 $249.99)** | Gemini CLI 지원 중단 | Antigravity Ultra 플랜(주간 한도 없음) 자동 적용 |
| **Gemini Code Assist Standard / 엔터프라이즈** | ✅ 변경 없음 | 선택적 마이그레이션, Gemini CLI 계속 작동 |
| **GitHub용 Gemini Code Assist (GCP를 통해 결제)** | 기존 설치는 변경 없음, 신규 설치는 차단됨 | 다음 갱신 전에 마이그레이션 계획 |

> **Standard/엔터프라이즈 플랜을 사용하는 워크숍 참가자의 경우:** 마이그레이션을 강제하지 않습니다. 지금 바로 Antigravity CLI를 사용할 수 있으며 평가해 볼 가치가 있지만, 기존 투자는 보호됩니다.

**Gemini CLI의 오픈 소스 바이너리를 계속 유지하려는 경우 두 가지 경로가 있습니다:**
1. **유료 Gemini API 키**(AI Studio 또는 Vertex AI)를 Apache 2.0 Gemini CLI 바이너리에 연결합니다. 스킬, 훅 및 MCP 설정은 변경할 필요가 없습니다.
2. 관리 및 지원되는 경로를 위해 **Gemini Code Assist Standard 또는 엔터프라이즈**로 업그레이드합니다.

> 참고: Antigravity CLI는 **비공개 소스**이며, 이는 Gemini CLI의 Apache 2.0 모델에서 의도적으로 벗어난 것입니다. 규제 대상 환경에서 공급업체 중립적 이식성, 감사 또는 포크 권한이 중요한 경우 유료 API 키 경로가 이러한 속성을 보존합니다.

---
## 9.2 — Antigravity CLI 설치 (5분)

> **모범 사례:** 전환 기간 동안 두 바이너리(`gemini` 및 `agy`)를 나란히 설치해 두세요. 완전히 전환하기 전에 두 가지 모두에서 워크플로우를 실행하여 동일하게 작동하는지 확인하세요.

### macOS 및 Linux

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

바이너리는 `~/.local/bin/agy`에 설치됩니다. 해당 디렉터리가 `PATH`에 없는 경우:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

### Windows PowerShell

```powershell
irm https://antigravity.google/cli/install.ps1 | iex
```

### Windows CMD

```cmd
curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && install.cmd && del install.cmd
```

### 첫 실행 및 OAuth

```bash
agy
```

그러면 Google OAuth를 위한 기본 브라우저가 열립니다. 플러그인 가져오기 시 올바른 작업 공간을 선택할 수 있도록 **Gemini CLI에 사용한 것과 동일한 계정**으로 로그인하세요. 원격 SSH 환경의 경우, `agy`는 세션을 감지하고 로컬에서 열 수 있는 인증 URL을 출력합니다(Gemini CLI의 이전 흐름보다 개선된 기능).

**설치 확인:**

```bash
agy --version
```

---
## 9.3 — 플러그인 및 확장 프로그램 마이그레이션 (5분)

Gemini CLI의 확장 프로그램은 Antigravity CLI 플러그인이 됩니다. import 명령이 이 작업의 대부분을 자동으로 처리합니다.

### 1단계 — 자동 가져오기

```bash
agy plugin import gemini
```

이 명령은 Gemini CLI 확장 프로그램 디렉터리를 스캔하고 각각을 Antigravity 플러그인으로 등록합니다. 사용자 지정 테마에 의존하던 플러그인은 테마가 조용히 삭제되므로, `plugin.json` 형식을 사용하여 수동으로 다시 빌드해야 합니다.

### 2단계 — 가져온 플러그인 확인

```bash
agy plugin list
```

### 3단계 — 작업 공간 스킬 이동

```bash
# Skills used to live here (per-workspace):
# .gemini/skills/

# They now live here:
# .agents/skills/

cp -r .gemini/skills/ .agents/skills/
```

전역 스킬 디렉터리는 새 경로에서 자동으로 로드됩니다. 스킬 SKILL.md 파일의 내용은 변경할 필요가 없습니다.

> **워크샵 컨텍스트 파일은 이전 버전과 호환됩니다.** `GEMINI.md` 및 `AGENTS.md` 모두 수정 없이 읽을 수 있습니다. 기존 프로젝트 컨텍스트 파일의 이름을 바꾸거나 형식을 다시 지정할 필요가 없습니다.

---
## 9.4 — MCP 서버 설정 마이그레이션 (5분)

MCP 서버 설정은 인라인 `settings.json`에서 전용 `mcp_config.json`으로 이동하며, 하나의 필드 이름이 변경됩니다.

### 이전 (Gemini CLI `settings.json`)

```json
{
  "mcpServers": {
    "bigquery-mcp": {
      "command": "npx",
      "args": ["-y", "@google/bigquery-mcp-server"],
      "url": "http://localhost:3000"
    },
    "developer-knowledge": {
      "command": "npx",
      "args": ["-y", "@google/developer-knowledge-mcp"],
      "url": "http://localhost:3001"
    }
  }
}
```

### 이후 (Antigravity CLI `mcp_config.json`)

```json
{
  "mcpServers": {
    "bigquery-mcp": {
      "command": "npx",
      "args": ["-y", "@google/bigquery-mcp-server"],
      "serverUrl": "http://localhost:3000"
    },
    "developer-knowledge": {
      "command": "npx",
      "args": ["-y", "@google/developer-knowledge-mcp"],
      "serverUrl": "http://localhost:3001"
    }
  }
}
```

**유일한 변경 사항은 `url`이 `serverUrl`로 바뀌는 것입니다.** 다른 모든 필드는 동일하게 유지됩니다.

**로드된 MCP 서버 확인:**

```bash
agy /mcp
```

---
## 9.5 — 훅 검증 및 엔드투엔드 실행 (5분)

Antigravity CLI에서 훅은 계속해서 작동합니다. 훅 기반 워크플로우를 다시 실행하여 `pre-tool-call` 및 `stop` 훅이 예상대로 실행되는지 확인합니다.

```bash
# Run a representative workflow you trust
agy "Analyze backend/controllers/orderController.js and summarize the error handling patterns"

# Compare to Gemini CLI output if you still have it running
gemini "Analyze backend/controllers/orderController.js and summarize the error handling patterns"
```

**CLI 인터페이스에서 변경된 사항 (주의 사항):**

| Gemini CLI | Antigravity CLI | 참고 |
|:---|:---|:---|
| `gemini --resume` | `agy --resume` | 동일한 동작 |
| `gemini -p "prompt"` | `agy -p "prompt"` | 헤드리스 모드 유지됨 |
| `/tools` | `/tools` | 변경 없음 |
| `/rewind` | `/rewind` | 변경 없음 |
| `gemini skills` (터미널 명령어) | agy 내에서 `/skills` 사용 | 터미널 수준 명령어 제거됨 |
| `--temperature`, `--top_k` | CLI 인터페이스에 노출되지 않음 | 설정 또는 프롬프트를 통해 설정 |

---
## 9.6 — 요청 제한 및 가격 현실 점검 (5분)

> **무료 플랜 사용자를 위한 주의 사항:** 무료 플랜은 이전 Gemini CLI의 무료 플랜보다 훨씬 더 제한적입니다.

| 플랜 | Gemini CLI (이전) | Antigravity CLI |
|:---|:---|:---|
| **무료 플랜** | 일일 약 1,000회 요청 | 주간 할당량; 엄격한 주간 한도 내에서 5시간마다 갱신됨 |
| **Pro (월 $19.99)** | 합리적인 일일 한도 | Antigravity Pro 플랜 |
| **Ultra (월 $249.99)** | 높은 일일 한도 | 주간 한도 없음 |

커뮤니티 보고서(GitHub Discussion #27274)에 따르면 무료 플랜의 주간 한도는 **4~5번의 채팅 턴** 만에 소진되며, 초기화까지 166시간이 걸립니다. 워크숍 실습에 Antigravity CLI를 사용하는 경우 이를 고려하여 계획하세요.

**워크숍 진행을 위한 실용적인 권장 사항:**
- 조직에 Standard/엔터프라이즈 라이선스가 있는 경우, 실습 모듈에는 계속해서 Gemini CLI를 사용하고 이 모듈을 사용하여 팀에게 마이그레이션 경로를 안내하세요.
- 개인 계정으로 실행하는 경우, 유료 Pro/Ultra 플랜을 사용하거나 API 키 기반의 대체 수단을 준비하세요.

---
## 9.7 — 의사 결정 프레임워크: 유지, 마이그레이션, 아니면 전환? (5분)

이 의사 결정 트리를 사용하여 올바른 경로를 추천하세요:

```
Are you on Gemini Code Assist Standard or Enterprise?
├── YES → Keep Gemini CLI. Evaluate Antigravity CLI in parallel.
│         No forced migration. Your access is unchanged.
└── NO → Continue below.

Do you need open-source auditability, forking rights, or vendor-neutral plumbing?
├── YES → Stay on Gemini CLI + paid Gemini API key (AI Studio or Vertex AI).
│         Apache 2.0 toolchain, zero migration required.
└── NO → Continue below.

Do you do heavy long-context refactors, CI agents, or MCP-intensive workflows?
├── YES → Evaluate Claude Code with Opus 4.6 (1M context, 77.2% SWE-bench).
│         Strongest open alternative for terminal-first coding.
└── NO → Migrate to Antigravity CLI.
         agy plugin import gemini covers 90% of the work.
```

---
## 실습: 라이브 마이그레이션 (시간이 허락하는 경우)

워크숍 저장소 자체에 대해 마이그레이션 체크리스트를 진행해 보세요:

```bash
# 1. Install
curl -fsSL https://antigravity.google/cli/install.sh | bash

# 2. Authenticate
agy

# 3. Import plugins
agy plugin import gemini

# 4. Move skills
cp -r .gemini/skills/ .agents/skills/

# 5. Create mcp_config.json from existing settings.json
# (change url → serverUrl for each server entry)

# 6. Validate
agy /mcp
agy /skills

# 7. Run a known-good workflow
agy "Trace the request lifecycle for placing an order in the ProShop demo app"
```

---
## 핵심 요약

- **기한:** 무료 플랜, AI Pro 및 AI Ultra 사용자의 경우 2026년 6월 18일입니다. 엔터프라이즈는 영향을 받지 않습니다.
- **마이그레이션 소요 시간:** 스킬, 훅 및 MCP 서버가 있는 작업 공간당 30~60분입니다.
- **`GEMINI.md`는 그대로 작동합니다.** 이름 변경이나 재포맷이 필요하지 않습니다.
- **가장 주의할 점:** MCP 구성이 `mcp_config.json`으로 이동하며 `url`이 `serverUrl`로 이름이 변경됩니다.
- **요청 제한:** 무료 플랜은 훨씬 더 엄격해집니다. 이에 맞춰 예산을 계획하세요.
- **엔터프라이즈 팀:** 기존 Gemini CLI에 대한 투자는 보호됩니다. 마이그레이션은 선택 사항입니다.

---
## 참고 자료

- [공식 발표 — Google Developers Blog](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
- [공식 마이그레이션 문서 — antigravity.google](https://antigravity.google/docs/gcli-migration)
- [커뮤니티 가이드 — Avinash Sangle](https://avinashsangle.com/blog/gemini-cli-to-antigravity-cli-guide)
- [GitHub Discussion #27274 — 커뮤니티 반응](https://github.com/google-gemini/gemini-cli/discussions/27274)
- [Antigravity CLI 다운로드](https://antigravity.google/download)
