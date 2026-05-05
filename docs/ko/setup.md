# 환경 설정

> 사용 사례를 시작하기 전에 이 단계를 완료하세요. 약 15분이 소요됩니다.
>
> *최종 업데이트: 2026-05-05 · [gemini-cli 저장소 기준 검증됨](https://github.com/google-gemini/gemini-cli)*

---
## 시스템 요구 사항

| 구성 요소      | 최소 사양 | 권장 사양                                               |
| -------------- | --------- | ------------------------------------------------------- |
| **Node.js**    | v18.0.0   | v20+ (LTS)                                              |
| **npm**        | v9+       | v10+                                                    |
| **Git**        | v2.30+    | v2.40+                                                  |
| **터미널**     | 제한 없음 | iTerm2 (macOS), Windows Terminal 또는 VS Code 통합 터미널 |
| **디스크 공간**| 500MB     | 1GB (데모 앱 + node_modules 포함)                       |
| **jq**         | 선택 사항 | 훅 예제에 필요                                          |

---
## 1단계: 워크숍 클론하기

```bash
git clone https://github.com/pauldatta/gemini-cli-field-workshop.git
cd gemini-cli-field-workshop
```

---
## 2단계: 설정 스크립트 실행

설정 스크립트가 Gemini CLI 설치, 데모 앱 체크아웃 및 구성을 포함한 모든 작업을 처리합니다:

```bash
chmod +x setup.sh
./setup.sh
```

**수행하는 작업:**

1. Node.js, npm 및 Git이 설치되어 있는지 확인합니다.
2. Gemini CLI를 전역으로 설치/업데이트합니다(`npm install -g @google/gemini-cli`).
3. `demo-app/` 하위 모듈(ProShop v2)을 초기화하고 `npm install`을 실행합니다.
4. 데모 앱에 샘플 구성을 복사합니다:
   - `GEMINI.md` 컨텍스트 계층 구조
   - 훅 스크립트(시크릿 스캐너, 자동 테스트, 세션 로거, 경로 가드)
   - 정책 엔진 규칙
   - 사용자 지정 서브에이전트 정의
5. Gemini CLI 인증을 확인합니다.

---
## 3단계: 인증

### 옵션 A: 개인 Google 계정 (무료 등급)

워크숍 및 평가용으로 가장 적합합니다. GCP 프로젝트가 필요하지 않습니다.

```bash
cd demo-app
gemini
# Follow the browser-based OAuth flow
```

> **무료 등급 한도:** 개인 Google AI 등급은 워크숍 사용에 적합한 넉넉한 일일 한도를 제공합니다. [할당량 및 가격 책정](https://geminicli.com/docs/resources/quota-and-pricing/)을 참조하세요.

### 옵션 B: Vertex AI (엔터프라이즈)

프로덕션 및 엔터프라이즈 배포용입니다. 결제가 설정된 GCP 프로젝트가 필요합니다.

```bash
# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Authenticate
gcloud auth application-default login
```

Gemini CLI는 Vertex AI 자격 증명을 자동으로 감지합니다. 엔터프라이즈 인증 적용에 대해서는 [엔터프라이즈 가이드](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md)를 참조하세요.

---
## 4단계: 설치 확인

```bash
# Check Gemini CLI version
gemini --version

# Quick test (should respond instantly)
gemini -p "Say 'Workshop ready!' in exactly two words."

# Verify the demo app is set up
ls demo-app/GEMINI.md          # Should exist
ls demo-app/.gemini/hooks/     # Should contain 4 hook scripts
ls demo-app/.gemini/policies/  # Should contain team-guardrails.toml
```

---
## 문제 해결

| 문제                                      | 해결 방법                                                                                                                                                                     |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `npm install -g` 명령이 `EACCES` 오류와 함께 실패함      | `sudo npm install -g @google/gemini-cli`를 사용하거나 npm 권한을 수정하세요: [npm docs](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally) |
| 설치 후 `gemini: command not found` 오류 발생 | 터미널을 다시 시작하거나 `source ~/.bashrc` / `source ~/.zshrc`를 실행하세요                                                                                                           |
| OAuth 흐름에서 브라우저가 열리지 않음           | 터미널에서 URL을 복사하여 수동으로 여세요                                                                                                                           |
| `git submodule update` 명령이 실패함              | `git submodule init && git submodule update --recursive`를 실행하세요                                                                                                                  |
| 데모 앱 `npm install` 명령이 실패함              | Node.js 버전을 확인하세요(`node --version`). ProShop v2는 Node 18 이상이 필요합니다.                                                                        |
| 워크숍 중 속도 제한(Rate limit) 오류 발생         | Vertex AI 인증으로 전환하거나 60초를 기다린 후 다시 시도하세요                                                                                              |
| 훅이 실행되지 않음                       | `chmod +x demo-app/.gemini/hooks/*.sh`를 실행하세요                                                                                                                                    |
| `jq: command not found` 오류 발생                  | jq를 설치하세요: `brew install jq` (macOS) 또는 `apt install jq` (Linux)                                                                                                     |

---
## 수동 설정 (setup.sh가 실패할 경우)

시스템에서 설정 스크립트가 작동하지 않으면 다음 단계를 수동으로 실행하세요:

```bash
# 1. Install Gemini CLI
npm install -g @google/gemini-cli

# 2. Initialize demo app
git submodule add https://github.com/bradtraversy/proshop-v2.git demo-app
cd demo-app && npm install && cd ..

# 3. Copy configs
mkdir -p demo-app/.gemini/agents demo-app/.gemini/hooks demo-app/.gemini/policies
cp samples/config/settings.json demo-app/.gemini/settings.json
cp samples/config/policy.toml demo-app/.gemini/policies/team-guardrails.toml
cp samples/agents/security-scanner.md demo-app/.gemini/agents/
cp samples/hooks/*.sh demo-app/.gemini/hooks/
chmod +x demo-app/.gemini/hooks/*.sh
cp samples/gemini-md/project-gemini.md demo-app/GEMINI.md
mkdir -p demo-app/backend
cp samples/gemini-md/backend-gemini.md demo-app/backend/GEMINI.md

# 4. Authenticate
cd demo-app && gemini
```

---
## 다음 단계

→ **[사용 사례 1: SDLC 생산성 향상](sdlc-productivity.md)**부터 시작하세요.
