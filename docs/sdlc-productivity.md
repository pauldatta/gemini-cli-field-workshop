# Use Case 1: SDLC Productivity Enhancement

> **Duration:** ~60 minutes  
> **Goal:** Build an enterprise-grade developer workflow from first install through context engineering, spec-driven development with Conductor, and governance guardrails.  
> **Exercise PRD:** [Product Wishlist Feature](https://github.com/pauldatta/gemini-cli-field-workshop/blob/main/exercises/prd_sdlc_productivity.md)

---

## 1.1 — First Contact (10 min)

### Install Gemini CLI

```bash
npm install -g @google/gemini-cli
```

### Launch and Authenticate

```bash
cd demo-app
gemini
# Follow the OAuth flow in your browser
```

### Your First Prompt

Start with something that proves the agent can read your codebase:

```
What is the tech stack of this project? List the main frameworks, 
database, and authentication mechanism.
```

> **What's happening:** The agent reads `package.json`, scans the directory structure, and maps the architecture. Unlike tools limited to open files, Gemini CLI can hold your entire codebase in a single session — it understands how your controllers, routes, models, and middleware connect.

### Explore the Tools

```
/tools
```

This shows every tool the agent can use: file operations, shell commands, web search, and any MCP servers you've configured.

### Key Shortcuts

| Shortcut | Action |
|---|---|
| `Tab` | Accept a suggested edit |
| `Shift+Tab` | Cycle through edit options |
| `Ctrl+X` | Open multi-line editor |
| `Ctrl+C` | Cancel current operation |
| `/stats` | Show token usage for this session |
| `/clear` | Clear context and start fresh |

---

## 1.2 — Context Engineering with GEMINI.md (15 min)

### The Context Hierarchy

Gemini CLI reads `GEMINI.md` files at multiple levels, each adding more specific context:

![GEMINI.md Context Hierarchy](assets/context-hierarchy.png)

> **JIT context discovery:** The agent only loads the GEMINI.md files relevant to the files it's currently working on. If it's editing `backend/controllers/productController.js`, it loads the project GEMINI.md AND the backend GEMINI.md — but not the frontend one.

### Examine the Project GEMINI.md

```bash
cat GEMINI.md
```

This file (copied from [`samples/gemini-md/project-gemini.md`](../samples/gemini-md/project-gemini.md) during setup) defines:
- Architecture rules (routes → controllers → models)
- Anti-patterns (no callbacks, no hardcoded credentials)
- Testing standards

### Test Context Enforcement

Ask the agent to violate a rule and see if it self-corrects:

```
Add a new GET endpoint to fetch featured products. 
Put the database query logic directly in the route file.
```

> **Expected:** The agent should recognize this violates the GEMINI.md rule ("No business logic in route files") and instead create the endpoint in a controller, with a thin route that delegates.

### Add Backend Context

```bash
cat backend/GEMINI.md
```

This adds backend-specific rules about error handling, async patterns, and security.

### Memory: Persistent Knowledge

The agent can remember things across sessions:

```
/memory show
```

Add project-specific knowledge:

```
/memory add "The ProShop app uses port 5000 for the backend API 
and port 3000 for the React dev server. MongoDB runs on default 
port 27017. Test database is 'proshop_test'."
```

The agent can also save memories itself using the `save_memory` tool when it discovers important patterns during a session.

### The .geminiignore File

Control what the agent can and cannot see:

```bash
cat .geminiignore
# node_modules/
# .env
# *.log
# coverage/
```

> **Why this matters:** Without `.geminiignore`, the agent might waste context tokens reading `node_modules/` (hundreds of thousands of files). With it, the agent focuses only on your source code.

---

## 1.3 — Conductor: Context-First Builds (15 min)

### Why Conductor?

Plan Mode is great for one-off features. But for multi-day projects where you need persistent specs, phased implementation plans, and progress tracking across sessions — that's Conductor.

### Install Conductor

```bash
gemini extensions install https://github.com/gemini-cli-extensions/conductor
```

Verify:

```
/extensions list
```

### Set Up Project Context

```
/conductor:setup prompt="This is a MERN stack eCommerce app (ProShop). 
Express.js backend with MongoDB. React frontend with Redux Toolkit. 
Use clean architecture: routes register middleware and delegate to 
controllers. Controllers handle business logic. Models define schema. 
No business logic in route files."
```

### Examine What Conductor Created

```bash
ls conductor/
# product.md  tech-stack.md  tracks/

cat conductor/product.md
cat conductor/tech-stack.md
```

> **Key insight:** These files are now the source of truth for your project. They're Markdown, they live in your repo, they get committed and reviewed like any other code. When you come back tomorrow — or hand this project to a colleague — the AI picks up exactly where you left off. The state is in the files, not in memory.

### Create a Feature Track

Use the wishlist PRD as the feature spec:

```
/conductor:newTrack prompt="Add a product wishlist feature. Users can 
add products to a personal wishlist from the product detail page. 
The wishlist is stored in MongoDB as an array of product references 
on the User model. Show a wishlist page with the ability to remove 
items or move them to the cart."
```

### Review the Generated Artifacts

```bash
# The specification
cat conductor/tracks/*/spec.md

# The implementation plan
cat conductor/tracks/*/plan.md
```

> **Look at the plan.** It's broken into phases with specific tasks and checkboxes. Phase 1: database schema. Phase 2: API endpoints. Phase 3: frontend components. Phase 4: tests. The agent follows this plan in order, checking off tasks as it goes.

> **If you disagree with the approach** — say you want GraphQL instead of REST — edit `plan.md` directly and rerun. The plan is the contract between you and the agent.

### Implement (if time allows)

```
/conductor:implement
```

> **Full-codebase awareness:** Right now, the agent is holding your `GEMINI.md` rules, the Conductor product docs, the specification, the implementation plan, AND the full ProShop codebase — all in context simultaneously. No file-splitting, no manual context management. The agent sees how every piece connects.

### Check Status

```
What's the current status on all active Conductor tracks?
```

---

## 1.4 — Extensions and MCP Servers (10 min)

### Extensions Overview

Extensions package skills, subagents, hooks, policies, and MCP servers into installable units:

```
/extensions list
```

### MCP Servers: Connecting External Tools

MCP (Model Context Protocol) connects Gemini CLI to external data sources and tools:

```bash
# Check your MCP configuration
cat .gemini/settings.json
```

The settings.json includes a GitHub MCP server. When configured with a `GITHUB_TOKEN`, the agent can:
- Read repositories, issues, and PRs
- Create issues and comments
- Open pull requests

### Try a Connected Prompt

```
List the open issues in this repository using the GitHub MCP server.
```

### MCP Tool Isolation for Subagents

You can restrict which MCP tools a subagent can access:

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

> **Enterprise value:** A `db-analyst` subagent gets read-only BigQuery access. It can query and list tables, but can never delete data. Tool isolation is governance at the agent level.

---

## 1.5 — Governance and Policy Engine (10 min)

### The Policy Engine

Policies are guardrails-as-code written in TOML:

```bash
cat .gemini/policies/team-guardrails.toml
```

### Policy Rules in Action

The sample policy:
- **Denies** reading `.env`, `.ssh`, and credential files
- **Denies** destructive shell commands (`rm -rf`, `curl`)
- **Allows** the implementer agent to run `npm test` and `npm run lint`
- **Defaults** everything else to `ask_user` (human approval required)

### Test the Policy

```
Read the contents of the .env file in this project.
```

> **Expected:** The agent should be blocked by the policy engine. You'll see a denial message explaining why.

### The 5-Tier Policy System

Policies cascade in priority order:

```
Default → Extension → Workspace → User → Admin (highest)
```

An admin policy (set at the system level) overrides everything else. This is how enterprises enforce organization-wide guardrails.

### Hooks in Action

The hooks configured in `settings.json` are already active:

1. **SessionStart → session-context**: Injected your branch name and dirty file count at the start of this session
2. **BeforeTool → secret-scanner**: Watching every file write for hardcoded credentials
3. **BeforeTool → git-context**: Injecting recent git history before file modifications
4. **AfterTool → test-nudge**: Reminding the agent to consider running tests

Check hook status:

```
/hooks panel
```

> **Design philosophy:** These hooks are lightweight context injectors and model steerers — not heavy test runners. They add <200ms total latency and improve the agent's decision quality without burdening the system.

### Enterprise Configuration

For organization-wide settings, admins can configure:

```json
{
  "tools": {
    "allowed": ["read_file", "write_file", "run_shell_command"],
    "blocked": ["web_fetch"]
  },
  "auth": {
    "required": true,
    "provider": "vertex-ai"
  }
}
```

### Sandboxing

Gemini CLI supports sandboxed execution:
- **Docker sandbox**: Runs shell commands in an isolated container
- **macOS seatbelt**: Uses macOS sandboxing to restrict file system access

```
# Check current sandbox mode
/sandbox status
```

---

## 1.6 — Session Management (5 min)

### Resume Previous Sessions

```
/resume
```

Lists recent sessions. Select one to continue where you left off.

### Rewind to a Previous State

```
/rewind
```

Shows a timeline of changes in the current session. Select a point to roll back to.

### Custom Commands

```
/commands
```

Shows available custom commands. You can define your own in `.gemini/commands/`.

---

## Summary: What You Learned

| Feature | What It Does |
|---|---|
| **GEMINI.md hierarchy** | Encodes project conventions at every level — agent follows them automatically |
| **JIT context discovery** | Only loads relevant context files for the current task |
| **Memory** | Persists knowledge across sessions |
| **Conductor** | Spec-driven development with persistent plans and progress tracking |
| **Extensions** | Installable packages of skills, agents, hooks, and policies |
| **MCP servers** | Connects to external tools (GitHub, BigQuery, Jira) |
| **Policy engine** | Guardrails-as-code in TOML — deny, allow, or ask_user |
| **Hooks** | Lightweight context injection and model steering at agent lifecycle events |
| **Sandboxing** | Isolated execution for untrusted environments |

---

## 1.7 — Custom Agents for the Full SDLC (20 min)

> **For power users and returning participants.** This section goes beyond code generation to cover the **full software development lifecycle** — reviews, documentation, compliance, and release management. Each agent can be used independently. Jump in at any point.

### Built-in Agents

Gemini CLI ships with default agents you can use immediately. List them with:

```
/agents
```

| Agent | Purpose | When to Use |
|---|---|---|
| **`generalist`** | Full-tool-access general agent | High-volume or turn-intensive tasks |
| **`codebase_investigator`** | Architecture mapping & dependency analysis | "Map how auth flows through this app" |
| **`cli_help`** | Gemini CLI documentation expert | "How do I configure MCP tool isolation?" |

Use the `@agent` syntax to delegate explicitly:

```
@codebase_investigator Map the complete data flow from the React 
product page through Redux, to the Express API, to the MongoDB model.
```

> **Why this matters:** The investigator operates in read-only mode with focused context. It won't accidentally modify files while mapping your architecture. The main agent then uses that map to plan implementation.

---

### Building Custom Agents

Custom agents are Markdown files with YAML frontmatter, dropped into `.gemini/agents/`. Each agent gets:

- A **name** you invoke with `@agent-name`
- A **description** the CLI uses for auto-routing
- A **tool allowlist** that controls what the agent can access
- A **system prompt** that defines its expertise and output format

> **Key design principle:** Separate thinkers from doers. Read-only agents for research and review. Write-access agents for implementation. Never mix investigation and mutation in the same context.

The examples below show that Gemini CLI isn't just a code generator — it's a **full SDLC platform** covering reviews, documentation, compliance, and release management.

---

### Agent 1: The PR Reviewer

A read-only agent that reviews code changes for quality, bugs, and style violations.

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

**Try it:**

```
@pr-reviewer Review all files changed in the last commit
```

> **Automate it in CI/CD:** For automated PR reviews on every pull request, use the official [`google-github-actions/run-gemini-cli`](https://github.com/google-github-actions/run-gemini-cli) GitHub Action. Install it from the CLI with `/setup-github` — it configures the workflow files, dispatch handler, and issue triage automatically. See [`samples/cicd/gemini-pr-review.yml`](../samples/cicd/gemini-pr-review.yml) for a working example.

---

### Agent 2: The Doc Writer

Generates API documentation, READMEs, and code comments from source code. Read-only — it can never modify your files.

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

**Try it:**

```
@doc-writer Generate API documentation for all endpoints in backend/routes/
```

> **Outer loop value:** This replaces hours of manual documentation work. Run it after each sprint to keep docs current.

---

### Agent 3: The Compliance Checker

Audits code for license headers, PII exposure, hardcoded secrets, and policy violations.

```bash
cp samples/agents/compliance-checker.md .gemini/agents/
```

```markdown
<!-- .gemini/agents/compliance-checker.md -->
---
name: compliance-checker
description: Audit code for compliance, PII exposure, and policy violations.
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - glob
  - grep_search
---

You are a compliance auditor. Scan for:
1. License headers — every source file needs one
2. PII exposure — emails, phone numbers, SSNs in code or logs
3. Hardcoded secrets — API keys, passwords, tokens
4. Logging hygiene — no user data in log statements

Report as: Category / Severity / File:Line / Finding / Remediation.
If clean, state "✅ PASS: [category]".
```

**Try it:**

```
@compliance-checker Audit the entire backend/ directory
```

> **Enterprise value:** Samsung's evaluation specifically tests "content filtering and centralized audit." This agent demonstrates that capability directly.

---

### Agent 4: The Release Notes Drafter

Reads git history and changed files to produce structured, stakeholder-friendly release notes.

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

**Try it:**

```
@release-notes-drafter Write release notes for the last 10 commits
```

> **Outer loop value:** Release notes are one of the most dreaded SDLC tasks. This agent reads git history AND the actual code changes to produce notes that make sense to product managers.

---

### Combining Agents: The Full Pipeline

The real power is combining agents into a workflow. Each agent gets **fresh, focused context** — no one agent accumulates the full conversation history:

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

> **Why this works:** Each step starts with clean context focused on its specific job. The investigator doesn't carry implementation details. The reviewer doesn't carry investigation noise. This is the principle behind every high-performance AI workflow.

---

### Going Deeper

For additional advanced techniques — prompting discipline, verification loops, context engineering, and parallel development — see the **[Advanced Patterns](advanced-patterns.md)** page:

- [Prompting Craft: Goals vs. Instructions](advanced-patterns.md#prompting-craft-goals-vs-instructions)
- [Context Discipline](advanced-patterns.md#context-discipline)
- [Verification Loops](advanced-patterns.md#verification-loops)
- [Parallel Development with Worktrees](advanced-patterns.md#parallel-development-with-worktrees)
- [Multi-Agent Orchestration](advanced-patterns.md#multi-agent-orchestration)

---

## Summary: What You Learned

| Feature | What It Does |
|---|---|
| **GEMINI.md hierarchy** | Encodes project conventions at every level — agent follows them automatically |
| **JIT context discovery** | Only loads relevant context files for the current task |
| **Memory** | Persists knowledge across sessions |
| **Conductor** | Spec-driven development with persistent plans and progress tracking |
| **Extensions** | Installable packages of skills, agents, hooks, and policies |
| **MCP servers** | Connects to external tools (GitHub, BigQuery, Jira) |
| **Policy engine** | Guardrails-as-code in TOML — deny, allow, or ask_user |
| **Hooks** | Lightweight context injection and model steering at agent lifecycle events |
| **Sandboxing** | Isolated execution for untrusted environments |
| **Custom agents** | Specialized agents for reviews, docs, compliance, release notes — not just coding |
| **Built-in agents** | `generalist`, `codebase_investigator`, `cli_help` — delegation without setup |

---

## Next Step

→ Continue to **[Use Case 2: Legacy Code Modernization](legacy-modernization.md)**

→ For power users: **[Advanced Patterns](advanced-patterns.md)** — prompting craft, verification loops, context engineering, and parallel development
