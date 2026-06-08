#!/usr/bin/env python3
"""
Translate workshop markdown files using the Gemini API.

Usage:
    python tools/i18n/translate.py docs/setup.md --lang ko
    python tools/i18n/translate.py --all --lang ko
    python tools/i18n/translate.py docs/setup.md --lang ko --dry-run
    python tools/i18n/translate.py --all --langs ko,zh,id --file-parallel 3
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import time
import warnings
import logging
from datetime import datetime, timezone
from pathlib import Path

# Suppress google-genai SDK warnings about thinking model thought_signature parts.
# We only use response.text — the thinking trace is not analyzed.
warnings.filterwarnings("ignore", message=".*non-text parts.*")
logging.getLogger("google_genai").setLevel(logging.ERROR)
# Suppress Python 3.9 EOL and LibreSSL warnings — not actionable during translation.
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")
warnings.filterwarnings("ignore", message=".*urllib3.*OpenSSL.*")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Allow an external caller (e.g. agy-cli-field-workshop) to override the repo
# root via an env var so the script can locate source files correctly.
import os as _os
_env_root = _os.environ.get("AGY_REPO_ROOT")
REPO_ROOT = Path(_env_root).resolve() if _env_root else Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = Path(__file__).resolve().parent  # always the i18n tools dir
MANIFEST_PATH = TOOLS_DIR / ".translation-manifest.json"

# The translatable workshop docs (must match actual files in docs/)
TRANSLATABLE_DOCS = [
    "docs/index.md",
    "docs/setup.md",
    "docs/sdlc-productivity.md",
    "docs/plugin-ecosystem.md",
    "docs/devops-automation.md",
    "docs/multi-agent-advanced.md",
    "docs/legacy-modernization.md",
    "docs/agy-sdk.md",
    "docs/cheatsheet.md",
    "docs/facilitator-guide.md",
    "docs/exercises/ex01_first_session.md",
    "docs/exercises/ex02_plugin_bridge.md",
    "docs/exercises/ex02b_first_sidecar.md",
    "docs/exercises/ex03_print_mode_pipeline.md",
    "docs/exercises/ex04_subagents.md",
    "docs/exercises/ex05_btw_scheduling.md",
    "docs/exercises/ex06_sandbox_governance.md",
    "docs/exercises/ex07_migration_walkthrough.md",
    "docs/exercises/ex08_dotnet_modernization.md",
    "docs/exercises/ex09_java_upgrade.md",
    "docs/exercises/ex10_first_agent.md",
    "docs/exercises/ex11_multi_agent_pipeline.md",
    "docs/exercises/ex12_agents_cli_lifecycle.md",
]

# Regex for fenced code blocks (``` with optional language tag)
CODE_BLOCK_RE = re.compile(r"(```[\w-]*\n.*?\n```)", re.DOTALL)

# Regex for markdown links: [text](path)
LINK_RE = re.compile(r"(\[.*?\])\(((?!http|#).*?)\)")


# ---------------------------------------------------------------------------
# Glossary loading
# ---------------------------------------------------------------------------

def load_glossary(lang: str) -> dict:
    """Load glossary from the markdown table format."""
    glossary_path = TOOLS_DIR / f"glossary-{lang}.md"
    if not glossary_path.exists():
        print(f"❌ Glossary not found: {glossary_path}")
        sys.exit(1)

    content = glossary_path.read_text(encoding="utf-8")
    result = {"never_translate": [], "terms": {}}

    # Extract never-translate block (between "## Never Translate" and next "##")
    never_match = re.search(
        r"## Never Translate\n\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if never_match:
        raw = never_match.group(1).strip()
        # Split on commas, clean up
        items = [item.strip() for item in raw.replace("\n", ",").split(",")]
        result["never_translate"] = [i for i in items if i]

    # Extract term table rows
    for line in content.split("\n"):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| English"):
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]  # Remove empty from leading/trailing |
        if len(parts) >= 2:
            result["terms"][parts[0]] = parts[1]

    return result


# ---------------------------------------------------------------------------
# Code block extraction / reinsertion
# ---------------------------------------------------------------------------

def extract_code_blocks(text: str) -> tuple[str, list[str]]:
    """Replace code blocks with numbered placeholders. Returns (text, blocks)."""
    blocks = []

    def replacer(match):
        blocks.append(match.group(1))
        return f"⟦CODE_BLOCK_{len(blocks)}⟧"

    cleaned = CODE_BLOCK_RE.sub(replacer, text)
    return cleaned, blocks


def reinsert_code_blocks(text: str, blocks: list[str]) -> str:
    """Put code blocks back in place of placeholders."""
    for i, block in enumerate(blocks, 1):
        text = text.replace(f"⟦CODE_BLOCK_{i}⟧", block)
    return text


# ---------------------------------------------------------------------------
# Link rewriting
# ---------------------------------------------------------------------------

def rewrite_links_for_lang(text: str) -> str:
    """Adjust relative links for one level deeper (docs/ko/ instead of docs/).

    Same-directory .md links that point to files NOT in TRANSLATABLE_DOCS
    are rewritten to relative paths that resolve against the English root
    instead of the language directory.
    """
    # Build set of translated basenames for fast lookup
    translated_basenames = {Path(f).name for f in TRANSLATABLE_DOCS}

    def rewrite(match):
        link_text = match.group(1)
        path = match.group(2)
        # Add one ../ for paths that go up to samples/, exercises/, etc.
        if path.startswith("../"):
            path = "../" + path
        # Asset paths (relative within docs/)
        elif path.startswith("assets/"):
            path = "../" + path
        # Same-directory .md links: check if the target is translated
        elif path.endswith(".md") and "/" not in path:
            if path not in translated_basenames:
                # Not translated — relative link up to docs/ root
                path = f"../{path}"
        # Other same-directory doc links stay as-is (docsify resolves within lang/)
        return f"{link_text}({path})"

    return LINK_RE.sub(rewrite, text)


# ---------------------------------------------------------------------------
# Translation via Gemini API
# ---------------------------------------------------------------------------

def build_system_prompt(glossary: dict, lang: str) -> str:
    """Build the system prompt with glossary and rules."""
    never_list = ", ".join(glossary["never_translate"][:50])
    term_lines = "\n".join(
        f"  - {eng} → {kor}" for eng, kor in glossary["terms"].items()
    )

    lang_names = {"ko": "Korean", "ja": "Japanese", "zh": "Chinese (Simplified)",
                  "th": "Thai", "vi": "Vietnamese", "id": "Indonesian",
                  "ms": "Malay", "tl": "Filipino", "my": "Burmese", "km": "Khmer"}
    lang_name = lang_names.get(lang, lang)

    return f"""You are translating technical workshop documentation from English to {lang_name}.

RULES — follow these exactly:
1. NEVER translate text inside ⟦CODE_BLOCK_N⟧ placeholders — leave them exactly as they appear.
2. NEVER translate: {never_list}
3. Preserve ALL markdown structure exactly: headings, tables, code fences, blockquotes, links, images, HTML tags.
4. Use these term translations consistently:
{term_lines}
5. Translate EVERY section — do not summarize, skip, or omit any content.
6. Output the COMPLETE translated document — partial output is a failure.
7. Do not add any commentary, notes, or explanations — output only the translated markdown.
8. Keep all markdown link paths exactly as they appear — only translate the link display text."""

# Cached client singleton
_client = None
_auth_mode = None


def get_client():
    """Create a Gemini client, auto-detecting API key vs Vertex AI (GCP)."""
    global _client, _auth_mode
    if _client is not None:
        return _client, _auth_mode

    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    if api_key:
        _client = genai.Client(api_key=api_key)
        _auth_mode = "API Key"
    elif project:
        _client = genai.Client(
            vertexai=True,
            project=project,
            location=location,
        )
        _auth_mode = f"Vertex AI ({project}/{location})"
    else:
        print("❌ No credentials found. Set one of:")
        print("   GEMINI_API_KEY or GOOGLE_API_KEY  (API key mode)")
        print("   GOOGLE_CLOUD_PROJECT              (Vertex AI mode)")
        sys.exit(1)

    return _client, _auth_mode


def translate_section(section: str, system_prompt: str, model_name: str) -> str:
    """Translate a single section using the Gemini API."""
    from google import genai

    client, _ = get_client()
    response = client.models.generate_content(
        model=model_name,
        contents=section,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            top_p=0.9,
        ),
    )
    return response.text


def translate_file(
    source_path: Path,
    lang: str,
    glossary: dict,
    model_name: str = "gemini-3.1-pro-preview",
    dry_run: bool = False,
    file_num: int = 0,
    file_total: int = 0,
    **kwargs,
) -> dict:
    """Translate a single file. Returns stats dict."""
    content = source_path.read_text(encoding="utf-8")
    src_lines = content.count("\n") + 1

    # Determine output path
    rel = source_path.relative_to(REPO_ROOT)
    parts = list(rel.parts)
    # docs/setup.md → docs/ko/setup.md
    parts.insert(1, lang)
    output_path = REPO_ROOT / Path(*parts)

    if dry_run:
        print(f"  [dry-run] {rel} → {output_path.relative_to(REPO_ROOT)}")
        return {"file": rel.name, "status": "dry-run"}

    counter = f"[{file_num}/{file_total}]" if file_total else ""
    print(f"\n{'─' * 56}")
    print(f"  📄 {counter} {rel}")

    # 1. Extract code blocks
    text_without_code, code_blocks = extract_code_blocks(content)
    print(f"     {src_lines} lines, {len(code_blocks)} code blocks extracted")

    # 2. Split into sections on ## headings for better isolation
    sections = re.split(r"(?=^## )", text_without_code, flags=re.MULTILINE)
    non_empty = [s for s in sections if s.strip()]
    print(f"     {len(non_empty)} sections to translate")

    # 3. Translate each section (parallel within file)
    system_prompt = build_system_prompt(glossary, lang)
    translated_sections = [None] * len(sections)
    failures = 0
    file_start = time.time()
    max_workers = kwargs.get("max_workers", 4)

    # Identify which sections need translation
    work_items = []
    for i, section in enumerate(sections):
        if not section.strip():
            translated_sections[i] = section
        else:
            work_items.append((i, section))

    def _translate_one(idx, section_text):
        start = time.time()
        result = translate_section(section_text, system_prompt, model_name)
        elapsed = time.time() - start
        heading = ""
        heading_match = re.search(r"^##+ (.+)", section_text, re.MULTILINE)
        if heading_match:
            heading = f" — {heading_match.group(1)[:40]}"
        return idx, result, elapsed, heading

    with ThreadPoolExecutor(max_workers=min(max_workers, len(work_items) or 1)) as pool:
        futures = {
            pool.submit(_translate_one, idx, sec): idx
            for idx, sec in work_items
        }
        try:
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    idx, translated, elapsed, heading = future.result()
                    translated_sections[idx] = translated
                    print(f"     ✅ Section {idx + 1}/{len(sections)}{heading} ({elapsed:.1f}s)")
                except Exception as e:
                    print(f"     ❌ Section {idx + 1} failed: {e}")
                    print(f"        Keeping English for this section.")
                    translated_sections[idx] = sections[idx]
                    failures += 1
        except KeyboardInterrupt:
            print(f"\n     ⚠️  Interrupted — cancelling remaining sections...")
            for f in futures:
                f.cancel()
            # Fill untranslated sections with English
            for i, s in enumerate(translated_sections):
                if s is None:
                    translated_sections[i] = sections[i]
                    failures += 1
            raise  # Re-raise to be caught by the main loop

    # 4. Reassemble
    translated_text = "\n".join(translated_sections)

    # 5. Reinsert code blocks (verbatim)
    translated_text = reinsert_code_blocks(translated_text, code_blocks)

    # 6. Rewrite links for lang/ depth
    translated_text = rewrite_links_for_lang(translated_text)

    # Ensure trailing newline for markdown lint (MD047)
    if not translated_text.endswith("\n"):
        translated_text += "\n"

    # 7. Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(translated_text, encoding="utf-8")

    out_lines = translated_text.count("\n") + 1
    file_elapsed = time.time() - file_start
    print(f"     → {output_path.relative_to(REPO_ROOT)} ({out_lines} lines, {file_elapsed:.1f}s)")

    return {
        "file": rel.name,
        "src_lines": src_lines,
        "out_lines": out_lines,
        "sections": len(non_empty),
        "code_blocks": len(code_blocks),
        "failures": failures,
        "elapsed": file_elapsed,
    }


# ---------------------------------------------------------------------------
# Manifest management
# ---------------------------------------------------------------------------

def git_blob_hash(filepath: Path) -> str:
    """Get the git blob hash of a file, or fall back to content hash."""
    try:
        result = subprocess.run(
            ["git", "hash-object", str(filepath)],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    # Fallback: SHA256 of content
    content = filepath.read_bytes()
    return hashlib.sha256(content).hexdigest()[:12]


def update_manifest(lang: str, source_path: Path):
    """Record the source hash at translation time."""
    manifest = {}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    if lang not in manifest:
        manifest[lang] = {}

    rel = str(source_path.relative_to(REPO_ROOT))
    manifest[lang][rel] = {
        "source_sha": git_blob_hash(source_path),
        "translated_at": datetime.now(timezone.utc).isoformat(),
    }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable duration."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.0f}s"


def _translate_one_file(file_path, lang, glossary, model_name, file_num, file_total, max_workers):
    """Wrapper for translate_file that handles errors gracefully.
    Used by both sequential and parallel execution paths."""
    try:
        stats = translate_file(
            file_path, lang, glossary, model_name,
            file_num=file_num, file_total=file_total,
            max_workers=max_workers,
        )
        update_manifest(lang, file_path)
        return stats
    except Exception as e:
        print(f"  ❌ {file_path.name} failed: {e}")
        return {"file": file_path.name, "status": "error", "error": str(e)}


def translate_lang(lang, files, model_name, dry_run, max_section_workers, max_file_workers):
    """Translate all files for a single language.
    Supports file-level parallelism via max_file_workers > 1."""

    glossary = load_glossary(lang)
    _, auth_mode = get_client()

    lang_names = {"ko": "Korean", "ja": "Japanese", "zh": "Chinese",
                  "th": "Thai", "vi": "Vietnamese", "id": "Indonesian",
                  "ms": "Malay", "tl": "Filipino", "my": "Burmese", "km": "Khmer"}
    lang_name = lang_names.get(lang, lang)

    print(f"\n{'═' * 56}")
    print(f"  🌐 AGY CLI Workshop — Translation Pipeline")
    print(f"{'═' * 56}")
    print(f"  Target:   {lang_name} ({lang})")
    print(f"  Model:    {model_name}")
    print(f"  Auth:     {auth_mode}")
    print(f"  Files:    {len(files)}")
    print(f"  Glossary: {len(glossary['never_translate'])} protected, "
          f"{len(glossary['terms'])} translated terms")
    print(f"  Workers:  {max_section_workers}/section, {max_file_workers}/file")

    if dry_run:
        print(f"\n🔍 Dry run — no API calls will be made:\n")
        for f in files:
            translate_file(f, lang, glossary, model_name, dry_run=True)
        return []

    total_start = time.time()
    valid_files = [(i, f) for i, f in enumerate(files, 1) if f.exists()]
    for _, f in [(i, f) for i, f in enumerate(files, 1) if not f.exists()]:
        print(f"\n  ⚠️  Skipping {f} (not found)")

    results = []
    interrupted = False

    try:
        if max_file_workers > 1 and len(valid_files) > 1:
            # File-level parallelism: translate multiple files concurrently
            with ThreadPoolExecutor(max_workers=min(max_file_workers, len(valid_files))) as pool:
                futures = {
                    pool.submit(
                        _translate_one_file, f, lang, glossary, model_name,
                        i, len(files), max_section_workers
                    ): f.name
                    for i, f in valid_files
                }
                for future in as_completed(futures):
                    stats = future.result()
                    if stats:
                        results.append(stats)
        else:
            # Sequential: one file at a time
            for i, f in valid_files:
                stats = _translate_one_file(
                    f, lang, glossary, model_name,
                    i, len(files), max_section_workers
                )
                results.append(stats)
    except KeyboardInterrupt:
        interrupted = True
        print(f"\n\n{'─' * 56}")
        print(f"  ⚠️  Interrupted by user (Ctrl+C)")
        print(f"{'─' * 56}")

    # Summary
    total_elapsed = time.time() - total_start
    total_src = sum(r.get("src_lines", 0) for r in results)
    total_out = sum(r.get("out_lines", 0) for r in results)
    total_failures = sum(r.get("failures", 0) for r in results)

    status = "⚠️  Translation Interrupted" if interrupted else "✅ Translation Complete"
    print(f"\n{'═' * 56}")
    print(f"  {status} — {lang_name}")
    print(f"{'═' * 56}")
    if results:
        print(f"  {'File':<30} {'Source':>6} {'Output':>6} {'Time':>8}")
        print(f"  {'─' * 52}")
        for r in results:
            elapsed = r.get('elapsed', 0)
            print(f"  {r.get('file', '?'):<30} "
                  f"{r.get('src_lines', '-'):>6} "
                  f"{r.get('out_lines', '-'):>6} "
                  f"{format_duration(elapsed) if elapsed else '-':>8}")
        print(f"  {'─' * 52}")
        print(f"  {'Total':<30} {total_src:>6} {total_out:>6} {format_duration(total_elapsed):>8}")
    else:
        print(f"  No files were completed.")

    if total_failures > 0:
        print(f"\n  ⚠️  {total_failures} section(s) failed — English preserved.")

    print(f"\n  ℹ️  Run: make post-translate L={lang}  to normalize lint")
    return results


def main():
    parser = argparse.ArgumentParser(description="Translate workshop docs")
    parser.add_argument("files", nargs="*", help="Source files to translate")
    parser.add_argument("--lang", help="Target language code (e.g., ko)")
    parser.add_argument("--langs", help="Comma-separated language codes for multi-lang parallel (e.g., ko,zh,id)")
    parser.add_argument("--all", action="store_true", help="Translate all workshop docs")
    parser.add_argument("--model", default="gemini-3.1-pro-preview", help="Gemini model")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be translated")
    parser.add_argument("--parallel", type=int, default=4,
                        help="Max parallel API calls per file section (default: 4)")
    parser.add_argument("--file-parallel", type=int, default=1,
                        help="Max files to translate concurrently per language (default: 1, sequential)")
    args = parser.parse_args()

    # Validate language args
    if not args.lang and not args.langs:
        parser.error("Specify --lang or --langs")

    # Determine languages
    if args.langs:
        languages = [l.strip() for l in args.langs.split(",") if l.strip()]
    else:
        languages = [args.lang]

    # Determine files
    if args.all:
        files = [REPO_ROOT / f for f in TRANSLATABLE_DOCS]
    elif args.files:
        files = [Path(f).resolve() for f in args.files]
    else:
        parser.error("Specify files or use --all")

    # Multi-language: run each language as a subprocess for true parallelism
    if len(languages) > 1:
        import multiprocessing
        print(f"{'═' * 56}")
        print(f"  🌐 Multi-Language Parallel Translation")
        print(f"{'═' * 56}")
        print(f"  Languages: {', '.join(languages)}")
        print(f"  Files:     {len(files)}")
        print(f"  Strategy:  {len(languages)} language processes × "
              f"{args.file_parallel} file workers × {args.parallel} section workers")
        print(f"{'═' * 56}")

        total_start = time.time()
        procs = []
        for lang in languages:
            cmd = [
                sys.executable, str(Path(__file__).resolve()),
                "--lang", lang,
                "--model", args.model,
                "--parallel", str(args.parallel),
                "--file-parallel", str(args.file_parallel),
            ]
            if args.all:
                cmd.append("--all")
            else:
                cmd.extend(str(f) for f in files)
            if args.dry_run:
                cmd.append("--dry-run")

            # Inherit all env vars including GOOGLE_CLOUD_PROJECT
            proc = subprocess.Popen(
                cmd,
                env={**os.environ, "AGY_REPO_ROOT": str(REPO_ROOT)},
                cwd=str(REPO_ROOT),
            )
            procs.append((lang, proc))

        # Wait for all
        failures = []
        for lang, proc in procs:
            proc.wait()
            if proc.returncode != 0:
                failures.append(lang)

        total_elapsed = time.time() - total_start
        print(f"\n{'═' * 56}")
        if failures:
            print(f"  ⚠️  Multi-language translation completed with errors")
            print(f"  Failed: {', '.join(failures)}")
        else:
            print(f"  ✅ All {len(languages)} languages translated")
        print(f"  Wall time: {format_duration(total_elapsed)}")
        print(f"{'═' * 56}")
        print(f"\n  Next: run 'make post-translate L=<lang>' for each language")
        sys.exit(1 if failures else 0)

    # Single language path
    translate_lang(
        languages[0], files, args.model, args.dry_run,
        max_section_workers=args.parallel,
        max_file_workers=args.file_parallel,
    )


if __name__ == "__main__":
    main()
