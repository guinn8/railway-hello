#!/usr/bin/env bash
# Concatenate source files into a single context blob for ChatGPT, copying to clipboard

set -euo pipefail

OUT=$(mktemp)
PROJECT_ROOT="$(dirname "$0")"

echo "Creating context blob..."

# List of relevant files (order matters for clarity)
FILES=(
  "main.py"
  "requirements.txt"
  "plan.md"
  "app/prompt.py"
  "app/llm.py"
  "app/resolver.py"
)

for file in "${FILES[@]}"; do
  if [[ -f "$PROJECT_ROOT/$file" ]]; then
    echo "--- $file ---" >> "$OUT"
    cat "$PROJECT_ROOT/$file" >> "$OUT"
    echo -e "\n" >> "$OUT"
  else
    echo "Warning: $file not found" >&2
  fi
done

# Pipe into xclip (assumes you're on Ubuntu X11)
xclip -selection clipboard "$OUT"

echo "✅ Copied to clipboard: $(wc -l < "$OUT") lines from ${#FILES[@]} files"
