#!/usr/bin/env bash
set -euo pipefail

# Creates a new notebook from the template.
# Usage: ./scripts/new-notebook.sh <slug>
# Example: ./scripts/new-notebook.sh dutch-institution-count

SLUG="${1:-}"

if [ -z "$SLUG" ]; then
  echo "Usage: ./scripts/new-notebook.sh <slug>"
  echo "Example: ./scripts/new-notebook.sh dutch-institution-count"
  exit 1
fi

if ! echo "$SLUG" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$'; then
  echo "'$SLUG' isn't a valid slug."
  echo "Use lowercase letters, numbers and hyphens only, e.g. dutch-institution-count"
  exit 1
fi

DEST="notebooks/$SLUG"

if [ -e "$DEST" ]; then
  echo "notebooks/$SLUG already exists. Pick a different slug or remove it first."
  exit 1
fi

cp -r notebooks/_template "$DEST"

TITLE=$(echo "$SLUG" | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')

if command -v python3 >/dev/null 2>&1; then
  python3 - "$DEST/metadata.json" "$TITLE" <<'PY'
import json
import sys

path, title = sys.argv[1], sys.argv[2]
with open(path) as f:
    data = json.load(f)
data["title"] = title
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
else
  echo "python3 not found -- edit $DEST/metadata.json by hand to set the title."
fi

sed -i.bak "s/{{TITLE}}/$TITLE/g" "$DEST/notebook.py"
rm -f "$DEST/notebook.py.bak"

echo "Created notebooks/$SLUG/"
echo "Title set to: $TITLE"
echo ""
echo "Open it with: uvx marimo edit --sandbox --watch $DEST/notebook.py"
