# Documentation Audit Report

## Audit Findings

- **agents-cli setup**: Docs mention `agents-cli setup` as a standalone command. Repo documentation clarifies it is often `uvx google-agents-cli setup`. Recommend aligning all docs.
- **Conductor Extension**: The setup for Conductor extension is referenced correctly, but documentation on MCP server requirements should be cross-referenced with `extensions-ecosystem.md`.
- **SCION Installation**: Docs recommend `go install github.com/GoogleCloudPlatform/scion/cmd/scion@latest`. This should be verified for compatibility with current `gemini extensions` capabilities.
- **Skill Activation**: Docs mention skills activate on-demand, but do not emphasize the `activate_skill` tool call for explicit control, which is standard in Gemini CLI.

## Recommendations

- Align all CLI installation commands to use `uvx` if appropriate or standardize the path reference.
- Update `docs/cheatsheet.md` to replace the hallucinated `gemini-2.5-flash` with `gemini-3.1-flash-lite-preview`.
- Clarify the distinction between built-in `/plan` and skill-based `/planning` in `docs/cheatsheet.md`.
- Explicitly add `activate_skill` usage examples to `advanced-patterns.md`.
- Validate all repository URLs provided in documentation.

## Parallel Audit Findings

### `docs/cheatsheet.md`

- **Model Versioning**: References `gemini-2.5-flash` in a subagent definition example. This version is non-existent; it should be updated to `gemini-3.1-flash-lite-preview` or `gemini-3-flash-preview`.
- **Installation Paths**: Lacks the `uvx google-agents-cli setup` installation path for ADK development, which is present in other workshop files.
- **Plan Mode Ambiguity**: Lists `/plan` for "Toggle Plan Mode". While correct for the built-in CLI command, it should be distinguished from the skill-based `/planning` command mentioned in `advanced-patterns.md`.

### `docs/devops-orchestration.md`

- **Headless Mode Commands**: Suggests `gemini -p "/resume"` to list sessions. A more idiomatic headless approach would use a dedicated flag like `gemini sessions` or `gemini --list-sessions`.
- **Sandbox Execution**: References the `--sandbox` flag for headless runs. Verification is needed to ensure this is the current canonical flag for enabling restricted execution environments in headless mode.
- **GitHub Action Verification**: Correctly references `google-github-actions/run-gemini-cli@v1`, which is the official first-party action.
