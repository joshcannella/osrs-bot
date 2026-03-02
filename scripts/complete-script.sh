#!/bin/bash
# Mark a script as complete
# Usage: ./scripts/complete-script.sh <script-id>
# Example: ./scripts/complete-script.sh al-kharid-iron-mining

set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/complete-script.sh <script-id>"
    exit 1
fi

SCRIPT_ID="$1"
DEV_DIR=".kiro/specs/scripts/dev/$SCRIPT_ID"
DEST_DIR=".kiro/specs/scripts/$SCRIPT_ID"

if [ ! -d "$DEV_DIR" ]; then
    echo "Error: $DEV_DIR does not exist"
    exit 1
fi

if [ -d "$DEST_DIR" ]; then
    echo "Error: $DEST_DIR already exists"
    exit 1
fi

mkdir -p "$DEST_DIR"

# Merge SETUP.md and changelog.md into a single SETUP.md
{
    if [ -f "$DEV_DIR/SETUP.md" ]; then
        cat "$DEV_DIR/SETUP.md"
    fi
    if [ -f "$DEV_DIR/changelog.md" ]; then
        echo ""
        echo "---"
        echo ""
        echo "# Changelog"
        echo ""
        cat "$DEV_DIR/changelog.md"
    fi
} > "$DEST_DIR/SETUP.md"

# Copy the script source
SCRIPT_CLASS=$(echo "$SCRIPT_ID" | sed -r 's/(^|-)(\w)/\U\2/g')
SCRIPT_FILE="scriptgen/src/main/java/com/scriptgen/scripts/${SCRIPT_CLASS}Script.java"
if [ -f "$SCRIPT_FILE" ]; then
    cp "$SCRIPT_FILE" "$DEST_DIR/"
    echo "  ✓ Copied $SCRIPT_FILE"
fi

# Remove dev directory
rm -rf "$DEV_DIR"

echo "✓ $SCRIPT_ID marked complete → $DEST_DIR"
echo "  Dev directory removed"
