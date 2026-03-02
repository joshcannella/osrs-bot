#!/bin/bash
# Sync scripts to ChromaScape, compile, and launch the web UI
# Usage: ./scripts/deploy.sh [--no-launch]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Sync and compile
echo "=== Syncing and compiling ==="
./scripts/sync-and-compile.sh

# Launch unless --no-launch flag
if [ "$1" != "--no-launch" ]; then
    echo ""
    echo "=== Launching ChromaScape ==="
    echo "Open http://localhost:8080 in your browser"
    echo "Press Ctrl+C to stop"
    echo ""
    cd ChromaScape
    export JAVA_HOME=/home/linuxbrew/.linuxbrew/opt/openjdk@17
    gradle bootRun
fi
