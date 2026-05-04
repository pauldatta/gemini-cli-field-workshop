#!/usr/bin/env python3
"""
Check translation drift by comparing the manifest against current source files.

The manifest records the git blob hash of each English source file at the time
it was translated. This script compares those hashes to the current state.

Usage:
    python tools/i18n/drift.py --lang ko
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = REPO_ROOT / "tools" / "i18n"
MANIFEST_PATH = TOOLS_DIR / ".translation-manifest.json"

TRANSLATABLE_DOCS = [
    "docs/setup.md",
    "docs/sdlc-productivity.md",
    "docs/legacy-modernization.md",
    "docs/devops-orchestration.md",
    "docs/advanced-patterns.md",
    "docs/cheatsheet.md",
]


def git_blob_hash(filepath: Path) -> str:
    """Get the git blob hash of a file."""
    try:
        result = subprocess.run(
            ["git", "hash-object", str(filepath)],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    import hashlib
    return hashlib.sha256(filepath.read_bytes()).hexdigest()[:12]


def main():
    parser = argparse.ArgumentParser(description="Check translation drift")
    parser.add_argument("--lang", required=True, help="Language code (e.g., ko)")
    args = parser.parse_args()

    if not MANIFEST_PATH.exists():
        print(f"⚠️  No manifest found at {MANIFEST_PATH}")
        print(f"   Run 'make translate LANG={args.lang}' first.")
        sys.exit(0)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    lang_manifest = manifest.get(args.lang, {})

    if not lang_manifest:
        print(f"⚠️  No translations recorded for '{args.lang}' in manifest.")
        print(f"   Run 'make translate LANG={args.lang}' first.")
        sys.exit(0)

    print(f"📊 Translation Drift Report ({args.lang})")
    print(f"{'═' * 60}\n")

    stale_count = 0
    current_count = 0
    missing_count = 0

    for doc in TRANSLATABLE_DOCS:
        source_path = REPO_ROOT / doc
        basename = Path(doc).name

        if not source_path.exists():
            continue

        entry = lang_manifest.get(doc)

        if not entry:
            print(f"  ⚠️  {basename:<30} NOT TRANSLATED")
            missing_count += 1
            continue

        current_hash = git_blob_hash(source_path)
        recorded_hash = entry["source_sha"]
        translated_at = entry["translated_at"][:10]  # Just the date

        if current_hash == recorded_hash:
            print(f"  ✅ {basename:<30} current (translated {translated_at})")
            current_count += 1
        else:
            print(f"  ⚠️  {basename:<30} STALE (translated {translated_at})")
            print(f"      → git diff {recorded_hash}..HEAD -- {doc}")
            stale_count += 1

    print(f"\n{'═' * 60}")
    print(f"  Current: {current_count}  Stale: {stale_count}  Missing: {missing_count}")

    if stale_count > 0:
        print(f"\n  Re-translate stale files with:")
        print(f"    make translate LANG={args.lang}")


if __name__ == "__main__":
    main()
