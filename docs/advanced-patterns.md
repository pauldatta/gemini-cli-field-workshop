# Advanced Patterns

> **Duration:** ~45 minutes (self-paced)  
> **Goal:** Master prompting discipline, verification loops, context engineering, and parallel development. These techniques work with any Gemini CLI workflow.  
> **Prerequisites:** Complete at least [Use Case 1: SDLC Productivity](sdlc-productivity.md) or be familiar with the basics.
>
> *Last updated: 2026-05-05 · [Source verified against gemini-cli repository](https://github.com/google-gemini/gemini-cli)*

---

## Prompting Craft: Goals vs. Instructions

The single biggest improvement you can make to AI output quality is changing **how you ask**.

### The Problem

Most developers give step-by-step instructions:

```
Create a wishlist model with userId and productId fields.
Then create a controller with addToWishlist and getWishlist functions.
Then add routes at /api/wishlist.
Then create a Redux slice.
Then create the WishlistScreen component.
```

This forces the agent down a specific path — even if a better approach exists. The agent can't push back, surface tradeoffs, or adapt.

### The Fix: Declarative Goals with Success Criteria

```
Add a product wishlist feature. When you're done:
1. A logged-in user can add/remove products from their wishlist
2. The wishlist persists across sessions (stored in MongoDB)
3. There's a /wishlist page accessible from the navbar
4. All existing tests still pass (npm test)
5. The code follows the conventions in GEMINI.md

Say "WISHLIST_COMPLETE" when all criteria are verified.
```

### Why This Works

| Imperative (❌) | Declarative (✅) |
|---|---|
| Prescribes implementation details | Describes the desired outcome |
| Agent can't push back or suggest alternatives | Agent chooses the best approach for the codebase |
| No verification — you have to check manually | Built-in verification loop via success criteria |
| One rigid path | Agent adapts to what it discovers |

> **Key insight:** "Don't tell it what to do — give it success criteria and watch it go." The agent is exceptionally good at looping until it meets specific goals. Weak criteria ("make it work") require constant hand-holding. Strong criteria let it run independently.

### Exercise

Try both approaches on the same task with ProShop. Compare:
1. How many turns did each take?
2. Did the declarative version find a better approach?
3. Which produced cleaner code?

---

## Context Discipline

Every token in the agent's context window makes the next response slightly less focused. Context is a budget — manage it like memory on a constrained device.

### Symptoms of Context Overload

- Agent starts repeating itself
- Hallucinations increase (referencing files that don't exist)
- Output quality drops noticeably after 15-20 turns
- Agent "forgets" earlier instructions

### The Toolkit

#### 1. Strategic Resets

When output quality degrades:

```
/clear
```

This resets conversational context while keeping GEMINI.md, memory, and file state intact. The agent restarts fresh but with all your project knowledge.

#### 2. Save Before You Clear

```
/memory add "The ProShop codebase uses a repository pattern for 
data access. All MongoDB queries go through model methods, never 
directly in controllers. Express middleware chain: cors → 
cookieParser → authMiddleware → routes."
```

Memory persists across sessions and `/clear` resets. Save important discoveries before clearing.

#### 3. Context Offloading

Move large specs out of the conversation and into files:

```bash
# Instead of pasting a long spec into chat:
echo "Your detailed spec..." > feature-spec.md

# Then reference it in your prompt with @:
# "Read @./feature-spec.md and implement it"
```

Or add it as an import in your GEMINI.md for persistent context:

```markdown
# GEMINI.md
@./feature-spec.md
```

> See [GEMINI.md reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md) for import syntax.

#### 4. Isolation via Agent Delegation

Each custom agent gets its own context window. Use this strategically:

```
# Bad: one agent doing everything (context bloat)
"Research the auth system, then refactor it, then write tests, then review"

# Good: isolated phases (each gets clean context)
@codebase_investigator Map the auth system
Now refactor based on the investigator's findings
@pr-reviewer Review the refactored auth code
```

### Exercise

1. Start a session and build three features sequentially (deliberately accumulate context)
2. Notice quality drop around turns 15-20
3. Run `/memory add` to save key facts
4. Run `/clear` — observe immediate quality improvement
5. Ask the agent to continue from where it left off — it picks up via memory + file state

---

## Verification Loops

The most reliable way to get correct code from an agent is to give it a **feedback loop** — a way to check its own work and fix mistakes automatically.

### The Pattern

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

### Why Completion Promises Work

The phrase "say X when done" gives the agent:

1. **A clear stopping point** — it knows when to stop working
2. **Self-verification incentive** — it checks its work before declaring done
3. **Iterative recovery** — if tests fail, it fixes and re-runs rather than asking you

### Automating the Loop

For large tasks, you can automate the feedback loop using hooks. An `AfterAgent` hook checks whether the completion promise appeared in the output. If not, it resets the conversation (keeping file changes) and re-runs with the original prompt + improved codebase:

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

> **Safety:** Always configure tool restrictions when running autonomous loops. Block destructive operations (`git push --force`, `rm -rf`) in your `settings.json` or `policy.toml`.

### Exercise

Give the agent a refactoring task with explicit success criteria and a completion promise. Watch it iterate through test failures until it reaches green.

---

## Parallel Development with Worktrees

Run multiple Gemini CLI sessions simultaneously on different branches — each in complete isolation.

### The Problem

You can only have one branch checked out at a time. If you want to work on a feature, a bugfix, and a refactor simultaneously with separate agents, they'll collide.

### The Solution

```bash
# Terminal 1: Feature work
gemini --worktree feature-wishlist

# Terminal 2: Bug fix
gemini --worktree fix-cart-rounding

# Terminal 3: Documentation
gemini --worktree update-api-docs
```

Each agent works in its own directory, on its own branch, with its own context. No conflicts.

### The Workflow

| Phase | Action |
|---|---|
| **Isolate** | Create a worktree per task/agent |
| **Configure** | Each worktree gets its own dev server port to avoid conflicts |
| **Execute** | Launch separate Gemini CLI sessions — each agent works independently |
| **Review** | Each agent commits to its branch within its worktree |
| **Integrate** | Merge branches back to `main` via PRs |
| **Cleanup** | `git worktree remove <path>` + `git worktree prune` |

> **Treat worktrees as disposable.** They're optimized for the duration of a single task. Remove them after merge.

### Exercise

Open two terminal windows. Use worktrees to:
1. Add a wishlist feature in one
2. Fix the cart total calculation in the other

Both agents work simultaneously. Neither sees the other's changes. Merge both via PRs.

---

## Multi-Agent Orchestration

For teams managing dozens of agents across projects, orchestration tools provide enterprise-grade isolation, observability, and scaling.

### Scion (Google Cloud Platform)

**[Scion](https://github.com/GoogleCloudPlatform/scion)** is an experimental multi-agent orchestrator that runs agents as isolated, concurrent processes — each in its own container.

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

| Concept | Description |
|---|---|
| **Agent** | A containerized process running Gemini CLI |
| **Grove** | A project namespace — typically 1:1 with a git repo |
| **Template** | An agent blueprint: system prompt + skills + tool permissions |
| **Runtime** | Docker, Podman, Apple Container, or Kubernetes |

> **When to use Scion:** Teams with 5+ concurrent agent tasks, projects requiring strict isolation between agents, or organizations scaling AI-managed development across multiple repositories.

---

## Engineering Constitution Pattern

If you have to tell the agent the same thing twice, it should be in a file.

### What Goes in a Constitution

A well-crafted `GEMINI.md` encodes your team's engineering standards so the agent follows them automatically:

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

### Exercise

1. Write a GEMINI.md with 5 rules for ProShop
2. Ask the agent to add a feature **without** the file — note the output
3. Ask the same thing **with** the file
4. Compare: Did the agent follow conventions? Did it ask clarifying questions it skipped before?

---

## Deterministic Enforcement

While an Engineering Constitution (`GEMINI.md`) is excellent for *guiding* an agent (Prompt Engineering), it cannot guarantee 100% compliance. Agents, like humans, can make mistakes or hallucinate incorrect patterns during a complex refactor (a phenomenon known as *Prompt Drift*).

To build a robust SDLC, you must pair AI generation with **Guardrails**—deterministic boundaries that restrict what an AI can see, do, and generate.

### Input vs. Output Guardrails

In an enterprise SDLC, guardrails fall into two categories:

1. **Input Guardrails (Pre-generation):** Protecting the agent from malicious inputs or restricting its context.
   - *Example:* The `.geminiignore` file prevents the agent from reading unnecessary files.
   - *Example:* `GEMINI.md` sets the architectural expectations upfront.
2. **Output Guardrails (Post-generation):** Verifying the agent's output *after* generation but *before* it is merged or deployed.
   - *Example:* Enforcing architectural boundaries using deterministic linters.
   - *Example:* Running a test suite or a scanner to detect leaked secrets.

### The Synergy: "AI Proposes, CI Disposes"

Instead of relying solely on the LLM to self-police its architecture, rely on traditional software engineering tools (Output Guardrails) to enforce the rules:

1. **The Guide (`GEMINI.md`):** Tells the agent *how* to write the code correctly the first time (Input).
2. **The Guard (Linters/Static Analysis):** Catches the agent deterministically if it makes a mistake (Output).
3. **The Loop:** If a guard tool fails, the error output is fed back to the agent (via a continuous verification loop using [Gemini CLI Hooks](https://geminicli.com/docs/hooks/)), and the agent automatically fixes its own mistake based on the hard feedback.

### Enforcement in Practice

Any deterministic tool that can exit with a non-zero code can serve as an enforcer. You can configure these tools to run in your CI/CD pipeline, as a Git `pre-commit` hook, or directly via Gemini CLI's `AfterAgent` hook.

**Examples of Deterministic Enforcers:**
- **Standard Linters:** ESLint or Ruff to enforce code complexity limits (e.g., `max-lines-per-function` in route files).
- **Security Scanners:** Tools like `gitleaks` to ensure the agent didn't accidentally hardcode an API key.
- **Architecture Linters:** Tools that parse the dependency graph to enforce layer boundaries.

#### Example: Enforcing Boundaries with `dependency-cruiser`

If your `GEMINI.md` rule states "No business logic in route files", you can enforce this in a JavaScript project using [dependency-cruiser](https://github.com/sverweij/dependency-cruiser). 

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

To automate this within the agent's workflow, you must format the linter's output as JSON so the Gemini CLI can understand it. First, create a hook script that runs the linter and captures errors:

```bash
#!/bin/bash
# .gemini/hooks/check-architecture.sh
output=$(npx depcruise src --config .dependency-cruiser.js 2>&1)
if [ $? -ne 0 ]; then
  # Inject the linter error directly into the agent's context
  jq -n --arg msg "$output" '{systemMessage: ("Architecture Violation Detected:\n" + $msg)}'
else
  echo '{}'
fi
```

Then, register this script as an `AfterAgent` hook in your settings:

```json
// .gemini/settings.json
{
  "hooks": {
    "AfterAgent": [
      {
        "name": "architecture-guard",
        "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/check-architecture.sh"
      }
    ]
  }
}
```

Now, if the agent creates an illegal import, the hook immediately feeds the linter error back into the conversation, forcing the agent to resolve the violation.

### Exercise
1. In a project, create a route file that imports a database model directly.
2. Configure a deterministic enforcer (like `dependency-cruiser` or a custom ESLint rule) to block this pattern.
3. Ask the agent to "Add a new endpoint to the route" and observe if it copies the bad pattern or fixes it.
4. Run the enforcer, feed the error back to the agent, and ask it to resolve the violation.

---

## Skills-Based Development

Skills are structured, reusable instruction files (`SKILL.md`) that encode senior-engineer workflows directly into the agent. Unlike raw prompts, each skill includes a step-by-step process, anti-rationalization tables (common excuses the agent might use to skip steps, with documented rebuttals), red flags, and verification gates.

### Why Skills Beat Raw Prompts

| Raw Prompt | Structured Skill |
|---|---|
| "Write tests for this" | Activates Red-Green-Refactor workflow with test pyramid targets (80/15/5) |
| "Review this code" | Runs five-axis review with severity labels (Nit/Optional/FYI) and change-size norms |
| "Make this secure" | Triggers OWASP Top 10 checklist with three-tier boundary system |
| No stopping criteria | Built-in verification gates — the agent must produce evidence before moving on |

### Installing Community Skills

The [agent-skills](https://github.com/addyosmani/agent-skills) pack provides 20 production-grade skills covering the full SDLC. Install them with one command:

```bash
# Install from GitHub (auto-discovers all SKILL.md files)
gemini skills install https://github.com/addyosmani/agent-skills.git --path skills

# Verify installation
/skills list
```

Once installed, skills activate on-demand when the agent recognizes a matching task. Building UI? The `frontend-ui-engineering` skill activates automatically. Debugging a test failure? `debugging-and-error-recovery` kicks in.

### SDLC Slash Commands

The skill pack ships 7 slash commands under `.gemini/commands/` that map to the development lifecycle:

| Command | Phase | What It Does |
|---|---|---|
| `/spec` | Define | Write a structured PRD before writing code |
| `/planning` | Plan | Break work into small, verifiable tasks with acceptance criteria |
| `/build` | Build | Implement the next task as a thin vertical slice |
| `/test` | Verify | Run TDD workflow — red, green, refactor |
| `/review` | Review | Five-axis code review with severity labels |
| `/code-simplify` | Review | Reduce complexity without changing behavior (Chesterton's Fence) |
| `/ship` | Ship | Pre-launch checklist via parallel persona fan-out |

> **Note:** Use `/planning` instead of `/plan` — `/plan` conflicts with Gemini CLI's built-in Plan Mode command.

### Skills vs GEMINI.md

Both influence agent behavior, but serve different purposes:

| | Skills | GEMINI.md |
|---|---|---|
| **Loaded** | On-demand, when task matches | Every prompt, always |
| **Token cost** | Minimal until activated | Constant overhead |
| **Best for** | Phase-specific workflows (TDD, security review, shipping) | Always-on project conventions (tech stack, coding standards) |

**Rule of thumb:** If you'd want it active for *every* prompt, put it in GEMINI.md. If it's phase-specific, install it as a skill.

### Exercise

1. Install the agent-skills pack into your ProShop workspace
2. Run `/spec` — write a spec for a "product comparison" feature
3. Run `/build` — implement the first slice incrementally
4. Run `/test` — watch TDD workflow enforce red-green-refactor
5. Compare: How does the structured workflow differ from a raw "add a comparison feature" prompt?

---

## Google Managed MCP Servers

Google provides **50+ managed MCP servers** that give your agent direct, governed access to Google Cloud services, Workspace apps, and developer tools — no local server installation required.

### Why Managed MCP?

| Concern | How Managed MCP Solves It |
|---|---|
| **Security** | IAM Deny policies for tool-level access control; Model Armor for prompt injection defense |
| **Discovery** | Agent Registry — a unified directory for finding and managing MCP servers |
| **Observability** | OTel Tracing + Cloud Audit Logs for full action forensics |
| **Interoperability** | Works with Gemini CLI, Claude Code, Cursor, VS Code, LangChain, ADK, CrewAI |

### Developer Knowledge MCP

The [Developer Knowledge MCP server](https://developers.google.com/knowledge/mcp) grounds your agent in official Google documentation — Firebase, Cloud, Android, Maps, and more. Instead of hallucinating API signatures, the agent queries the live documentation corpus.

**One-liner install (API key auth):**

```bash
gemini mcp add -t http \
  -H "X-Goog-Api-Key: YOUR_API_KEY" \
  google-developer-knowledge \
  https://developerknowledge.googleapis.com/mcp --scope user
```

**Or via `settings.json` (ADC auth for enterprise):**

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

**Available tools:**

| Tool | Purpose |
|---|---|
| `search_documents` | Find relevant documentation chunks for a query |
| `get_documents` | Retrieve full page content for a specific document |
| `answer_query` | Get a synthesized, grounded answer from the documentation corpus |

### High-Value MCP Servers by Category

| Category | Servers | Example Use Case |
|---|---|---|
| **Developer Docs** | Developer Knowledge API | "How do I configure Cloud Run autoscaling?" → source-cited answer |
| **Data & Analytics** | BigQuery, Spanner, Firestore, AlloyDB | Query production data directly from agent context |
| **Infrastructure** | Cloud Run, GKE, Compute Engine | Provision, scale, and manage infra via natural language |
| **Productivity** | Gmail, Drive, Calendar, Chat | Summarize threads, draft docs, manage invites |
| **Security** | Security Operations, Model Armor | Investigate threats, block prompt injection in real-time |

> **Governance:** Use [IAM Deny policies](https://docs.cloud.google.com/mcp/control-mcp-use-iam#deny-all-mcp-tool-use) to restrict which MCP tools agents can invoke. Combine with [Model Armor](https://docs.cloud.google.com/model-armor/model-armor-mcp-google-cloud-integration) to defend against indirect prompt injection and data exfiltration.

### Exercise

1. Get a Developer Knowledge API key from your Google Cloud project
2. Add the Developer Knowledge MCP server to your Gemini CLI config using the one-liner above
3. Ask the agent: *"How do I deploy a Cloud Run service with a custom domain?"*
4. Verify: Does the response cite official documentation? Compare to an answer without the MCP server connected

---

## Building Agents with agents-cli

[`agents-cli`](https://github.com/google/agents-cli) is a CLI and skill pack that teaches your coding agent how to build, evaluate, and deploy agents on Google's [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform). It is not a replacement for Gemini CLI — it is a tool *for* coding agents.

### Quick Setup

```bash
# Install CLI + skills into all detected coding agents
uvx google-agents-cli setup

# Or install just the skills (your coding agent handles the rest)
npx skills add google/agents-cli
```

> **Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/getting-started/installation/), and Node.js. See `setup.sh` for environment notes.

### Core Workflow

| Command | What It Does |
|---|---|
| `agents-cli scaffold <name>` | Create a new ADK agent project with best-practice structure |
| `agents-cli scaffold enhance` | Add deployment, CI/CD, or RAG to an existing agent project |
| `agents-cli eval run` | Run agent evaluations (LLM-as-judge, trajectory scoring) |
| `agents-cli deploy` | Deploy to Google Cloud (Agent Runtime, Cloud Run, or GKE) |
| `agents-cli publish gemini-enterprise` | Register agent with Gemini Enterprise |

### Skills It Installs

When you run `agents-cli setup`, it installs 7 skills into your coding agent:

| Skill | What Your Coding Agent Learns |
|---|---|
| `google-agents-cli-workflow` | Development lifecycle, code preservation rules, model selection |
| `google-agents-cli-adk-code` | ADK Python API — agents, tools, orchestration, callbacks, state |
| `google-agents-cli-scaffold` | Project scaffolding — `create`, `enhance`, `upgrade` |
| `google-agents-cli-eval` | Evaluation methodology — metrics, evalsets, LLM-as-judge |
| `google-agents-cli-deploy` | Deployment — Agent Runtime, Cloud Run, GKE, CI/CD, secrets |
| `google-agents-cli-publish` | Gemini Enterprise registration |
| `google-agents-cli-observability` | Cloud Trace, logging, third-party integrations |

### When to Use agents-cli vs Raw ADK

| Scenario | Tool |
|---|---|
| Building an agent from scratch with best practices | `agents-cli scaffold` |
| Adding RAG or deployment to an existing agent | `agents-cli scaffold enhance` |
| Evaluating agent quality with structured metrics | `agents-cli eval run` |
| Deploying manually with full control | `adk deploy` directly |
| Writing ADK code without scaffolding | Raw ADK + your coding agent |

### Exercise

1. Install agents-cli: `uvx google-agents-cli setup`
2. Scaffold a new agent: `agents-cli scaffold my-review-bot`
3. Open the scaffolded project in Gemini CLI and ask: *"Enhance this agent with RAG capabilities using Cloud Storage"*
4. Run evaluations: `agents-cli eval run`
5. Observe how the installed skills guide Gemini CLI through ADK-specific patterns it wouldn't otherwise know

---

## Further Reading

| Resource | What |
|---|---|
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 20 production-grade engineering skills for coding agents |
| [google/agents-cli](https://github.com/google/agents-cli) | CLI + skills for building ADK agents on Google Cloud |
| [Developer Knowledge MCP](https://developers.google.com/knowledge/mcp) | Ground agents in official Google developer documentation |
| [Google Managed MCP Servers](https://cloud.google.com/blog/products/ai-machine-learning/google-managed-mcp-servers-are-available-for-everyone) | 50+ enterprise MCP servers (Cloud Blog) |
| [Supported MCP Products](https://docs.cloud.google.com/mcp/supported-products) | Full catalog of Google-managed MCP servers |
| [GoogleCloudPlatform/scion](https://github.com/GoogleCloudPlatform/scion) | Multi-agent orchestration for teams |
| [pauldatta/gemini-cli-field-workshop](https://github.com/pauldatta/gemini-cli-field-workshop) | This workshop's source repository |
| [Gemini CLI Docs](https://geminicli.com) | Official documentation |

---

## Next Step

→ Return to **[Use Case 1: SDLC Productivity](sdlc-productivity.md)** for core features

→ Continue to **[Use Case 2: Legacy Code Modernization](legacy-modernization.md)** for brownfield workflows
