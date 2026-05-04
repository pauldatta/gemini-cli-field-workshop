#!/usr/bin/env bash
# BeforeTool hook: Lightweight secret detection in file writes
# Matcher: write_file|replace_in_file
# Performance: <50ms — simple regex, no external calls
#
# PURPOSE: Prevents the agent from writing hardcoded credentials.
# This steers the model toward using env vars instead of
# embedding secrets directly in code.

input=$(cat)
content=$(echo "$input" | jq -r '.tool_input.content // .tool_input.new_string // ""' 2>/dev/null)

# Quick regex scan — no network calls, no disk I/O beyond stdin
if echo "$content" | grep -qEi '(AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{48}|password\s*[:=]\s*["\x27][^\s"]{8,})'; then
    echo '{"decision":"deny","reason":"Hardcoded credential detected. Use environment variables via process.env instead. Store secrets in .env (which is gitignored) and access them with process.env.YOUR_SECRET_NAME."}'
else
    echo '{}'
fi
