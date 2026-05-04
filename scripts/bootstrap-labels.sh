#!/usr/bin/env bash
# Bootstrap GitHub labels for issue triage.
# Usage: ./scripts/bootstrap-labels.sh [owner/repo]
# Requires: gh CLI authenticated

set -euo pipefail

REPO="${1:-pauldatta/gemini-cli-field-workshop}"

echo "🏷️  Bootstrapping labels for ${REPO}..."

# Delete defaults that conflict
for label in "bug" "enhancement" "question" "documentation" "help wanted" "good first issue" "invalid" "wontfix" "duplicate"; do
  gh label delete "$label" --repo "$REPO" --yes 2>/dev/null || true
done

# Type labels
gh label create "type/bug"         --repo "$REPO" --color "d73a4a" --description "Something isn't working" --force
gh label create "type/improvement" --repo "$REPO" --color "a2eeef" --description "Enhancement or new content" --force
gh label create "type/feedback"    --repo "$REPO" --color "7057ff" --description "Workshop delivery feedback" --force
gh label create "type/question"    --repo "$REPO" --color "d876e3" --description "Usage or content question" --force

# Area labels
gh label create "area/setup"       --repo "$REPO" --color "0075ca" --description "setup.sh, installation, auth" --force
gh label create "area/content"     --repo "$REPO" --color "0075ca" --description "Workshop docs, walkthroughs" --force
gh label create "area/hooks"       --repo "$REPO" --color "0075ca" --description "Hook samples, settings, policy" --force
gh label create "area/facilitator" --repo "$REPO" --color "0075ca" --description "Facilitator guide, delivery" --force
gh label create "area/cicd"        --repo "$REPO" --color "0075ca" --description "GitHub Actions, headless mode" --force
gh label create "area/docsify"     --repo "$REPO" --color "0075ca" --description "Docsify site, nav, search" --force
gh label create "area/i18n"        --repo "$REPO" --color "0075ca" --description "Translations, language parity" --force
gh label create "area/unknown"     --repo "$REPO" --color "ededed" --description "Uncategorized" --force

# Priority labels
gh label create "priority/high"    --repo "$REPO" --color "b60205" --description "Blocks workshop delivery" --force
gh label create "priority/medium"  --repo "$REPO" --color "fbca04" --description "Degrades experience, has workarounds" --force
gh label create "priority/low"     --repo "$REPO" --color "0e8a16" --description "Nice-to-have, cosmetic" --force

# Status labels
gh label create "status/triage"    --repo "$REPO" --color "f9d0c4" --description "Awaiting automated triage" --force
gh label create "status/confirmed" --repo "$REPO" --color "c5def5" --description "Confirmed by maintainer" --force

echo "✅ Labels bootstrapped for ${REPO}"
