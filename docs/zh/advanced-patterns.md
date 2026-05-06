# 高级模式

> **时长：** 约 45 分钟（自定进度）  
> **目标：** 掌握提示词规范、验证循环、上下文工程和并行开发。这些技术适用于任何 Gemini CLI 工作流。  
> **先决条件：** 至少完成[使用场景 1：SDLC 生产力提升](sdlc-productivity.md)或熟悉基础知识。
>
> *最后更新：2026-05-05 · [已针对 gemini-cli 仓库验证源码](https://github.com/google-gemini/gemini-cli)*

---
## 提示词技巧：目标与指令的对比

要提高 AI 输出质量，你能做出的最大改进就是改变**提问方式**。

### 问题所在

大多数开发者会给出循序渐进的指令：

```
Create a wishlist model with userId and productId fields.
Then create a controller with addToWishlist and getWishlist functions.
Then add routes at /api/wishlist.
Then create a Redux slice.
Then create the WishlistScreen component.
```

这会迫使代理走上一条特定的路径——即使存在更好的方法。代理无法提出异议、展示权衡或进行调整。

### 解决方案：带有成功标准的声明式目标

```
Add a product wishlist feature. When you're done:
1. A logged-in user can add/remove products from their wishlist
2. The wishlist persists across sessions (stored in MongoDB)
3. There's a /wishlist page accessible from the navbar
4. All existing tests still pass (npm test)
5. The code follows the conventions in GEMINI.md

Say "WISHLIST_COMPLETE" when all criteria are verified.
```

### 为什么这行得通

| 命令式 (❌) | 声明式 (✅) |
|---|---|
| 规定实现细节 | 描述期望的结果 |
| 代理无法提出异议或建议替代方案 | 代理为代码库选择最佳方法 |
| 没有验证——你必须手动检查 | 通过成功标准内置验证循环 |
| 单一僵化的路径 | 代理根据其发现进行调整 |

> **关键洞察：**“不要告诉它怎么做——给它成功标准，然后看它发挥。”代理非常擅长循环执行，直到满足特定目标。薄弱的标准（“让它能运行”）需要不断的指导。强大的标准则能让它独立运行。

### 练习

在 ProShop 的同一个任务上尝试这两种方法。比较：
1. 每种方法各花了多少轮对话？
2. 声明式版本是否找到了更好的方法？
3. 哪种方法生成的代码更整洁？

---
## 上下文纪律

代理的上下文窗口中的每一个令牌都会使下一次响应的焦点略微分散。上下文是一种预算——要像管理受限设备上的内存一样管理它。

### 上下文过载的症状

- 代理开始重复自己的话
- 幻觉增加（引用不存在的文件）
- 在 15-20 轮对话后，输出质量显著下降
- 代理“忘记”了早期的指令

### 工具包

#### 1. 策略性重置

当输出质量下降时：

```
/clear
```

这会重置对话上下文，同时保持 GEMINI.md、记忆和文件状态完好无损。代理会重新开始，但保留了你所有的项目知识。

#### 2. 清除前保存

```
/memory add "The ProShop codebase uses a repository pattern for 
data access. All MongoDB queries go through model methods, never 
directly in controllers. Express middleware chain: cors → 
cookieParser → authMiddleware → routes."
```

记忆在会话和 `/clear` 重置之间是持久存在的。在清除之前保存重要的发现。

#### 3. 上下文卸载

将大型规范移出对话并放入文件中：

```bash
# Instead of pasting a long spec into chat:
echo "Your detailed spec..." > feature-spec.md

# Then reference it in your prompt with @:
# "Read @./feature-spec.md and implement it"
```

或者将其作为导入添加到你的 GEMINI.md 中，以实现持久的上下文：

```markdown
# GEMINI.md
@./feature-spec.md
```

> 有关导入语法，请参阅 [GEMINI.md 参考](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md)。

#### 4. 通过代理委派进行隔离

每个自定义代理都有自己的上下文窗口。策略性地使用这一点：

```
# Bad: one agent doing everything (context bloat)
"Research the auth system, then refactor it, then write tests, then review"

# Good: isolated phases (each gets clean context)
@codebase_investigator Map the auth system
Now refactor based on the investigator's findings
@pr-reviewer Review the refactored auth code
```

### 练习

1. 启动一个会话并按顺序构建三个功能（故意积累上下文）
2. 注意在 15-20 轮对话左右质量的下降
3. 运行 `/memory add` 来保存关键事实
4. 运行 `/clear` —— 观察质量的立即提升
5. 要求代理从它停下的地方继续 —— 它会通过记忆 + 文件状态接续工作

---
## 验证循环

从代理获取正确代码的最可靠方法是为其提供一个**反馈循环**——一种检查自身工作并自动修复错误的方法。

### 模式

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

### 为什么完成承诺有效

“完成后说 X”这句话赋予了代理：

1. **明确的停止点**——它知道何时停止工作
2. **自我验证的动机**——它在宣布完成之前会检查自己的工作
3. **迭代恢复**——如果测试失败，它会修复并重新运行，而不是询问你

### 自动化循环

对于大型任务，你可以使用钩子自动化反馈循环。一个 `AfterAgent` 钩子会检查输出中是否出现了完成承诺。如果没有，它会重置对话（保留文件更改），并使用原始提示词 + 改进后的代码库重新运行：

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

> **安全提示：** 在运行自主循环时，始终配置工具限制。在你的 `settings.json` 或 `policy.toml` 中阻止破坏性操作（`git push --force`、`rm -rf`）。

### 练习

给代理一个带有明确成功标准和完成承诺的重构任务。观察它在测试失败中不断迭代，直到测试通过（变绿）。

---
## 使用工作树进行并行开发

在不同分支上同时运行多个 Gemini CLI 会话——每个会话都完全隔离。

### 问题

一次只能检出一个分支。如果你想使用独立的代理同时处理新功能、错误修复和重构，它们就会发生冲突。

### 解决方案

```bash
# Terminal 1: Feature work
gemini --worktree feature-wishlist

# Terminal 2: Bug fix
gemini --worktree fix-cart-rounding

# Terminal 3: Documentation
gemini --worktree update-api-docs
```

每个代理都在自己的目录、自己的分支和自己的上下文中工作。不会产生冲突。

### 工作流

| 阶段 | 操作 |
|---|---|
| **隔离** | 为每个任务/代理创建一个工作树 |
| **配置** | 每个工作树分配独立的开发服务器端口以避免冲突 |
| **执行** | 启动独立的 Gemini CLI 会话——每个代理独立工作 |
| **审查** | 每个代理在其工作树内向自己的分支提交代码 |
| **集成** | 通过 PR 将分支合并回 `main` |
| **清理** | `git worktree remove <path>` + `git worktree prune` |

> **将工作树视为一次性用品。** 它们针对单个任务的持续时间进行了优化。合并后请将其删除。

### 练习

打开两个终端窗口。使用工作树来：
1. 在一个窗口中添加愿望清单功能
2. 在另一个窗口中修复购物车总价计算问题

两个代理同时工作。彼此都看不到对方的更改。通过 PR 合并两者。

---
## 多代理编排

对于跨项目管理数十个代理的团队，编排工具提供了企业级的隔离性、可观测性和扩展性。

### Scion (Google Cloud Platform)

**[Scion](https://github.com/GoogleCloudPlatform/scion)** 是一个实验性的多代理编排器，它将代理作为隔离的并发进程运行——每个代理都在自己的容器中。

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

| 概念 | 描述 |
|---|---|
| **代理** | 运行 Gemini CLI 的容器化进程 |
| **Grove** | 项目命名空间——通常与 git 仓库 1:1 对应 |
| **模板** | 代理蓝图：系统提示词 + 技能 + 工具权限 |
| **运行时** | Docker、Podman、Apple Container 或 Kubernetes |

> **何时使用 Scion：** 拥有 5 个以上并发代理任务的团队，需要在代理之间进行严格隔离的项目，或者在多个仓库中扩展 AI 管理的开发的组织。

---
## 工程章程模式

如果你必须向代理重复同一件事两次，那么它就应该被写进文件里。

### 章程中应包含什么内容

一个精心编写的 `GEMINI.md` 能够编码你团队的工程标准，以便代理自动遵循它们：

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

### 练习

1. 为 ProShop 编写一个包含 5 条规则的 GEMINI.md
2. 在**没有**该文件的情况下，要求代理添加一个功能 —— 注意输出结果
3. 在**有**该文件的情况下，提出相同的要求
4. 比较：代理是否遵循了约定？它是否提出了之前跳过的澄清问题？

---
## 确定性强制执行

`GEMINI.md` 非常适合用于*指导*代理，但它不能保证 100% 的合规性。在复杂的重构过程中，代理可能会产生错误模式的幻觉——例如，即使你的章程规定不能这样做，它也可能在路由文件中直接导入模型。

解决方法：将基于提示词的指导与**确定性护栏**相结合——即通过机械方式捕获违规行为的硬性边界。

### 输入护栏与输出护栏

| 层级 | 时机 | 示例 |
|---|---|---|
| **输入**（生成前） | 在代理看到上下文之前 | `.geminiignore` 限制文件访问；`GEMINI.md` 设定架构预期 |
| **输出**（生成后） | 生成之后，合并之前 | Linter 强制执行边界；扫描器检测泄露的机密信息；测试套件验证行为 |

输入护栏减少错误。输出护栏*捕获*错误。

### 模式：“AI 提议，CI 处置”

与其依赖 LLM 自我监督，不如使用传统的工程工具来强制执行规则：

1. **指南** (`GEMINI.md`) —— 告诉代理如何在第一次就正确地编写代码。
2. **守卫**（Linter、静态分析）—— 确定性地捕获违规行为。
3. **循环** —— 如果守卫失败，错误将通过 [`AfterAgent` 钩子](https://www.geminicli.com/docs/hooks/)反馈给代理，迫使其自我纠正。这与[验证循环](#verification-loops)模式相同，只是实现了自动化。

### 实践中的强制执行

任何以非零状态退出的工具都可以作为护栏。将其接入 CI、git 的 `pre-commit` 钩子或 Gemini CLI 的 `AfterAgent` 事件中：

| 执行器 | 捕获内容 |
|---|---|
| **ESLint / Ruff** | 代码复杂度、代码风格违规、被禁用的 API |
| **gitleaks** | 硬编码的 API 密钥、源码中的凭据 |
| **dependency-cruiser** | 非法的跨层导入（架构边界） |
| **自定义测试套件** | 行为回退 |

#### 示例：使用 dependency-cruiser 强制执行层级边界

如果你的 `GEMINI.md` 规则规定“路由文件中不能有业务逻辑”，请使用 [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) 确定性地强制执行它：

```javascript
// .dependency-cruiser.js
module.exports = {
  forbidden: [
    {
      name: 'no-business-logic-in-routes',
      comment: 'Routes should only delegate to controllers. Never import models directly.',
      severity: 'error',
      from: { path: '^src/routes/' },
      to: { path: '^src/models/' }
    }
  ]
};
```

创建一个钩子脚本，运行 Linter 并在失败时返回结构化的 JSON：

```bash
#!/usr/bin/env bash
# .gemini/hooks/check-architecture.sh
input=$(cat)  # Read hook input from stdin (required)

output=$(npx depcruise src --config .dependency-cruiser.js 2>&1)
if [ $? -ne 0 ]; then
  # Return a denial — AfterAgent treats this as a retry prompt
  jq -n --arg msg "$output" '{
    "decision": "deny",
    "reason": ("Architecture violation detected. Fix the illegal import:\n" + $msg)
  }'
else
  echo '{"decision": "allow"}'
fi
```

> **`AfterAgent` 重试机制的工作原理：** 当钩子返回 `decision: "deny"` 时，Gemini CLI 会拒绝代理的响应，并将 `reason` 文本作为新的提示词发送回代理。然后，代理会尝试自动修复违规行为。有关完整的架构，请参阅[钩子参考](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md)。

使用标准的钩子配置架构在你的设置中注册该脚本：

**`.gemini/settings.json`**

```json
{
  "hooks": {
    "AfterAgent": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/check-architecture.sh",
            "name": "architecture-guard",
            "description": "Enforces layer boundaries via dependency-cruiser after each agent turn"
          }
        ]
      }
    ]
  }
}
```

现在，如果代理创建了非法的导入，钩子将拒绝该响应并将 Linter 错误作为重试提示词反馈回去——代理将自行修复其违规行为。

### 练习

1. 在项目中，创建一个直接导入数据库模型的路由文件
2. 配置 `dependency-cruiser`（或自定义的 ESLint 规则）以阻止这种模式
3. 使用上述配置将其注册为 `AfterAgent` 钩子
4. 要求代理“向路由添加一个新端点”——观察它是否会复制这种不良模式
5. 如果确实如此，观察钩子如何拒绝响应以及代理如何自我纠正

---
## 基于技能的开发

技能是结构化的、可重用的指令文件（`SKILL.md`），它们将高级工程师的工作流直接编码到代理中。与原始提示词不同，每项技能都包含分步流程、反合理化表格（代理可能用来跳过步骤的常见借口，以及记录在案的反驳）、危险信号和验证关卡。

### 为什么技能优于原始提示词

| 原始提示词 | 结构化技能 |
|---|---|
| "为此编写测试" | 激活红-绿-重构工作流，并带有测试金字塔目标 (80/15/5) |
| "审查此代码" | 运行带有严重性标签 (Nit/Optional/FYI) 和变更大小规范的五轴审查 |
| "确保其安全" | 触发带有三层边界系统的 OWASP Top 10 检查表 |
| 没有停止标准 | 内置验证关卡 — 代理必须在继续之前提供证据 |

### 安装社区技能

[agent-skills](https://github.com/addyosmani/agent-skills) 包提供了 20 个覆盖完整 SDLC 的生产级技能。使用一条命令即可安装它们：

```bash
# Install from GitHub (auto-discovers all SKILL.md files)
gemini skills install https://github.com/addyosmani/agent-skills.git --path skills

# Verify installation
/skills list
```

安装后，当代理识别到匹配的任务时，技能会按需激活。正在构建 UI？`frontend-ui-engineering` 技能会自动激活。正在调试测试失败？`debugging-and-error-recovery` 会开始发挥作用。

### SDLC 斜杠命令

该技能包在 `.gemini/commands/` 下附带了 7 个映射到开发生命周期的斜杠命令：

| 命令 | 阶段 | 作用 |
|---|---|---|
| `/spec` | 定义 | 在编写代码之前编写结构化的 PRD |
| `/planning` | 计划 | 将工作分解为带有验收标准的小型、可验证任务 |
| `/build` | 构建 | 将下一个任务实现为薄垂直切片 |
| `/test` | 验证 | 运行 TDD 工作流 — 红、绿、重构 |
| `/review` | 审查 | 带有严重性标签的五轴代码审查 |
| `/code-simplify` | 审查 | 在不改变行为的情况下降低复杂性（切斯特顿栅栏） |
| `/ship` | 发布 | 通过并行角色扇出的发布前检查表 |

> **注意：** 请使用 `/planning` 而不是 `/plan` — `/plan` 会与 Gemini CLI 内置的计划模式命令冲突。

### 技能对比 GEMINI.md

两者都会影响代理行为，但服务于不同的目的：

| | 技能 | GEMINI.md |
|---|---|---|
| **加载方式** | 按需，当任务匹配时 | 每次提示词，始终加载 |
| **令牌成本** | 激活前极低 | 固定的开销 |
| **最适用于** | 特定阶段的工作流（TDD、安全审查、发布） | 始终开启的项目约定（技术栈、编码标准） |

**经验法则：** 如果你希望它在*每次*提示词中都处于激活状态，请将其放入 GEMINI.md 中。如果它是特定于阶段的，请将其作为技能安装。

### 练习

1. 将 agent-skills 包安装到你的 ProShop 工作区中
2. 运行 `/spec` — 为“产品比较”功能编写规范
3. 运行 `/build` — 增量实现第一个切片
4. 运行 `/test` — 观察 TDD 工作流强制执行红-绿-重构
5. 比较：结构化工作流与原始的“添加比较功能”提示词有何不同？

---
## Google 托管的 MCP 服务器

Google 提供了 **50 多个托管的 MCP 服务器**，使您的代理能够直接、受控地访问 Google Cloud 服务、Workspace 应用程序和开发者工具——无需在本地安装服务器。

### 为什么选择托管的 MCP？

| 关注点 | 托管的 MCP 如何解决 |
|---|---|
| **安全性** | 用于工具级别访问控制的 IAM 拒绝策略；用于防御提示词注入的 Model Armor |
| **发现** | 代理注册表（Agent Registry）——用于查找和管理 MCP 服务器的统一目录 |
| **可观测性** | OTel 追踪 + Cloud Audit Logs 用于完整的操作取证 |
| **互操作性** | 与 Gemini CLI、Claude Code、Cursor、VS Code、LangChain、ADK、CrewAI 兼容 |

### 开发者知识 MCP

[开发者知识 MCP 服务器](https://developers.google.com/knowledge/mcp)将您的代理建立在官方 Google 文档（Firebase、Cloud、Android、Maps 等）的基础之上。代理不会凭空捏造 API 签名，而是查询实时的文档语料库。

**单行安装（API 密钥认证）：**

```bash
gemini mcp add -t http \
  -H "X-Goog-Api-Key: YOUR_API_KEY" \
  google-developer-knowledge \
  https://developerknowledge.googleapis.com/mcp --scope user
```

**或者通过 `settings.json`（面向企业的 ADC 认证）：**

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

**可用工具：**

| 工具 | 目的 |
|---|---|
| `search_documents` | 查找与查询相关的文档块 |
| `get_documents` | 检索特定文档的完整页面内容 |
| `answer_query` | 从文档语料库中获取综合的、有根据的答案 |

### 按类别划分的高价值 MCP 服务器

| 类别 | 服务器 | 示例使用场景 |
|---|---|---|
| **开发者文档** | 开发者知识 API | “我该如何配置 Cloud Run 自动扩缩容？” → 带有来源引用的答案 |
| **数据与分析** | BigQuery、Spanner、Firestore、AlloyDB | 直接从代理上下文查询生产数据 |
| **基础设施** | Cloud Run、GKE、Compute Engine | 通过自然语言配置、扩展和管理基础设施 |
| **生产力** | Gmail、Drive、Calendar、Chat | 总结邮件线索、起草文档、管理邀请 |
| **安全性** | Security Operations、Model Armor | 调查威胁、实时拦截提示词注入 |

> **治理：** 使用 [IAM 拒绝策略](https://docs.cloud.google.com/mcp/control-mcp-use-iam#deny-all-mcp-tool-use)来限制代理可以调用哪些 MCP 工具。结合 [Model Armor](https://docs.cloud.google.com/model-armor/model-armor-mcp-google-cloud-integration) 来防御间接提示词注入和数据泄露。

### 练习

1. 从您的 Google Cloud 项目获取开发者知识 API 密钥
2. 使用上面的单行命令将开发者知识 MCP 服务器添加到您的 Gemini CLI 配置中
3. 询问代理：*“我该如何使用自定义域名部署 Cloud Run 服务？”*
4. 验证：回复是否引用了官方文档？与未连接 MCP 服务器时的答案进行比较

---
## 使用 agents-cli 构建代理

[`agents-cli`](https://github.com/google/agents-cli) 是一个 CLI 和技能包，用于教导您的编码代理如何在 Google 的 [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform) 上构建、评估和部署代理。它不是 Gemini CLI 的替代品——它是*为*编码代理提供的一个工具。

### 快速设置

```bash
# Install CLI + skills into all detected coding agents
uvx google-agents-cli setup

# Or install just the skills (your coding agent handles the rest)
npx skills add google/agents-cli
```

> **先决条件：** Python 3.11+、[uv](https://docs.astral.sh/uv/getting-started/installation/) 和 Node.js。有关环境说明，请参阅 `setup.sh`。

### 核心工作流

| 命令 | 作用 |
|---|---|
| `agents-cli scaffold <name>` | 使用最佳实践结构创建一个新的 ADK 代理项目 |
| `agents-cli scaffold enhance` | 向现有的代理项目添加部署、CI/CD 或 RAG |
| `agents-cli eval run` | 运行代理评估（LLM 作为裁判、轨迹评分） |
| `agents-cli deploy` | 部署到 Google Cloud（Agent Runtime、Cloud Run 或 GKE） |
| `agents-cli publish gemini-enterprise` | 在 Gemini Enterprise 中注册代理 |

### 它安装的技能

当您运行 `agents-cli setup` 时，它会将 7 个技能安装到您的编码代理中：

| 技能 | 您的编码代理学到了什么 |
|---|---|
| `google-agents-cli-workflow` | 开发生命周期、代码保留规则、模型选择 |
| `google-agents-cli-adk-code` | ADK Python API — 代理、工具、编排、回调、状态 |
| `google-agents-cli-scaffold` | 项目脚手架 — `create`、`enhance`、`upgrade` |
| `google-agents-cli-eval` | 评估方法 — 指标、评估集、LLM 作为裁判 |
| `google-agents-cli-deploy` | 部署 — Agent Runtime、Cloud Run、GKE、CI/CD、机密信息 |
| `google-agents-cli-publish` | Gemini Enterprise 注册 |
| `google-agents-cli-observability` | Cloud Trace、日志记录、第三方集成 |

### 何时使用 agents-cli 与原生 ADK

| 场景 | 工具 |
|---|---|
| 使用最佳实践从头开始构建代理 | `agents-cli scaffold` |
| 向现有的代理添加 RAG 或部署 | `agents-cli scaffold enhance` |
| 使用结构化指标评估代理质量 | `agents-cli eval run` |
| 完全控制的手动部署 | 直接使用 `adk deploy` |
| 在没有脚手架的情况下编写 ADK 代码 | 原生 ADK + 您的编码代理 |

### 练习

1. 安装 agents-cli：`uvx google-agents-cli setup`
2. 为新代理搭建脚手架：`agents-cli scaffold my-review-bot`
3. 在 Gemini CLI 中打开搭建好脚手架的项目并提问：*“使用 Cloud Storage 增强此代理的 RAG 功能”*
4. 运行评估：`agents-cli eval run`
5. 观察安装的技能如何引导 Gemini CLI 完成它原本不知道的特定于 ADK 的模式

---
## 延伸阅读

| 资源 | 说明 |
|---|---|
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 20 个用于编码代理的生产级工程技能 |
| [google/agents-cli](https://github.com/google/agents-cli) | 用于在 Google Cloud 上构建 ADK 代理的 CLI + 技能 |
| [Developer Knowledge MCP](https://developers.google.com/knowledge/mcp) | 将代理建立在官方 Google 开发者文档的基础上 |
| [Google 托管的 MCP 服务器](https://cloud.google.com/blog/products/ai-machine-learning/google-managed-mcp-servers-are-available-for-everyone) | 50 多个企业级 MCP 服务器（Cloud 博客） |
| [支持的 MCP 产品](https://docs.cloud.google.com/mcp/supported-products) | Google 托管的 MCP 服务器完整目录 |
| [GoogleCloudPlatform/scion](https://github.com/GoogleCloudPlatform/scion) | 面向团队的多代理编排 |
| [pauldatta/gemini-cli-field-workshop](https://github.com/pauldatta/gemini-cli-field-workshop) | 本研讨会的源代码仓库 |
| [Gemini CLI 文档](https://geminicli.com) | 官方文档 |

---
## 下一步

→ 返回 **[使用场景 1：SDLC 生产力提升](sdlc-productivity.md)** 了解核心功能

→ 继续前往 **[使用场景 2：遗留代码现代化](legacy-modernization.md)** 了解棕地工作流
