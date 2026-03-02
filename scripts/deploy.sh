#!/bin/bash
# Sync scripts to ChromaScape and compile — ready for Windows to pull and run
# Usage: ./scripts/deploy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

./scripts/sync-and-compile.sh

echo ""
echo "✓ Ready — pull from Windows and run ChromaScape"
