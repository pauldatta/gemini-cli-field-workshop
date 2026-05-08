# Workshop Changelog

Content-specific changes to workshop materials — CLI breakages, deprecated commands, and doc corrections. For general repo changes see the [commit history](https://github.com/pauldatta/gemini-cli-field-workshop/commits/main).

---

## 2026-05-08

### ⚠️ `/memory add` command removed (Gemini CLI ≥ v0.41.1)

**Affects:** UC1 — SDLC Productivity Enhancement (Memory section), Cheatsheet

The `/memory add` slash command no longer works in Gemini CLI v0.41.1 and later. Running it produces:

```
✗  save_memory {"fact":"..."}
Tool "save_memory" not found.
```

**Root cause:** Memory V2 is now the default architecture. Under Memory V2, the underlying `save_memory` tool is not registered with the agent, so any attempt to call it fails. The `/memory add` subcommand has been removed from the CLI's slash menu when Memory V2 is active (which it is by default for all Gemini 3 model users).

**Upstream reference:** [google-gemini/gemini-cli#26563](https://github.com/google-gemini/gemini-cli/issues/26563) — confirmed by Google contributor Sandy Tao: *"Now the model will use edit or write_file to remember things… This /memory add option will be removed soon."*

**What still works:**

| Command | Status |
|---|---|
| `/memory show` | ✅ Works |
| `/memory reload` / `/memory refresh` | ✅ Works |
| `/memory list` | ✅ Works |
| `/memory inbox` | ✅ Works (requires Auto Memory enabled) |
| `/memory add` | ❌ Removed in Memory V2 |

**Alternatives:**

1. **Natural language** — Tell the agent directly what to remember. Example:
   ```
   Remember that the ProShop backend runs on port 5000 and the React dev server on port 3000.
   ```
   The agent will use `write_file` or `edit` to update your `GEMINI.md` file directly — same result, no slash command needed.

2. **Auto Memory** — Enable background extraction in `~/.gemini/settings.json`:
   ```json
   {
     "experimental": {
       "autoMemory": true
     }
   }
   ```
   After idle sessions, Gemini CLI mines transcripts for durable facts and proposes them via `/memory inbox` for your review before committing.

3. **Direct file edit** — Manually edit `~/.gemini/GEMINI.md` (global) or `.gemini/GEMINI.md` (project-local) at any time.

**Workshop materials updated:** `docs/sdlc-productivity.md`, `docs/cheatsheet.md`
