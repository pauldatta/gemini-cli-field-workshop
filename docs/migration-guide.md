# M09 — Migration Guide: Gemini CLI → Antigravity CLI

**Duration:** 30 minutes  
**Audience:** All  
**Prerequisites:** M01 (First Contact)  
**Goal:** Understand the June 18, 2026 transition, migrate all existing configuration, and decide the right path forward for your team.

> **⚠️ Time-Sensitive:** Gemini CLI stops serving free, Google AI Pro, and Google AI Ultra users on **June 18, 2026**. This module walks every migration step so your team doesn't wake up to broken workflows.

---

## Background: Why This Is Happening

When Google shipped Gemini CLI in 2025, the goal was to bring Gemini directly into the terminal. Over 100,000 GitHub stars, 6,000 merged pull requests, and millions of users later, the team learned something important: developers now need **multiple agents communicating with each other**, sharing a unified backend with the rest of their workflow.

That architectural need drove the consolidation. **Antigravity CLI** (`agy`) is the result — a Go-based, agent-first terminal experience that shares the same harness as the Antigravity 2.0 desktop application. Every core improvement to the agent engine automatically applies everywhere.

Key changes from Gemini CLI:

| Dimension | Gemini CLI | Antigravity CLI |
|:---|:---|:---|
| **Language** | Node.js / TypeScript | Go (faster cold starts) |
| **Binary name** | `gemini` | `agy` |
| **License** | Apache 2.0 (open source) | Closed source |
| **Multi-agent** | Subagents (single session) | Async, background orchestration |
| **Desktop sync** | None | Shared harness with Antigravity 2.0 |
| **Skills path** | `.gemini/skills/` | `.agents/skills/` |
| **Plugin format** | Extensions in `settings.json` | Antigravity plugins (`plugin.json`) |
| **MCP config** | Inline in `settings.json` | Separate `mcp_config.json` |
| **Context file** | `GEMINI.md` | `GEMINI.md` **or** `AGENTS.md` (both work) |

**References:**
- [Google I/O announcement (May 19, 2026)](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
- [Official migration docs](https://antigravity.google/docs/gcli-migration)
- [Community migration guide](https://avinashsangle.com/blog/gemini-cli-to-antigravity-cli-guide)

---

## 9.1 — Who Is Affected? (5 min)

**Show the impact matrix:**

| Tier | Status on June 18, 2026 | Recommended Action |
|:---|:---|:---|
| **Free (Gemini Code Assist for individuals)** | Cut off | Migrate to Antigravity CLI |
| **Google AI Pro ($19.99/mo)** | Cut off from Gemini CLI | Antigravity Pro tier auto-applies; check new rate limits |
| **Google AI Ultra ($249.99/mo)** | Cut off from Gemini CLI | Antigravity Ultra tier (no weekly cap) auto-applies |
| **Gemini Code Assist Standard / Enterprise** | ✅ Unchanged | Optional migration; Gemini CLI keeps working |
| **Gemini Code Assist for GitHub (paid via GCP)** | Existing installs unchanged; new installs blocked | Plan migration before next renewal |

> **For workshop attendees on Standard/Enterprise:** You are not forced to migrate. Antigravity CLI is available to you now and worth evaluating, but your existing investment is protected.

**Two paths exist if you want to keep Gemini CLI's open-source binary:**
1. Wire a **paid Gemini API key** (AI Studio or Vertex AI) into the Apache 2.0 Gemini CLI binary — your skills, hooks, and MCP configs need no changes.
2. Upgrade to **Gemini Code Assist Standard or Enterprise** for a managed, supported path.

> Note: Antigravity CLI is **closed source** — a deliberate break from Gemini CLI's Apache 2.0 model. If vendor-neutral portability, audit, or forking rights matter in your regulated environment, the paid-API-key path preserves those properties.

---

## 9.2 — Install Antigravity CLI (5 min)

> **Best practice:** Keep both binaries (`gemini` and `agy`) installed side-by-side during the transition. Run a workflow through both to confirm parity before cutting over.

### macOS and Linux

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

The binary lands at `~/.local/bin/agy`. If that directory isn't on your `PATH`:

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

### First Run & OAuth

```bash
agy
```

This opens your default browser for Google OAuth. Sign in with the **same account you used for Gemini CLI** so plugin imports pick up the correct workspace. On a remote SSH box, `agy` detects the session and prints an authorization URL to open locally (an improvement over Gemini CLI's old flow).

**Verify the install:**

```bash
agy --version
```

---

## 9.3 — Migrate Plugins & Extensions (5 min)

Gemini CLI's extensions become Antigravity CLI plugins. The import command handles the bulk of this automatically.

### Step 1 — Auto-Import

```bash
agy plugin import gemini
```

This scans your Gemini CLI extensions directory and registers each as an Antigravity plugin. Plugins that relied on custom themes will have their themes silently dropped — rebuild these manually using the `plugin.json` format.

### Step 2 — Verify Imported Plugins

```bash
agy plugin list
```

### Step 3 — Move Workspace Skills

```bash
# Skills used to live here (per-workspace):
# .gemini/skills/

# They now live here:
# .agents/skills/

cp -r .gemini/skills/ .agents/skills/
```

Global skills directories auto-load from the new path. No content changes required to skill SKILL.md files.

> **Workshop context files are backwards-compatible.** Both `GEMINI.md` and `AGENTS.md` are read without modification. You do not need to rename or reformat existing project context files.

---

## 9.4 — Migrate MCP Server Configs (5 min)

MCP server configuration moves from inline `settings.json` into a dedicated `mcp_config.json`, and one field is renamed.

### Before (Gemini CLI `settings.json`)

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

### After (Antigravity CLI `mcp_config.json`)

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

**The only change is `url` → `serverUrl`.** All other fields stay the same.

**Verify MCP servers loaded:**

```bash
agy /mcp
```

---

## 9.5 — Validate Hooks & Run End-to-End (5 min)

Hooks continue to work in Antigravity CLI. Re-run a hook-driven workflow to confirm that `pre-tool-call` and `stop` hooks fire as expected.

```bash
# Run a representative workflow you trust
agy "Analyze backend/controllers/orderController.js and summarize the error handling patterns"

# Compare to Gemini CLI output if you still have it running
gemini "Analyze backend/controllers/orderController.js and summarize the error handling patterns"
```

**Things that changed in the CLI surface (heads up):**

| Gemini CLI | Antigravity CLI | Notes |
|:---|:---|:---|
| `gemini --resume` | `agy --resume` | Same semantics |
| `gemini -p "prompt"` | `agy -p "prompt"` | Headless mode intact |
| `/tools` | `/tools` | Unchanged |
| `/rewind` | `/rewind` | Unchanged |
| `gemini skills` (terminal command) | Use `/skills` inside `agy` | Terminal-level command removed |
| `--temperature`, `--top_k` | Not exposed in CLI surface | Set via config or prompts |

---

## 9.6 — Rate Limits & Pricing Reality Check (5 min)

> **Heads up for free-tier users:** The free tier is significantly more restrictive than Gemini CLI's old free tier.

| Tier | Gemini CLI (old) | Antigravity CLI |
|:---|:---|:---|
| **Free** | ~1,000 requests/day | Weekly quota; refreshes every 5 hours up to a hard weekly cap |
| **Pro ($19.99/mo)** | Reasonable daily limits | Antigravity Pro tier |
| **Ultra ($249.99/mo)** | High daily limits | No weekly cap |

Community reports (GitHub Discussion #27274) indicate that the free-tier weekly cap empties in **4–5 chat turns** with a 166-hour reset window. Plan for this if you're using Antigravity CLI for workshop exercises.

**Practical recommendation for workshop delivery:**
- If your organization has Standard/Enterprise licenses, continue using Gemini CLI for the hands-on modules and use this module to orient the team on the migration path.
- If running on personal accounts, use paid Pro/Ultra tiers or prepare API-key-backed fallback.

---

## 9.7 — Decision Framework: Stay, Migrate, or Switch? (5 min)

Use this decision tree to recommend the right path:

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

## Activity: Live Migration (if time allows)

Run through the migration checklist against the workshop repo itself:

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

## Key Takeaways

- **Deadline:** June 18, 2026 for free-tier, AI Pro, and AI Ultra users. Enterprise is unaffected.
- **Migration time:** 30–60 minutes per workspace with skills, hooks, and MCP servers.
- **`GEMINI.md` just works.** No rename, no reformatting.
- **The biggest gotcha:** MCP configs move to `mcp_config.json` with `url` renamed to `serverUrl`.
- **Rate limits:** The free tier is dramatically tighter. Budget accordingly.
- **Enterprise teams:** Your existing Gemini CLI investment is protected. Migration is optional.

---

## References

- [Official announcement — Google Developers Blog](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
- [Official migration docs — antigravity.google](https://antigravity.google/docs/gcli-migration)
- [Community guide — Avinash Sangle](https://avinashsangle.com/blog/gemini-cli-to-antigravity-cli-guide)
- [GitHub Discussion #27274 — Community reaction](https://github.com/google-gemini/gemini-cli/discussions/27274)
- [Antigravity CLI download](https://antigravity.google/download)
