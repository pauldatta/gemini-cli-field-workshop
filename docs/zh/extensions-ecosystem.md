# 扩展生态系统

> **时长：** 约 30 分钟（自定进度）
> **目标：** 了解什么是扩展，发现并安装社区扩展，并学习组织如何打包知识和工具以进行分发。
> **先决条件：** 至少完成 [使用场景 1：SDLC 生产力提升](sdlc-productivity.md) 或熟悉基础知识。您应该已经了解 `GEMINI.md`、代理和技能的工作原理。
>
> *最后更新：2026-05-05 · [源代码已针对 gemini-cli 仓库进行验证](https://github.com/google-gemini/gemini-cli)*

---
## 什么是扩展？

在 [SDLC 生产力提升](sdlc-productivity.md) 中，您安装了 Conductor 扩展。在 [高级模式](advanced-patterns.md) 中，您安装了 agent-skills 包。两者的安装方式相同 —— `gemini extensions install <url>` —— 因为它们都是**扩展**。

扩展将多种功能打包成一个单一的、可安装的单元：

| 功能 | 说明 | 调用者 |
|---|---|---|
| **MCP 服务器** | 向模型暴露新工具和数据源 | 模型 |
| **自定义命令** | 用于复杂提示词或 shell 命令的 `/my-cmd` 快捷方式 | 用户 |
| **上下文文件** (`GEMINI.md`) | 每次会话加载的常驻指令 | CLI → 模型 |
| **代理技能** | 按需激活的专门工作流（TDD、代码审查等） | 模型 |
| **钩子** | 生命周期拦截器 —— 在工具调用、模型响应、会话之前/之后 | CLI |
| **主题** | 用于 CLI UI 个性化的颜色定义 | 用户 (`/theme`) |
| **策略引擎** | 以第 2 层优先级提供的安全规则和工具限制 | CLI |

> **关键见解：** 您已经使用了两个扩展。来自高级模式的 agent-skills 包*主要*是一个技能扩展 —— 它提供了 20 个技能和 7 个斜杠命令。Conductor 主要是一个命令 + MCP 服务器扩展。扩展是灵活的容器 —— 它们可以打包上述 7 种功能的任意组合。

### 清单文件：`gemini-extension.json`

每个扩展都有一个清单文件。这是扩展和 Gemini CLI 之间的契约：

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

| 字段 | 用途 |
|---|---|
| `name` | 唯一标识符 —— 必须与目录名称匹配 |
| `contextFileName` | 每次会话将此文件加载到上下文中。如果存在，默认为 `GEMINI.md` |
| `mcpServers` | 要启动的 MCP 服务器 —— 格式与 `settings.json` 相同。使用 `${extensionPath}` 以实现可移植性 |
| `excludeTools` | 阻止特定的工具或命令（例如，通过 shell 执行的 `rm -rf`） |
| `settings` | 用户可配置的值 —— `sensitive: true` 会存储在系统钥匙串中 |

### 扩展 vs. 技能 vs. 代理 —— 何时使用何种功能

| | 扩展 | 技能 (`SKILL.md`) | 代理 (`.gemini/agents/*.md`) |
|---|---|---|---|
| **范围** | 在用户/机器之间共享 | 本地或捆绑在扩展中 | 本地项目 |
| **安装来源** | GitHub、本地路径 | 扩展或项目的一部分 | 项目目录 |
| **最适用场景** | 可分发的工具包、组织标准、MCP 集成 | 特定阶段的工作流（TDD、安全审计） | 专门的角色（审查员、合规检查员） |
| **示例** | `oh-my-gemini-cli`、`agent-skills`、`conductor` | `subagent-driven-development`、`debugging` | `@pr-reviewer`、`@compliance-checker` |

---
## 发现与安装

### 查找扩展

[扩展库](https://geminicli.com/extensions/browse/)会自动索引公开的扩展。任何带有 `gemini-cli-extension` 主题的 GitHub 仓库都会出现在该库中——无需提交。

### 安装

```bash
# Install from GitHub
gemini extensions install https://github.com/owner/repo

# Install a specific version (branch, tag, or commit)
gemini extensions install https://github.com/owner/repo --ref v1.2.0

# Enable auto-updates
gemini extensions install https://github.com/owner/repo --auto-update
```

### 管理已安装的扩展

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

### Google 管理的扩展

Google 在 [**gemini-cli-extensions**](https://github.com/gemini-cli-extensions) 维护了一个官方扩展组织，包含 60 多个涵盖安全、数据库、CI/CD 和 Google Cloud 服务的扩展：

| 扩展 | 重点 | 添加内容 |
|---|---|---|
| [**security**](https://github.com/gemini-cli-extensions/security) | 安全分析 | 完整的 SAST 引擎，通过 OSV-Scanner 进行依赖扫描，PoC 生成，自动修补。90% 准确率，93% 召回率 |
| [**conductor**](https://github.com/gemini-cli-extensions/conductor) | 规范驱动开发 | 结构化规划，实现跟踪，以及上下文驱动开发 |
| [**workspace**](https://github.com/gemini-cli-extensions/workspace) | Google Workspace | Gmail、Drive、Calendar、Sheets 集成，带有针对代理优化的 JSON 输出 |
| [**cicd**](https://github.com/gemini-cli-extensions/cicd) | CI/CD | 流水线生成，工作流调试，以及部署自动化 |
| [**firebase**](https://github.com/gemini-cli-extensions/firebase) | Firebase | Firebase 项目管理，Firestore 查询，以及托管部署 |
| [**bigquery-data-analytics**](https://github.com/gemini-cli-extensions/bigquery-data-analytics) | 数据分析 | 用于数据探索、查询优化和分析的 BigQuery 技能 |
| [**cloud-sql-***](https://github.com/gemini-cli-extensions) | 数据库 | 适用于 PostgreSQL、MySQL、SQL Server、AlloyDB、OracleDB 的技能 |
| [**vertex**](https://github.com/gemini-cli-extensions/vertex) | Vertex AI | 提示词管理和 Vertex AI 集成 |

使用以下命令安装其中任何一个：

```text
gemini extensions install https://github.com/gemini-cli-extensions/<name>
```

### 值得注意的社区扩展

除了官方生态系统之外，社区还构建了越来越复杂的扩展：

| 扩展 | 重点 | 添加内容 |
|---|---|---|
| [**oh-my-gemini-cli**](https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli) | 编排 | 12 个代理，9 项技能，43 个斜杠命令，生命周期钩子。带有审批网关的完整多代理框架 |
| [**superpowers**](https://github.com/obra/superpowers) | 方法论 | 14 项用于 TDD、调试、代码审查、子代理驱动开发的技能。跨工具：也适用于 Cursor 和 OpenCode |
| [**gws (Google Workspace CLI)**](https://github.com/googleworkspace/cli) | Workspace 集成 | 适用于 Gmail、Drive、Calendar、Sheets 的动态 CLI。针对代理优化的 JSON 输出。Model Armor 集成 |

---
## 动手实践：安装和使用社区扩展

您已经安装了 **agent-skills** 包（高级模式）和 **Conductor**（SDLC 生产力提升）。现在让我们探索一下官方生态系统之外社区构建的内容。

### 练习 1：Superpowers — 方法论作为扩展

`superpowers` 扩展教会您的代理*如何工作*，而不仅仅是做什么。其旗舰功能是**子代理驱动开发 (SDD)** — 一种为每个任务分发全新子代理并进行两阶段审查的正式方法论。

```bash
# Install
gemini extensions install https://github.com/obra/superpowers

# Verify — you should see superpowers in the list
/extensions list
```

**尝试 plan 技能：**

```
Write a plan for adding a "recently viewed products" feature to the ProShop app.
Use the $plan skill.
```

**尝试子代理驱动开发：**

```
I want to add a "recently viewed" sidebar widget. Use subagent-driven development 
to implement this — dispatch a subagent for each component and review each one.
```

观察 SDD 是如何工作的：
1. 为每个组件（数据模型、API 端点、React 组件）创建规范
2. 为每个组件分发一个全新的子代理 — 任务之间没有上下文泄漏
3. 分两阶段审查每个子代理的输出：首先是规范合规性，然后是代码质量
4. 报告包含所有发现的摘要

> **关键要点：** 将此与原始的“添加最近查看的侧边栏”提示词进行比较。SDD 生成经过审查和验证的代码。而原始提示词生成的代码需要您手动审查。这就是开发人员与开发*过程*之间的区别。

**跨工具可移植性：** Superpowers 也可以在 Cursor (`.cursor-plugin/`) 和 OpenCode (`.opencode/`) 中工作。相同的 `SKILL.md` 文件，不同的插件清单。技能不受供应商锁定。

---

### 练习 2：Oh-My-Gemini-CLI — 编排作为扩展

此扩展实现了一个带有审批网关的完整多代理工作流 — 这正是企业团队所需要的治理类型。

```bash
# Install
gemini extensions install https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli
```

**尝试意图驱动的工作流：**

```
/omg:intent Add user profile avatars to the ProShop application
```

注意发生了什么：
- 代理不会立即开始编码。它会启动一次**苏格拉底式访谈** — 询问范围、约束和验收标准
- 只有在您确认范围后，`omg-planner` 代理才会创建一个结构化的计划
- 计划被移交给 `omg-executor` 进行实施
- 实施后，`omg-reviewer` 会运行质量网关检查

**剖析一瞥：** 此扩展同时使用了所有 7 个扩展功能：

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

> **关键要点：** OMG 展示了“开箱即用”的扩展是什么样的。苏格拉底式访谈网关可防止代理对模棱两可的请求进行自动执行 — 这是每个企业都应考虑的模式。

---

### 练习 3：Google Workspace CLI（可选）

> **注意：** 此练习需要 Google Workspace（Gmail、Drive、Calendar）。如果您的组织不使用 Workspace，请跳过此步骤。

`gws` 扩展为您的代理提供了对 Workspace API 的直接、结构化访问：

```bash
# Install as a Gemini extension
gemini extensions install https://github.com/googleworkspace/cli

# Authenticate (one-time setup)
gws auth setup
```

**尝试收件箱分类：**

```
Use gws to triage my inbox — show me unread emails grouped by priority
```

**尝试站会报告：**

```
Use gws to generate a standup report from my calendar and recent email activity
```

`gws` 输出针对代理使用而优化的结构化 JSON。它还支持 `--sanitize`，以便在代理处理之前通过 Model Armor 模板路由 API 响应。

---

### 练习 4：安全扩展 — 生产级 SAST

[安全扩展](https://github.com/gemini-cli-extensions/security) 是 Google 官方的 Gemini CLI 安全分析工具。与手动编写的合规性代理不同，它附带了完整的 SAST 引擎、依赖项扫描器和基准测试结果。

```bash
# Install
gemini extensions install https://github.com/gemini-cli-extensions/security
```

**对您当前的更改运行安全分析：**

```
/security:analyze
```

该扩展运行结构化的两遍分析：
1. **侦察阶段** — 根据其漏洞分类对所有更改的文件进行快速扫描
2. **调查阶段** — 深入研究标记的模式，追踪从源到接收器的数据流

它检查硬编码机密、注入漏洞（SQLi、XSS、SSRF、SSTI）、失效的访问控制、PII 暴露、弱加密和 LLM 安全问题。

**扫描依赖项以查找已知的 CVE：**

```
/security:scan-deps
```

这使用 [OSV-Scanner](https://github.com/google/osv-scanner) 针对 [osv.dev](https://osv.dev) — Google 的开源漏洞数据库。

**自定义范围：**

```
/security:analyze Analyze all source code under the src/ folder. Skip docs and config files.
```

**关键功能：**
- **PoC 生成** — 生成概念验证脚本以验证发现（`poc` 技能）
- **自动修补** — 应用针对已确认漏洞的修复程序（`security-patcher` 技能）
- **允许列表** — 将已接受的风险持久化在 `.gemini_security/vuln_allowlist.txt` 中
- **CI 集成** — 附带一个随时可用的 [GitHub Actions 工作流](https://github.com/gemini-cli-extensions/security/blob/main/.github/workflows/gemini-review.yml)，用于自动化的 PR 安全审查

> **企业价值：** 这与 [SDLC 生产力提升 §1.7](sdlc-productivity.md) 和 [§2.3](sdlc-productivity.md) 中引用的扩展相同。它取代了构建自定义合规性检查代理的需求 — 一次 `gemini extensions install` 即可为您的整个团队提供生产级安全管道。

---
## 构建你自己的扩展

### 从模板搭建脚手架

Gemini CLI 提供 7 个内置模板：

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

### 使用 `link` 进行本地开发

使用 `link` 测试更改而无需重新安装：

```bash
cd my-extension
npm install
gemini extensions link .
```

重启你的 Gemini CLI 会话后，更改会立即生效。在开发过程中无需重新安装。

### 发布到扩展库

发布是自动的——无需提交：

1. **推送到公开的 GitHub 仓库**，并在根目录下包含有效的 `gemini-extension.json`
2. **添加 GitHub 主题** `gemini-cli-extension` 到你仓库的 About（关于）部分
3. **打标签发布**（例如，`v1.0.0`）

扩展库爬虫每天会索引打过标签的仓库。验证通过后，你的扩展会自动出现。

### 练习：构建一个迷你扩展

创建一个简单的扩展，为你的团队代码审查清单添加一个斜杠命令：

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

重启 Gemini CLI 并运行 `/team:review`——你的自定义审查清单现在只需一个命令即可执行。

---
## 企业级扩展模式

### 组织知识分发

企业团队最具价值的模式：**将您组织的知识打包为一个扩展。**

与其让入职文档在 Confluence 中腐烂，不如发布一个扩展，教导代理了解您组织的模式：

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

**优势：**
- **版本化：** 更新扩展，每个人在下次执行 `gemini extensions update` 时都会获得最新标准
- **分布式：** 第一天执行 `gemini extensions install` —— 新员工即可获取您完整的机构知识
- **易于维护：** 一个代码仓库，一个 PR 即可更新所有开发者代理中的组织标准
- **一致性：** 团队中的每个代理都遵循相同的规则，使用相同的检查清单进行审查，通过相同的关卡进行部署

> **这取代了“阅读 wiki”的入职模式。** 与其指望开发者找到并阅读您的样式指南，不如让代理自动强制执行它。

### 治理模式

扩展在 **第 2 层级优先级** 提供策略规则 —— 高于默认值，低于用户/管理员的覆盖设置：

```toml
# policies/safety.toml (contributed by your org extension)
[[rule]]
toolName = "run_shell_command"
commandRegex = ".*--force.*"
decision = "deny"
priority = 100
denyMessage = "Force operations are blocked by organization policy."
```

> **安全模型：** 扩展策略在第 2 层级优先级运行。用户（第 4 层级）和管理员（第 5 层级）策略始终优先。这意味着扩展可以设置护栏，但用户和管理员可以在必要时覆盖它们。有关完整的层级详细信息，请参阅 [策略引擎](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md)；有关实战演练，请参阅 [使用策略引擎保护 Gemini CLI](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy)。

**带有钥匙串存储的设置：** 扩展可以定义存储在系统钥匙串中的设置：

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

标记为 `sensitive: true` 的值会加密存储在操作系统钥匙串中，并在 CLI 输出中进行混淆处理。

### 跨工具可移植性

`superpowers` 扩展展示了一个关键的企业模式：相同的 `SKILL.md` 文件可以在 Gemini CLI、Cursor 和 OpenCode 之间通用 —— 尽管它们各自有自己的插件清单格式（`gemini-extension.json`、`.cursor-plugin/`、`.opencode/`）。这意味着：

- **技能没有供应商锁定** —— 投资于方法论，而不是特定于工具的配置
- **使用不同编辑器的团队** 可以共享相同的工程标准
- **迁移风险低** —— 切换工具意味着编写一个新的清单，而不是重写技能

### 内部注册表模式

对于维护私有扩展生态系统的组织：

1. **GitHub 组织** —— 创建一个内部组织（例如，`my-company-gemini-extensions`）
2. **主题标记** —— 使用私有约定（例如，`internal-gemini-extension`）
3. **版本固定** —— 使用 `--ref` 标签进行安装以确保生产环境的稳定性：
   ```bash
   gemini extensions install https://github.internal.com/org/my-ext --ref v2.1.0
   ```
4. **自动更新** —— 对于“最新即最好”的扩展（如样式指南），使用 `--auto-update`
5. **工作区作用域** —— 为特定项目禁用组织扩展：
   ```bash
   gemini extensions disable org-standards --scope workspace
   ```

---
## 总结

| 概念 | 核心要点 |
|---|---|
| **扩展包含的内容** | 7 个特性：MCP 服务器、命令、上下文、技能、钩子、主题、策略 |
| **Google 托管** | 在 [gemini-cli-extensions](https://github.com/gemini-cli-extensions) 提供了 60 多个扩展 — 涵盖安全、数据库、CI/CD、Workspace |
| **安装** | `gemini extensions install <url>` — 一条命令 |
| **扩展库** | 通过 `gemini-cli-extension` GitHub 主题自动索引 |
| **构建** | 通过 7 个模板使用 `gemini extensions new`，使用 `link` 进行本地开发 |
| **企业价值** | 打包组织知识，强制执行标准，通过安装命令进行分发 |
| **安全** | 包含 SAST + 依赖扫描的官方安全扩展。第 2 层的扩展策略。密钥存储在钥匙串中 |
| **可移植性** | 技能可在 Gemini CLI、Cursor 和 OpenCode 之间通用 |

---
## 下一步

→ 返回 **[使用场景 1：SDLC 生产力提升](sdlc-productivity.md)** — 第 2 部分涵盖外循环代理（ADR、入职培训、依赖审计）

→ 继续前往 **[高级模式](advanced-patterns.md)** — 提示词技巧、上下文工程以及代理技能安装
