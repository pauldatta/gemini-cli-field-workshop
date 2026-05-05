# Environment Setup

> Complete this before starting any use case. Takes ~15 minutes.
>
> *Last updated: 2026-05-05 · [Source verified against gemini-cli repository](https://github.com/google-gemini/gemini-cli)*

---

## System Requirements

| Component      | Minimum  | Recommended                                             |
| -------------- | -------- | ------------------------------------------------------- |
| **Node.js**    | v18.0.0  | v20+ (LTS)                                              |
| **npm**        | v9+      | v10+                                                    |
| **Git**        | v2.30+   | v2.40+                                                  |
| **Terminal**   | Any      | iTerm2 (macOS), Windows Terminal, or VS Code integrated |
| **Disk Space** | 500MB    | 1GB (includes demo app + node_modules)                  |
| **jq**         | Optional | Required for hook examples                              |

---

## Step 1: Clone the Workshop

```bash
git clone https://github.com/pauldatta/gemini-cli-field-workshop.git
cd gemini-cli-field-workshop
```

---

## Step 2: Run the Setup Script

The setup script handles everything — Gemini CLI installation, demo app checkout, and configuration:

```bash
chmod +x setup.sh
./setup.sh
```

**What it does:**

1. Verifies Node.js, npm, and Git are installed
2. Installs/updates Gemini CLI globally (`npm install -g @google/gemini-cli`)
3. Initializes the `demo-app/` submodule (ProShop v2) and runs `npm install`
4. Copies sample configurations into the demo app:
   - `GEMINI.md` context hierarchy
   - Hook scripts (secret scanner, auto-test, session logger, path guard)
   - Policy engine rules
   - Custom subagent definitions
5. Verifies Gemini CLI authentication

---

## Step 3: Authentication

### Option A: Personal Google Account (Free Tier)

Best for workshops and evaluation. No GCP project required.

```bash
cd demo-app
gemini
# Follow the browser-based OAuth flow
```

> **Free tier limits:** The personal Google AI tier has generous daily limits suitable for workshop use. See [Quota and pricing](https://geminicli.com/docs/resources/quota-and-pricing/).

### Option B: Vertex AI (Enterprise)

For production and enterprise deployments. Requires a GCP project with billing.

```bash
# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Authenticate
gcloud auth application-default login
```

Gemini CLI will auto-detect Vertex AI credentials. For enterprise-enforced authentication, see the [Enterprise guide](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md).

---

## Step 4: Verify Installation

```bash
# Check Gemini CLI version
gemini --version

# Quick test (should respond instantly)
gemini -p "Say 'Workshop ready!' in exactly two words."

# Verify the demo app is set up
ls demo-app/GEMINI.md          # Should exist
ls demo-app/.gemini/hooks/     # Should contain 4 hook scripts
ls demo-app/.gemini/policies/  # Should contain team-guardrails.toml
```

---

## Troubleshooting

| Issue                                     | Solution                                                                                                                                                                      |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `npm install -g` fails with `EACCES`      | Use `sudo npm install -g @google/gemini-cli` or fix npm permissions: [npm docs](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally) |
| `gemini: command not found` after install | Restart your terminal or run `source ~/.bashrc` / `source ~/.zshrc`                                                                                                           |
| OAuth flow doesn't open browser           | Copy the URL from the terminal and open it manually                                                                                                                           |
| `git submodule update` fails              | Run `git submodule init && git submodule update --recursive`                                                                                                                  |
| Demo app `npm install` fails              | Check Node.js version (`node --version`). ProShop v2 requires Node 18+.                                                                                                       |
| Rate limit errors during workshop         | Switch to Vertex AI auth, or wait 60 seconds and retry                                                                                                                        |
| Hooks not executing                       | Run `chmod +x demo-app/.gemini/hooks/*.sh`                                                                                                                                    |
| `jq: command not found`                   | Install jq: `brew install jq` (macOS) or `apt install jq` (Linux)                                                                                                             |

---

## Manual Setup (if setup.sh fails)

If the setup script doesn't work on your system, run these steps manually:

```bash
# 1. Install Gemini CLI
npm install -g @google/gemini-cli

# 2. Initialize demo app
git submodule add https://github.com/bradtraversy/proshop-v2.git demo-app
cd demo-app && npm install && cd ..

# 3. Copy configs
mkdir -p demo-app/.gemini/agents demo-app/.gemini/hooks demo-app/.gemini/policies
cp samples/config/settings.json demo-app/.gemini/settings.json
cp samples/config/policy.toml demo-app/.gemini/policies/team-guardrails.toml
cp samples/agents/security-scanner.md demo-app/.gemini/agents/
cp samples/hooks/*.sh demo-app/.gemini/hooks/
chmod +x demo-app/.gemini/hooks/*.sh
cp samples/gemini-md/project-gemini.md demo-app/GEMINI.md
mkdir -p demo-app/backend
cp samples/gemini-md/backend-gemini.md demo-app/backend/GEMINI.md

# 4. Authenticate
cd demo-app && gemini
```

---

## Next Step

→ Start with **[Use Case 1: SDLC Productivity Enhancement](sdlc-productivity.md)**
