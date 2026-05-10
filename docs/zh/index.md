# Gemini CLI 工作坊

> **面向企业开发者的动手实践赋能** — 通过 Gemini CLI 的工具辅助探索、计划模式和可扩展的代理系统，掌握代理化编程、遗留系统现代化和 DevOps 自动化。
>
> *最后更新：2026-05-05 · [来源已根据 gemini-cli 仓库进行验证](https://github.com/google-gemini/gemini-cli)*

---
## 研讨会流程

本研讨会结构分为 **3 个渐进的使用场景**。每个场景都是独立的，但都建立在前一个场景的技能基础之上：

![研讨会流程](../assets/workshop-flow.png)

**为什么这样安排顺序：** 使用场景 1 建立基础技能（安装、上下文工程、治理）。使用场景 2 在此基础上增加了规划和委派。使用场景 3 引入自动化和 CI/CD 作为顶点。每个场景都建立在前一个场景的基础之上。

---
## 先决条件

| 要求 | 详情 |
|---|---|
| **Node.js** | v18+ ([nodejs.org](https://nodejs.org)) |
| **npm** | 随 Node.js 一起提供 |
| **Git** | v2.30+ ([git-scm.com](https://git-scm.com)) |
| **终端** | 任何现代终端（iTerm2、Windows Terminal、VS Code 集成终端） |
| **Google 账号** | 个人 Google 账号（免费层）或 Vertex AI 凭据（企业版） |
| **jq** | 用于钩子示例 ([jqlang.github.io/jq](https://jqlang.github.io/jq/download/)) |

---
## 快速入门

```bash
# Clone the workshop repo
git clone https://github.com/pauldatta/gemini-cli-field-workshop.git
cd gemini-cli-field-workshop

# Run the setup script (installs CLI, sets up demo app, copies configs)
./setup.sh

# Start the workshop
cd demo-app && gemini
```

然后打开工作坊网站：**[pauldatta.github.io/gemini-cli-field-workshop](https://pauldatta.github.io/gemini-cli-field-workshop/)**

---
## 使用场景概览

### [1. SDLC 生产力提升](sdlc-productivity.md)
构建企业级开发者工作流，从首次安装到上下文工程、使用 Conductor 进行规范驱动的开发，以及治理护栏。这是所有其他内容的基础。

### [2. 遗留代码现代化](legacy-modernization.md)
使用计划模式、自定义子代理、技能和检查点，将传统的 .NET Framework 4.8 应用程序迁移到 Cloud Run 上的 .NET 8。学习如何安全地分解庞大的代码库。

### [3. 代理化 DevOps 编排](devops-orchestration.md)
构建 CI/CD 自动化，用于诊断流水线故障、创建修复程序、提交 PR 并通知团队——所有这些都通过无头模式、钩子和 GitHub Actions 完成。

---
## 演示应用程序

本工作坊使用 **[ProShop v2](https://github.com/bradtraversy/proshop-v2)** — 一个全栈 MERN 电子商务应用程序（Express.js + MongoDB + React + Redux Toolkit）。它作为 git 子模块包含在 `demo-app/` 中。

---
## 额外工具

> **[gemini-cli-scanner](https://github.com/pauldatta/gemini-cli-scanner)** — 一个 TUI 工具，用于扫描本地 Gemini CLI 安装并生成成熟度报告。在研讨会结束后运行它，以审计参与者的技能掌握情况、工具使用模式和配置质量 —— 这是一个很棒的收尾活动，能让学习进度变得可视化。

---
## 资源

| 资源 | 链接 |
|---|---|
| Gemini CLI 文档 | [geminicli.com/docs](https://geminicli.com/docs/) |
| Gemini CLI GitHub | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) |
| CLI 速查表 | [geminicli.com/docs/cli/cli-reference](https://geminicli.com/docs/cli/cli-reference/) |
| 扩展注册表 | [github.com/gemini-cli-extensions](https://github.com/gemini-cli-extensions) |
| MCP 服务器 | [geminicli.com/docs/tools/mcp-server](https://geminicli.com/docs/tools/mcp-server/) |
