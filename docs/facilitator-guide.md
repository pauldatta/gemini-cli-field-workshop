# Facilitator Guide

> How to deliver this workshop to enterprise customers and internal teams.

---

## Pre-Session Checklist

- [ ] **Environment tested:** Run `./setup.sh` on a clean clone within the last 24 hours
- [ ] **Auth verified:** `gemini -p "Hello"` returns a response (no auth errors)
- [ ] **Demo app running:** `cd demo-app && npm run dev` starts without errors
- [ ] **Conductor installed:** `gemini extensions install https://github.com/gemini-cli-extensions/conductor`
- [ ] **Terminal setup:** Font size 16+, dark theme, no transparent background
- [ ] **Backup plan:** Have pre-recorded terminal sessions for network failures
- [ ] **MCP tokens:** GitHub Personal Access Token configured if demoing MCP
- [ ] **Rate limits:** Check free tier quotas — Vertex AI recommended for full-day workshops

---

## Timing Options

### Quick Demo (2 hours)
| Block | Time | Content |
|---|---|---|
| Setup | 15 min | Environment setup + first prompt |
| UC1 (SDLC) | 45 min | GEMINI.md + Conductor + Policy engine |
| UC3 (DevOps) | 30 min | Headless mode + hooks demo |
| Q&A | 30 min | Open discussion |

### Standard Workshop (4 hours)
| Block | Time | Content |
|---|---|---|
| Setup | 15 min | Full environment setup |
| UC1 (SDLC) | 60 min | Complete walkthrough |
| Break | 15 min | |
| UC2 (AppMod) | 60 min | Plan Mode + subagents |
| Break | 15 min | |
| UC3 (DevOps) | 45 min | Headless + GitHub Actions |
| Wrap-up | 30 min | Q&A + next steps |

### Full Day (8 hours)
| Block | Time | Content |
|---|---|---|
| Morning Session | 3.5 hrs | All 3 use cases with hands-on exercises |
| Lunch | 1 hr | |
| Extensions + Outer Loop | 1 hr | Extensions Ecosystem (30 min) + UC1 Part 2 Outer Loop (20 min) |
| Afternoon Session | 2.5 hrs | Customer-specific exercises using their own repos |

---

## Audience-Specific Delivery

| Audience | Start With | Emphasize | Skip/Skim |
|---|---|---|---|
| **Backend Developers** | UC1 (SDLC) | GEMINI.md, Conductor, subagents | Enterprise config |
| **Platform/DevOps** | UC3 (DevOps) | Headless mode, hooks, GitHub Actions | Conductor |
| **Tech Leads/Architects** | UC2 (AppMod) | Plan Mode, model routing, governance | Hook scripting details |
| **Security/Compliance** | UC1 §1.5 (Governance) | Policy engine, sandboxing, tool isolation | Conductor, batch ops |
| **Engineering Leadership** | Quick Demo | All 3 use cases at overview level | Hands-on exercises |

---

## Live Demo Tips

### Terminal Setup
- **Font size:** 16pt minimum (18pt recommended for conference rooms)
- **Theme:** Dark background, high contrast
- **Terminal width:** At least 120 columns
- **No transparency:** Solid background so projectors work
- **Split panes:** Keep the walkthrough doc visible alongside the terminal

### Pacing
- **Show, don't tell:** Run the command first, explain after
- **Wait for output:** Let the agent complete before narrating
- **Acknowledge latency:** "This is thinking — it's analyzing the entire codebase right now"
- **Have fallbacks:** If the agent gives an unexpected response, use it as a teaching moment: "See how we can steer it?"

### Common Issues During Live Demos

| Issue | Recovery |
|---|---|
| Rate limit hit | Switch to Vertex AI auth, or use a different Google account |
| Agent gives wrong answer | Use model steering: "That's not quite right. The pattern we use is..." |
| Hook fails silently | Check `/hooks panel` — usually a permissions or JSON issue |
| Conductor not installed | `gemini extensions install https://github.com/gemini-cli-extensions/conductor` |
| Slow response | Normal for first prompt (cold start). Subsequent prompts use token caching. |

---

## Customizing for a Customer

### Before the Workshop
1. **Clone their repo** (or a representative sample) into `demo-app/`
2. **Write a custom GEMINI.md** encoding their coding standards
3. **Write a custom PRD** targeting a real feature they want to build
4. **Configure MCP servers** for their tool chain (Jira, GitHub Enterprise, etc.)

### During the Workshop
- Replace ProShop examples with their codebase
- Use their coding standards in GEMINI.md demos
- Demo MCP against their actual Jira/GitHub instance
- Have them write policy rules for their security requirements

### After the Workshop
- Share the repo link for self-paced follow-up
- Offer to review their GEMINI.md files
- Connect them with the Google Cloud AI team for Vertex AI setup

---

## Bonus: gemini-cli-scanner

The [gemini-cli-scanner](https://github.com/pauldatta/gemini-cli-scanner) is a TUI tool that scans a developer's Gemini CLI installation and generates a maturity report.

**Use it as:**
- **Pre-workshop audit:** Scan participant environments to identify setup issues
- **Closing activity:** Have participants scan their setup after the workshop to see their "maturity score"
- **Team assessment:** Aggregate scans across a team to identify standardization opportunities

---

## Key Talking Points

### On Context Window
> "Other tools only see the files you manually open. Gemini CLI reads your entire codebase — architecture, dependencies, test suites, configs — and reasons across all of it at once. Your agent doesn't just autocomplete lines. It understands how your systems connect."

### On Governance
> "Claude Code and Cursor don't have a policy engine. They don't have hooks. They don't have tool isolation for subagents. When your CISO asks 'how do we prevent the AI from running rm -rf?' — you need guardrails-as-code, not just a checkbox."

### On Cost
> "Gemini CLI with a personal Google account is free. Free. With token caching, your enterprise Vertex AI costs are a fraction of what you'd pay for comparable tools. Full-codebase awareness means fewer sessions and less back-and-forth — you stop explaining context and start shipping code."

### On Conductor
> "Most AI tools generate code one prompt at a time. Conductor gives you persistent specs, phased plans, and progress tracking that survives across sessions. It's the difference between giving a contractor verbal instructions and handing them architectural blueprints."
