# Contributing to Gemini CLI Field Workshop

Thanks for your interest in improving this workshop! Every contribution — from typo fixes to new use cases — helps enterprise developers learn Gemini CLI faster.

## How to Contribute

### Report Issues or Share Feedback

Use [GitHub Issues](https://github.com/pauldatta/gemini-cli-field-workshop/issues/new/choose) to:

| Template | When to use |
|:---------|:------------|
| **Bug Report** | Setup scripts fail, broken links, incorrect code samples |
| **Content Improvement** | Suggest new exercises, better explanations, additional use cases |
| **Workshop Feedback** | Share your experience after attending a workshop session |

All issues are automatically triaged by Gemini CLI with type, area, and priority labels.

### Submit Changes

1. **Fork** the repository
2. **Create a branch** from `main` (`git checkout -b fix/broken-link-m03`)
3. **Make your changes** — see [Content Guidelines](#content-guidelines) below
4. **Test locally** — run the Docsify site with `npx docsify-cli serve docs`
5. **Submit a PR** — reference any related issue numbers

### Content Guidelines

- **Voice:** Instructional, concise, and encouraging. Write for enterprise developers who may be new to AI-assisted coding.
- **Code samples:** Must be tested and copy-pasteable. Use fenced code blocks with language tags.
- **Module structure:** Each use case follows the pattern: context → demo → hands-on exercise → recap.
- **Date stamps:** Update the `Last updated` line in any file you modify. This appears in the blockquote header of each doc.
- **Grounding:** All technical claims must be verifiable against the [gemini-cli source repo](https://github.com/google-gemini/gemini-cli). See [`AUDIT.md`](AUDIT.md) for the full checklist.
- **Translations:** If updating English content, note in your PR that `ko/` translations may need updating for parity. Keep technical terms (tool names, commands, code) in English within Korean prose.

### Repository Structure

```
docs/
├── setup.md                 # Environment setup guide
├── sdlc-productivity.md     # Use Case 1
├── legacy-modernization.md  # Use Case 2
├── devops-orchestration.md  # Use Case 3
├── advanced-patterns.md     # Advanced topics
├── extensions-ecosystem.md  # Extensions deep-dive
├── facilitator-guide.md     # Delivery guide for CEs
├── cheatsheet.md            # Quick reference
├── ko/                      # Korean translations
└── assets/                  # Images and media
AUDIT.md                     # Agent-readable audit instructions
```

## Code of Conduct

Be respectful and constructive. This is a learning resource — we welcome contributors of all experience levels.

## Questions?

For questions that aren't bugs or feature requests, open an issue using the **Bug Report** template and select "Other" as the area.
