#!/usr/bin/env bash
# Check if DreamBot SNAPSHOT has been updated since last check.
# Outputs instructions for the agent if an update is detected.
# Used as an agentSpawn hook on osrs-scripter.

set -euo pipefail

METADATA_URL="https://maven.dreambot.org/org/dreambot/client/4.0.0-SNAPSHOT/maven-metadata.xml"
STATE_FILE=".kiro/.dreambot-snapshot-state"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Fetch current build number and timestamp from Maven
metadata=$(curl -sf "$METADATA_URL" 2>/dev/null) || {
    echo "⚠️ Could not reach DreamBot Maven repo — skipping version check"
    exit 0
}

remote_build=$(echo "$metadata" | grep -oP '<buildNumber>\K[0-9]+')
remote_ts=$(echo "$metadata" | grep -oP '<lastUpdated>\K[0-9]+')

if [ -z "$remote_build" ]; then
    echo "⚠️ Could not parse SNAPSHOT metadata — skipping version check"
    exit 0
fi

# Load previous state
local_build=""
if [ -f "$STATE_FILE" ]; then
    local_build=$(cat "$STATE_FILE")
fi

# Compare
if [ "$remote_build" = "$local_build" ]; then
    echo "✅ DreamBot SNAPSHOT is current (build #${remote_build}, updated ${remote_ts})"
    exit 0
fi

# New version detected
echo "🔔 DreamBot SNAPSHOT updated: build #${local_build:-unknown} → #${remote_build} (${remote_ts})"
echo ""
echo "ACTION REQUIRED — run these steps:"
echo "1. Refresh Gradle dependency:  cd dreambot && ./gradlew --refresh-dependencies compileJava"
echo "2. Regenerate API docs:        uv run scripts/refresh-javadocs.py --validate"
echo "3. Update state file:          echo '${remote_build}' > ${STATE_FILE}"
echo "4. Commit:                     git add -A && git commit -m 'docs: refresh javadocs (build #${remote_build})' && git push"

# Save new state so next spawn doesn't re-trigger
mkdir -p "$(dirname "$STATE_FILE")"
echo "$remote_build" > "$STATE_FILE"
