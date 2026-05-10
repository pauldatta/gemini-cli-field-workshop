# Translation Guide

This guide covers how to add, review, and maintain translations for the workshop.

## Quick Reference

```bash
# See what languages are available
make translate-list

# Translate all workshop docs to Korean
make translate L=ko

# Translate with more parallel workers (default: 4)
make translate L=ko P=8

# Translate a single file
make translate-file FILE=docs/setup.md L=ko

# Validate translations
make translate-validate L=ko

# Check which translations are stale
make translate-drift L=ko
```

## How It Works

1. **English is the source of truth.** All content changes go into `docs/*.md`.
2. **`make translate`** sends each file to Gemini 3.1 Pro, section by section.
3. Code blocks are **extracted before translation** and reinserted after — the
   model never sees code, so it can never corrupt it.
4. A **glossary** pins technical terms to consistent translations.
5. A **manifest** records what was translated from what, enabling drift detection.

## Adding a New Language

```bash
# 1. Copy an existing glossary as a starting point
cp tools/i18n/glossary-ko.md tools/i18n/glossary-ja.md

# 2. Have a native speaker edit the glossary table
#    (change Korean terms to target-language terms)

# 3. Translate (with optional parallel workers)
make translate L=ja
make translate L=ja P=8   # 8 workers for faster runs

# 4. Validate
make translate-validate L=ja

# 5. Add to the language switcher in mkdocs.yml
#    Under plugins.i18n.languages, add:
#    - locale: ja
#      name: 日本語
#      build: true

# 6. Verify it appears
make translate-list

# Done.
```

### Supported Language Codes

Use ISO 639-1 two-letter codes. Here are common ones for the Asia-Pacific region:

| Code | Language | Native Name |
|---|---|---|
| `ko` | Korean | 한국어 |
| `ja` | Japanese | 日本語 |
| `zh` | Chinese (Simplified) | 简体中文 |
| `th` | Thai | ภาษาไทย |
| `vi` | Vietnamese | Tiếng Việt |
| `id` | Indonesian | Bahasa Indonesia |
| `ms` | Malay | Bahasa Melayu |
| `tl` | Filipino/Tagalog | Filipino |
| `my` | Burmese | မြန်မာ |
| `km` | Khmer | ខ្មែរ |

## Reviewing the Glossary

The glossary lives at `tools/i18n/glossary-{lang}.md`. It's a markdown file
with two sections:

### Never Translate
Product names, CLI commands, and technical identifiers that must stay in English.
These appear as a comma-separated list.

### Term Translations
A markdown table mapping English terms to their translations. Edit this table
directly — add rows, change translations, add notes in the third column.

**Review process:**
1. Open the glossary file in any text editor
2. Edit the table — the format is `| English | Translation | Notes |`
3. Save and commit
4. Re-run `make translate L=xx` to apply the updated glossary

## What Gets Translated

The 8 workshop docs plus a generated sidebar:

| File | Content |
|---|---|
| `docs/index.md` | Landing page (MkDocs homepage for each language) |
| `docs/setup.md` | Environment setup instructions |
| `docs/sdlc-productivity.md` | Use Case 1 |
| `docs/legacy-modernization.md` | Use Case 2 |
| `docs/devops-orchestration.md` | Use Case 3 |
| `docs/advanced-patterns.md` | Advanced techniques |
| `docs/extensions-ecosystem.md` | Extensions & ecosystem |
| `docs/cheatsheet.md` | Quick reference |

**Not translated:** facilitator guide, exercises, samples, agent configs.

## Drift Detection

When English content changes, translations become stale. Run:

```bash
make translate-drift L=ko
```

This compares the git hash of each English file against the hash recorded when
it was last translated. It shows which files are stale and the git diff command
to see what changed.

**Drift is informational, not blocking.** The language owner decides when to
re-translate based on the scope of the English changes.

## Important Rules

- **Never edit `docs/{lang}/*.md` directly.** These are generated files. Manual
  edits will be overwritten on the next `make translate` run.
- **Always edit English source first**, then re-run the pipeline.
- **To fix a translation issue**, update the glossary or file a bug — don't
  patch the output.
