# Documentation Audit Instructions

> **Purpose:** Agent-readable instructions for auditing workshop documentation against the [gemini-cli](https://github.com/google-gemini/gemini-cli) source-of-truth repository.
> **Trigger:** Run this audit whenever the upstream `google-gemini/gemini-cli` repo has a significant release, or before any workshop delivery.
> **Last audit:** 2026-05-05

---

## Pre-Audit Setup

1. **Clone the source-of-truth repository** (shallow clone is sufficient):

   ```bash
   git clone --depth=1 https://github.com/google-gemini/gemini-cli.git /tmp/gemini-cli-audit
   ```

2. **Index key reference files** from the cloned repo:

   | Source File | Contains |
   |---|---|
   | `docs/cli/tools.md` | Canonical tool names and signatures |
   | `docs/reference/hooks.md` | Hook event lifecycle and JSON schema |
   | `docs/reference/policy-engine.md` | Policy TOML schema and priority tiers |
   | `docs/cli/memory.md` | Memory system (manual + autoMemory) |
   | `docs/cli/checkpointing.md` | Checkpointing configuration |
   | `docs/cli/sandbox.md` | Sandbox modes and configuration |
   | `docs/cli/enterprise.md` | Enterprise authentication setup |
   | `docs/cli/gemini-md.md` | GEMINI.md context hierarchy and `@./` import syntax |
   | `docs/cli/agents.md` | Sub-agent YAML frontmatter schema |
   | `docs/cli/extensions.md` | Extension manifest and policy contribution |
   | `docs/cli/slash-commands.md` | Built-in slash commands |
   | `packages/core/src/tools/` | Tool implementation source code |
   | `packages/cli/src/ui/key/keyBindings.ts` | Keyboard shortcuts and deprecated bindings |
   | `packages/cli/src/ui/hooks/slashCommandProcessor.ts` | Slash command implementations |

---

## Audit Checklist

For **each file** in `docs/` (English) and `docs/ko/` (Korean translations):

### 1. Tool Names
Verify every tool name referenced in documentation matches the canonical names from `docs/cli/tools.md`.

**Common errors to check:**
- `replace_in_file` → should be `replace`
- `search_in_files` → should be `grep_search`
- `web_search` → should be `google_web_search`
- `list_files` → should be `list_directory`

### 2. Slash Commands
Verify every `/command` referenced exists in `docs/cli/slash-commands.md`.

**Common errors to check:**
- `/checkpoint` → not a real command. Checkpointing is configured via `settings.json` with `checkpointing: true`
- `/sandbox status` → not a real command. Use `/settings` to check sandbox mode
- `/resume` in headless mode → should be `gemini --list-sessions` / `gemini --resume SESSION_ID`

### 3. Policy Engine TOML
Verify all TOML policy examples match the schema in `docs/reference/policy-engine.md`.

**Common errors to check:**
- `denyMessage` → should be `deny_message`
- `when = { command_matches = "..." }` → should be `commandRegex = "..."` or `commandPrefix = [...]`
- Claims about extensions being unable to set `allow` → verify against current policy-engine.md
- Missing `deny_message` field on deny rules

**Priority tiers (verify current order):**
1. Default (lowest)
2. Extension
3. Workspace
4. User
5. Admin (highest)

### 4. Hook Event Schema
Verify hook JSON schemas match `docs/reference/hooks.md`.

**Common errors to check:**
- `notification.message` → should be `.message` (top-level)
- `notification.title` → should be `.title` (top-level)
- Incorrect event name list (verify against all 11 lifecycle events)

### 5. Import Syntax
Verify GEMINI.md import syntax matches `docs/cli/gemini-md.md`.

**Common errors to check:**
- `@import ./path` → should be `@./path`

### 6. Agent Frontmatter
Verify sub-agent YAML frontmatter matches `docs/cli/agents.md`.

**Common errors to check:**
- Deprecated model names (e.g., `gemini-2.5-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`)
- Tool names that don't match the canonical tool list

### 7. Ungrounded Claims
Flag any claims that cannot be verified from the source repo. Examples:

**Common errors to check:**
- "full codebase awareness" → unverifiable marketing language
- "automatic model routing" → verify if documented or internal implementation detail
- Fabricated JSON schemas for authentication config → defer to `docs/cli/enterprise.md`
- `.gemini/context/` directory → not a documented convention

### 8. Feature Flags & Experimental Features
Verify which features require explicit opt-in:

| Feature | Setting | Documentation Link |
|---|---|---|
| Auto Memory | `autoMemory: true` in `settings.json` | `docs/cli/memory.md` |
| Checkpointing | `checkpointing: true` in `settings.json` | `docs/cli/checkpointing.md` |
| Sandbox | `sandbox` settings in `settings.json` | `docs/cli/sandbox.md` |

### 9. External Links
Verify all links to the `google-gemini/gemini-cli` repository resolve correctly. Run:

```bash
grep -rn 'github.com/google-gemini/gemini-cli' docs/ | grep -v node_modules
```

Spot-check that linked files and paths exist in the cloned repo.

### 10. Keyboard Shortcuts & UI Bindings
Verify all keyboard shortcuts documented in workshop materials match the actual bindings in the upstream source code at `packages/cli/src/ui/key/keyBindings.ts`.

**How to verify:**
1. Extract all `Ctrl+`, `Shift+`, `Alt+` references from workshop docs:
   ```bash
   grep -rn 'Ctrl+\|Shift+\|Alt+\|Cmd+' docs/ --include='*.md'
   ```
2. Cross-reference each against the `defaultKeyBindingConfig` map in `keyBindings.ts`
3. Check for `DEPRECATED_` prefixed commands — these bindings still work but should not be taught as primary shortcuts

**Known deprecations (verify current state):**
- `Ctrl+X` → **DEPRECATED** for external editor. Current binding: `Ctrl+G` / `Ctrl+Shift+G`

**Key bindings to verify:**
| Workshop Claim | Source Command | Source Binding |
|---|---|---|
| `Tab` accepts edits | `ACCEPT_SUGGESTION` | `tab`, `enter` |
| `Shift+Tab` cycles modes | `CYCLE_APPROVAL_MODE` | `shift+tab` |
| `Ctrl+G` opens editor | `OPEN_EXTERNAL_EDITOR` | `ctrl+g`, `ctrl+shift+g` |
| `Ctrl+C` cancels | `QUIT` | `ctrl+c` |
| `Ctrl+Y` toggles YOLO | `TOGGLE_YOLO` | `ctrl+y` |

**Also verify against source (not just docs):**
- Slash command implementations in `packages/cli/src/ui/hooks/slashCommandProcessor.ts`
- Tool signatures in `packages/core/src/tools/`
- Settings schema in `schemas/`

---

## Korean Translation Sync

After fixing English files, propagate changes to `docs/ko/`:

1. **Date stamp:** Each Korean file must have the same `최종 업데이트` date as its English counterpart.
2. **Technical terms:** Keep in English within Korean prose: tool names, commands, TOML keys, model names, file paths.
3. **Code blocks:** Must be identical between English and Korean — only surrounding prose is translated.
4. **Policy examples:** Must use the same corrected TOML schema as English.

**Translation style:**
- Prose in Korean, technical terms in English
- Maintain the same document structure and section ordering
- Preserve all blockquote callouts and tables

---

## Output Format

Generate an audit report with:

```markdown
## Audit Results — [DATE]

### Summary
- Files audited: X
- Issues found: Y
- Issues by severity: Critical (N) / Warning (N) / Info (N)

### Findings

#### [CRITICAL] File: docs/example.md, Line: XX
- **Issue:** Tool name `replace_in_file` does not exist
- **Source:** docs/cli/tools.md shows the correct name is `replace`
- **Fix:** Replace `replace_in_file` with `replace`

#### [WARNING] File: docs/example.md, Line: XX
- **Issue:** Unverifiable claim about feature X
- **Source:** Not found in gemini-cli docs
- **Fix:** Remove or soften language
```

---

## Post-Audit Cleanup

```bash
# Remove the audit clone
rm -rf /tmp/gemini-cli-audit

# Run markdownlint to verify no structural regressions
npx markdownlint-cli2 "docs/**/*.md"
```

---

## References

- [gemini-cli repository](https://github.com/google-gemini/gemini-cli)
- [Policy Engine Guide](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md)
- [Secure Gemini CLI with the Policy Engine](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy) — Battle-tested enterprise policy examples
