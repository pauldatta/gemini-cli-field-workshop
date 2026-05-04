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
        test-links test-docsify test-live lint-md test-ci help

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

