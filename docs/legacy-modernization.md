# Use Case 2: Legacy Code Modernization

> **Duration:** ~60 minutes  
> **Goal:** Migrate a legacy application using Plan Mode, custom subagents, skills, and checkpointing. Learn to decompose massive codebases safely.  
> **Exercise PRDs:** [.NET Modernization](../exercises/prd_dotnet_modernization.md) · [Java Upgrade](../exercises/prd_java_upgrade.md)

---

## 2.1 — Plan Mode: Safe Research (15 min)

### Enter Plan Mode

Plan Mode is read-only research. The agent analyzes your codebase, proposes changes, but **doesn't modify anything** until you approve.

```
/plan
```

> The prompt indicator changes to show you're in Plan Mode. The agent loses access to write tools — it can only read files, search the web, and think.

### Analyze the Codebase

```
Analyze this codebase for a migration to a modern architecture. 
Identify:
1. Key dependencies and their versions
2. Architectural patterns currently in use
3. Areas of technical debt
4. Migration risks and complexity hotspots
```

> **What's happening:** The agent reads the entire project — package.json, source files, configuration — and builds a mental model. It can hold your full architecture in context: every dependency, every pattern, every anti-pattern — simultaneously.

### Review the Plan

The agent produces a structured migration plan. Review it carefully:

```
Propose a step-by-step plan to modernize the authentication system 
from session-based to JWT with refresh tokens. Include:
- Files that need to change
- Order of operations
- Risk assessment for each step
- Rollback strategy
```

### Collaborative Plan Editing

Open the multi-line editor to refine the plan:

```
Ctrl+X
```

This opens your `$EDITOR` (or a built-in editor) where you can modify the plan directly. The agent sees your edits and adjusts its approach.

### Exit Plan Mode

```
/plan
```

Toggle back to normal mode. Now the agent can execute the approved plan.

---

## 2.2 — Model Routing and Steering (10 min)

### Automatic Model Routing

Gemini CLI automatically routes between models based on task complexity:

| Task Type | Model Used | Why |
|---|---|---|
| Planning, architecture analysis | **Gemini Pro** | Complex reasoning, long-form analysis |
| Code generation, file edits | **Gemini Flash** | Fast execution, lower cost |
| Simple queries, status checks | **Gemini Flash** | Speed-optimized |

> You don't configure this — it happens automatically. The agent picks the right model for each step.

### Model Steering 🔬

During execution, you can steer the agent mid-stream:

```
# While the agent is working on a migration step:
Actually, skip the database migration for now. Focus on the API 
layer first — we need the endpoints working before we touch the schema.
```

> **Model steering** lets you course-correct without starting over. The agent adjusts its plan based on your input and continues from the new direction.

### Check Which Model Is Active

```
/stats
```

Shows the current model, token usage, and caching status.

---

## 2.3 — Context Engineering for Migrations (10 min)

### Setting Up Migration Standards

Create a GEMINI.md that encodes your target architecture:

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

### The @ Import Syntax

For large projects, split GEMINI.md into modular files:

```markdown
# GEMINI.md
@import ./docs/architecture.md
@import ./docs/coding-standards.md
@import ./docs/migration-checklist.md
```

> **Why imports matter:** A single GEMINI.md can get unwieldy for enterprise projects. Imports let you organize context into focused documents that are easier to maintain and review.

### Memory for Migration Patterns

As the agent discovers patterns during migration, it saves them:

```
/memory show
```

You can also explicitly teach it:

```
/memory add "When migrating Entity Framework 6 to EF Core, always 
check for .edmx files and replace them with code-first models. 
The database-first approach is deprecated in EF Core."
```

---

## 2.4 — Subagents: Delegating Specialized Work (15 min)

### Built-in Subagents

Gemini CLI includes built-in subagents for common tasks:

```
@codebase_investigator Map the relationships between all controllers 
in the backend/ directory. Show which models each controller depends 
on and which routes call each controller.
```

> **@codebase_investigator** is a read-only agent that maps code relationships, traces call chains, and identifies architectural patterns. It never modifies files.

### Custom Subagents

Create a security scanner for your migration:

```bash
cat .gemini/agents/security-scanner.md
```

The security scanner subagent (from `samples/agents/security-scanner.md`):
- Has a focused system prompt for security analysis
- Can be restricted to specific tools
- Uses a specific model (you can assign Flash for speed or Pro for depth)

### Using Custom Subagents

```
@security-scanner Review the authentication middleware for OWASP 
Top 10 vulnerabilities. Check for:
1. Injection attacks (SQL, NoSQL)
2. Broken authentication
3. Sensitive data exposure
4. Missing rate limiting
```

### Subagent Tool Isolation

Each subagent can have its own tool allowlist:

```markdown
# .gemini/agents/security-scanner.md
---
model: gemini-2.5-flash
tools:
  - read_file
  - list_directory
  - web_search
# No write_file, no run_shell_command — this agent is read-only
---

You are a security analyst. Your job is to find vulnerabilities...
```

> **Enterprise value:** The security scanner can read code and search for CVEs, but it can never modify files or run commands. Tool isolation is defense-in-depth.

---

## 2.5 — Skills: Reusable Expertise (5 min)

### View Available Skills

```
/skills list
```

Skills are reusable instruction sets that the agent activates when relevant:

### How Skills Work

1. **Auto-activation:** The agent reads skill descriptions and activates relevant ones based on your prompt
2. **Manual activation:** You can force a skill with its name
3. **Persistence:** Skills survive across sessions — learn once, use everywhere

### Auto Memory 🔬

Auto Memory extracts skills from your sessions automatically:

```
/memory show
```

> After completing a migration, the agent might auto-save: "When migrating Express.js middleware, check for `req.query` vs `req.params` mismatches — the old API used query strings, the new one uses path parameters."

---

## 2.6 — Checkpointing and Git Worktrees (5 min)

### Checkpointing

Before risky changes, save a checkpoint:

```
/checkpoint
```

This saves the current state of all modified files. If something goes wrong:

```
/restore
```

> **Checkpoints are lightweight** — they track file changes, not full git history. Use them freely before any multi-file refactor.

### Git Worktrees 🔬

For parallel migration work, use Git worktrees:

```
# Create a worktree for the auth migration
git worktree add ../proshop-auth-migration feature/auth-migration
cd ../proshop-auth-migration
gemini
```

> **Why worktrees?** You can have the original code in one terminal and the migrated code in another. Run tests on both simultaneously. Compare approaches without branch switching.

---

## Hands-On Exercise

Open the **.NET Modernization PRD** or **Java Upgrade PRD** and work through a migration:

1. Enter **Plan Mode** → analyze the target codebase
2. Create a **GEMINI.md** with migration standards
3. Use **Conductor** to create a phased migration plan
4. Use **@codebase_investigator** to map dependencies
5. Create a **checkpoint** before starting
6. Begin the migration — use **model steering** to course-correct as needed
7. After each phase, check with **@security-scanner**
8. Review what **Auto Memory** learned from the session

---

## Summary: What You Learned

| Feature | What It Does |
|---|---|
| **Plan Mode** | Read-only research — analyze before modifying |
| **Model routing** | Automatic Pro (planning) → Flash (coding) selection |
| **Model steering** | Course-correct the agent mid-stream |
| **@ import syntax** | Modular GEMINI.md for large projects |
| **@codebase_investigator** | Read-only codebase analysis subagent |
| **Custom subagents** | Specialized agents with tool isolation |
| **Skills** | Reusable instruction sets that auto-activate |
| **Auto Memory** | Agent learns patterns from sessions |
| **Checkpointing** | Save/restore state before risky changes |
| **Git Worktrees** | Parallel branches for simultaneous work |

---

## Next Step

→ Continue to **[Use Case 3: Agentic DevOps Orchestration](devops-orchestration.md)**

→ For power users: **[Advanced Patterns](advanced-patterns.md)** — prompting craft, verification loops, and parallel development
