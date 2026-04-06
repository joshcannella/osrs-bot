"""osrs-bot CLI — manage DreamBot scripts, deployments, logs, and bugs."""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


def get_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p] + list(p.parents):
        if (parent / ".kiro").is_dir():
            return parent
    print("Error: could not find project root (.kiro/ directory)", file=sys.stderr)
    sys.exit(1)


ROOT = get_root()
DREAMBOT_PROJECT = ROOT / "dreambot"
SCRIPTS_SRC = DREAMBOT_PROJECT / "src/main/java/scripts"
SPECS = ROOT / ".kiro/specs/scripts"
TRACKER = ROOT / ".kiro/scripts.json"
TEMPLATE = SPECS / "TEMPLATE.md"
LOCAL_LOGS = ROOT / ".kiro/logs"

ENV_MAP = {
    "dropbox_dir": "OSRS_BOT_DROPBOX",
    "dreambot_scripts": "OSRS_BOT_DREAMBOT",
    "dreambot_logs": "OSRS_BOT_DREAMBOT_LOGS",
}


# === Config ===

def load_config() -> dict:
    conf = {
        "dropbox_dir": Path.home() / "Dropbox/osrs-bot/builds",
        "dreambot_scripts": Path.home() / "DreamBot/Scripts",
        "dreambot_logs": Path.home() / "DreamBot/BotData/logs",
    }
    conf_file = ROOT / ".osrs-bot.conf"
    if conf_file.exists():
        for line in conf_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if k in conf:
                    conf[k] = Path(v).expanduser()
    for k, env_key in ENV_MAP.items():
        val = os.environ.get(env_key)
        if val:
            conf[k] = Path(val).expanduser()
    return conf


CONFIG = load_config()


# === Tracker ===

def load_tracker() -> dict:
    if TRACKER.exists():
        data = json.loads(TRACKER.read_text())
        # Migrate old format
        if "scripts" not in data:
            data = {"scripts": data}
        return data
    return {"scripts": {}}


def save_tracker(data: dict):
    TRACKER.write_text(json.dumps(data, indent=2) + "\n")


def id_to_class(script_id: str) -> str:
    return "".join(w.capitalize() for w in script_id.split("-")) + "Script"


def jar_timestamp() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d-%H%M")


def _bump_script_version(entry: dict, major: bool = False):
    """Bump a script's major.minor version in the tracker."""
    v = entry.get("version", {"major": 0, "minor": 0})
    if isinstance(v, str):
        parts = v.split(".")
        v = {"major": int(parts[0]), "minor": int(parts[1]) if len(parts) > 1 else 0}
    if major:
        v["major"] += 1
        v["minor"] = 0
    else:
        v["minor"] += 1
    entry["version"] = v
    return f"{v['major']}.{v['minor']}"


# === Helpers ===

def run_cmd(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd or ROOT, check=check)


def gradle(args: list[str]):
    wrapper = DREAMBOT_PROJECT / ("gradlew.bat" if platform.system() == "Windows" else "gradlew")
    if wrapper.exists():
        cmd = [str(wrapper)] + args
    else:
        cmd = ["gradle"] + args
    run_cmd(cmd, cwd=DREAMBOT_PROJECT)


def today() -> str:
    return date.today().isoformat()


def find_log_file() -> Path | None:
    log_dir = CONFIG["dreambot_logs"]
    if not log_dir.exists():
        return None
    logs = sorted(log_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def extract_log_errors(n: int = 20) -> list[str]:
    log_file = find_log_file()
    if not log_file:
        return []
    lines = log_file.read_text().splitlines()
    errors = [l for l in lines if "ERROR" in l or "WARN" in l or "Exception" in l]
    return errors[-n:]


# === Commands ===

def cmd_init(args):
    sid = args.script_id
    tracker = load_tracker()
    if sid in tracker["scripts"]:
        print(f"'{sid}' already exists in tracker")
        return

    class_name = id_to_class(sid)
    pkg_name = sid.replace("-", "")
    tracker["scripts"][sid] = {
        "class": class_name,
        "package": f"scripts.{pkg_name}",
        "status": "dev",
        "version": {"major": 0, "minor": 1},
        "category": "MISC",
        "bugs": [],
        "notes": [],
    }
    save_tracker(tracker)

    # Create script package
    pkg_dir = SCRIPTS_SRC / pkg_name
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Scaffold script
    script_file = pkg_dir / f"{class_name}.java"
    if not script_file.exists():
        if args.simple:
            script_file.write_text(f"""package scripts.{pkg_name};

import org.dreambot.api.script.AbstractScript;
import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.utilities.Logger;

@ScriptManifest(name = "{sid}", author = "osrs-bot", version = 0.1,
                description = "", category = Category.MISC)
public class {class_name} extends AbstractScript {{

    @Override
    public void onStart() {{
        Logger.log("Starting {class_name}");
    }}

    @Override
    public int onLoop() {{
        // TODO: implement
        return 600;
    }}

    @Override
    public void onExit() {{
        Logger.log("Stopping {class_name}");
    }}
}}
""")
        else:
            # TaskScript scaffold
            nodes_dir = pkg_dir / "nodes"
            nodes_dir.mkdir(exist_ok=True)
            script_file.write_text(f"""package scripts.{pkg_name};

import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.script.impl.TaskScript;
import org.dreambot.api.utilities.Logger;
import scripts.shared.antiban.AntiBanNode;

@ScriptManifest(name = "{sid}", author = "osrs-bot", version = 0.1,
                description = "", category = Category.MISC)
public class {class_name} extends TaskScript {{

    @Override
    public void onStart() {{
        Logger.log("Starting {class_name}");
        addNodes(new AntiBanNode());
        // TODO: add script-specific nodes
    }}

    @Override
    public void onExit() {{
        Logger.log("Stopping {class_name}");
    }}
}}
""")

    # Create spec directory
    spec_dir = SPECS / sid
    spec_dir.mkdir(parents=True, exist_ok=True)
    req = spec_dir / "requirements.md"
    if not req.exists() and TEMPLATE.exists():
        content = TEMPLATE.read_text()
        content = content.replace("[Name]", sid).replace("[kebab-case-id]", sid)
        req.write_text(content)

    print(f"✓ Initialized {sid}")
    print(f"  class:   {class_name}")
    print(f"  package: scripts.{pkg_name}")
    print(f"  source:  {pkg_dir.relative_to(ROOT)}")
    print(f"  type:    {'AbstractScript' if args.simple else 'TaskScript'}")


def cmd_build(args):
    gradle(["jar"])
    print("✓ Build successful")


def _changed_scripts(tracker: dict) -> list[str]:
    """Return script IDs whose source files changed since last commit."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    # Also check staged files
    staged = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    # And untracked new files
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "dreambot/src/"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    changed_files = set(
        (result.stdout + staged.stdout + untracked.stdout).strip().splitlines()
    )
    changed = []
    for sid, entry in tracker.get("scripts", {}).items():
        pkg = entry.get("package", "").replace(".", "/")
        if any(f.startswith(f"dreambot/src/main/java/{pkg}/") for f in changed_files):
            changed.append(sid)
    return changed


def _update_manifest_version(script_id: str, tracker: dict, ver: str):
    """Update @ScriptManifest version in the script's Java source file."""
    entry = tracker["scripts"][script_id]
    pkg = entry.get("package", "").replace(".", "/")
    pkg_dir = DREAMBOT_PROJECT / "src/main/java" / pkg
    if not pkg_dir.exists():
        return
    for java_file in pkg_dir.glob("*Script.java"):
        text = java_file.read_text()
        updated = re.sub(
            r'(@ScriptManifest\([^)]*version\s*=\s*)[\d.]+',
            rf'\g<1>{ver}',
            text,
        )
        if updated != text:
            java_file.write_text(updated)


def cmd_deploy(args):
    tracker = load_tracker()

    ts = jar_timestamp()
    jar_name = "osrs-scripts"

    # Bump versions for changed scripts
    changed = _changed_scripts(tracker)
    for sid in changed:
        entry = tracker["scripts"][sid]
        major = args.major_script and sid in args.major_script
        ver = _bump_script_version(entry, major=major)
        _update_manifest_version(sid, tracker, ver)
        print(f"  ↑ {sid} → v{ver}")

    save_tracker(tracker)

    # Build
    gradle(["jar", f"-PjarName={jar_name}", f"-PjarVersion={ts}"])
    print(f"✓ Compiled {jar_name}-{ts}.jar")

    # Copy to Dropbox
    dropbox = CONFIG["dropbox_dir"]
    dropbox.mkdir(parents=True, exist_ok=True)
    built_jar = DREAMBOT_PROJECT / "build/libs" / f"{jar_name}-{ts}.jar"
    if not built_jar.exists():
        print(f"Error: jar not found at {built_jar}", file=sys.stderr)
        sys.exit(1)
    dest = dropbox / f"{jar_name}-{ts}.jar"
    shutil.copy2(built_jar, dest)
    print(f"✓ Copied to {dest}")

    if args.dry_run:
        print("✓ Deploy complete (dry-run)")
        return

    if args.quick:
        # Quick deploy still commits live feed so Linux can see it
        run_cmd(["git", "add", ".kiro/live", ".kiro/scripts.json", ".kiro/specs"], check=False)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
        if result.returncode != 0:
            run_cmd(["git", "commit", "-m", f"quick deploy: {ts}"])
            run_cmd(["git", "push"])
        print(f"\n✓ Quick deploy complete — {ts}")
        print(f"  Dropbox will sync to Windows automatically")
        return

    # Git push
    run_cmd(["git", "add", "-A"])
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    if result.returncode != 0:
        run_cmd(["git", "commit", "-m", f"deploy: {ts}"])
        run_cmd(["git", "push"])
        print("✓ Pushed to git")
    else:
        print("  No changes to push")

    print(f"\n✓ Deploy complete — {ts}")
    print(f"  Dropbox will sync to Windows automatically")
    print(f"  Then run: osrs-bot run")

    # Clear live feed after full deploy
    if LIVE_DIR.exists():
        for f in LIVE_DIR.glob("*.md"):
            f.unlink()
        print("  Live feed cleared")


def _copy_latest_jar(dropbox: Path, dreambot: Path) -> str | None:
    """Copy latest jar from Dropbox to DreamBot. Returns jar name or None if already current."""
    jars = sorted(dropbox.glob("osrs-scripts-*.jar"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not jars:
        return None
    src = jars[0]
    current = list(dreambot.glob("osrs-scripts-*.jar"))
    if current and current[0].name == src.name:
        return None
    for old in dreambot.glob("osrs-scripts-*.jar"):
        old.unlink()
    shutil.copy2(src, dreambot / src.name)
    return src.name


def cmd_run(args):
    if platform.system() == "Windows":
        dropbox = CONFIG["dropbox_dir"]
        dreambot = CONFIG["dreambot_scripts"]
        dreambot.mkdir(parents=True, exist_ok=True)

        if args.watch:
            import time
            print(f"👀 Watching {dropbox} for new jars... (Ctrl+C to stop)")
            last_seen = None
            current = list(dreambot.glob("osrs-scripts-*.jar"))
            if current:
                last_seen = current[0].name
                print(f"  Current: {last_seen}")
            while True:
                name = _copy_latest_jar(dropbox, dreambot)
                if name and name != last_seen:
                    last_seen = name
                    print(f"\n✓ New jar detected: {name}")
                    print(f"  ⚠ Stop your script in DreamBot, then Refresh local scripts")
                time.sleep(5)
            return

        # One-shot mode
        jars = sorted(dropbox.glob("osrs-scripts-*.jar"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not jars:
            print(f"No jars found in {dropbox}", file=sys.stderr)
            print("Run 'osrs-bot deploy' on the dev machine first")
            sys.exit(1)

        src = jars[0]
        current = list(dreambot.glob("osrs-scripts-*.jar"))
        if current and current[0].name == src.name:
            print(f"  Already running {src.name}")
            print(f"  ⚠ Stop your script in DreamBot before updating")
            return

        if current:
            print(f"  Old: {current[0].name}")
        print(f"  New: {src.name}")

        for old in dreambot.glob("osrs-scripts-*.jar"):
            old.unlink()
        shutil.copy2(src, dreambot / src.name)
        print(f"✓ Copied {src.name} → {dreambot}")

        run_cmd(["git", "pull"], check=False)
        tracker = load_tracker()
        scripts = tracker.get("scripts", {})
        if scripts:
            print(f"\n  Scripts:")
            for sid, entry in scripts.items():
                v = entry.get("version", {})
                vstr = f"v{v['major']}.{v['minor']}" if isinstance(v, dict) else f"v{v}"
                print(f"    {sid} {vstr}")

        print(f"\n  ⚠ Stop your script in DreamBot, then Refresh local scripts")
    else:
        run_cmd(["git", "pull"])
        tracker = load_tracker()
        print(f"✓ Pulled latest")
        scripts = tracker.get("scripts", {})
        if scripts:
            for sid, entry in scripts.items():
                v = entry.get("version", {})
                vstr = f"{v['major']}.{v['minor']}" if isinstance(v, dict) else str(v)
                print(f"  {sid} v{vstr} ({entry.get('status', '?')})")


def copy_images(sid: str, image_paths: list[str]) -> list[str]:
    spec_dir = SPECS / sid
    spec_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for p in image_paths:
        src = Path(p).expanduser().resolve()
        if not src.exists():
            print(f"  ⚠ Image not found: {p}", file=sys.stderr)
            continue
        dest = spec_dir / src.name
        if dest.exists():
            stem, suffix = dest.stem, dest.suffix
            i = 1
            while dest.exists():
                dest = spec_dir / f"{stem}_{i}{suffix}"
                i += 1
        shutil.copy2(src, dest)
        saved.append(str(dest.relative_to(ROOT)))
    return saved


def cmd_bug(args):
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker["scripts"]:
        print(f"Unknown script '{sid}'. Run: osrs-bot init {sid}", file=sys.stderr)
        sys.exit(1)

    desc = args.message
    bug = {"date": today(), "description": desc, "resolved": False}

    errors = extract_log_errors(20)
    if errors:
        bug["log_tail"] = errors

    if args.image:
        saved = copy_images(sid, args.image)
        if saved:
            bug["images"] = saved

    tracker["scripts"][sid]["bugs"].append(bug)
    save_tracker(tracker)
    print(f"✓ Bug added to {sid}: {desc}")
    if errors:
        print(f"  Attached {len(errors)} error/warn lines from log")


def cmd_note(args):
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker["scripts"]:
        print(f"Unknown script '{sid}'. Run: osrs-bot init {sid}", file=sys.stderr)
        sys.exit(1)

    note = {
        "date": today(),
        "from": "windows" if platform.system() == "Windows" else "linux",
        "text": args.message,
    }
    if args.image:
        saved = copy_images(sid, args.image)
        if saved:
            note["images"] = saved

    tracker["scripts"][sid]["notes"].append(note)
    save_tracker(tracker)
    print(f"✓ Note added to {sid}")


def cmd_resolve(args):
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker["scripts"]:
        print(f"Unknown script '{sid}'", file=sys.stderr)
        sys.exit(1)

    for bug in reversed(tracker["scripts"][sid]["bugs"]):
        if not bug["resolved"]:
            bug["resolved"] = True
            save_tracker(tracker)
            print(f"✓ Resolved: {bug['description']}")
            return
    print(f"No unresolved bugs for {sid}")


def cmd_complete(args):
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker["scripts"]:
        print(f"Unknown script '{sid}'", file=sys.stderr)
        sys.exit(1)

    tracker["scripts"][sid]["status"] = "complete"
    save_tracker(tracker)
    print(f"✓ {sid} marked complete")


def cmd_lint(args):
    issues = []
    for f in SCRIPTS_SRC.rglob("*Script.java"):
        text = f.read_text()
        if "@ScriptManifest" not in text:
            issues.append(f"  ✗ {f.relative_to(ROOT)}: missing @ScriptManifest")
        if "extends TaskScript" in text and "addNodes" not in text:
            issues.append(f"  ✗ {f.relative_to(ROOT)}: TaskScript without addNodes() in onStart()")
    if issues:
        print(f"⚠ {len(issues)} issue(s):")
        for i in issues:
            print(i)
        sys.exit(1)
    print("✓ All scripts pass lint")


def cmd_logs_pull(args):
    log_file = find_log_file()
    if not log_file:
        print(f"No log files found in {CONFIG['dreambot_logs']}", file=sys.stderr)
        print(f"  Expected: {CONFIG['dreambot_logs']}/*.log")
        sys.exit(1)
    LOCAL_LOGS.mkdir(parents=True, exist_ok=True)
    dest = LOCAL_LOGS / f"{args.script_id}.log"
    shutil.copy2(log_file, dest)
    print(f"✓ Copied log to {dest.relative_to(ROOT)} (local only, gitignored)")


def cmd_logs_tail(args):
    log_file = find_log_file()
    if not log_file:
        print(f"No log files found in {CONFIG['dreambot_logs']}", file=sys.stderr)
        sys.exit(1)
    lines = log_file.read_text().splitlines()
    for line in lines[-args.n:]:
        print(line)


def cmd_logs_summary(args):
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker["scripts"]:
        print(f"Unknown script '{sid}'", file=sys.stderr)
        sys.exit(1)

    errors = extract_log_errors(args.n)
    if not errors:
        print("No errors/warnings found in log")
        return

    summary = "\n".join(errors)
    tracker["scripts"][sid]["notes"].append({
        "date": today(),
        "from": "windows" if platform.system() == "Windows" else "linux",
        "text": f"Log summary ({len(errors)} errors/warnings):\n{summary}",
    })
    save_tracker(tracker)
    print(f"✓ Added {len(errors)} error/warn lines as note to {sid}")


def cmd_push(args):
    """Lightweight push — commit and push tracker/specs without building."""
    run_cmd(["git", "add", "-A"])
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    if result.returncode != 0:
        run_cmd(["git", "commit", "-m", "sync: bugs, notes, specs"])
        run_cmd(["git", "push"])
        print("✓ Pushed feedback to git")
    else:
        print("  Nothing to push")


# === Live Feed ===

LIVE_DIR = ROOT / ".kiro/live"


def _live_file(script_id: str) -> Path:
    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    return LIVE_DIR / f"{script_id}.md"


def _append_live(script_id: str, message: str, images: list[str] | None = None, log_lines: int = 0):
    """Append a timestamped entry to the live feed."""
    from datetime import datetime
    ts = datetime.now().strftime("%H:%M:%S")
    f = _live_file(script_id)

    lines = [f"- **{ts}** — {message}"]
    if images:
        saved = copy_images(script_id, images)
        for img in saved:
            lines.append(f"  - 📎 {img}")
    if log_lines > 0:
        errors = extract_log_errors(log_lines)
        if errors:
            lines.append(f"  - 📋 Log ({len(errors)} lines):")
            for e in errors:
                lines.append(f"    - `{e[:120]}`")

    entry = "\n".join(lines) + "\n"

    # Create file with header if new
    if not f.exists():
        f.write_text(f"# Live Feed: {script_id}\n\n{entry}")
    else:
        with open(f, "a") as fh:
            fh.write(entry)

    print(f"[{ts}] Sent: {message}")


def cmd_live(args):
    """Send a live message, or tail the feed."""
    if args.tail:
        # Show all live feeds
        if not LIVE_DIR.exists():
            print("No live feed yet")
            return
        for f in sorted(LIVE_DIR.glob("*.md")):
            print(f.read_text())
        return

    if args.clear:
        if LIVE_DIR.exists():
            for f in LIVE_DIR.glob("*.md"):
                f.unlink()
        print("✓ Live feed cleared")
        return

    if not args.script_id or not args.message:
        print("Usage: osrs-bot live <script-id> \"message\" [-i img] [-l 10]", file=sys.stderr)
        sys.exit(1)

    _append_live(
        args.script_id,
        " ".join(args.message),
        images=args.image,
        log_lines=args.log or 0,
    )


def cmd_inbox(args):
    """Show unresolved bugs, recent notes, and live feed across all scripts."""
    tracker = load_tracker()
    scripts = tracker.get("scripts", {})
    found = False

    # Collect script IDs from tracker + any live feed files
    all_ids = set(scripts.keys())
    if LIVE_DIR.exists():
        for f in LIVE_DIR.glob("*.md"):
            all_ids.add(f.stem)

    for sid in sorted(all_ids):
        entry = scripts.get(sid, {})
        bugs = [b for b in entry.get("bugs", []) if not b["resolved"]]
        notes = entry.get("notes", [])
        recent_notes = notes[-5:] if notes else []
        live_file = LIVE_DIR / f"{sid}.md" if LIVE_DIR.exists() else None
        has_live = live_file and live_file.exists()

        if not bugs and not recent_notes and not has_live:
            continue

        found = True
        v = entry.get("version", {})
        vstr = f"v{v['major']}.{v['minor']}" if isinstance(v, dict) and v else ""
        print(f"\n{sid} {vstr}")

        for b in bugs:
            print(f"  🐛 [{b['date']}] {b['description']}")
            for img in b.get("images", []):
                print(f"      📎 {img}")

        for n in recent_notes:
            src = f"({n['from']})" if n.get("from") else ""
            text = n["text"]
            if "\n" in text:
                text = text.split("\n")[0] + " ..."
            print(f"  📝 [{n['date']}] {src} {text}")

        if has_live:
            print(f"  💬 Live:")
            for line in live_file.read_text().splitlines():
                if line.startswith("- **"):
                    print(f"    {line[2:]}")  # strip leading "- "

    if not found:
        print("✓ Inbox clear — no bugs, notes, or live messages")


def cmd_status(args):
    tracker = load_tracker()
    scripts = tracker.get("scripts", {})

    # Check Dropbox for latest jar
    dropbox = CONFIG["dropbox_dir"]
    jars = sorted(dropbox.glob("osrs-scripts-*.jar"), key=lambda f: f.stat().st_mtime, reverse=True) if dropbox.exists() else []
    if jars:
        print(f"=== Latest Jar: {jars[0].name} ===\n")
    else:
        print(f"=== No jars in {dropbox} ===\n")

    dev = {k: v for k, v in scripts.items() if v.get("status") == "dev"}
    done = {k: v for k, v in scripts.items() if v.get("status") == "complete"}

    print("\n=== Dev ===")
    if dev:
        for sid, entry in sorted(dev.items()):
            open_bugs = sum(1 for b in entry.get("bugs", []) if not b["resolved"])
            notes_count = len(entry.get("notes", []))
            flags = []
            if open_bugs:
                flags.append(f"{open_bugs} bug{'s' if open_bugs > 1 else ''}")
            if notes_count:
                flags.append(f"{notes_count} note{'s' if notes_count > 1 else ''}")
            suffix = f"  [{', '.join(flags)}]" if flags else ""
            v = entry.get("version", {})
            vstr = f"v{v['major']}.{v['minor']}" if isinstance(v, dict) else f"v{v}"
            print(f"  {sid} {vstr} ({entry.get('category', '?')}){suffix}")
    else:
        print("  (none)")

    print("\n=== Complete ===")
    if done:
        for sid in sorted(done):
            print(f"  {sid}")
    else:
        print("  (none)")

    # Script files on disk
    script_files = sorted(f.stem for f in SCRIPTS_SRC.rglob("*Script.java") if "shared" not in str(f))
    if script_files:
        print(f"\n=== Script Files ({len(script_files)}) ===")
        for s in script_files:
            print(f"  {s}")


def cmd_show(args):
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker["scripts"]:
        print(f"Unknown script '{sid}'", file=sys.stderr)
        sys.exit(1)

    entry = tracker["scripts"][sid]
    v = entry.get("version", {})
    vstr = f"{v['major']}.{v['minor']}" if isinstance(v, dict) else str(v)
    print(f"Script:   {sid}")
    print(f"Class:    {entry['class']}")
    print(f"Package:  {entry.get('package', '?')}")
    print(f"Version:  {vstr}")
    print(f"Category: {entry.get('category', '?')}")
    print(f"Status:   {entry['status']}")

    bugs = entry.get("bugs", [])
    if bugs:
        print(f"\nBugs ({len(bugs)}):")
        for b in bugs:
            resolved = "✓" if b["resolved"] else "✗"
            print(f"  {resolved} [{b['date']}] {b['description']}")

    notes = entry.get("notes", [])
    if notes:
        print(f"\nNotes ({len(notes)}):")
        for n in notes:
            src = f"({n['from']})" if n.get("from") else ""
            text = n["text"]
            if "\n" in text:
                text = text.split("\n")[0] + " ..."
            print(f"  [{n['date']}] {src} {text}")


def main():
    parser = argparse.ArgumentParser(prog="osrs-bot")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize a new script")
    p_init.add_argument("script_id", help="Script ID (kebab-case)")
    p_init.add_argument("--simple", action="store_true", help="Use AbstractScript instead of TaskScript")

    sub.add_parser("build", help="Compile all scripts")
    sub.add_parser("lint", help="Check scripts for common issues")

    p_deploy = sub.add_parser("deploy", help="Compile, copy to Dropbox, push")
    p_deploy.add_argument("--dry-run", action="store_true")
    p_deploy.add_argument("--quick", action="store_true", help="Skip git push — just build + Dropbox")
    p_deploy.add_argument("--major-script", nargs="+", metavar="ID", help="Bump major version for specific script(s)")

    p_run = sub.add_parser("run", help="Windows: copy jar to DreamBot. Linux: git pull")
    p_run.add_argument("--watch", action="store_true", help="Watch Dropbox for new jars and auto-copy (Windows)")

    p_bug = sub.add_parser("bug", help="Report a bug")
    p_bug.add_argument("script_id")
    p_bug.add_argument("message", help="Bug description")
    p_bug.add_argument("-i", "--image", nargs="+", help="Attach image(s)")

    p_note = sub.add_parser("note", help="Add a note")
    p_note.add_argument("script_id")
    p_note.add_argument("message", help="Note text")
    p_note.add_argument("-i", "--image", nargs="+", help="Attach image(s)")

    p_resolve = sub.add_parser("resolve", help="Resolve latest bug")
    p_resolve.add_argument("script_id")

    p_complete = sub.add_parser("complete", help="Mark script as complete")
    p_complete.add_argument("script_id")

    p_show = sub.add_parser("show", help="Show script details")
    p_show.add_argument("script_id")

    p_logs = sub.add_parser("logs", help="Manage runtime logs")
    logs_sub = p_logs.add_subparsers(dest="logs_command")
    p_lp = logs_sub.add_parser("pull", help="Copy log to local (gitignored)")
    p_lp.add_argument("script_id")
    p_lt = logs_sub.add_parser("tail", help="Show last N lines")
    p_lt.add_argument("-n", type=int, default=50)
    p_ls = logs_sub.add_parser("summary", help="Extract errors as a note")
    p_ls.add_argument("script_id")
    p_ls.add_argument("-n", type=int, default=20)

    sub.add_parser("status", help="Show all scripts and latest jar")
    sub.add_parser("push", help="Push tracker/specs to git without building")
    sub.add_parser("inbox", help="Show unresolved bugs, notes, and live feed")

    p_live = sub.add_parser("live", help="Send live feedback during testing")
    p_live.add_argument("script_id", nargs="?", help="Script ID")
    p_live.add_argument("message", nargs="*", help="Message text")
    p_live.add_argument("-i", "--image", nargs="+", help="Attach screenshot(s)")
    p_live.add_argument("-l", "--log", type=int, metavar="N", help="Attach last N log error lines")
    p_live.add_argument("--tail", action="store_true", help="Show all live feeds")
    p_live.add_argument("--clear", action="store_true", help="Clear all live feeds")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "build": cmd_build,
        "lint": cmd_lint,
        "deploy": cmd_deploy,
        "run": cmd_run,
        "bug": cmd_bug,
        "note": cmd_note,
        "resolve": cmd_resolve,
        "complete": cmd_complete,
        "show": cmd_show,
        "status": cmd_status,
        "push": cmd_push,
        "inbox": cmd_inbox,
        "live": cmd_live,
        "logs": lambda a: {
            "pull": cmd_logs_pull,
            "tail": cmd_logs_tail,
            "summary": cmd_logs_summary,
        }.get(getattr(a, "logs_command", None), lambda _: p_logs.print_help())(a),
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
