#!/usr/bin/env bash
# BeforeTool hook: Injects git context into the model's awareness
# Matcher: write_file|replace_in_file
# Performance: <100ms — single git command
#
# PURPOSE: Before any file write, inject recent git changes for the
# target file so the agent is aware of recent modifications.
# This improves context quality without burdening the model
# with irrelevant information.

input=$(cat)
filepath=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null)

# Only inject context if the file exists and has git history
if [ -n "$filepath" ] && [ -f "$filepath" ]; then
    recent_changes=$(git log --oneline -3 -- "$filepath" 2>/dev/null | head -3)
    if [ -n "$recent_changes" ]; then
        echo "{\"systemMessage\":\"Recent changes to $filepath:\\n$recent_changes\"}"
    else
        echo '{}'
    fi
else
    echo '{}'
fi
