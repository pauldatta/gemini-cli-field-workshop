# 使用场景 2：遗留代码现代化

> **时长：** 约 60 分钟  
> **目标：** 使用计划模式、自定义子代理、技能和检查点机制迁移遗留应用程序。学习如何安全地分解庞大的代码库。  
> **练习 PRD：** [.NET 现代化](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_dotnet_modernization.md) · [Java 升级](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_java_upgrade.md)
>
> *最后更新：2026-05-05 · [已根据 gemini-cli 仓库验证源码](https://github.com/google-gemini/gemini-cli)*

---
## 2.1 — 计划模式：安全研究 (15 分钟)

### 进入计划模式

计划模式是只读的研究。代理会分析你的代码库，提出修改建议，但在你批准之前**不会修改任何内容**。

```
/plan
```

> CLI 会指示你处于计划模式。代理将失去对写入工具的访问权限——它只能读取文件、搜索网络和思考。

### 分析代码库

```
Analyze this codebase for a migration to a modern architecture. 
Identify:
1. Key dependencies and their versions
2. Architectural patterns currently in use
3. Areas of technical debt
4. Migration risks and complexity hotspots
```

> **发生了什么：** 代理读取项目——package.json、源文件、配置——并构建一个心智模型。它使用 `read_file`、`glob` 和 `grep_search` 等工具按需探索你的代码库，以追踪每一个依赖项、模式和反模式。

### 审查计划

代理会生成一个结构化的迁移计划。请仔细审查：

```
Propose a step-by-step plan to modernize the authentication system 
from session-based to JWT with refresh tokens. Include:
- Files that need to change
- Order of operations
- Risk assessment for each step
- Rollback strategy
```

### 协作编辑计划

打开外部编辑器来完善计划：

```
Ctrl+G
```

这将打开你的 `$EDITOR`（或内置编辑器），你可以直接在其中修改计划。代理会看到你的编辑并调整其方法。

### 退出计划模式

```
/plan
```

切换回正常模式。现在代理可以执行已批准的计划了。

---
## 2.2 — 模型路由与模型引导 (10 分钟)

### 自动模型路由

Gemini CLI 可以根据任务复杂性在模型之间进行自动选择：

| 任务类型 | 典型模型 | 原因 |
|---|---|---|
| 规划、架构分析 | **Gemini Pro** | 复杂推理、长篇分析 |
| 代码生成、文件编辑 | **Gemini Flash** | 快速执行、成本更低 |
| 简单查询、状态检查 | **Gemini Flash** | 速度优化 |

> 这种路由是启发式的，而非确定性的——CLI 会评估提示词的复杂性并据此进行选择。你可以使用 `/model` 进行覆盖以选择特定模型。有关详细信息，请参阅 [模型路由](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/model-routing.md)。

### 模型引导 🔬

在执行过程中，你可以在中途对代理进行引导：

```
# While the agent is working on a migration step:
Actually, skip the database migration for now. Focus on the API 
layer first — we need the endpoints working before we touch the schema.
```

> **模型引导**允许你在不重新开始的情况下纠正路线。代理会根据你的输入调整其计划，并从新的方向继续执行。

### 检查哪个模型处于活动状态

```
/stats
```

显示当前模型、令牌使用情况和缓存状态。

---
## 2.3 — 迁移的上下文工程 (10 分钟)

迁移项目是上下文工程能带来最大回报的地方。遗留代码库中充满了隐性知识——架构模式、已弃用的 API 使用、隐藏的依赖链——这些都没有记录在任何地方。代理在安全地进行任何更改之前，需要先内化这些知识。

有两种方法：**手动**（由您编写 GEMINI.md）和**代理驱动**（由代理为您编写）。两者产生相同的产物，但代理驱动的方法通常能发现您可能会遗漏的内容。

### 代理驱动：使用 @codebase_investigator 自我入职

迁移中最强大的模式是让代理**调查代码库并编写自己的 GEMINI.md**。这就是“代理自我入职”模式——它模仿了高级工程师加入新项目时的做法，但以机器速度进行。

**第 1 步 — 调查：**

```
@codebase_investigator Analyze this entire codebase. Map:
1. Framework versions, build system, and dependency tree
2. Architectural patterns (MVC, data access layers, security config)
3. All javax.* imports that will need jakarta.* migration
4. Configuration files and property sources
5. Test frameworks and coverage patterns
Report any migration risks or complexity hotspots.
```

> **原理解析：** `@codebase_investigator` 子代理读取每个文件，追踪导入，映射类层次结构，并构建完整的图景——所有这些都在只读模式下进行。它绝不会修改任何内容。

**第 2 步 — 生成上下文：**

```
Based on your codebase analysis, write a GEMINI.md that:
1. Documents what you found (current state: Boot 2.6, Java 8, javax.*)
2. Defines the target state (Boot 3.3, Java 21, jakarta.*)
3. Lists migration rules (one module at a time, preserve API contracts)
4. Encodes testing standards (every phase must pass mvn clean verify)
5. Flags the specific risks you identified

Write this file to the project root as GEMINI.md.
```

**第 3 步 — 审查和完善：**

代理会根据它在代码中实际发现的内容（而不是猜测）生成一个 GEMINI.md。审查它，添加任何团队特定的约定，然后批准。从此时起，代理执行的每个迁移命令都将受此上下文引导。

> **为什么这很有效：** 代理在为自己编写指令。它生成的 GEMINI.md 成为其后续工作的护栏。这是一个自我强化的循环：更好的上下文 → 更好的代码更改 → 代理学习到更多模式 → 上下文进一步改善（通过自动记忆）。

> **实践案例：** [Java Upgrade PRD](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_java_upgrade.md) 将此模式用作第 0 阶段——代理在接触任何迁移代码之前必须先自我入职。

### 手动：直接编写迁移标准

对于已有既定标准的团队，请自行编写 GEMINI.md：

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

### @file 导入语法

对于大型项目，请将 GEMINI.md 拆分为模块化文件：

```markdown
# GEMINI.md
@./docs/architecture.md
@./docs/coding-standards.md
@./docs/migration-checklist.md
```

> **为什么导入很重要：** 对于企业级项目，单个 GEMINI.md 可能会变得难以管理。导入功能让您可以将上下文组织成重点突出的文档，从而更容易维护和审查。有关完整语法，请参阅 [GEMINI.md 参考文档](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md)。

### 迁移模式的记忆

当代理在迁移过程中发现模式时，它会将其保存下来：

```
/memory show
```

您也可以明确地教导它：

```
/memory add "When migrating Entity Framework 6 to EF Core, always 
check for .edmx files and replace them with code-first models. 
The database-first approach is deprecated in EF Core."
```

> **上下文工程生命周期：** 最好的迁移工作流结合了这三者：代理生成的 GEMINI.md（初始上下文）、@file 导入（模块化标准）和自动记忆（在执行期间学习到的模式）。它们相互强化。

---
## 2.4 — 子代理：委派专业工作 (15 分钟)

### 内置子代理

Gemini CLI 包含用于常见任务的内置子代理：

```
@codebase_investigator Map the relationships between all controllers 
in the backend/ directory. Show which models each controller depends 
on and which routes call each controller.
```

> **@codebase_investigator** 是一个只读代理，用于映射代码关系、追踪调用链并识别架构模式。它从不修改文件。

### 自定义子代理

为您的迁移创建一个安全扫描器：

```bash
cat .gemini/agents/security-scanner.md
```

安全扫描器子代理（来自 [`samples/agents/security-scanner.md`](../../samples/agents/security-scanner.md)）：
- 具有专注于安全分析的系统提示词
- 可以限制为使用特定工具
- 使用特定模型（您可以分配 Flash 以追求速度，或分配 Pro 以追求深度）

### 使用自定义子代理

```
@security-scanner Review the authentication middleware for OWASP 
Top 10 vulnerabilities. Check for:
1. Injection attacks (SQL, NoSQL)
2. Broken authentication
3. Sensitive data exposure
4. Missing rate limiting
```

### 子代理工具隔离

每个子代理都可以有自己的工具许可名单：

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

> **企业价值：** 安全扫描器可以读取代码并搜索 CVE，但它绝不能修改文件或运行命令。工具隔离是纵深防御。

---
## 2.5 — 技能：可复用的专业知识 (5 分钟)

### 查看可用技能

```
/skills list
```

技能是可复用的指令集，代理会在相关时激活它们：

### 技能如何工作

1. **自动激活：** 代理会读取技能描述，并根据你的提示词激活相关的技能
2. **手动激活：** 你可以使用技能名称强制激活某个技能
3. **持久化：** 技能在不同会话中保持有效 —— 一次学习，随处使用

### 自动记忆 🔬

自动记忆会从你的会话中提取模式，并将它们保存到 GEMINI.md 中：

```
/memory show
```

> **实验性：** 自动记忆需要在 `settings.json` 中启用 `experimental.autoMemory`。请参阅 [自动记忆文档](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/auto-memory.md)。启用后，代理可能会自动保存如下模式：“在迁移 Express.js 中间件时，请检查 `req.query` 与 `req.params` 是否不匹配。”

---
## 2.6 — 检查点与 Git 工作树 (5 分钟)

### 检查点

检查点功能会在更改前自动保存修改文件的状态，允许你在出现问题时进行还原。要启用它，请将其添加到你的 `settings.json` 中：

```json
{
  "general": {
    "checkpointing": {
      "enabled": true
    }
  }
}
```

启用后，使用 `/restore` 还原到之前的检查点：

```
/restore
```

> **检查点是轻量级的** — 它们跟踪文件更改，而不是完整的 git 历史记录。有关详细信息，请参阅 [检查点文档](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/checkpointing.md)。

### Git 工作树 🔬

对于并行的迁移工作，请使用 Git 工作树：

```
# Create a worktree for the auth migration
git worktree add ../proshop-auth-migration feature/auth-migration
cd ../proshop-auth-migration
gemini
```

> **为什么使用工作树？** 你可以在一个终端中保留原始代码，在另一个终端中保留迁移后的代码。同时在两者上运行测试。无需切换分支即可比较不同的方法。

---
## 动手练习

打开 **.NET 现代化 PRD** 或 **Java 升级 PRD** 并完成一次迁移。选择你的方法：

### 方法 A：Conductor 优先（计划 → 上下文 → 执行）

从结构化计划开始，让计划驱动上下文的创建：

1. 进入**计划模式**（`/plan`）→ 以只读方式分析目标代码库
2. 使用 **Conductor** 创建与 PRD 阶段匹配的分阶段迁移计划
3. 编写一个 **GEMINI.md**，将迁移标准和批准的计划编码其中
4. 使用 **@codebase_investigator** 映射依赖关系并验证计划
5. 在开始之前创建一个**检查点**
6. 退出计划模式 → 开始迁移，一次完成一个阶段
7. 根据需要使用**模型引导**来纠正路线
8. 在每个阶段之后，运行 `mvn clean verify` 和安全扫描（见下文）
9. 回顾 **Auto Memory** 从本次会话中学到了什么

### 方法 B：自我入职（调查 → 上下文 → 计划 → 执行）

让代理首先建立自己的理解，然后根据其发现进行计划：

1. 使用 **@codebase_investigator** 分析目标代码库并映射依赖关系
2. 让代理根据其分析**编写一个 GEMINI.md**（代理自我入职）
3. 审查并完善生成的上下文 — 添加团队特定的标准
4. 进入**计划模式** → 让 **Conductor** 根据 GEMINI.md 提供的信息创建一个分阶段迁移计划
5. 在开始之前创建一个**检查点**
6. 开始迁移 — 根据需要使用**模型引导**来纠正路线
7. 在每个阶段之后，运行 `mvn clean verify` 和安全扫描（见下文）
8. 回顾 **Auto Memory** 从本次会话中学到了什么

> **选择哪种方法？** 当你已经了解代码库并希望以结构化为主导时，方法 A 效果很好。方法 B 更适合不熟悉的遗留代码 — 代理通常会发现人工编写的计划可能会遗漏的迁移风险。尝试这两种方法，并比较最终生成的计划的质量。

> **迁移后安全扫描：** 在对遗留代码进行现代化改造后，运行官方的 [Security Extension](https://github.com/gemini-cli-extensions/security) 以捕获迁移过程中引入的漏洞。使用 `gemini extensions install https://github.com/gemini-cli-extensions/security` 安装它，然后运行 `/security:analyze` 来扫描你的更改。有关完整详细信息，请参阅 [扩展生态系统 — 练习 4](extensions-ecosystem.md)。

---
## 总结：你学到了什么

| 功能 | 作用 |
|---|---|
| **计划模式** | 只读研究 — 在修改前进行分析 |
| **模型路由** | 自动选择 Pro（计划）→ Flash（编码） |
| **模型引导** | 在中途纠正代理的方向 |
| **代理自我引导** | 代理调查代码库并编写自己的 GEMINI.md |
| **@ import 语法** | 用于大型项目的模块化 GEMINI.md |
| **@codebase_investigator** | 只读代码库分析子代理 |
| **自定义子代理** | 具有工具隔离的专用代理 |
| **技能** | 自动激活的可重用指令集 |
| **自动记忆** | 代理从会话中学习模式 |
| **检查点** | 在进行危险更改之前自动保存/恢复状态（在 settings.json 中启用） |
| **Git 工作树** | 用于同时工作的并行分支 |
| **安全扩展** | 使用 `/security:analyze` 进行迁移后漏洞扫描 |

---
## 下一步

→ 继续前往 **[使用场景 3：代理式 DevOps 编排](devops-orchestration.md)**

→ 面向高级用户：**[高级模式](advanced-patterns.md)** —— 提示词技巧、验证循环和并行开发
