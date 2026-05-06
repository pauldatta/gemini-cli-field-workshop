# 环境设置

> 在开始任何使用场景之前完成此操作。大约需要 15 分钟。
>
> *最后更新：2026-05-05 · [已对照 gemini-cli 仓库验证来源](https://github.com/google-gemini/gemini-cli)*

---
## 系统要求

| 组件 | 最低配置 | 推荐配置 |
| -------------- | -------- | ------------------------------------------------------- |
| **Node.js** | v18.0.0 | v20+ (LTS) |
| **npm** | v9+ | v10+ |
| **Git** | v2.30+ | v2.40+ |
| **终端** | 任意 | iTerm2 (macOS)、Windows Terminal 或 VS Code 集成终端 |
| **磁盘空间** | 500MB | 1GB（包含演示应用 + node_modules） |
| **jq** | 可选 | 钩子示例需要 |

---
## 步骤 1：克隆工作坊

```bash
git clone https://github.com/pauldatta/gemini-cli-field-workshop.git
cd gemini-cli-field-workshop
```

---
## 第 2 步：运行设置脚本

设置脚本会处理所有事情——Gemini CLI 安装、演示应用程序检出和配置：

```bash
chmod +x setup.sh
./setup.sh
```

**它的作用：**

1. 验证是否已安装 Node.js、npm 和 Git
2. 全局安装/更新 Gemini CLI（`npm install -g @google/gemini-cli`）
3. 初始化 `demo-app/` 子模块（ProShop v2）并运行 `npm install`
4. 将示例配置复制到演示应用程序中：
   - `GEMINI.md` 上下文层级
   - 钩子脚本（机密扫描器、自动测试、会话记录器、路径守卫）
   - 策略引擎规则
   - 自定义子代理定义
5. 验证 Gemini CLI 身份验证

---
## 第 3 步：身份验证

### 选项 A：个人 Google 账号（免费层）

最适合工作坊和评估使用。不需要 GCP 项目。

```bash
cd demo-app
gemini
# Follow the browser-based OAuth flow
```

> **免费层限制：** 个人 Google AI 层具有宽裕的每日限制，非常适合工作坊使用。请参阅 [配额与定价](https://geminicli.com/docs/resources/quota-and-pricing/)。

### 选项 B：Vertex AI（企业版）

适用于生产环境和企业部署。需要一个启用了结算功能的 GCP 项目。

```bash
# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Authenticate
gcloud auth application-default login
```

Gemini CLI 将自动检测 Vertex AI 凭据。有关企业强制身份验证的信息，请参阅 [企业指南](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md)。

---
## 第 4 步：验证安装

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
## 故障排除

| 问题                                      | 解决方案                                                                                                                                                                      |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `npm install -g` 失败并提示 `EACCES`      | 使用 `sudo npm install -g @google/gemini-cli` 或修复 npm 权限：[npm 文档](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally) |
| 安装后提示 `gemini: command not found` | 重启终端或运行 `source ~/.bashrc` / `source ~/.zshrc`                                                                                                           |
| OAuth 流程未打开浏览器           | 从终端复制 URL 并手动打开                                                                                                                           |
| `git submodule update` 失败              | 运行 `git submodule init && git submodule update --recursive`                                                                                                                  |
| 演示应用程序 `npm install` 失败              | 检查 Node.js 版本 (`node --version`)。ProShop v2 需要 Node 18+。                                                                                                       |
| 研讨会期间出现速率限制错误         | 切换到 Vertex AI 身份验证，或等待 60 秒后重试                                                                                                                        |
| 钩子未执行                       | 运行 `chmod +x demo-app/.gemini/hooks/*.sh`                                                                                                                                    |
| 提示 `jq: command not found`                   | 安装 jq：`brew install jq` (macOS) 或 `apt install jq` (Linux)                                                                                                             |

---
## 手动设置（如果 setup.sh 失败）

如果设置脚本在您的系统上无法运行，请手动执行以下步骤：

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
## 下一步

→ 从 **[使用场景 1：SDLC 生产力提升](sdlc-productivity.md)** 开始
