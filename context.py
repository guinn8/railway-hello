#!/usr/bin/env python3
import argparse, subprocess, sys, tempfile
from pathlib import Path

def collect(root: Path, want_app: bool, want_tests: bool) -> list[Path]:
    files = [root / "main.py", root / "requirements.txt"]

    def add(pattern):
        files.extend(p for p in pattern if p.is_file())

    if not want_app and not want_tests:  # default = current behaviour
        add((root / "app").glob("*.py"))
        add((root / "app" / "prompts").rglob("*.md"))
    else:
        if want_app:
            add((root / "app").glob("*.py"))
            add((root / "app" / "prompts").rglob("*.md"))
        if want_tests:
            add((root / "tests").rglob("*"))

    return files

def main() -> None:
    argp = argparse.ArgumentParser()
    argp.add_argument("--app", action="store_true", help="copy app/ context only")
    argp.add_argument("--tests", action="store_true", help="copy tests/ context")
    args = argp.parse_args()

    root = Path(__file__).resolve().parent
    files = collect(root, args.app, args.tests)
    out = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
    print("Creating context blob...")

    copied = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
            out.write(f"--- {f.relative_to(root)} ---\n{text}\n\n")
            copied += 1
        except UnicodeDecodeError:
            continue

    out.close()
    subprocess.run(["xclip", "-selection", "clipboard", out.name], check=True)
    lines = sum(1 for _ in open(out.name, encoding="utf-8"))
    print(f"✅ Copied to clipboard: {lines} lines from {copied} files")

if __name__ == "__main__":
    main()
