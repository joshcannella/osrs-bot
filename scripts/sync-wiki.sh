#!/bin/bash
# Syncs the ChromaScape wiki from GitHub into .kiro/knowledge/chromascape-wiki/
# Run this periodically to pick up wiki updates.

WIKI_DIR=".kiro/knowledge/chromascape-wiki"
TEMP_DIR=$(mktemp -d)

git clone --depth 1 https://github.com/StaticSweep/ChromaScape.wiki.git "$TEMP_DIR" 2>/dev/null

if [ $? -eq 0 ]; then
    mkdir -p "$WIKI_DIR"
    cp "$TEMP_DIR"/*.md "$WIKI_DIR/"
    rm -rf "$TEMP_DIR"
    echo "Wiki synced to $WIKI_DIR"
    ls "$WIKI_DIR"
else
    rm -rf "$TEMP_DIR"
    echo "Failed to clone wiki" >&2
    exit 1
fi
