#!/usr/bin/env bash
# Concatenate source files into a single context blob for ChatGPT, copying to clipboard

set -euo pipefail

OUT=$(mktemp)
PROJECT_ROOT="$(dirname "$0")"

echo "Creating context blob..."

# Static top-level files
FILES=(
  "main.py"
  "requirements.txt"
)

# Append all Python files under app/
while IFS= read -r -d $'\0' file; do
  FILES+=("${file#$PROJECT_ROOT/}")
done < <(find "$PROJECT_ROOT/app" -type f -name "*.py" -print0 | sort -z)

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
