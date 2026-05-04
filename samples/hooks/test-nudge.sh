#!/usr/bin/env bash
# AfterTool hook: Lightweight post-write reminder
# Matcher: write_file|replace_in_file
# Performance: <10ms — no external calls, pure string output
#
# PURPOSE: After file writes to test-related paths, nudge the agent
# to consider running tests. This steers behavior without
# actually running tests (which adds latency). The agent
# decides whether to act on the nudge.

input=$(cat)
filepath=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null)

# Nudge for source files — remind the agent about tests
if echo "$filepath" | grep -qE '\.(js|ts|jsx|tsx)$'; then
    if echo "$filepath" | grep -qvE '(test|spec|__tests__)'; then
        echo "{\"systemMessage\":\"Reminder: you modified a source file. Consider running 'npm test' to verify no regressions.\"}"
    else
        echo '{}'
    fi
else
    echo '{}'
fi
