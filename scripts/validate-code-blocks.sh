#!/usr/bin/env bash
# validate-code-blocks.sh — Extract fenced code blocks from markdown and validate by language
#
# Extracts every ```lang ... ``` block from docs/*.md, classifies by language tag,
# and runs the appropriate syntax validator. Catches broken JSON, TOML, YAML, and
# bash snippets embedded in workshop documentation before students hit them.
#
# Usage: ./scripts/validate-code-blocks.sh [dir]
#   dir: directory containing .md files (default: docs/)
#
# Exit code: 1 if validation errors found, 0 if all clean
#
# Intentional skips:
#   - YAML blocks with ${{ }}   → GitHub Actions templates, invalid until rendered
#   - YAML blocks starting with "- uses:"  → partial step fragments
#   - Bash blocks with embedded JSON objects → mixed-language docs blocks
#   - Code blocks tagged as: text, markdown, plaintext, or untagged

set -euo pipefail

DOCS_DIR="${1:-docs}"
ERRORS=0
CHECKED=0
SKIPPED=0

# Colors (disabled if not a terminal)
if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' NC=''
fi

log_ok()    { echo -e "  ${GREEN}✅${NC} $*"; }
log_warn()  { echo -e "  ${YELLOW}⚠️${NC}  $*"; }
log_fail()  { echo -e "  ${RED}❌${NC} $*"; }

# Check for optional dependencies
HAS_PYYAML=false
if python3 -c "import yaml" 2>/dev/null; then
  HAS_PYYAML=true
fi

# extract_blocks_to_files <language> <file> <output_dir>
# Writes each code block to a separate file in output_dir: block_0, block_1, ...
# Prints the number of blocks extracted to stdout.
extract_blocks_to_files() {
  local lang="$1" file="$2" outdir="$3"
  awk -v lang="$lang" -v outdir="$outdir" '
    BEGIN { inside=0; count=0; outfile="" }
    /^```/ {
      if (inside) {
        close(outfile)
        inside=0
        next
      }
      tag = $0
      sub(/^```[ \t]*/, "", tag)
      sub(/[ \t].*$/, "", tag)
      if (tolower(tag) == tolower(lang)) {
        outfile = outdir "/block_" count
        count++
        inside=1
        next
      }
    }
    inside { print > outfile }
    END { print count }
  ' "$file"
}

# Create a temp directory for extracted blocks
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "📋 Validating code blocks in ${DOCS_DIR}/"
if ! $HAS_PYYAML; then
  log_warn "pyyaml not installed — YAML validation will be skipped"
  echo "     Install with: pip install pyyaml (or use a venv)"
fi
echo ""

for md_file in "${DOCS_DIR}"/*.md; do
  [ -f "$md_file" ] || continue
  file_errors=0

  for lang in json toml yaml bash; do
    block_dir="${TMPDIR}/$(basename "$md_file")_${lang}"
    mkdir -p "$block_dir"

    count=$(extract_blocks_to_files "$lang" "$md_file" "$block_dir")

    for (( i=0; i<count; i++ )); do
      block_file="${block_dir}/block_${i}"
      [ -f "$block_file" ] || continue
      [ -s "$block_file" ] || continue  # skip empty blocks
      CHECKED=$((CHECKED + 1))

      preview=$(head -2 "$block_file" | tr '\n' ' ' | cut -c1-80)

      case "$lang" in
        json)
          # Skip partial JSON snippets (contain // comments or ...)
          if grep -qE '^\s*(//|\.\.\.)' "$block_file"; then
            SKIPPED=$((SKIPPED + 1))
            continue
          fi
          if ! jq . "$block_file" > /dev/null 2>&1; then
            log_fail "Invalid JSON in $md_file (block $((i+1)))"
            echo "     Preview: ${preview}"
            file_errors=$((file_errors + 1))
          fi
          ;;
        toml)
          if ! python3 -c "
import sys, tomllib
with open(sys.argv[1], 'rb') as f:
    tomllib.load(f)
" "$block_file" 2>/dev/null; then
            log_fail "Invalid TOML in $md_file (block $((i+1)))"
            echo "     Preview: ${preview}"
            file_errors=$((file_errors + 1))
          fi
          ;;
        yaml)
          # Skip when pyyaml is not available
          if ! $HAS_PYYAML; then
            SKIPPED=$((SKIPPED + 1))
            continue
          fi
          # Skip YAML with GitHub Actions template expressions
          if grep -qF '${{' "$block_file"; then
            SKIPPED=$((SKIPPED + 1))
            continue
          fi
          # Skip partial GitHub Actions step fragments (e.g., just a "- uses:" step)
          if head -1 "$block_file" | grep -qE '^\s*- uses:'; then
            SKIPPED=$((SKIPPED + 1))
            continue
          fi
          if ! python3 -c "
import sys, yaml
with open(sys.argv[1]) as f:
    yaml.safe_load(f)
" "$block_file" 2>/dev/null; then
            log_fail "Invalid YAML in $md_file (block $((i+1)))"
            echo "     Preview: ${preview}"
            file_errors=$((file_errors + 1))
          fi
          ;;
        bash)
          # Skip bash blocks that contain embedded JSON/config objects.
          # These are mixed-language documentation blocks where a comment says
          # "add this to settings.json:" followed by raw JSON. bash -n can't
          # parse those, and that's expected.
          if grep -qE '^\s*"[a-z]+"\s*:' "$block_file"; then
            SKIPPED=$((SKIPPED + 1))
            continue
          fi
          if ! bash -n "$block_file" 2>/dev/null; then
            log_fail "Invalid bash syntax in $md_file (block $((i+1)))"
            echo "     Preview: ${preview}"
            file_errors=$((file_errors + 1))
          fi
          ;;
      esac
    done
  done

  if [ "$file_errors" -eq 0 ]; then
    log_ok "$md_file"
  fi
  ERRORS=$((ERRORS + file_errors))
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Checked: $CHECKED blocks  (Skipped: $SKIPPED)"
echo "Errors:  $ERRORS"

if [ "$ERRORS" -gt 0 ]; then
  echo -e "${RED}FAILED${NC}"
  exit 1
else
  echo -e "${GREEN}ALL PASSED${NC}"
  exit 0
fi
