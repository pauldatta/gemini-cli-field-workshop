# Gemini CLI Workshop

> **Hands-on enablement for enterprise developers** — master agentic coding, legacy modernization, and DevOps automation with Gemini CLI's full-codebase awareness, Plan Mode, and extensible agent system.

---

## Workshop Flow

This workshop is structured as **3 progressive use cases**. Each is self-contained but builds on skills from the previous:

```
┌──────────────────────────────────────────────────────┐
│  0. Environment Setup              (setup)    15 min │
├──────────────────────────────────────────────────────┤
│  1. SDLC Productivity Enhancement  (sdlc)     60 min │
│     → Install · GEMINI.md · Memory · Conductor       │
│     → MCP · Extensions · Governance · Policy         │
├──────────────────────────────────────────────────────┤
│  2. Legacy Code Modernization      (appmod)   60 min │
│     → Plan Mode · Model Routing · Subagents          │
│     → Skills · Checkpointing · Git Worktrees         │
├──────────────────────────────────────────────────────┤
│  3. Agentic DevOps Orchestration   (devops)   45 min │
│     → Headless Mode · Hooks · GitHub Actions         │
│     → MCP + Jira · Auto Memory · Batch Ops           │
├──────────────────────────────────────────────────────┤
│  📄 Cheatsheet (handout)                             │
└──────────────────────────────────────────────────────┘
```

**Why this order:** Use Case 1 builds foundational skills (install, context engineering, governance). Use Case 2 layers on planning and delegation. Use Case 3 brings automation and CI/CD as the capstone. Each builds on the previous.

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Node.js** | v18+ ([nodejs.org](https://nodejs.org)) |
| **npm** | Included with Node.js |
| **Git** | v2.30+ ([git-scm.com](https://git-scm.com)) |
| **Terminal** | Any modern terminal (iTerm2, Windows Terminal, VS Code integrated) |
| **Google Account** | Personal Google account (free tier) or Vertex AI credentials (enterprise) |
| **jq** | For hook examples ([jqlang.github.io/jq](https://jqlang.github.io/jq/download/)) |

---

## Quick Start

```bash
# Clone the workshop repo
git clone https://github.com/pauldatta/gemini-cli-field-workshop.git
cd gemini-cli-field-workshop

# Run the setup script (installs CLI, sets up demo app, copies configs)
./setup.sh

# Start the workshop
cd demo-app && gemini
```

Then open the workshop site: **[pauldatta.github.io/gemini-cli-field-workshop](https://pauldatta.github.io/gemini-cli-field-workshop/)**

---

## Use Cases at a Glance

### [1. SDLC Productivity Enhancement](sdlc-productivity.md)
Build an enterprise-grade developer workflow from first install through context engineering, spec-driven development with Conductor, and governance guardrails. The foundation for everything else.

### [2. Legacy Code Modernization](legacy-modernization.md)
Migrate a legacy .NET Framework 4.8 app to .NET 8 on Cloud Run using Plan Mode, custom subagents, skills, and checkpointing. Learn to decompose massive codebases safely.

### [3. Agentic DevOps Orchestration](devops-orchestration.md)
Build CI/CD automation that diagnoses pipeline failures, creates fixes, submits PRs, and notifies teams — all from headless mode, hooks, and GitHub Actions.

---

## Demo Application

This workshop uses **[ProShop v2](https://github.com/bradtraversy/proshop-v2)** — a full-stack MERN eCommerce application (Express.js + MongoDB + React + Redux Toolkit). It's included as a git submodule in `demo-app/`.

---

## Bonus Tools

> **[gemini-cli-scanner](https://github.com/pauldatta/gemini-cli-scanner)** — A TUI tool that scans your local Gemini CLI installation and generates a maturity report. Useful for trainers to audit participant environments before the workshop or as a fun closing activity.

---

## Resources

| Resource | Link |
|---|---|
| Gemini CLI Documentation | [geminicli.com/docs](https://geminicli.com/docs/) |
| Gemini CLI GitHub | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) |
| CLI Cheatsheet | [geminicli.com/docs/cli/cli-reference](https://geminicli.com/docs/cli/cli-reference/) |
| Extensions Registry | [github.com/gemini-cli-extensions](https://github.com/gemini-cli-extensions) |
| MCP Servers | [geminicli.com/docs/tools/mcp-server](https://geminicli.com/docs/tools/mcp-server/) |
