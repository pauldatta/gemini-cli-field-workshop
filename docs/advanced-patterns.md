# Advanced Patterns

> **Duration:** ~45 minutes (self-paced)  
> **Goal:** Master prompting discipline, verification loops, context engineering, and parallel development. These techniques work with any Gemini CLI workflow.  
> **Prerequisites:** Complete at least [Use Case 1: SDLC Productivity](sdlc-productivity.md) or be familiar with the basics.

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
echo "Your detailed spec..." > .gemini/context/feature-spec.md

# Then reference it:
# "Read the spec in .gemini/context/feature-spec.md and implement it"
```

The agent loads context files on-demand (JIT) — they don't consume tokens until needed.

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

## Further Reading

| Resource | What |
|---|---|
| [GoogleCloudPlatform/scion](https://github.com/GoogleCloudPlatform/scion) | Multi-agent orchestration for teams |
| [pauldatta/gemini-cli-field-workshop](https://github.com/pauldatta/gemini-cli-field-workshop) | This workshop's source repository |
| [Gemini CLI Docs](https://geminicli.com) | Official documentation |

---

## Next Step

→ Return to **[Use Case 1: SDLC Productivity](sdlc-productivity.md)** for core features

→ Continue to **[Use Case 2: Legacy Code Modernization](legacy-modernization.md)** for brownfield workflows
