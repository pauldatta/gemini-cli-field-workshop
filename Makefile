# ═══════════════════════════════════════════════════════════
# Gemini CLI Field Workshop — Test Harness
# ═══════════════════════════════════════════════════════════
#
# Usage:
#   make test             Run all offline tests (structure + code blocks + drift)
#   make test-structure   Validate file structure and config syntax
#   make test-blocks      Validate code blocks in documentation
#   make test-drift       Check for doc ↔ code drift (local only)
#   make test-drift-full  Check drift including upstream CLI docs (needs network)
#   make test-links       Check for dead links (needs network + npx)
#   make test-docsify     Smoke test Docsify site renders
#   make test-live        Run live Gemini CLI smoke tests (needs GEMINI_API_KEY)
#   make lint-md          Lint markdown files
#   make test-ci          Check GitHub Actions workflow status (needs gh CLI)
#
# See: .gemini/AGENTS.md for documentation on this testing infrastructure.

.PHONY: test test-structure test-blocks test-drift test-drift-full \
        test-links test-docsify test-live lint-md test-ci help \
        translate translate-file translate-validate translate-drift translate-list

# Default: run all offline tests
test: test-structure test-blocks test-drift  ## Run all offline tests

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ───────────────────────────────────────────────────────────
# Structure Tests — validate files exist and configs parse
# ───────────────────────────────────────────────────────────

test-structure:  ## Validate file structure and config syntax
	@echo "📋 Checking file structure..."
	@echo ""
	@# --- Required files ---
	@test -f setup.sh || (echo "❌ Missing setup.sh" && exit 1)
	@echo "  ✅ setup.sh exists"
	@test -f README.md || (echo "❌ Missing README.md" && exit 1)
	@echo "  ✅ README.md exists"
	@test -f docs/index.html || (echo "❌ Missing docs/index.html (Docsify)" && exit 1)
	@echo "  ✅ docs/index.html exists"
	@test -f docs/_sidebar.md || (echo "❌ Missing docs/_sidebar.md" && exit 1)
	@echo "  ✅ docs/_sidebar.md exists"
	@echo ""
	@# --- Config file syntax ---
	@echo "  Validating config syntax..."
	@test -f samples/config/settings.json || (echo "❌ Missing settings.json" && exit 1)
	@jq . samples/config/settings.json > /dev/null
	@echo "  ✅ settings.json — valid JSON"
	@test -f samples/config/policy.toml || (echo "❌ Missing policy.toml" && exit 1)
	@python3 -c "import tomllib; tomllib.load(open('samples/config/policy.toml','rb'))"
	@echo "  ✅ policy.toml — valid TOML"
	@echo ""
	@# --- Shell script syntax ---
	@echo "  Validating shell scripts..."
	@bash -n setup.sh && echo "  ✅ setup.sh — syntax OK"
	@for f in samples/hooks/*.sh; do \
		bash -n "$$f" && echo "  ✅ $$f — syntax OK"; \
	done
	@echo ""
	@# --- Agent frontmatter ---
	@echo "  Validating agent definitions..."
	@for f in samples/agents/*.md; do \
		if head -1 "$$f" | grep -q '^---'; then \
			echo "  ✅ $$f — frontmatter present"; \
		else \
			echo "❌ $$f — missing YAML frontmatter" && exit 1; \
		fi; \
	done
	@echo ""
	@echo "✅ Structure checks passed"

# ───────────────────────────────────────────────────────────
# Code Block Validation — syntax check inline code in docs
# ───────────────────────────────────────────────────────────

test-blocks:  ## Validate code blocks in documentation
	@echo ""
	@./scripts/validate-code-blocks.sh docs/

# ───────────────────────────────────────────────────────────
# Drift Detection — doc ↔ code alignment
# ───────────────────────────────────────────────────────────

test-drift:  ## Check for doc ↔ code drift (local only)
	@./scripts/detect-drift.sh

test-drift-full:  ## Check drift + upstream CLI docs (needs network)
	@./scripts/detect-drift.sh --upstream

# ───────────────────────────────────────────────────────────
# Link Checker — dead URL detection (needs network)
# ───────────────────────────────────────────────────────────

test-links:  ## Check for dead links (needs network)
	@echo "🔗 Checking links..."
	@npx -y lychee --no-progress --exclude localhost --exclude '127\.0\.0\.1' \
		'docs/**/*.md' 'README.md'
	@echo "✅ Link checks passed"

# ───────────────────────────────────────────────────────────
# Docsify Smoke Test — verify the site renders
# ───────────────────────────────────────────────────────────

test-docsify:  ## Smoke test Docsify site (starts server, curls pages)
	@echo "🌐 Starting Docsify server..."
	@npx -y docsify-cli serve docs/ --port 4173 & \
		DOCSIFY_PID=$$!; \
		sleep 3; \
		FAILED=0; \
		for page in "" "setup" "sdlc-productivity" "legacy-modernization" \
		            "devops-orchestration" "advanced-patterns" "cheatsheet"; do \
			STATUS=$$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:4173/#/$${page}"); \
			if [ "$$STATUS" = "200" ]; then \
				echo "  ✅ /$${page} → $$STATUS"; \
			else \
				echo "  ❌ /$${page} → $$STATUS"; \
				FAILED=$$((FAILED + 1)); \
			fi; \
		done; \
		kill $$DOCSIFY_PID 2>/dev/null || true; \
		if [ "$$FAILED" -gt 0 ]; then exit 1; fi
	@echo "✅ Docsify smoke test passed"

# ───────────────────────────────────────────────────────────
# Markdown Lint — style and structure validation
# ───────────────────────────────────────────────────────────

lint-md:  ## Lint markdown files
	@echo "📝 Linting markdown..."
	@npx -y markdownlint-cli2 "docs/**/*.md" "README.md"
	@echo "✅ Markdown lint passed"

# ───────────────────────────────────────────────────────────
# Live Tests — requires GEMINI_API_KEY (nightly / manual)
# ───────────────────────────────────────────────────────────

test-live:  ## Run live Gemini CLI tests (needs GEMINI_API_KEY)
	@if [ -z "$${GEMINI_API_KEY:-}" ]; then \
		echo "❌ GEMINI_API_KEY not set. Export it or run from CI with secrets."; \
		exit 1; \
	fi
	@echo "🤖 Running live smoke tests..."
	@echo "  Testing headless mode..."
	@gemini -p "Respond with exactly: WORKSHOP_SMOKE_OK" 2>/dev/null | grep -q "WORKSHOP_SMOKE_OK" \
		&& echo "  ✅ Headless mode works" \
		|| (echo "  ❌ Headless mode failed" && exit 1)
	@echo "✅ Live tests passed"

# ───────────────────────────────────────────────────────────
# CI Status — check GitHub Actions runs via gh CLI
# ───────────────────────────────────────────────────────────

test-ci:  ## Check GitHub Actions workflow status (needs gh CLI)
	@if ! command -v gh >/dev/null 2>&1; then \
		echo "❌ gh CLI not found. Install: https://cli.github.com"; \
		exit 1; \
	fi
	@echo "🔄 GitHub Actions Status"
	@echo ""
	@echo "  Workflow files:"
	@for f in .github/workflows/*.yml; do \
		echo "  ✅ $$f"; \
	done
	@echo ""
	@echo "  Recent runs:"
	@gh run list --limit 5 2>/dev/null || echo "  ⚠️  Not in a GitHub repo or not authenticated"
	@echo ""
	@echo "  Failed runs (if any):"
	@gh run list --status failure --limit 3 2>/dev/null || true

# ───────────────────────────────────────────────────────────
# Translation Pipeline — multi-language support
# ───────────────────────────────────────────────────────────
# Usage: make translate L=ko
#        make translate-file FILE=docs/setup.md L=ko
#        make translate-validate L=ko
#        make translate-drift L=ko
#        make translate-list
# See: tools/i18n/TRANSLATE.md for the full guide.

# Auto-discover available languages from glossary files
AVAILABLE_LANGS := $(sort $(patsubst tools/i18n/glossary-%.md,%,$(wildcard tools/i18n/glossary-*.md)))

# Helper: check L is set and glossary exists
define check_lang
	@if [ -z "$(L)" ]; then \
		echo "❌ Language not specified."; \
		echo ""; \
		echo "  Available: $(AVAILABLE_LANGS)"; \
		echo "  Usage: make $@ L=ko"; \
		exit 1; \
	fi
	@if [ ! -s "tools/i18n/glossary-$(L).md" ]; then \
		echo "❌ No glossary for '$(L)'. Available: $(AVAILABLE_LANGS)"; \
		echo "  Create tools/i18n/glossary-$(L).md first (see tools/i18n/TRANSLATE.md)"; \
		exit 1; \
	fi
endef

translate-list:  ## Show available languages and translation status
	@echo "🌐 Translation Pipeline — Available Languages"
	@echo ""
	@if [ -z "$(AVAILABLE_LANGS)" ]; then \
		echo "  No glossaries found in tools/i18n/"; \
		echo "  Create one with: cp tools/i18n/glossary-ko.md tools/i18n/glossary-{lang}.md"; \
	else \
		for lang in $(AVAILABLE_LANGS); do \
			count=$$(ls docs/$$lang/*.md 2>/dev/null | wc -l | tr -d ' '); \
			if [ "$$count" -gt 0 ]; then \
				echo "  ✅ $$lang — $$count translated files"; \
			else \
				echo "  ⬚  $$lang — glossary exists, no translations yet"; \
			fi; \
		done; \
	fi
	@echo ""
	@echo "  Translate: make translate L=xx"
	@echo "  Validate:  make translate-validate L=xx"
	@echo "  Drift:     make translate-drift L=xx"

translate:  ## Translate all workshop docs (requires L=xx)
	$(check_lang)
	@python3 tools/i18n/translate.py --all --lang $(L)

translate-file:  ## Translate one file (requires L=xx FILE=path)
	$(check_lang)
	@test -n "$(FILE)" || (echo "❌ Specify FILE=docs/setup.md" && exit 1)
	@python3 tools/i18n/translate.py $(FILE) --lang $(L)

translate-validate:  ## Validate translations (requires L=xx)
	$(check_lang)
	@python3 tools/i18n/validate.py --all --lang $(L)

translate-drift:  ## Show stale translations (requires L=xx)
	$(check_lang)
	@python3 tools/i18n/drift.py --lang $(L)

