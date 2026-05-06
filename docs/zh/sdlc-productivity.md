# 使用场景 1：SDLC 生产力提升

> **时长：** 约 60 分钟  
> **目标：** 构建企业级开发者工作流，涵盖从首次安装到上下文工程、使用 Conductor 进行规范驱动开发以及治理护栏。  
> **练习 PRD：** [产品心愿单功能](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_sdlc_productivity.md)
>
> *最后更新：2026-05-05 · [已对照 gemini-cli 仓库验证源码](https://github.com/google-gemini/gemini-cli)*

---
## 1.1 — 首次接触 (10 分钟)

### 安装 Gemini CLI

```bash
npm install -g @google/gemini-cli
```

### 启动与身份验证

```bash
cd demo-app
gemini
# Follow the OAuth flow in your browser
```

### 你的第一个提示词

从一些能证明代理可以读取你的代码库的内容开始：

```
What is the tech stack of this project? List the main frameworks, 
database, and authentication mechanism.
```

> **发生了什么：** 代理读取了 `package.json`，扫描了目录结构，并映射了架构。Gemini CLI 会按需探索你的代码库——根据需要使用 `read_file`、`glob` 和 `grep_search` 等工具来读取文件、搜索模式和追踪依赖关系。

### 探索工具

```
/tools
```

这显示了代理可以使用的所有工具：文件操作、shell 命令、网络搜索以及你配置的任何 MCP 服务器。

### 常用快捷键

| 快捷键 | 操作 |
|---|---|
| `Tab` | 接受建议的编辑 |
| `Shift+Tab` | 在审批模式之间循环切换 |
| `Ctrl+G` | 打开外部编辑器（编辑提示词或计划） |
| `Ctrl+C` | 取消当前操作 |
| `/stats` | 显示当前会话的令牌使用情况 |
| `/clear` | 清除上下文并重新开始 |

---
## 1.2 — 使用 GEMINI.md 进行上下文工程 (15 分钟)

### 上下文层级

Gemini CLI 在多个层级读取 `GEMINI.md` 文件，每个层级都会添加更具体的上下文：

![GEMINI.md 上下文层级](../assets/context-hierarchy.png)

> **JIT 上下文发现：** 代理仅加载与其当前正在处理的文件相关的 GEMINI.md 文件。如果它正在编辑 `backend/controllers/productController.js`，它将加载项目 GEMINI.md 和后端 GEMINI.md —— 但不会加载前端的 GEMINI.md。

### 检查项目 GEMINI.md

```bash
cat GEMINI.md
```

此文件（在环境设置期间从 [`samples/gemini-md/project-gemini.md`](../../samples/gemini-md/project-gemini.md) 复制而来）定义了：
- 架构规则（路由 → 控制器 → 模型）
- 反模式（无回调，无硬编码凭据）
- 测试标准

### 测试上下文强制执行

要求代理违反规则，并查看它是否会自我纠正：

```
Add a new GET endpoint to fetch featured products. 
Put the database query logic directly in the route file.
```

> **预期结果：** 代理应识别出这违反了 GEMINI.md 规则（“路由文件中不得包含业务逻辑”），并改为在控制器中创建端点，使用一个轻量级的路由进行委托。

> **强制执行规则：** `GEMINI.md` 提供了强有力的指导，但代理在复杂的重构过程中仍然可能会犯错。请将这些基于提示词的规则与集成到 CI/CD 或 [Gemini CLI Hooks](https://www.geminicli.com/docs/hooks/) 中的确定性代码检查工具（如 `dependency-cruiser`）结合使用。有关完整的环境设置，请参阅高级模式指南中的 [确定性强制执行](advanced-patterns.md#deterministic-enforcement)。

### 添加后端上下文

```bash
cat backend/GEMINI.md
```

这添加了关于错误处理、异步模式和安全性的后端特定规则。

### 记忆：持久化知识

代理可以在跨会话期间记住事物：

```
/memory show
```

添加项目特定的知识：

```
/memory add "The ProShop app uses port 5000 for the backend API 
and port 3000 for the React dev server. MongoDB runs on default 
port 27017. Test database is 'proshop_test'."
```

代理还可以使用 `save_memory` 工具自行保存记忆 —— 无论是在您明确要求它记住某些内容时，还是在您于 [settings.json](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/auto-memory.md) 中启用 `experimental.autoMemory` 时自动保存。

### .geminiignore 文件

控制代理可以和不可以查看的内容：

```bash
cat .geminiignore
# node_modules/
# .env
# *.log
# coverage/
```

> **为什么这很重要：** 如果没有 `.geminiignore`，代理可能会浪费上下文令牌去读取 `node_modules/`（数十万个文件）。有了它，代理将只专注于您的源代码。

---
## 1.3 — Conductor：上下文优先构建 (15 分钟)

### 为什么选择 Conductor？

计划模式对于一次性功能非常有用。但对于需要持久化规范、分阶段实施计划以及跨会话进度跟踪的多日项目——这就是 Conductor 的用武之地。

### 安装 Conductor

```bash
gemini extensions install https://github.com/gemini-cli-extensions/conductor
```

验证：

```
/extensions list
```

### 设置项目上下文

```
/conductor:setup prompt="This is a MERN stack eCommerce app (ProShop). 
Express.js backend with MongoDB. React frontend with Redux Toolkit. 
Use clean architecture: routes register middleware and delegate to 
controllers. Controllers handle business logic. Models define schema. 
No business logic in route files."
```

### 检查 Conductor 创建的内容

```bash
ls conductor/
# product.md  tech-stack.md  tracks/

cat conductor/product.md
cat conductor/tech-stack.md
```

> **关键见解：** 这些文件现在是您项目的真实数据源。它们是 Markdown 格式，存放在您的代码库中，像其他任何代码一样被提交和审查。当您明天回来——或者将这个项目移交给同事时——AI 会准确地从您离开的地方继续。状态保存在文件中，而不是内存中。

### 创建功能轨道

使用愿望清单 PRD 作为功能规范：

```
/conductor:newTrack prompt="Add a product wishlist feature. Users can 
add products to a personal wishlist from the product detail page. 
The wishlist is stored in MongoDB as an array of product references 
on the User model. Show a wishlist page with the ability to remove 
items or move them to the cart."
```

### 审查生成的工件

```bash
# The specification
cat conductor/tracks/*/spec.md

# The implementation plan
cat conductor/tracks/*/plan.md
```

> **查看计划。** 它被分解为带有特定任务和复选框的多个阶段。阶段 1：数据库模式。阶段 2：API 端点。阶段 3：前端组件。阶段 4：测试。代理会按顺序遵循此计划，并在进行过程中勾选已完成的任务。

> **如果您不同意该方法**——比如您想要 GraphQL 而不是 REST——请直接编辑 `plan.md` 并重新运行。该计划是您和代理之间的契约。

### 实施（如果时间允许）

```
/conductor:implement
```

> **按需探索：** 代理通过工具导航您的代码库——在实施计划的每个步骤时读取文件、追踪导入并交叉引用模式。像 `GEMINI.md` 和 Conductor 规范这样的上下文文件会与代理正在积极处理的文件一起加载。

### 检查状态

```
What's the current status on all active Conductor tracks?
```

---
## 1.4 — 扩展与 MCP 服务器 (10 分钟)

### 扩展概述

扩展将技能、子代理、钩子、策略以及 MCP 服务器打包成可安装的单元：

```
/extensions list
```

### MCP 服务器：连接外部工具

MCP (Model Context Protocol) 将 Gemini CLI 连接到外部数据源和工具：

```bash
# Check your MCP configuration
cat .gemini/settings.json
```

settings.json 包含一个 GitHub MCP 服务器。当配置了 `GITHUB_TOKEN` 时，代理可以：
- 读取仓库、议题（issues）和 PR
- 创建议题和评论
- 开启拉取请求（pull requests）

### 尝试连接提示词

```
List the open issues in this repository using the GitHub MCP server.
```

### 子代理的 MCP 工具隔离

您可以限制子代理可以访问哪些 MCP 工具：

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

> **企业价值：** 一个 `db-analyst` 子代理获得只读的 BigQuery 访问权限。它可以查询和列出表，但永远不能删除数据。工具隔离是代理级别的治理。

---
## 1.5 — 治理与策略引擎 (10 分钟)

### 策略引擎

策略是用 TOML 编写的护栏即代码：

```bash
cat .gemini/policies/team-guardrails.toml
```

### 策略规则实战

示例策略：
- **拒绝**读取 `.env`、`.ssh` 和凭据文件
- **拒绝**破坏性的 shell 命令（`rm -rf`、`curl`）
- **允许**实现者代理运行 `npm test` 和 `npm run lint`
- **默认**将其他所有操作设为 `ask_user`（需要人工批准）

### 测试策略

```
Read the contents of the .env file in this project.
```

> **预期结果：** 代理应该被策略引擎拦截。您将看到一条解释原因的拒绝消息。

### 5 层策略系统

策略按优先级顺序级联：

```
Default → Extension → Workspace → User → Admin (highest)
```

管理员策略（在系统级别设置）会覆盖其他所有策略。这就是企业强制执行全组织范围护栏的方式。

> **注意：** 工作区（Workspace）层级目前在 CLI 源码中已被禁用。有关最新的层级状态，请参阅 [策略引擎参考](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md)。

### 钩子实战

在 `settings.json` 中配置的钩子已经处于活动状态：

1. **SessionStart → session-context**：在本次会话开始时注入了您的分支名称和脏文件数量
2. **BeforeTool → secret-scanner**：监控每次文件写入以查找硬编码的凭据
3. **BeforeTool → git-context**：在修改文件之前注入最近的 git 历史记录
4. **AfterTool → test-nudge**：提醒代理考虑运行测试

检查钩子状态：

```
/hooks panel
```

> **设计理念：** 这些钩子是轻量级的上下文注入器和模型引导器——而不是繁重的测试运行器。它们增加的总延迟不到 200 毫秒，并在不给系统增加负担的情况下提高了代理的决策质量。

### 企业配置

对于全组织范围的工具限制，请使用带有管理员层级 TOML 策略的 [策略引擎](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md)。如需实用演练，请参阅 [使用策略引擎保护 Gemini CLI](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy)。

**管理员层级策略**（通过 MDM 部署到 `/etc/gemini-cli/policies/`）强制执行单个开发者无法覆盖的全组织范围安全措施：

```toml
# /etc/gemini-cli/policies/admin.toml

# Block network exfiltration tools
[[rule]]
toolName = "run_shell_command"
commandPrefix = ["curl", "wget", "nc", "netcat", "nmap", "ssh"]
decision = "deny"
priority = 900
deny_message = "Network commands are blocked to prevent data exfiltration."

# Block reading sensitive system files and secrets
[[rule]]
toolName = ["read_file", "grep_search", "glob"]
argsPattern = "(\\.env|/etc/shadow|/etc/passwd|\\.ssh/|\\.aws/)"
decision = "deny"
priority = 900
deny_message = "Access to system secrets and environment variables is prohibited."

# Block privilege escalation
[[rule]]
toolName = "run_shell_command"
commandPrefix = ["sudo", "su ", "chmod 777", "chown "]
decision = "deny"
priority = 950
deny_message = "Agents are not permitted to elevate privileges."
```

**工作区层级策略**（检入到您的仓库中的 `.gemini/policies/dev.toml`）设置团队级别的默认值：

```toml
# .gemini/policies/dev.toml

# Allow the CLI to read freely to build context
[[rule]]
toolName = ["read_file", "grep_search", "glob"]
decision = "allow"
priority = 100

# Auto-approve safe local commands
[[rule]]
toolName = "run_shell_command"
commandPrefix = ["npm test", "git diff"]
decision = "allow"
priority = 100

# Explicitly prompt for file modifications
[[rule]]
toolName = ["write_file", "replace"]
decision = "ask_user"
priority = 100

# Block destructive commands
[[rule]]
toolName = "run_shell_command"
commandRegex = "^rm -rf /"
decision = "deny"
priority = 999
deny_message = "Blocked by policy: Destructive root commands are prohibited."
```

> **检查活动策略：** 在 CLI 中使用 `/policies list` 查看管理您会话的所有规则，包括它们的决策、优先级层级和源文件。

对于企业身份验证强制执行，请在系统级别的 `settings.json` 中使用 `security.auth.enforcedType`（请参阅 [企业指南](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md)）。

### 沙盒

Gemini CLI 支持 [沙盒执行](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/sandbox.md)：
- **Docker 沙盒**：在隔离的容器中运行 shell 命令
- **macOS 沙盒**：使用 macOS 沙盒机制来限制文件系统访问

```bash
# Launch with sandboxing enabled
gemini --sandbox
```

---
## 1.6 — 会话管理 (5 分钟)

### 恢复之前的会话

```
/resume
```

列出最近的会话。选择一个以从上次中断的地方继续。

### 回退到之前的状态

```
/rewind
```

显示当前会话中更改的时间线。选择一个点进行回滚。

### 自定义命令

```
/commands
```

显示可用的自定义命令。您可以在 `.gemini/commands/` 中定义自己的命令。

---
## 总结：你学到了什么

| 功能 | 作用 |
|---|---|
| **GEMINI.md 层级结构** | 在每个层级编码项目约定 —— 代理会自动遵循它们 |
| **JIT 上下文发现** | 仅为当前任务加载相关的上下文文件 |
| **记忆** | 在跨会话中持久化知识 |
| **Conductor** | 具有持久化计划和进度跟踪的规范驱动开发 |
| **扩展** | 技能、代理、钩子和策略的可安装包 |
| **MCP 服务器** | 连接到外部工具（GitHub、BigQuery、Jira） |
| **策略引擎** | TOML 中的护栏即代码 —— 拒绝 (deny)、允许 (allow) 或询问用户 (ask_user) |
| **钩子** | 在代理生命周期事件中进行轻量级上下文注入和模型引导 |
| **沙盒** | 针对不受信任环境的隔离执行 |

---
## 1.7 — 覆盖完整 SDLC 的自定义代理 (20 分钟)

> **面向高级用户和老学员。** 本节超越了代码生成，涵盖了**完整的软件开发生命周期 (SDLC)** —— 审查、文档、合规性和发布管理。每个代理都可以独立使用。您可以随时切入。

### 内置代理

Gemini CLI 附带了您可以立即使用的默认代理。使用以下命令列出它们：

```
/agents
```

| 代理 | 目的 | 何时使用 |
|---|---|---|
| **`generalist`** | 拥有完整工具访问权限的通用代理 | 大工作量或需要频繁交互的任务 |
| **`codebase_investigator`** | 架构映射和依赖项分析 | “映射此应用中的身份验证流程” |
| **`cli_help`** | Gemini CLI 文档专家 | “我该如何配置 MCP 工具隔离？” |

使用 `@agent` 语法进行显式委派：

```
@codebase_investigator Map the complete data flow from the React 
product page through Redux, to the Express API, to the MongoDB model.
```

> **为什么这很重要：** investigator（调查员）在只读模式下运行，具有集中的上下文。它在映射您的架构时不会意外修改文件。然后，主代理使用该映射来规划实现。

---

### 构建自定义代理

自定义代理是带有 YAML 前言（frontmatter）的 Markdown 文件，放置在 `.gemini/agents/` 目录中。每个代理包含：

- 一个您可以使用 `@agent-name` 调用的**名称**
- CLI 用于自动路由的**描述**
- 控制代理可以访问哪些内容的**工具允许列表**
- 定义其专业知识和输出格式的**系统提示词**

> **关键设计原则：** 将思考者与执行者分开。只读代理用于研究和审查。具有写访问权限的代理用于实现。切勿在同一个上下文中混合调查和修改操作。

以下示例表明，Gemini CLI 不仅仅是一个代码生成器 —— 它是一个涵盖审查、文档、合规性和发布管理的**完整 SDLC 平台**。

---

### 代理 1：PR 审查员

一个只读代理，用于审查代码更改中的质量、错误和代码风格违规问题。

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

**试一试：**

```
@pr-reviewer Review all files changed in the last commit
```

> **在 CI/CD 中实现自动化：** 要在每个拉取请求上进行自动化的 PR 审查，请使用官方的 [`google-github-actions/run-gemini-cli`](https://github.com/google-github-actions/run-gemini-cli) GitHub Action。通过 CLI 使用 `/setup-github` 安装它 —— 它会自动配置工作流文件、分发处理程序和问题分类。有关工作示例，请参见 [`samples/cicd/gemini-pr-review.yml`](../../samples/cicd/gemini-pr-review.yml)。

---

### 代理 2：文档编写员

从源代码生成 API 文档、README 文件和代码注释。只读 —— 它绝不会修改您的文件。

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

**试一试：**

```
@doc-writer Generate API documentation for all endpoints in backend/routes/
```

> **外循环价值：** 这取代了数小时的手动文档工作。在每个冲刺（sprint）之后运行它，以保持文档的最新状态。

---

### 代理 3：安全分析（官方扩展）

无需构建自定义合规性检查器，直接安装**官方 [Security Extension](https://github.com/gemini-cli-extensions/security)** 即可 —— 这是一个由 Google 维护的扩展，具有完整的 SAST 引擎，通过 [OSV-Scanner](https://github.com/google/osv-scanner) 进行依赖项扫描，并具有经过基准测试的性能（针对真实 CVE 的精确度为 90%，召回率为 93%）。

```bash
# Install the Security Extension (requires Gemini CLI v0.4.0+)
gemini extensions install https://github.com/gemini-cli-extensions/security
```

**分析代码更改中的漏洞：**

```
/security:analyze
```

该扩展对您当前的分支差异（diff）运行两遍 SAST 分析，检查以下内容：
- 硬编码的机密信息和 API 密钥
- SQL 注入、XSS、SSRF 和命令注入
- 损坏的访问控制和身份验证绕过
- 日志和 API 响应中的 PII（个人身份信息）暴露
- LLM 安全问题（提示词注入、不安全的工具使用）

**扫描依赖项中的已知 CVE：**

```
/security:scan-deps
```

这使用 [OSV-Scanner](https://github.com/google/osv-scanner) 将您的依赖项与 Google 的开源漏洞数据库 [osv.dev](https://osv.dev) 进行交叉引用。

**自定义范围：**

```
/security:analyze Analyze all the source code under the backend/ folder. Skip tests and config files.
```

> **企业价值：** 此扩展附带用于 PoC 生成 (`poc`)、自动修补 (`security-patcher`) 和漏洞允许列表的技能。它开箱即用，可直接用于生产环境 —— 无需构建自定义合规性代理。

---

### 代理 4：发布说明起草员

读取 git 历史记录和更改的文件，以生成结构化且对利益相关者友好的发布说明。

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

**试一试：**

```
@release-notes-drafter Write release notes for the last 10 commits
```

> **外循环价值：** 发布说明是最令人畏惧的 SDLC 任务之一。此代理读取 git 历史记录**以及**实际的代码更改，以生成对产品经理有意义的说明。

---

### 组合代理：完整的流水线

真正的威力在于将多个代理组合成一个工作流。每个代理都会获得**全新的、集中的上下文** —— 没有任何一个代理会累积完整的对话历史记录：

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

> **为什么这行得通：** 每个步骤都以专注于其特定工作的干净上下文开始。investigator（调查员）不会携带实现细节。reviewer（审查员）不会携带调查噪音。这是每个高性能 AI 工作流背后的原则。

---

### 深入探索

有关其他高级技术 —— 提示词规范、验证循环、上下文工程和并行开发 —— 请参阅**[高级模式](advanced-patterns.md)**页面：

- [提示词技巧：目标与指令](advanced-patterns.md#prompting-craft-goals-vs-instructions)
- [上下文规范](advanced-patterns.md#context-discipline)
- [验证循环](advanced-patterns.md#verification-loops)
- [使用工作树进行并行开发](advanced-patterns.md#parallel-development-with-worktrees)
- [多代理编排](advanced-patterns.md#multi-agent-orchestration)

---
## 第 2 部分 — 外循环：超越代码编写

> **时长：** 约 20 分钟（自定进度）
> **先决条件：** 完成上面的第 1 部分。熟悉自定义代理 (§1.5) 和 Conductor (§1.4) 会很有帮助。

上面的练习主要集中在**内循环**——编写、测试和审查代码。但是代理也可以处理**外循环**——围绕代码的工作流：架构决策、开发者入职、依赖审计和 CI 管道自动化。

在第 1 部分中，您已经构建了基础模块：用于专门角色的子代理、用于规范驱动开发的 Conductor，以及用于策略执行的合规性检查器。第 2 部分将展示如何将这些模式推广到外循环工作流中。

---

### 2.1 — 使用子代理驱动开发的 ADR 生成器

架构决策记录 (ADR) 记录了做出某项技术选择的*原因*。手动编写它们非常繁琐，以至于团队往往完全跳过它们。借助来自 [superpowers 扩展](extensions-ecosystem.md#exercise-1-superpowers--methodology-as-extension) 的子代理驱动开发 (SDD) 方法论，您可以根据代码更改自动生成 ADR。

**环境设置：**

```bash
# Install superpowers if you haven't already
gemini extensions install https://github.com/obra/superpowers
```

**创建 ADR 代理：**

创建 `.gemini/agents/adr-writer.md`：

```markdown
---
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - list_directory
  - run_shell_command
---
You are an Architecture Decision Record (ADR) writer. When given a set 
of code changes:

1. Run `git diff main...HEAD` to understand what changed
2. Analyze the architectural significance — what decision was made?
3. Generate an ADR in this format:

## ADR-{number}: {title}

**Status:** Proposed
**Date:** {today}
**Context:** What problem or requirement drove this decision?
**Decision:** What was decided and why?
**Consequences:** What are the tradeoffs? What becomes easier? Harder?
**Alternatives Considered:** What other approaches were evaluated?

Focus on the *why*, not the *what*. The code shows *what* changed — 
the ADR explains *why* it was the right choice.
```

**使用它：**

进行代码更改（添加功能、更改架构模式），然后：

```
@adr-writer Generate an ADR for the changes on this branch
```

**使用 SDD 两阶段审查：**

```
Use subagent-driven development to generate an ADR for my current branch 
changes. The first subagent should draft the ADR. The second should review 
it for completeness — does it explain the *why*, not just the *what*?
```

> **为什么这很重要：** ADR 是团队可以产出的最有价值的工件之一，也是最容易被忽视的工件之一。一个能从每个 PR 中生成 ADR 草稿的代理，将门槛从“编写文档”降低到了“审查文档”。采用这种模式的团队会自动建立起架构历史记录。

---

### 2.2 — 开发者入职代理

新开发者在能够做出贡献之前，往往需要花费数天时间来梳理代码库。入职代理可以在几分钟内完成这种梳理。

**创建代理：**

创建 `.gemini/agents/onboarding-guide.md`：

```markdown
---
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - list_directory
  - grep_search
---
You are a codebase onboarding guide. When a new developer asks about 
this codebase, help them understand:

1. **Architecture:** What frameworks and patterns are used? 
   (Check package.json, project structure, GEMINI.md)
2. **Data flow:** How do requests move through the system? 
   (Trace from routes → controllers → models → database)
3. **Authentication:** How does auth work? 
   (Find auth middleware, token handling, session management)
4. **Testing:** How are tests organized? What's the testing strategy?
5. **Deployment:** How does the app get deployed? 
   (Check CI/CD configs, Dockerfiles, deployment scripts)

Always cite specific files and line numbers. Don't summarize — 
show the actual code paths.
```

**尝试一下：**

```
@onboarding-guide How does authentication work in this application?
```

```
@onboarding-guide What's the testing strategy? Show me an example test 
and explain the patterns I should follow.
```

```
@onboarding-guide I need to add a new API endpoint. Walk me through the 
pattern — which files do I create and in what order?
```

> **关键洞察：** 将此与阅读 README 并祈祷它是最新版本进行比较。代理追踪的是实际的代码路径，而不是可能已经偏离的文档。这是第 1 部分 (§1.5) 中 `@codebase_investigator` 模式的体现——但专门针对入职问题进行了优化，并持久化为可重用的代理。

---

### 2.3 — CI 管道中的安全分析

在第 1 部分中，您安装了 [安全扩展](https://github.com/gemini-cli-extensions/security) 用于本地分析。下一步是将其推广到 CI 中——在每个拉取请求上进行自动化的安全分析。

#### 模式：GitHub Actions 中的安全扩展

安全扩展附带了一个开箱即用的 GitHub Actions 工作流。直接复制它：

```bash
# Copy the extension's CI workflow into your repo
cp $(gemini extensions path security)/.github/workflows/gemini-review.yml \
  .github/workflows/security-review.yml
```

或者参考[官方工作流模板](https://github.com/gemini-cli-extensions/security/blob/main/.github/workflows/gemini-review.yml)并手动添加。该工作流：

1. 将安全扩展安装到 CI 运行器中
2. 在 PR 差异上运行 `/security:analyze`
3. 运行 `/security:scan-deps` 以查找依赖项漏洞
4. 将发现的问题作为 PR 评论发布

**为什么安全扩展优于手写提示词：**

| 手写审计提示词 | 安全扩展 |
|---|---|
| 自由格式的提示词——每次运行结果各异 | 具有一致方法论的结构化两轮 SAST 引擎 |
| 无漏洞分类 | 7 个类别，20 多种漏洞类型，严重程度评级（严重/高/中/低） |
| 无依赖项扫描 | 集成了针对 Google 漏洞数据库的 OSV-Scanner |
| 无修复工作流 | 内置 PoC 生成和自动修补技能 |
| 无白名单机制 | 用于已接受风险的持久化 `.gemini_security/vuln_allowlist.txt` |

> **这是幻灯片 18 中的 CI 模式**，但使用了生产级、经过基准测试的扩展（90% 准确率，93% 召回率），而不是手写的提示词。您在 §1.7 中本地运行的同一个 `/security:analyze` 命令现在会在每个 PR 上自动运行。

---

### 融会贯通

第 1 部分为您提供了基础模块：子代理、Conductor、策略引擎、钩子。第 2 部分展示了如何将这些模式推广到外循环中：

| 基础模块（第 1 部分） | 外循环应用（第 2 部分） |
|---|---|
| 自定义子代理 (§1.5) | ADR 编写器、入职指南 |
| 安全扩展 (§1.7) | CI 安全分析管道 |
| Conductor 规范到代码 (§1.4) | PRD → ADR → 实现管道 |
| 无头模式（在 UC3 中引用） | GitHub Action 自动化 |

模式始终如一：**本地构建 → 验证 → 推广到 CI/CD → 在整个组织内扩展。** 帮助一名开发者的代理将成为帮助整个团队的自动化工具。

---
## 总结：你学到了什么

| 功能 | 作用 |
|---|---|
| **GEMINI.md 层级结构** | 在每个级别编码项目约定 —— 代理会自动遵循它们 |
| **JIT 上下文发现** | 仅加载当前任务相关的上下文文件 |
| **记忆** | 在会话之间持久化知识 |
| **Conductor** | 具有持久化计划和进度跟踪的规范驱动开发 |
| **扩展** | 包含技能、代理、钩子和策略的可安装包 |
| **MCP 服务器** | 连接到外部工具（GitHub、BigQuery、Jira） |
| **策略引擎** | TOML 中的护栏即代码 —— 拒绝 (deny)、允许 (allow) 或询问用户 (ask_user) |
| **钩子** | 在代理生命周期事件中进行轻量级上下文注入和模型引导 |
| **沙盒** | 针对不受信任环境的隔离执行 |
| **自定义代理** | 用于代码审查、文档、发布说明的专用代理 —— 不仅仅是编码 |
| **安全扩展** | 官方 SAST + 依赖扫描，支持 PoC 生成和自动修补 |
| **内置代理** | `generalist`、`codebase_investigator`、`cli_help` —— 无需设置即可委派 |
| **ADR 生成** | 由子代理驱动，从 git diff 生成架构决策记录 |
| **入职代理** | 为新开发者提供代码库映射 —— 追踪实际代码路径 |
| **CI 安全流水线** | GitHub Actions 中的安全扩展，用于自动化漏洞分析 |

---
## 下一步

→ 继续前往 **[使用场景 2：遗留代码现代化](legacy-modernization.md)**

→ 探索扩展生态系统：**[扩展生态系统](extensions-ecosystem.md)** — 发现、安装、构建和企业模式

→ 面向高级用户：**[高级模式](advanced-patterns.md)** — 提示词技巧、验证循环、上下文工程和并行开发
