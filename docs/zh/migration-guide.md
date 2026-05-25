# M09 — 迁移指南：Gemini CLI → Antigravity CLI

**时长：** 30 分钟  
**受众：** 所有人  
**先决条件：** M01（初次接触）  
**目标：** 了解 2026 年 6 月 18 日的过渡，迁移所有现有配置，并为您的团队决定正确的前进道路。

> **⚠️ 时间紧迫：** Gemini CLI 将于 **2026 年 6 月 18 日**停止为免费、Google AI Pro 和 Google AI Ultra 用户提供服务。本模块将逐步介绍每个迁移步骤，以免您的团队一觉醒来发现工作流已中断。

---
## 背景：为什么会发生这种变化

当 Google 在 2025 年发布 Gemini CLI 时，目标是将 Gemini 直接引入终端。在获得了超过 10 万个 GitHub 星标、6,000 个合并的拉取请求以及数百万用户之后，团队认识到了一个重要的事实：开发人员现在需要**多个相互通信的代理**，并与其工作流的其余部分共享一个统一的后端。

这种架构需求推动了此次整合。**Antigravity CLI** (`agy`) 便是这一结果——一个基于 Go 语言、代理优先的终端体验，它与 Antigravity 2.0 桌面应用程序共享相同的运行框架。对代理引擎的每一项核心改进都会自动应用到所有地方。

与 Gemini CLI 相比的主要变化：

| 维度 | Gemini CLI | Antigravity CLI |
|:---|:---|:---|
| **语言** | Node.js / TypeScript | Go（更快的冷启动） |
| **二进制文件名称** | `gemini` | `agy` |
| **许可证** | Apache 2.0 (开源) | 闭源 |
| **多代理** | 子代理（单会话） | 异步，后台编排 |
| **桌面同步** | 无 | 与 Antigravity 2.0 共享运行框架 |
| **技能路径** | `.gemini/skills/` | `.agents/skills/` |
| **插件格式** | `settings.json` 中的扩展 | Antigravity 插件 (`plugin.json`) |
| **MCP 配置** | 在 `settings.json` 中内联 | 独立的 `mcp_config.json` |
| **上下文文件** | `GEMINI.md` | `GEMINI.md` **或** `AGENTS.md`（两者均可） |

**参考资料：**
- [Google I/O 公告 (2026 年 5 月 19 日)](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
- [官方迁移文档](https://antigravity.google/docs/gcli-migration)
- [社区迁移指南](https://avinashsangle.com/blog/gemini-cli-to-antigravity-cli-guide)

---
## 9.1 — 谁会受到影响？ (5 分钟)

**显示影响矩阵：**

| 层级 | 2026 年 6 月 18 日的状态 | 推荐操作 |
|:---|:---|:---|
| **免费 (面向个人的 Gemini Code Assist)** | 停止服务 | 迁移至 Antigravity CLI |
| **Google AI Pro ($19.99/月)** | 停止提供 Gemini CLI 服务 | 自动应用 Antigravity Pro 层级；请检查新的请求频率限制 |
| **Google AI Ultra ($249.99/月)** | 停止提供 Gemini CLI 服务 | 自动应用 Antigravity Ultra 层级（无每周上限） |
| **Gemini Code Assist 标准版 / 企业级** | ✅ 无变化 | 可选迁移；Gemini CLI 继续工作 |
| **Gemini Code Assist for GitHub (通过 GCP 付费)** | 现有安装无变化；阻止新安装 | 在下次续订前计划迁移 |

> **对于使用标准版/企业级的研讨会参与者：** 您不会被强制要求迁移。Antigravity CLI 现在已对您可用且值得评估，但您现有的投资会受到保护。

**如果您想保留 Gemini CLI 的开源二进制文件，有两条路径可走：**
1. 将**付费的 Gemini API 密钥**（AI Studio 或 Vertex AI）接入 Apache 2.0 Gemini CLI 二进制文件中——您的技能、钩子和 MCP 配置无需更改。
2. 升级到 **Gemini Code Assist 标准版或企业级**，以获得托管且受支持的路径。

> 注意：Antigravity CLI 是**闭源**的——这是对 Gemini CLI 的 Apache 2.0 模式的刻意打破。如果在您的受监管环境中，供应商中立的可移植性、审计或分叉权利很重要，那么付费 API 密钥路径可以保留这些特性。

---
## 9.2 — 安装 Antigravity CLI (5 分钟)

> **最佳实践：** 在过渡期间，将两个二进制文件（`gemini` 和 `agy`）并排安装。在切换之前，通过两者运行一个工作流以确认一致性。

### macOS 和 Linux

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

二进制文件会安装在 `~/.local/bin/agy`。如果该目录不在您的 `PATH` 中：

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

### 首次运行与 OAuth

```bash
agy
```

这将在您的默认浏览器中打开 Google OAuth。请使用**您用于 Gemini CLI 的相同帐户**登录，以便插件导入能够获取正确的工作区。在远程 SSH 服务器上，`agy` 会检测会话并打印一个授权 URL 供本地打开（这是对 Gemini CLI 旧流程的改进）。

**验证安装：**

```bash
agy --version
```

---
## 9.3 — 迁移插件与扩展 (5 分钟)

Gemini CLI 的扩展将变为 Antigravity CLI 插件。import 命令会自动处理大部分迁移工作。

### 第 1 步 — 自动导入

```bash
agy plugin import gemini
```

这将扫描您的 Gemini CLI 扩展目录，并将每个扩展注册为 Antigravity 插件。依赖自定义主题的插件将静默丢弃其主题 — 请使用 `plugin.json` 格式手动重建这些主题。

### 第 2 步 — 验证导入的插件

```bash
agy plugin list
```

### 第 3 步 — 移动工作区技能

```bash
# Skills used to live here (per-workspace):
# .gemini/skills/

# They now live here:
# .agents/skills/

cp -r .gemini/skills/ .agents/skills/
```

全局技能目录会从新路径自动加载。无需对技能的 SKILL.md 文件进行任何内容更改。

> **研讨会上下文文件向后兼容。** `GEMINI.md` 和 `AGENTS.md` 均可直接读取而无需修改。您无需重命名或重新格式化现有的项目上下文文件。

---
## 9.4 — 迁移 MCP 服务器配置 (5 分钟)

MCP 服务器配置从内联的 `settings.json` 移至专用的 `mcp_config.json` 中，并且重命名了一个字段。

### 之前 (Gemini CLI `settings.json`)

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

### 之后 (Antigravity CLI `mcp_config.json`)

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

**唯一的更改是 `url` → `serverUrl`。** 所有其他字段保持不变。

**验证 MCP 服务器已加载：**

```bash
agy /mcp
```

---
## 9.5 — 验证钩子并运行端到端测试 (5 分钟)

钩子在 Antigravity CLI 中继续有效。重新运行由钩子驱动的工作流，以确认 `pre-tool-call` 和 `stop` 钩子按预期触发。

```bash
# Run a representative workflow you trust
agy "Analyze backend/controllers/orderController.js and summarize the error handling patterns"

# Compare to Gemini CLI output if you still have it running
gemini "Analyze backend/controllers/orderController.js and summarize the error handling patterns"
```

**CLI 界面中发生的变化（注意）：**

| Gemini CLI | Antigravity CLI | 备注 |
|:---|:---|:---|
| `gemini --resume` | `agy --resume` | 语义相同 |
| `gemini -p "prompt"` | `agy -p "prompt"` | 无头模式保持不变 |
| `/tools` | `/tools` | 未改变 |
| `/rewind` | `/rewind` | 未改变 |
| `gemini skills` (终端命令) | 在 `agy` 内部使用 `/skills` | 终端级别的命令已移除 |
| `--temperature`, `--top_k` | 未在 CLI 界面中暴露 | 通过配置或提示词设置 |

---
## 9.6 — 请求频率限制与定价现状核实 (5 分钟)

> **免费层用户请注意：** 免费层比 Gemini CLI 旧版的免费层限制要严格得多。

| 层级 | Gemini CLI (旧版) | Antigravity CLI |
|:---|:---|:---|
| **免费** | 约 1,000 次请求/天 | 每周配额；每 5 小时刷新一次，直至达到每周硬性上限 |
| **Pro ($19.99/月)** | 合理的每日限制 | Antigravity Pro 层级 |
| **Ultra ($249.99/月)** | 较高的每日限制 | 无每周上限 |

社区报告 (GitHub Discussion #27274) 指出，免费层的每周上限在 **4–5 轮对话**内就会耗尽，重置窗口期为 166 小时。如果您在研讨会练习中使用 Antigravity CLI，请为此做好计划。

**研讨会交付的实用建议：**
- 如果您的组织拥有标准版/企业级许可证，请继续使用 Gemini CLI 进行动手实践模块，并使用本模块来指导团队了解迁移路径。
- 如果在个人帐户上运行，请使用付费的 Pro/Ultra 层级，或准备基于 API 密钥的备用方案。

---
## 9.7 — 决策框架：保留、迁移还是切换？ (5 分钟)

使用此决策树来推荐正确的路径：

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
## 活动：现场迁移（如果时间允许）

针对研讨会仓库本身执行迁移清单：

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
## 核心要点

- **截止日期：** 免费层、AI Pro 和 AI Ultra 用户的截止日期为 2026 年 6 月 18 日。企业级用户不受影响。
- **迁移时间：** 包含技能、钩子和 MCP 服务器的每个工作区大约需要 30–60 分钟。
- **`GEMINI.md` 开箱即用。** 无需重命名，无需重新格式化。
- **最大的注意事项：** MCP 配置移至 `mcp_config.json`，且 `url` 重命名为 `serverUrl`。
- **请求频率限制：** 免费层的限制大幅收紧。请据此做好预算。
- **企业级团队：** 您现有的 Gemini CLI 投资受到保护。迁移是可选的。

---
## 参考资料

- [官方公告 — Google 开发者博客](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
- [官方迁移文档 — antigravity.google](https://antigravity.google/docs/gcli-migration)
- [社区指南 — Avinash Sangle](https://avinashsangle.com/blog/gemini-cli-to-antigravity-cli-guide)
- [GitHub 讨论 #27274 — 社区反应](https://github.com/google-gemini/gemini-cli/discussions/27274)
- [Antigravity CLI 下载](https://antigravity.google/download)
