#!/bin/bash
# Quick compile check for scriptgen scripts

set -e

echo "=== Checking scriptgen compilation ==="

cd scriptgen

# Check if build.gradle.kts exists
if [ ! -f "build.gradle.kts" ]; then
    echo "ERROR: No build.gradle.kts found in scriptgen/"
    exit 1
fi

./gradlew clean compileJava

echo "✓ Scriptgen compiles successfully"
