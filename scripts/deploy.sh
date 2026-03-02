#!/bin/bash
# Sync scripts to ChromaScape, compile, commit, and push — ready for Windows to pull
# Usage: ./scripts/deploy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

./scripts/sync-and-compile.sh

echo ""
echo "=== Committing and pushing ==="
git add ChromaScape/src/main/java/com/chromascape/scripts/ \
        ChromaScape/src/main/resources/images/user/ \
        scriptgen/ \
        .kiro/specs/scripts/ 2>/dev/null || true

if git diff --cached --quiet; then
    echo "  No changes to commit"
else
    git commit -m "deploy: sync scripts to ChromaScape"
    git push
    echo "  ✓ Pushed"
fi

echo ""
echo "✓ Ready — pull from Windows and run ChromaScape"
