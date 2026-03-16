#!/bin/bash
# Compile scripts, sync to ChromaScape, and compile ChromaScape

set -e

SCRIPTGEN_SCRIPTS="scriptgen/src/main/java/com/scriptgen/scripts"
CHROMASCAPE_SCRIPTS="ChromaScape/src/main/java/com/chromascape/scripts"
SCRIPTGEN_RESOURCES="scriptgen/src/main/resources/images/user"
CHROMASCAPE_RESOURCES="ChromaScape/src/main/resources/images/user"

echo "=== Compiling scripts ==="
export JAVA_HOME=/home/linuxbrew/.linuxbrew/opt/openjdk@17
(cd scriptgen && gradle compileJava)

echo "=== Syncing scripts to ChromaScape ==="

# Copy all scripts
rsync -av "$SCRIPTGEN_SCRIPTS/" "$CHROMASCAPE_SCRIPTS/"

# Update package declarations and imports in script files
echo "  ✓ Updating imports..."
find "$CHROMASCAPE_SCRIPTS" -name "*.java" -type f -exec sed -i 's/package com.scriptgen.scripts;/package com.chromascape.scripts;/g' {} \;

echo "=== Syncing image resources ==="
mkdir -p "$CHROMASCAPE_RESOURCES"
rsync -av "$SCRIPTGEN_RESOURCES/" "$CHROMASCAPE_RESOURCES/"

echo "=== Patching logging ==="
./scripts/patch-logging.sh

echo "=== Compiling ChromaScape ==="
cd ChromaScape
gradle compileJava

if [ $? -eq 0 ]; then
    echo "✓ Sync and compile complete"
else
    echo "✗ Compilation failed"
    exit 1
fi
