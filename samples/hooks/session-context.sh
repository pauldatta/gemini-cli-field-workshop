#!/usr/bin/env bash
# SessionStart hook: Injects project state into the session context
# Performance: <200ms — reads package.json + git status
#
# PURPOSE: At the start of every session, give the agent a quick
# summary of the project state: current branch, pending changes,
# and key dependencies. This steers early prompts toward
# awareness of what's in-flight.

input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd' 2>/dev/null)

# Gather lightweight project state
branch=$(git -C "$cwd" branch --show-current 2>/dev/null || echo "unknown")
dirty_count=$(git -C "$cwd" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
node_version=$(node --version 2>/dev/null || echo "not found")

context="Session context: branch=$branch, uncommitted_files=$dirty_count, node=$node_version"

# Inject as system message — the agent sees this as background context
echo "{\"systemMessage\":\"$context\"}"
