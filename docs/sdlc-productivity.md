# Use Case 1: SDLC Productivity Enhancement

> **Duration:** ~60 minutes  
> **Goal:** Build an enterprise-grade developer workflow from first install through context engineering, spec-driven development with Conductor, and governance guardrails.  
> **Exercise PRD:** [Product Wishlist Feature](../exercises/prd_sdlc_productivity.md)

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

```
~/.gemini/GEMINI.md          → Global preferences (all projects)
./GEMINI.md                  → Project-level conventions
./backend/GEMINI.md          → Backend-specific rules
./frontend/GEMINI.md         → Frontend-specific rules
```

> **JIT context discovery:** The agent only loads the GEMINI.md files relevant to the files it's currently working on. If it's editing `backend/controllers/productController.js`, it loads the project GEMINI.md AND the backend GEMINI.md — but not the frontend one.

### Examine the Project GEMINI.md

```bash
cat GEMINI.md
```

This file (copied from `samples/gemini-md/project-gemini.md` during setup) defines:
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

## Next Step

→ Continue to **[Use Case 2: Legacy Code Modernization](legacy-modernization.md)**
