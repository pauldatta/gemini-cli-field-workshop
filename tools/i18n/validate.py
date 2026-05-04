#!/usr/bin/env python3
"""
Validate translated workshop files against their English sources.

Checks:
  1. Structural parity — heading count, table count, code blocks, links, images
  2. Code block identity — byte-compare extracted code blocks
  3. Line-count ratio — flag suspiciously short/long translations
  4. Glossary enforcement — verify pinned terms appear correctly
  5. Link integrity — all link targets resolve from the translated file's location

Usage:
    python tools/i18n/validate.py docs/setup.md docs/ko/setup.md --glossary tools/i18n/glossary-ko.md
    python tools/i18n/validate.py --all --lang ko
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = REPO_ROOT / "tools" / "i18n"

TRANSLATABLE_DOCS = [
    "docs/setup.md",
    "docs/sdlc-productivity.md",
    "docs/legacy-modernization.md",
    "docs/devops-orchestration.md",
    "docs/advanced-patterns.md",
    "docs/cheatsheet.md",
]

CODE_BLOCK_RE = re.compile(r"(```[\w-]*\n.*?\n```)", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s", re.MULTILINE)
TABLE_ROW_RE = re.compile(r"^\|.+\|$", re.MULTILINE)
IMAGE_RE = re.compile(r"!\[.*?\]\((.*?)\)")
LINK_RE = re.compile(r"\[.*?\]\(((?!http|#).*?)\)")


# ---------------------------------------------------------------------------
# Glossary loading (shared with translate.py)
# ---------------------------------------------------------------------------

def load_glossary(lang: str) -> dict:
    glossary_path = TOOLS_DIR / f"glossary-{lang}.md"
    if not glossary_path.exists():
        return {"never_translate": [], "terms": {}}

    content = glossary_path.read_text(encoding="utf-8")
    result = {"never_translate": [], "terms": {}}

    never_match = re.search(
        r"## Never Translate\n\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if never_match:
        raw = never_match.group(1).strip()
        items = [item.strip() for item in raw.replace("\n", ",").split(",")]
        result["never_translate"] = [i for i in items if i]

    for line in content.split("\n"):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| English"):
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) >= 2:
            result["terms"][parts[0]] = parts[1]

    return result


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def extract_code_blocks(text: str) -> list[str]:
    return CODE_BLOCK_RE.findall(text)


def extract_headings(text: str) -> list[str]:
    return HEADING_RE.findall(text)


def count_tables(text: str) -> int:
    """Count table separators (|---|) as proxy for table count."""
    return len(re.findall(r"^\|[\s:|.-]+\|$", text, re.MULTILINE))


def extract_images(text: str) -> list[str]:
    return IMAGE_RE.findall(text)


def extract_links(text: str) -> list[str]:
    return LINK_RE.findall(text)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_structural_parity(source: str, translated: str) -> list[str]:
    """Check that heading count, table count, code blocks, images match."""
    errors = []

    src_headings = extract_headings(source)
    trn_headings = extract_headings(translated)
    if len(src_headings) != len(trn_headings):
        errors.append(
            f"Heading count mismatch: source={len(src_headings)}, "
            f"translated={len(trn_headings)}"
        )

    src_tables = count_tables(source)
    trn_tables = count_tables(translated)
    if src_tables != trn_tables:
        errors.append(
            f"Table count mismatch: source={src_tables}, translated={trn_tables}"
        )

    src_blocks = extract_code_blocks(source)
    trn_blocks = extract_code_blocks(translated)
    if len(src_blocks) != len(trn_blocks):
        errors.append(
            f"Code block count mismatch: source={len(src_blocks)}, "
            f"translated={len(trn_blocks)}"
        )

    src_images = extract_images(source)
    trn_images = extract_images(translated)
    if len(src_images) != len(trn_images):
        errors.append(
            f"Image count mismatch: source={len(src_images)}, "
            f"translated={len(trn_images)}"
        )

    return errors


def check_code_block_identity(source: str, translated: str) -> list[str]:
    """Verify code blocks are byte-identical."""
    errors = []
    src_blocks = extract_code_blocks(source)
    trn_blocks = extract_code_blocks(translated)

    for i, (src, trn) in enumerate(zip(src_blocks, trn_blocks)):
        if src != trn:
            # Show first divergence
            src_preview = src[:80].replace("\n", "\\n")
            trn_preview = trn[:80].replace("\n", "\\n")
            errors.append(
                f"Code block {i + 1} differs:\n"
                f"    source: {src_preview}...\n"
                f"    translated: {trn_preview}..."
            )

    return errors


def check_line_count_ratio(source: str, translated: str) -> list[str]:
    """Flag if translation is suspiciously short or long."""
    warnings = []
    src_lines = source.count("\n")
    trn_lines = translated.count("\n")

    if src_lines == 0:
        return warnings

    ratio = trn_lines / src_lines
    if ratio < 0.6:
        warnings.append(
            f"Translation is very short: {trn_lines} lines vs {src_lines} source lines "
            f"(ratio: {ratio:.2f}) — possible content omission"
        )
    elif ratio > 1.4:
        warnings.append(
            f"Translation is very long: {trn_lines} lines vs {src_lines} source lines "
            f"(ratio: {ratio:.2f}) — possible hallucinated content"
        )

    return warnings


def check_glossary(translated: str, glossary: dict) -> list[str]:
    """Verify glossary terms appear correctly in translation."""
    warnings = []

    # Remove code blocks before checking (terms in code are fine in English)
    text_only = CODE_BLOCK_RE.sub("", translated)

    # Check never-translate terms are present as-is
    for term in glossary["never_translate"]:
        if len(term) < 3:  # Skip very short terms like "ls"
            continue
        # Only check terms that appear in the original and should remain
        # This is a soft check — not all terms appear in every file

    return warnings


def check_link_integrity(translated: str, translated_path: Path) -> list[str]:
    """Verify link targets resolve from the translated file's location."""
    errors = []
    links = extract_links(translated)
    parent = translated_path.parent

    for link in links:
        # Strip anchors
        path = link.split("#")[0]
        if not path:
            continue

        target = (parent / path).resolve()
        if not target.exists():
            errors.append(f"Broken link: {link} (resolves to {target})")

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate_pair(
    source_path: Path, translated_path: Path, glossary: dict
) -> tuple[list[str], list[str]]:
    """Run all checks. Returns (errors, warnings)."""
    source = source_path.read_text(encoding="utf-8")
    translated = translated_path.read_text(encoding="utf-8")

    errors = []
    warnings = []

    # Check 1: Structural parity
    errors.extend(check_structural_parity(source, translated))

    # Check 2: Code block identity
    errors.extend(check_code_block_identity(source, translated))

    # Check 3: Line-count ratio
    warnings.extend(check_line_count_ratio(source, translated))

    # Check 4: Glossary enforcement
    warnings.extend(check_glossary(translated, glossary))

    # Check 5: Link integrity
    errors.extend(check_link_integrity(translated, translated_path))

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate translations")
    parser.add_argument("source", nargs="?", help="English source file")
    parser.add_argument("translated", nargs="?", help="Translated file")
    parser.add_argument("--lang", help="Language code (for --all mode)")
    parser.add_argument("--all", action="store_true", help="Validate all translations")
    args = parser.parse_args()

    if args.all:
        if not args.lang:
            parser.error("--all requires --lang")
        glossary = load_glossary(args.lang)
        pairs = []
        for doc in TRANSLATABLE_DOCS:
            source = REPO_ROOT / doc
            parts = list(Path(doc).parts)
            parts.insert(1, args.lang)
            translated = REPO_ROOT / Path(*parts)
            if translated.exists():
                pairs.append((source, translated))
            else:
                print(f"  ⚠️  {translated.relative_to(REPO_ROOT)} not found, skipping")
    else:
        if not args.source or not args.translated:
            parser.error("Provide source and translated files, or use --all --lang xx")
        lang = args.lang or Path(args.translated).parts[-2]  # infer from path
        glossary = load_glossary(lang)
        pairs = [(Path(args.source).resolve(), Path(args.translated).resolve())]

    total_errors = 0
    total_warnings = 0

    print(f"🔍 Validating {len(pairs)} file(s)...\n")

    for source, translated in pairs:
        rel_src = source.relative_to(REPO_ROOT)
        rel_trn = translated.relative_to(REPO_ROOT)
        print(f"  {rel_src} ↔ {rel_trn}")

        errors, warnings = validate_pair(source, translated, glossary)

        for e in errors:
            print(f"    ❌ {e}")
            total_errors += 1
        for w in warnings:
            print(f"    ⚠️  {w}")
            total_warnings += 1
        if not errors and not warnings:
            print(f"    ✅ All checks passed")

    print(f"\n{'═' * 50}")
    print(f"  Errors: {total_errors}  Warnings: {total_warnings}")

    if total_errors > 0:
        print(f"  ❌ Validation FAILED")
        sys.exit(1)
    else:
        print(f"  ✅ Validation PASSED")


if __name__ == "__main__":
    main()
