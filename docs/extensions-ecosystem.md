# Extensions Ecosystem

> **Duration:** ~30 minutes (self-paced)
> **Goal:** Understand what extensions are, discover and install community extensions, and learn how organizations package knowledge and tools for distribution.
> **Prerequisites:** Complete at least [Use Case 1: SDLC Productivity](sdlc-productivity.md) or be familiar with the basics. You should already know how `GEMINI.md`, agents, and skills work.
>
> *Last updated: 2026-05-05 · [Source verified against gemini-cli repository](https://github.com/google-gemini/gemini-cli)*

---

## What Are Extensions?

In [SDLC Productivity](sdlc-productivity.md) you installed the Conductor extension. In [Advanced Patterns](advanced-patterns.md) you installed the agent-skills pack. Both were installed the same way — `gemini extensions install <url>` — because both are **extensions**.

Extensions package multiple capabilities into a single, installable unit:

| Feature | What It Is | Invoked By |
|---|---|---|
| **MCP Servers** | Expose new tools and data sources to the model | Model |
| **Custom Commands** | `/my-cmd` shortcuts for complex prompts or shell commands | User |
| **Context File** (`GEMINI.md`) | Always-on instructions loaded every session | CLI → Model |
| **Agent Skills** | Specialized workflows activated on-demand (TDD, code review, etc.) | Model |
| **Hooks** | Lifecycle interceptors — before/after tool calls, model responses, sessions | CLI |
| **Themes** | Color definitions for CLI UI personalization | User (`/theme`) |
| **Policy Engine** | Safety rules and tool restrictions contributed at tier 2 precedence | CLI |

> **Key insight:** You've already used two extensions. The agent-skills pack from Advanced Patterns is *primarily* a skills extension — it contributes 20 skills and 7 slash commands. Conductor is primarily a commands + MCP server extension. Extensions are flexible containers — they can package any combination of the 7 features above.

### The Manifest: `gemini-extension.json`

Every extension has one. This is the contract between the extension and Gemini CLI:

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

| Field | Purpose |
|---|---|
| `name` | Unique identifier — must match the directory name |
| `contextFileName` | Loads this file into context every session. Defaults to `GEMINI.md` if present |
| `mcpServers` | MCP servers to start — same format as `settings.json`. Use `${extensionPath}` for portability |
| `excludeTools` | Block specific tools or commands (e.g., `rm -rf` via shell) |
| `settings` | User-configurable values — `sensitive: true` stores in system keychain |

### Extension vs. Skill vs. Agent — When to Use What

| | Extension | Skill (`SKILL.md`) | Agent (`.gemini/agents/*.md`) |
|---|---|---|---|
| **Scope** | Shared across users/machines | Local or bundled in an extension | Local project |
| **Installs from** | GitHub, local path | Part of an extension or project | Project directory |
| **Best for** | Distributable toolkits, org standards, MCP integrations | Phase-specific workflows (TDD, security audit) | Specialized personas (reviewer, compliance checker) |
| **Example** | `oh-my-gemini-cli`, `agent-skills`, `conductor` | `subagent-driven-development`, `debugging` | `@pr-reviewer`, `@compliance-checker` |

---

## Discovery & Installation

### Finding Extensions

The [Extension Gallery](https://geminicli.com/extensions/browse/) automatically indexes public extensions. Any GitHub repo with the `gemini-cli-extension` topic appears in the gallery — no submission required.

### Installing

```bash
# Install from GitHub
gemini extensions install https://github.com/owner/repo

# Install a specific version (branch, tag, or commit)
gemini extensions install https://github.com/owner/repo --ref v1.2.0

# Enable auto-updates
gemini extensions install https://github.com/owner/repo --auto-update
```

### Managing Installed Extensions

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

### Google-Managed Extensions

Google maintains an official extension organization at [**gemini-cli-extensions**](https://github.com/gemini-cli-extensions) with 60+ extensions covering security, databases, CI/CD, and Google Cloud services:

| Extension | Focus | What It Adds |
|---|---|---|
| [**security**](https://github.com/gemini-cli-extensions/security) | Security analysis | Full SAST engine, dependency scanning via OSV-Scanner, PoC generation, auto-patching. 90% precision, 93% recall |
| [**conductor**](https://github.com/gemini-cli-extensions/conductor) | Spec-driven development | Structured planning, implementation tracking, and context-driven development |
| [**workspace**](https://github.com/gemini-cli-extensions/workspace) | Google Workspace | Gmail, Drive, Calendar, Sheets integration with agent-optimized JSON output |
| [**cicd**](https://github.com/gemini-cli-extensions/cicd) | CI/CD | Pipeline generation, workflow debugging, and deployment automation |
| [**firebase**](https://github.com/gemini-cli-extensions/firebase) | Firebase | Firebase project management, Firestore queries, and hosting deployment |
| [**bigquery-data-analytics**](https://github.com/gemini-cli-extensions/bigquery-data-analytics) | Data analytics | BigQuery skills for data exploration, query optimization, and analytics |
| [**cloud-sql-***](https://github.com/gemini-cli-extensions) | Databases | Skills for PostgreSQL, MySQL, SQL Server, AlloyDB, OracleDB |
| [**vertex**](https://github.com/gemini-cli-extensions/vertex) | Vertex AI | Prompt management and Vertex AI integration |

Install any of them with:

```text
gemini extensions install https://github.com/gemini-cli-extensions/<name>
```

### Notable Community Extensions

Beyond the official ecosystem, the community has built increasingly sophisticated extensions:

| Extension | Focus | What It Adds |
|---|---|---|
| [**oh-my-gemini-cli**](https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli) | Orchestration | 12 agents, 9 skills, 43 slash commands, lifecycle hooks. Full multi-agent framework with approval gates |
| [**superpowers**](https://github.com/obra/superpowers) | Methodology | 14 skills for TDD, debugging, code review, subagent-driven development. Cross-tool: also works in Cursor and OpenCode |
| [**gws (Google Workspace CLI)**](https://github.com/googleworkspace/cli) | Workspace integration | Dynamic CLI for Gmail, Drive, Calendar, Sheets. Agent-optimized JSON output. Model Armor integration |

---

## Hands-On: Install & Use Community Extensions

You've already installed the **agent-skills** pack (Advanced Patterns) and **Conductor** (SDLC Productivity). Now let's explore what the community has built beyond the official ecosystem.

### Exercise 1: Superpowers — Methodology as Extension

The `superpowers` extension teaches your agent *how to work*, not just what to do. Its flagship feature is **Subagent-Driven Development (SDD)** — a formal methodology for dispatching fresh subagents per task with two-stage review.

```bash
# Install
gemini extensions install https://github.com/obra/superpowers

# Verify — you should see superpowers in the list
/extensions list
```

**Try the plan skill:**

```
Write a plan for adding a "recently viewed products" feature to the ProShop app.
Use the $plan skill.
```

**Try Subagent-Driven Development:**

```
I want to add a "recently viewed" sidebar widget. Use subagent-driven development 
to implement this — dispatch a subagent for each component and review each one.
```

Watch how SDD:
1. Creates a spec for each component (data model, API endpoint, React component)
2. Dispatches a fresh subagent for each — no context bleed between tasks
3. Reviews each subagent's output in two stages: spec compliance, then code quality
4. Reports a summary with all findings

> **Key takeaway:** Compare this to the raw "add a recently viewed sidebar" prompt. SDD produces reviewed, validated code. A raw prompt produces code you have to review manually. This is the difference between a developer and a development *process*.

**Cross-tool portability:** Superpowers also works in Cursor (`.cursor-plugin/`) and OpenCode (`.opencode/`). Same `SKILL.md` files, different plugin manifests. Skills aren't vendor-locked.

---

### Exercise 2: Oh-My-Gemini-CLI — Orchestration as Extension

This extension implements a complete multi-agent workflow with approval gates — the kind of governance enterprise teams need.

```bash
# Install
gemini extensions install https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli
```

**Try the intent-driven workflow:**

```
/omg:intent Add user profile avatars to the ProShop application
```

Notice what happens:
- The agent doesn't immediately start coding. It launches a **Socratic interview** — asking about scope, constraints, and acceptance criteria
- Only after you confirm the scope does the `omg-planner` agent create a structured plan
- The plan is handed off to `omg-executor` for implementation
- After implementation, `omg-reviewer` runs a quality gate check

**Anatomy peek:** This extension uses all 7 extension features simultaneously:

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

> **Key takeaway:** OMG shows what a "batteries-included" extension looks like. The Socratic interview gateway prevents the agent from auto-executing on ambiguous requests — a pattern every enterprise should consider.

---

### Exercise 3: Google Workspace CLI (Optional)

> **Note:** This exercise requires Google Workspace (Gmail, Drive, Calendar). Skip this if your organization doesn't use Workspace.

The `gws` extension gives your agent direct, structured access to Workspace APIs:

```bash
# Install as a Gemini extension
gemini extensions install https://github.com/googleworkspace/cli

# Authenticate (one-time setup)
gws auth setup
```

**Try inbox triage:**

```
Use gws to triage my inbox — show me unread emails grouped by priority
```

**Try a standup report:**

```
Use gws to generate a standup report from my calendar and recent email activity
```

`gws` outputs structured JSON optimized for agent consumption. It also supports `--sanitize` to route API responses through Model Armor templates before the agent processes them.

---

### Exercise 4: Security Extension — Production-Grade SAST

The [Security Extension](https://github.com/gemini-cli-extensions/security) is Google's official security analysis tool for Gemini CLI. Unlike a hand-rolled compliance agent, it ships with a full SAST engine, dependency scanner, and benchmarked results.

```bash
# Install
gemini extensions install https://github.com/gemini-cli-extensions/security
```

**Run a security analysis on your current changes:**

```
/security:analyze
```

The extension runs a structured two-pass analysis:
1. **Reconnaissance pass** — fast scan of all changed files against its vulnerability taxonomy
2. **Investigation pass** — deep-dive into flagged patterns, tracing data flows from source to sink

It checks for hardcoded secrets, injection vulnerabilities (SQLi, XSS, SSRF, SSTI), broken access control, PII exposure, weak crypto, and LLM safety issues.

**Scan dependencies for known CVEs:**

```
/security:scan-deps
```

This uses [OSV-Scanner](https://github.com/google/osv-scanner) against [osv.dev](https://osv.dev) — Google's open-source vulnerability database.

**Customize the scope:**

```
/security:analyze Analyze all source code under the src/ folder. Skip docs and config files.
```

**Key capabilities:**
- **PoC generation** — generate proof-of-concept scripts to validate findings (`poc` skill)
- **Auto-patching** — apply fixes for confirmed vulnerabilities (`security-patcher` skill)
- **Allowlisting** — persist accepted risks in `.gemini_security/vuln_allowlist.txt`
- **CI integration** — ships a ready-to-use [GitHub Actions workflow](https://github.com/gemini-cli-extensions/security/blob/main/.github/workflows/gemini-review.yml) for automated PR security reviews

> **Enterprise value:** This is the same extension referenced in [SDLC Productivity §1.7](sdlc-productivity.md) and [§2.3](sdlc-productivity.md). It replaces the need to build a custom compliance-checker agent — one `gemini extensions install` gives your entire team a production-grade security pipeline.

---

## Building Your Own Extension

### Scaffold from Templates

Gemini CLI provides 7 built-in templates:

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

### Develop Locally with `link`

Use `link` to test changes without reinstalling:

```bash
cd my-extension
npm install
gemini extensions link .
```

Changes are reflected immediately after restarting your Gemini CLI session. No need to reinstall during development.

### Publish to the Gallery

Publishing is automatic — no submission required:

1. **Push to a public GitHub repo** with a valid `gemini-extension.json` at the root
2. **Add the GitHub topic** `gemini-cli-extension` to your repo's About section
3. **Tag a release** (e.g., `v1.0.0`)

The gallery crawler indexes tagged repos daily. Your extension appears automatically after validation.

### Exercise: Build a Mini Extension

Create a simple extension that adds a slash command for your team's code review checklist:

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

Restart Gemini CLI and run `/team:review` — your custom review checklist is now a one-command action.

---

## Extension Patterns for Enterprise

### Org Knowledge Distribution

The highest-value pattern for enterprise teams: **package your organization's knowledge as an extension.**

Instead of onboarding docs that rot in Confluence, ship an extension that teaches the agent your org's patterns:

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

**Benefits:**
- **Versioned:** Update the extension, everyone gets the latest standards on next `gemini extensions update`
- **Distributed:** `gemini extensions install` on day 1 — new hires get your entire institutional knowledge
- **Maintained:** One repo, one PR to update org standards across every developer's agent
- **Consistent:** Every agent on your team follows the same rules, reviews with the same checklist, deploys with the same gates

> **This replaces the "read the wiki" onboarding pattern.** Instead of hoping developers find and read your style guide, the agent enforces it automatically.

### Governance Patterns

Extensions contribute policy rules at **tier 2 precedence** — higher than defaults, lower than user/admin overrides:

```toml
# policies/safety.toml (contributed by your org extension)
[[rule]]
toolName = "run_shell_command"
commandRegex = ".*--force.*"
decision = "deny"
priority = 100
denyMessage = "Force operations are blocked by organization policy."
```

> **Security model:** Extension policies operate at tier 2 precedence. User (tier 4) and admin (tier 5) policies always take precedence. This means an extension can set guardrails, but users and admins can override them when necessary. See [Policy Engine](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md) for full tier details and [Secure Gemini CLI with the Policy Engine](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy) for a practical walkthrough.

**Settings with keychain storage:** Extensions can define settings that are stored in the system keychain:

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

Values marked `sensitive: true` are stored encrypted in the OS keychain and obfuscated in the CLI output.

### Cross-Tool Portability

The `superpowers` extension demonstrates a key enterprise pattern: the same `SKILL.md` files work across Gemini CLI, Cursor, and OpenCode — each with its own plugin manifest format (`gemini-extension.json`, `.cursor-plugin/`, `.opencode/`). This means:

- **Skills aren't vendor-locked** — invest in methodology, not tool-specific configs
- **Teams using different editors** share the same engineering standards
- **Migration is low-risk** — switching tools means writing a new manifest, not rewriting skills

### Internal Registry Patterns

For organizations maintaining a private extension ecosystem:

1. **GitHub Organization** — Create an internal org (e.g., `my-company-gemini-extensions`)
2. **Topic tagging** — Use a private convention (e.g., `internal-gemini-extension`)
3. **Version pinning** — Install with `--ref` tags for production stability:
   ```bash
   gemini extensions install https://github.internal.com/org/my-ext --ref v2.1.0
   ```
4. **Auto-updates** — Use `--auto-update` for extensions where latest-is-best (style guides)
5. **Workspace scoping** — Disable org extensions for specific projects:
   ```bash
   gemini extensions disable org-standards --scope workspace
   ```

---

## Summary

| Concept | Key Takeaway |
|---|---|
| **What extensions package** | 7 features: MCP servers, commands, context, skills, hooks, themes, policies |
| **Google-managed** | 60+ extensions at [gemini-cli-extensions](https://github.com/gemini-cli-extensions) — security, databases, CI/CD, Workspace |
| **Installation** | `gemini extensions install <url>` — one command |
| **Gallery** | Auto-indexed via `gemini-cli-extension` GitHub topic |
| **Building** | `gemini extensions new` from 7 templates, `link` for local dev |
| **Enterprise value** | Package org knowledge, enforce standards, distribute via install command |
| **Security** | Official Security Extension with SAST + dep scanning. Extension policies at tier 2. Secrets in keychain |
| **Portability** | Skills work across Gemini CLI, Cursor, and OpenCode |

---

## Next Step

→ Return to **[Use Case 1: SDLC Productivity](sdlc-productivity.md)** — Part 2 covers Outer Loop agents (ADRs, onboarding, dependency auditing)

→ Continue to **[Advanced Patterns](advanced-patterns.md)** — prompting craft, context engineering, and agent-skills installation
