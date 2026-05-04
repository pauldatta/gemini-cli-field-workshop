#!/usr/bin/env bash
# detect-drift.sh — Detect documentation ↔ code drift in the workshop
#
# Two layers of validation:
#   1. LOCAL DRIFT:  File paths referenced in docs → do they exist?
#                    Agents/hooks in samples/ → are they mentioned in docs?
#   2. UPSTREAM DRIFT: CLI features used in docs → do they still exist
#                      in the official Gemini CLI reference?
#
# Usage: ./scripts/detect-drift.sh [--upstream]
#   --upstream: Also check against geminicli.com (requires network, slower)
#
# Exit code: number of errors found (0 = all clean)

set -euo pipefail

CHECK_UPSTREAM=false
if [[ "${1:-}" == "--upstream" ]]; then
  CHECK_UPSTREAM=true
fi

ERRORS=0
WARNINGS=0

# Colors
if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  CYAN='\033[0;36m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' CYAN='' NC=''
fi

log_ok()    { echo -e "  ${GREEN}✅${NC} $*"; }
log_warn()  { echo -e "  ${YELLOW}⚠️${NC}  $*"; WARNINGS=$((WARNINGS + 1)); }
log_fail()  { echo -e "  ${RED}❌${NC} $*"; ERRORS=$((ERRORS + 1)); }
log_section() { echo -e "\n${CYAN}$*${NC}"; }

# ═══════════════════════════════════════════════════════════
# LOCAL DRIFT CHECKS
# ═══════════════════════════════════════════════════════════

log_section "🔍 Local Drift Detection"

# --- 1. File paths referenced in docs should exist ---
log_section "  Checking file path references..."

# Extract paths like samples/config/..., samples/hooks/..., etc. from docs
grep -rhoE '(samples|exercises)/[a-zA-Z0-9_./-]+' docs/*.md 2>/dev/null | sort -u | while read -r ref_path; do
  # Normalize: strip trailing punctuation that grep might catch
  ref_path=$(echo "$ref_path" | sed 's/[).,;:]*$//')
  
  if [ -e "$ref_path" ]; then
    log_ok "Referenced path exists: $ref_path"
  elif [ -e "$(dirname "$ref_path")" ]; then
    # Directory exists but specific file doesn't — might be a wildcard reference
    log_warn "Path not found (parent exists): $ref_path"
  else
    log_fail "Referenced path not found: $ref_path"
  fi
done

# --- 2. Every agent in samples/agents/ should be mentioned in docs ---
log_section "  Checking agent documentation coverage..."

for agent_file in samples/agents/*.md; do
  [ -f "$agent_file" ] || continue
  agent_name=$(basename "$agent_file" .md)
  if grep -rq "$agent_name" docs/*.md 2>/dev/null; then
    log_ok "Agent '$agent_name' is documented"
  else
    log_warn "Agent '$agent_name' exists in samples/ but is not referenced in any doc"
  fi
done

# --- 3. Every hook in samples/hooks/ should be mentioned in docs ---
log_section "  Checking hook documentation coverage..."

for hook_file in samples/hooks/*.sh; do
  [ -f "$hook_file" ] || continue
  hook_name=$(basename "$hook_file" .sh)
  if grep -rq "$hook_name" docs/*.md 2>/dev/null; then
    log_ok "Hook '$hook_name' is documented"
  else
    log_warn "Hook '$hook_name' exists in samples/ but is not referenced in any doc"
  fi
done

# --- 4. Hooks referenced in settings.json should exist in samples/ ---
log_section "  Checking settings.json ↔ hook file alignment..."

if [ -f "samples/config/settings.json" ]; then
  # Extract hook script filenames from settings.json
  grep -oE 'hooks/[a-zA-Z0-9_-]+\.sh' samples/config/settings.json | sort -u | while read -r hook_ref; do
    hook_basename=$(basename "$hook_ref" .sh)
    if [ -f "samples/hooks/${hook_basename}.sh" ]; then
      log_ok "settings.json hook '${hook_basename}' has matching script"
    else
      log_fail "settings.json references '${hook_ref}' but samples/hooks/${hook_basename}.sh not found"
    fi
  done
fi

# --- 5. Sidebar entries should have matching doc files ---
log_section "  Checking sidebar ↔ doc file alignment..."

if [ -f "docs/_sidebar.md" ]; then
  grep -oE '\([a-zA-Z0-9_-]+\.md\)' docs/_sidebar.md | tr -d '()' | while read -r sidebar_file; do
    if [ -f "docs/${sidebar_file}" ]; then
      log_ok "Sidebar entry '${sidebar_file}' exists"
    else
      log_fail "Sidebar references '${sidebar_file}' but docs/${sidebar_file} not found"
    fi
  done
fi

# ═══════════════════════════════════════════════════════════
# UPSTREAM DRIFT CHECKS (optional, needs network)
# ═══════════════════════════════════════════════════════════

if $CHECK_UPSTREAM; then
  log_section "🌐 Upstream Drift Detection (Gemini CLI docs)"

  # Cache the CLI reference page for 24h to avoid hammering the site
  CLI_REF_CACHE="/tmp/gemini-cli-ref-cache.html"
  CACHE_MAX_AGE=1440  # minutes

  if [ ! -f "$CLI_REF_CACHE" ] || [ "$(find "$CLI_REF_CACHE" -mmin +${CACHE_MAX_AGE} -print 2>/dev/null)" ]; then
    echo "  Fetching CLI reference from geminicli.com..."
    if curl -sL "https://geminicli.com/docs/cli/cli-reference/" > "$CLI_REF_CACHE" 2>/dev/null; then
      log_ok "Fetched CLI reference (cached for 24h)"
    else
      log_warn "Could not fetch CLI reference — skipping upstream checks"
      CLI_REF_CACHE=""
    fi
  else
    echo "  Using cached CLI reference (< 24h old)"
  fi

  if [ -n "$CLI_REF_CACHE" ] && [ -f "$CLI_REF_CACHE" ]; then
    # Check CLI flags used in our docs
    log_section "  Checking CLI flags against upstream reference..."
    grep -rhoE 'gemini --[a-z-]+' docs/*.md 2>/dev/null | sed 's/gemini //' | sort -u | while read -r flag; do
      # Use -- to prevent grep from interpreting --worktree etc. as its own flags
      if grep -qi -- "$flag" "$CLI_REF_CACHE"; then
        log_ok "CLI flag '$flag' found in upstream reference"
      else
        log_warn "CLI flag '$flag' used in workshop but not found in CLI reference"
      fi
    done

    # Check slash commands used in our docs
    # Only check actual Gemini CLI slash commands, not URL path segments.
    # We use an allowlist of commands the workshop teaches, extracted from
    # cheatsheet.md and doc pages. This avoids false positives from URLs
    # like /controllers, /backend, /pauldatta etc.
    log_section "  Checking slash commands against upstream reference..."
    KNOWN_SLASH_CMDS="plan stats clear tools resume rewind checkpoint restore memory hooks skills extensions sandbox commands agent e stdout tasks remove updates wishlist mcp"
    for cmd_name in $KNOWN_SLASH_CMDS; do
      # Check if this command appears in our docs
      if grep -rqw "/${cmd_name}" docs/*.md 2>/dev/null; then
        if grep -qi -- "$cmd_name" "$CLI_REF_CACHE"; then
          log_ok "Slash command '/${cmd_name}' found in upstream reference"
        else
          log_warn "Slash command '/${cmd_name}' used in workshop but not found in CLI reference"
        fi
      fi
    done
  fi
else
  echo ""
  echo "  (Skipping upstream checks. Run with --upstream to enable.)"
fi

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"

if [ "$ERRORS" -gt 0 ]; then
  echo -e "${RED}DRIFT DETECTED${NC}"
  exit 1
else
  echo -e "${GREEN}ALL CLEAN${NC}"
  exit 0
fi
