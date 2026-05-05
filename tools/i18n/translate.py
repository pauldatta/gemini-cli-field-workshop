#!/usr/bin/env python3
"""
Translate workshop markdown files using the Gemini API.

Usage:
    python tools/i18n/translate.py docs/setup.md --lang ko
    python tools/i18n/translate.py --all --lang ko
    python tools/i18n/translate.py docs/setup.md --lang ko --dry-run
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
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # public-workshop/
TOOLS_DIR = REPO_ROOT / "tools" / "i18n"
MANIFEST_PATH = TOOLS_DIR / ".translation-manifest.json"

# The 7 workshop docs that get translated
TRANSLATABLE_DOCS = [
    "docs/setup.md",
    "docs/sdlc-productivity.md",
    "docs/legacy-modernization.md",
    "docs/devops-orchestration.md",
    "docs/advanced-patterns.md",
    "docs/extensions-ecosystem.md",
    "docs/cheatsheet.md",
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
    """Adjust relative links for one level deeper (docs/ko/ instead of docs/)."""

    def rewrite(match):
        link_text = match.group(1)
        path = match.group(2)
        # Add one ../ for paths that go up to samples/, exercises/, etc.
        if path.startswith("../"):
            path = "../" + path
        # Asset paths (relative within docs/)
        elif path.startswith("assets/"):
            path = "../" + path
        # Same-directory doc links stay as-is (docsify resolves within ko/)
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

    lang_names = {"ko": "Korean", "ja": "Japanese", "zh": "Chinese"}
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
# Sidebar generation
# ---------------------------------------------------------------------------

def generate_sidebar(lang: str, glossary: dict):
    """Generate a translated _sidebar.md for the language.

    Only translates the display text inside [...], never the link targets
    inside (...). Uses absolute paths so Docsify routes correctly:
    - Translated files:   /{lang}/file.md
    - Untranslated files: /file.md  (falls back to English)
    """
    source = REPO_ROOT / "docs" / "_sidebar.md"
    if not source.exists():
        print("  ⚠️  No _sidebar.md found, skipping sidebar generation")
        return

    lines = source.read_text(encoding="utf-8").splitlines()
    out_lines = []

    # Files that exist in the translated directory
    translated_dir = REPO_ROOT / "docs" / lang
    translated_files = {f.name for f in translated_dir.glob("*.md")} if translated_dir.exists() else set()

    for line in lines:
        # Check if line has a link to a .md file
        link_match = re.search(r'\(([^)]+\.md)\)', line)
        untranslated = False
        if link_match:
            target = link_match.group(1)
            if target not in translated_files and target != '/':
                untranslated = True

        # Only translate display text inside [...], rewrite link targets
        def translate_display(m):
            display = m.group(1)
            target = m.group(2)
            for eng, translated in glossary["terms"].items():
                display = display.replace(eng, translated)
            # Rewrite link targets to absolute Docsify routes
            if target == '/':
                # Home link stays in the language context
                target = f"/{lang}/"
            elif target.endswith('.md'):
                if untranslated:
                    # Untranslated: link to English root
                    target = f"/{target}"
                else:
                    # Translated: link within language directory
                    target = f"/{lang}/{target}"
            return f"[{display}]({target})"

        line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', translate_display, line)

        # Translate bold text like **Use Cases**
        for eng, translated in glossary["terms"].items():
            if f"**{eng}**" in line:
                line = line.replace(f"**{eng}**", f"**{translated}**")

        out_lines.append(line)

    # Add language switch link
    out_lines.append("")
    out_lines.append("* [🇺🇸 English](/)")
    out_lines.append("")

    content = "\n".join(out_lines)
    output = REPO_ROOT / "docs" / lang / "_sidebar.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"  → docs/{lang}/_sidebar.md")


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


def main():
    parser = argparse.ArgumentParser(description="Translate workshop docs")
    parser.add_argument("files", nargs="*", help="Source files to translate")
    parser.add_argument("--lang", required=True, help="Target language code (e.g., ko)")
    parser.add_argument("--all", action="store_true", help="Translate all workshop docs")
    parser.add_argument("--model", default="gemini-3.1-pro-preview", help="Gemini model")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be translated")
    parser.add_argument("--parallel", type=int, default=4,
                        help="Max parallel API calls per file (default: 4)")
    args = parser.parse_args()

    # Determine files
    if args.all:
        files = [REPO_ROOT / f for f in TRANSLATABLE_DOCS]
    elif args.files:
        files = [Path(f).resolve() for f in args.files]
    else:
        parser.error("Specify files or use --all")

    # Load glossary and init client
    glossary = load_glossary(args.lang)
    _, auth_mode = get_client()

    lang_names = {"ko": "Korean", "ja": "Japanese", "zh": "Chinese",
                  "th": "Thai", "vi": "Vietnamese", "id": "Indonesian",
                  "ms": "Malay", "tl": "Filipino", "my": "Burmese", "km": "Khmer"}
    lang_name = lang_names.get(args.lang, args.lang)

    print(f"{'═' * 56}")
    print(f"  🌐 Gemini CLI Workshop — Translation Pipeline")
    print(f"{'═' * 56}")
    print(f"  Target:   {lang_name} ({args.lang})")
    print(f"  Model:    {args.model}")
    print(f"  Auth:     {auth_mode}")
    print(f"  Files:    {len(files)}")
    print(f"  Glossary: {len(glossary['never_translate'])} protected, "
          f"{len(glossary['terms'])} translated terms")

    if args.dry_run:
        print(f"\n🔍 Dry run — no API calls will be made:\n")
        for f in files:
            translate_file(f, args.lang, glossary, args.model, dry_run=True)
        return

    total_start = time.time()
    results = []

    print(f"  Parallel: {args.parallel} workers per file")

    for i, f in enumerate(files, 1):
        if not f.exists():
            print(f"\n  ⚠️  Skipping {f} (not found)")
            continue
        stats = translate_file(
            f, args.lang, glossary, args.model,
            file_num=i, file_total=len(files),
            max_workers=args.parallel,
        )
        results.append(stats)
        update_manifest(args.lang, f)

    # Generate sidebar
    print(f"\n{'─' * 56}")
    print("  📑 Generating sidebar...")
    generate_sidebar(args.lang, glossary)

    # Summary
    total_elapsed = time.time() - total_start
    total_src = sum(r.get("src_lines", 0) for r in results)
    total_out = sum(r.get("out_lines", 0) for r in results)
    total_failures = sum(r.get("failures", 0) for r in results)

    print(f"\n{'═' * 56}")
    print(f"  ✅ Translation Complete")
    print(f"{'═' * 56}")
    print(f"  {'File':<30} {'Source':>6} {'Output':>6} {'Time':>8}")
    print(f"  {'─' * 52}")
    for r in results:
        print(f"  {r.get('file', '?'):<30} "
              f"{r.get('src_lines', '?'):>6} "
              f"{r.get('out_lines', '?'):>6} "
              f"{format_duration(r.get('elapsed', 0)):>8}")
    print(f"  {'─' * 52}")
    print(f"  {'Total':<30} {total_src:>6} {total_out:>6} {format_duration(total_elapsed):>8}")

    if total_failures > 0:
        print(f"\n  ⚠️  {total_failures} section(s) failed — English preserved for those sections.")

    print(f"\n  Next: make translate-validate L={args.lang}")


if __name__ == "__main__":
    main()
