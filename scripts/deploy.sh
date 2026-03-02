#!/bin/bash
# Sync scripts to ChromaScape, compile, commit, and push — ready for Windows to pull
# Usage: ./scripts/deploy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

./scripts/sync-and-compile.sh

echo ""
echo "=== Dry-run verification ==="
cd ChromaScape
gradle bootRun --dry-run
cd "$PROJECT_ROOT"
echo "  ✓ Dry-run passed"

echo ""
echo "=== Pushing ChromaScape submodule ==="
cd ChromaScape
git add -A
if git diff --cached --quiet; then
    echo "  No submodule changes to commit"
else
    git commit -m "deploy: sync custom scripts and resources"
    git push
    echo "  ✓ Submodule pushed"
fi
cd "$PROJECT_ROOT"

echo ""
echo "=== Pushing parent repo ==="
git add -A
if git diff --cached --quiet; then
    echo "  No changes to commit"
else
    git commit -m "deploy: sync scripts to ChromaScape"
    git push
    echo "  ✓ Pushed"
fi

echo ""
echo "✓ Ready — pull from Windows and run ChromaScape"
