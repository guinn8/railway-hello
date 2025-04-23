#!/usr/bin/env bash
set -euo pipefail

OUT=$(mktemp)
PROJECT_ROOT="$(dirname "$0")"
echo "Creating context blob..."

# Explicit list of top-level files
FILES=(
  "main.py"
  "requirements.txt"
)

# Add all Python files in app/
FILES+=( $(find "$PROJECT_ROOT/app" -maxdepth 1 -name "*.py" | sort) )

# Add all Markdown files in app/prompts/
FILES+=( $(find "$PROJECT_ROOT/app/prompts" -name "*.md" | sort) )

for file in "${FILES[@]}"; do
  if [[ -f "$file" ]]; then
    echo "--- ${file#$PROJECT_ROOT/} ---" >> "$OUT"
    cat "$file" >> "$OUT"
    echo -e "\n" >> "$OUT"
  else
    echo "Warning: $file not found" >&2
  fi
done

xclip -selection clipboard "$OUT"
echo "✅ Copied to clipboard: $(wc -l < "$OUT") lines from ${#FILES[@]} files"
