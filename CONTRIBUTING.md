# Contributing to Gemini CLI Field Workshop

Thanks for your interest in improving this workshop! Every contribution — from typo fixes to new use cases — helps enterprise developers learn Gemini CLI faster.

## Getting Started with Gemini CLI

This repo is built to be navigated with Gemini CLI itself. Before contributing, let Gemini CLI read the project context so it can guide you:

```bash
# Clone and enter the repo
git clone https://github.com/pauldatta/gemini-cli-field-workshop.git
cd gemini-cli-field-workshop

# Start Gemini CLI — it auto-reads .gemini/AGENTS.md for project context
gemini
```

### Key Context Files

| File | Purpose | How Gemini CLI uses it |
|---|---|---|
| `.gemini/AGENTS.md` | Testing infrastructure, CI architecture, quality rules | Auto-loaded on every session — Gemini CLI understands the test suite |
| `AUDIT.md` | Agent-readable audit checklist against upstream gemini-cli repo | Ask: `@AUDIT.md Run the documentation audit` |
| `tools/i18n/TRANSLATE.md` | Translation pipeline docs | Ask: `Read @tools/i18n/TRANSLATE.md and translate setup.md to Japanese` |
| `samples/agents/*.md` | Subagent definitions for code review, docs, security | Reference when building new agents |

### Example Contributor Workflows

```bash
# "I want to fix a broken code example"
# Gemini CLI already knows the test suite from AGENTS.md
gemini "Find all bash code blocks in docs/legacy-modernization.md and check if they're syntactically valid"

# "I want to add a new section to a module"
gemini "Read AUDIT.md and check if the hooks documentation in devops-orchestration.md matches the upstream gemini-cli source"

# "I want to add a new language translation"
gemini "Read @tools/i18n/TRANSLATE.md and walk me through adding Japanese (ja) support"

# "I want to understand the test suite before changing CI"
gemini "Explain the testing architecture from .gemini/AGENTS.md and show me what make test runs"
```

## How to Contribute

### Report Issues or Share Feedback

Use [GitHub Issues](https://github.com/pauldatta/gemini-cli-field-workshop/issues/new/choose) to:

| Template | When to use |
|:---------|:------------|
| **Bug Report** | Setup scripts fail, broken links, incorrect code samples |
| **Content Improvement** | Suggest new exercises, better explanations, additional use cases |
| **Workshop Feedback** | Share your experience after attending a workshop session |

All issues are automatically triaged with type, area, and priority labels.

### Submit Changes

1. **Fork** the repository
2. **Create a branch** from `main` (`git checkout -b fix/broken-link-m03`)
3. **Make your changes** — see [Content Guidelines](#content-guidelines) below
4. **Test locally**:
   ```bash
   make test                        # Structure, code blocks, drift (~5s)
   make translate-validate L=ko     # Check translation integrity
   npx docsify-cli serve docs       # Preview the site
   ```
5. **Submit a PR** — reference any related issue numbers
6. **Gemini reviews your PR** — the CI pipeline runs a custom [Gemini CLI code review](.github/workflows/gemini-code-review.yml) that checks workshop content quality, i18n impact, and security

### Content Guidelines

- **Voice:** Instructional, concise, and encouraging. Write for enterprise developers who may be new to AI-assisted coding.
- **Code samples:** Must be tested and copy-pasteable. Use fenced code blocks with language tags (`bash`, `json`, `toml`, `markdown`).
- **Module structure:** Each use case follows: context → demo → hands-on exercise → recap.
- **Models:** Use `gemini-3.1-flash-lite-preview` or `gemini-3-flash-preview`. Never reference deprecated models (`gemini-1.5-flash`, `gemini-1.5-pro`).
- **Grounding:** All technical claims must be verifiable against the [gemini-cli source repo](https://github.com/google-gemini/gemini-cli). See [`AUDIT.md`](AUDIT.md) for the full checklist.

### Translations (i18n)

The workshop supports multiple languages via an automated pipeline:

| Language | Code | Status |
|---|---|---|
| English | `en` | Source of truth |
| Korean | `ko` | Active |
| Indonesian | `id` | Active |
| Chinese (Simplified) | `zh` | Active |

**If you change English source files:**
- Note in your PR that translations will need regeneration
- Translation owners run `make translate L=<lang> P=8` to update
- Never edit `docs/{lang}/*.md` directly — these are generated files

**To add a new language:** See [`tools/i18n/TRANSLATE.md`](tools/i18n/TRANSLATE.md).

## Code of Conduct

Be respectful and constructive. This is a learning resource — we welcome contributors of all experience levels.

## Questions?

For questions that aren't bugs or feature requests, open an issue using the **Bug Report** template and select "Other" as the area.
