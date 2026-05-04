# Workshop Testing Infrastructure — Agent Context

This document describes the automated testing and quality infrastructure for the
Gemini CLI Field Workshop. Read this before making changes to documentation,
configuration files, sample code, or CI workflows.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Testing Layers                                │
├──────────────────┬──────────────────┬───────────────────────────┤
│  Pre-commit      │  CI (every PR)   │  Nightly                  │
│  ─────────       │  ─────────       │  ─────────                │
│  markdownlint    │  Structure       │  Link checker (lychee)    │
│                  │  Code blocks     │  Upstream drift           │
│                  │  Local drift     │  Live smoke tests         │
│                  │  Markdown lint   │                           │
├──────────────────┴──────────────────┴───────────────────────────┤
│  Local Harness: make test                                       │
│  Runs: test-structure + test-blocks + test-drift                │
│  Time: ~5 seconds    Cost: $0                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Reference

```bash
# Run all offline tests (do this before pushing)
make test

# Individual targets
make test-structure   # File existence, JSON/TOML/YAML syntax, shell syntax
make test-blocks      # Validate code blocks in docs/*.md
make test-drift       # Check doc ↔ code alignment
make test-drift-full  # + upstream Gemini CLI docs (needs network)
make test-links       # Dead URL detection (needs network)
make test-docsify     # Serve + curl every page
make lint-md          # markdownlint-cli2
make test-live        # Headless Gemini CLI (needs GEMINI_API_KEY)
make test-ci          # GitHub Actions status via gh CLI
make help             # Show all targets
```

## What Each Test Catches

### `test-structure` — File & Config Validation
**Files:** `Makefile` (inline)

Validates that the workshop's physical structure is intact:
- Required files exist: `setup.sh`, `README.md`, `docs/index.html`, `docs/_sidebar.md`
- `samples/config/settings.json` is valid JSON (parsed with `jq`)
- `samples/config/policy.toml` is valid TOML (parsed with `tomllib`)
- `setup.sh` and all `samples/hooks/*.sh` pass `bash -n` (syntax check)
- All `samples/agents/*.md` have YAML frontmatter (start with `---`)

**When it fails:** You renamed a config file, broke JSON/TOML syntax, or added an
agent without frontmatter.

### `test-blocks` — Code Block Extraction & Validation
**Files:** `scripts/validate-code-blocks.sh`

Extracts every fenced code block from `docs/*.md`, classifies by language tag
(json, toml, yaml, bash), and runs the appropriate syntax validator:

| Language | Validator | What it catches |
|----------|-----------|-----------------|
| `json`   | `jq .`    | Malformed JSON in inline examples |
| `toml`   | `tomllib` | Invalid TOML in policy examples |
| `yaml`   | `yaml.safe_load` | YAML indentation errors in workflow examples |
| `bash`   | `bash -n` | Syntax errors in shell command examples |

**Intentional gap:** `bash -n` only catches syntax errors, not runtime errors.
Code blocks tagged as `text`, `markdown`, or with no language tag are skipped.

**Intentional skips (not errors):**
- YAML blocks with `${{ }}` — GitHub Actions template expressions are not valid YAML
- YAML blocks starting with `- uses:` — partial step fragments from workflow examples
- Bash blocks containing `"key":` patterns — mixed-language blocks with embedded JSON
- All blocks when `pyyaml` is not installed locally (CI installs it)

**When it fails:** You edited an inline JSON example and introduced a trailing comma,
or your YAML workflow example has wrong indentation.

### `test-drift` — Doc ↔ Code Drift Detection
**Files:** `scripts/detect-drift.sh`

Checks five alignment surfaces:

1. **File path references:** Paths like `samples/config/settings.json` referenced in
   docs → validates they exist on disk.
2. **Agent coverage:** Every `.md` in `samples/agents/` should be mentioned somewhere
   in `docs/`.
3. **Hook coverage:** Every `.sh` in `samples/hooks/` should be mentioned somewhere
   in `docs/`.
4. **settings.json ↔ hooks:** Hook scripts referenced in `settings.json` should exist
   in `samples/hooks/`.
5. **Sidebar ↔ doc files:** Every `.md` file listed in `docs/_sidebar.md` should
   exist in `docs/`.

**With `--upstream` flag:** Also fetches the Gemini CLI reference from
`geminicli.com`, caches it for 24h, and checks that CLI flags (`--worktree`,
`--resume`) and slash commands (`/memory`, `/skills`) used in our docs still exist
in the upstream reference.

**When it fails:** You added a new hook but forgot to document it, or Gemini CLI
deprecated a flag you're teaching.

### `test-links` — Dead URL Detection
**Files:** `.github/workflows/workshop-links.yml`, `Makefile` (target)

Uses [lychee](https://github.com/lycheeverse/lychee) to check every URL in the
docs for 404s, redirects, and timeouts. Excludes `localhost`, placeholder URLs
(`YOUR_KEY`, `your-org`), and email addresses.

**When it fails:** An upstream dependency moved (npm package, GitHub repo, Google
Cloud docs page) or you have a backtick-contaminated URL.

### `lint-md` — Markdown Lint
**Files:** `.markdownlint-cli2.jsonc`

Runs `markdownlint-cli2` with a config tuned for Docsify. Key disabled rules:
- `MD013` (line length) — our tables are wide
- `MD033` (inline HTML) — we use `<p align="center">` and `<details>`
- `MD041` (first line heading) — Docsify pages may start with HTML
- `MD024` (duplicate headings) — we repeat "Example" headings intentionally

Key enabled rules that catch rendering bugs:
- `MD001` (heading increment), `MD025` (single h1), `MD042` (empty links)

## File Inventory

```
├── .gemini/
│   └── AGENTS.md              ← You are here
├── .github/workflows/
│   ├── issue-triage.yml       ← Existing: Gemini-powered issue triage
│   ├── workshop-links.yml     ← NEW: Lychee link checker
│   └── workshop-structural.yml ← NEW: Structure + blocks + drift + lint
├── .markdownlint-cli2.jsonc   ← NEW: Markdown lint config
├── Makefile                   ← NEW: Local test harness
└── scripts/
    ├── validate-code-blocks.sh ← NEW: Code block extractor + validator
    └── detect-drift.sh         ← NEW: Doc ↔ code drift detector
```

## Rules for Modifying Workshop Content

When you change workshop content, follow these rules to keep CI green:

### Adding a new doc page
1. Create `docs/new-page.md`
2. Add entry to `docs/_sidebar.md`
3. Run `make test-drift` to verify sidebar alignment

### Adding a new agent definition
1. Create `samples/agents/agent-name.md` with YAML frontmatter (`---` header)
2. Reference it somewhere in `docs/*.md`
3. Run `make test-structure` (frontmatter check) and `make test-drift` (coverage check)

### Adding a new hook
1. Create `samples/hooks/hook-name.sh` (must be executable, must accept JSON on stdin)
2. If registering it in settings.json, add the entry to `samples/config/settings.json`
3. Reference it somewhere in `docs/*.md`
4. Run `make test` to verify all three surfaces

### Editing inline code examples in docs
1. Ensure code blocks have the correct language tag: ` ```json `, ` ```bash `, etc.
2. Run `make test-blocks` to validate syntax
3. If the block is intentionally partial (a snippet, not a complete file), use the
   `text` language tag to skip validation

### Adding external URLs
1. Prefer linking to stable URLs (docs landing pages, not deep anchors)
2. Run `make test-links` to verify no dead links were introduced

### Referencing Gemini CLI features
1. Before teaching a new CLI flag or slash command, verify it exists at
   https://geminicli.com/docs/cli/cli-reference/
2. Check for the 🔬 (experimental) marker — note this in the workshop docs
3. Run `make test-drift-full` to verify alignment with upstream

## CI Workflow Details

### `workshop-structural.yml` (every PR)
Runs 4 parallel jobs:
- `structure` — file existence + config syntax
- `code-blocks` — inline code validation
- `drift` — doc ↔ code alignment
- `markdown-lint` — style + structure

All 4 must pass for the PR check to go green. No API keys needed. Runs in ~30s.

### `workshop-links.yml` (PRs + nightly)
Runs lychee link checker with caching. The nightly run catches external link rot
(upstream docs reorgs, deleted repos) even when the workshop hasn't changed.

### Secrets Required
| Secret | Used by | Purpose |
|--------|---------|---------|
| `GEMINI_API_KEY` | `test-live` (future) | Headless CLI smoke tests |

The structural workflows require **zero secrets** — this is intentional.
