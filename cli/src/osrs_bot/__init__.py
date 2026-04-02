"""osrs-bot CLI — manage scripts, deployments, logs, and bugs."""

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
        if (parent / "CLAUDE.md").is_file():
            return parent
    print("Error: could not find project root (CLAUDE.md not found)", file=sys.stderr)
    sys.exit(1)


ROOT = get_root()
CHROMASCAPE = ROOT / "ChromaScape"
SCRIPTS_DIR = CHROMASCAPE / "src/main/java/com/chromascape/scripts"
RESOURCES_DIR = CHROMASCAPE / "src/main/resources/images/user"
SPECS = ROOT / "specs/scripts"
TRACKER = ROOT / "scripts.json"
TEMPLATE = SPECS / "TEMPLATE.md"
LOG_FILE = CHROMASCAPE / "logs/chromascape.log"
LOCAL_LOGS = ROOT / "logs"


# === Tracker ===

def load_tracker() -> dict:
    if TRACKER.exists():
        return json.loads(TRACKER.read_text())
    return {}


def save_tracker(data: dict):
    TRACKER.write_text(json.dumps(data, indent=2) + "\n")


def id_to_class(script_id: str) -> str:
    return "".join(w.capitalize() for w in script_id.split("-")) + "Script"


# === Helpers ===

def run_cmd(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd or ROOT, check=check)


def gradle(args: list[str], cwd: Path = CHROMASCAPE):
    if platform.system() == "Windows":
        cmd = [str(cwd / "gradlew.bat")] + args
    else:
        cmd = ["gradle"] + args
    run_cmd(cmd, cwd=cwd)


def today() -> str:
    return date.today().isoformat()


# === Sync: generate SETUP.md from Java source ===

def sync_script(script_id: str, tracker: dict):
    """Scan Java source and generate/update SETUP.md."""
    entry = tracker.get(script_id)
    if not entry:
        return
    class_name = entry.get("class", id_to_class(script_id))
    java_file = SCRIPTS_DIR / f"{class_name}.java"
    if not java_file.exists():
        return

    source = java_file.read_text()
    spec_dir = SPECS / script_id
    spec_dir.mkdir(parents=True, exist_ok=True)

    # Extract image references
    images = sorted(set(re.findall(r'/images/user/([^"]+\.png)', source)))
    existing = {f.name for f in RESOURCES_DIR.iterdir()} if RESOURCES_DIR.exists() else set()

    # Extract ColourObj definitions
    colours = re.findall(
        r'ColourObj\(\s*"(\w+)".*?Scalar\((\d+),\s*(\d+),\s*(\d+)',
        source
    )

    # Detect features
    uses_idler = "Idler." in source or "waitUntilIdle" in source
    uses_shift_drop = "shiftDrop" in source.lower() or "shift" in source.lower() and "drop" in source.lower()
    uses_walker = "Walker" in source
    uses_bank = "Bank." in source
    uses_colour = "ColourClick" in source

    # Build SETUP.md
    lines = [f"# {class_name} — Setup Instructions\n"]
    lines.append("## RuneLite Requirements (Mandatory)")
    lines.append("- Windows Display Scaling: **100%**")
    lines.append("- RuneScape UI: **\"Fixed - Classic\"**")
    lines.append("- Display Brightness: **middle (50%)**")
    lines.append("- ChromaScape RuneLite Profile: **activated**\n")

    if uses_colour and colours:
        lines.append("## RuneLite Plugin Configuration\n")
        for name, h, s, v in colours:
            lines.append(f"### {name.capitalize()} Colour Tag")
            lines.append(f"- Tag the target in **{name}** — HSV ~{h}, {s}, {v}")
            lines.append(f"- Use **Hull** or **Tile** highlight style\n")

    if uses_idler:
        lines.append("### Idle Notifier")
        lines.append("- **Enable** this plugin — required for idle detection\n")

    lines.append("## Game Settings")
    if uses_shift_drop:
        lines.append("- **Shift-click drop**: must be enabled (Settings → Controls)\n")

    lines.append("## Image Templates")
    for img in images:
        status = "✓" if img in existing else "✗ MISSING"
        lines.append(f"- `{img}` {status}")
    if not images:
        lines.append("- (none detected)")
    lines.append("")

    lines.append("## How to Run")
    lines.append(f"- Script class: **{class_name}**")
    lines.append("- Start ChromaScape, open the web UI at `http://localhost:8080/`")
    lines.append(f"- Select **{class_name}** from the sidebar and click Start\n")

    # Write — auto-generated marker so we know it's safe to overwrite
    content = "\n".join(lines)
    setup_file = spec_dir / "SETUP.md"
    # Only overwrite if auto-generated or doesn't exist
    if not setup_file.exists() or setup_file.read_text().startswith("# " + class_name + " — Setup"):
        setup_file.write_text(content)


def extract_log_errors(n: int = 20) -> list[str]:
    """Extract last N ERROR/WARN lines from runtime log."""
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text().splitlines()
    errors = [l for l in lines if " ERROR " in l or " WARN " in l]
    return errors[-n:]


# === Commands ===

def cmd_init(args):
    """Initialize a new script spec directory and tracker entry."""
    sid = args.script_id
    tracker = load_tracker()
    if sid in tracker:
        print(f"'{sid}' already exists in tracker")
        return

    class_name = id_to_class(sid)
    tracker[sid] = {
        "class": class_name,
        "status": "dev",
        "bugs": [],
        "notes": [],
    }
    save_tracker(tracker)

    spec_dir = SPECS / sid
    spec_dir.mkdir(parents=True, exist_ok=True)

    # Copy requirements template
    req = spec_dir / "requirements.md"
    if not req.exists() and TEMPLATE.exists():
        content = TEMPLATE.read_text()
        content = content.replace("[Name]", sid).replace("[kebab-case-id]", sid)
        req.write_text(content)

    print(f"✓ Initialized {sid}")
    print(f"  class:        {class_name}")
    print(f"  requirements: {req.relative_to(ROOT)}")
    print(f"  tracker:      scripts.json")


def cmd_build(args):
    gradle(["classes"])
    print("✓ Build successful")


def cmd_deploy(args):
    # Sync all dev scripts before deploying
    tracker = load_tracker()
    for sid, entry in tracker.items():
        if entry.get("status") == "dev":
            sync_script(sid, tracker)

    gradle(["classes"])
    print("✓ Compiled")

    if args.dry_run:
        print("✓ Deploy complete (dry-run)")
        return

    # Push ChromaScape
    run_cmd(["git", "add", "-A"], cwd=CHROMASCAPE)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=CHROMASCAPE, check=False)
    if result.returncode != 0:
        run_cmd(["git", "commit", "-m", "deploy: update scripts and resources"], cwd=CHROMASCAPE)
        run_cmd(["git", "push"], cwd=CHROMASCAPE)
        print("✓ ChromaScape pushed")
    else:
        print("  No ChromaScape changes to push")

    # Push parent
    run_cmd(["git", "add", "-A"])
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    if result.returncode != 0:
        run_cmd(["git", "commit", "-m", "deploy: update specs"])
        run_cmd(["git", "push"])
        print("✓ Parent repo pushed")
    else:
        print("  No parent changes to push")

    print("\n✓ Deploy complete — pull from Windows and run")


def cmd_run(args):
    run_cmd(["git", "pull"])
    run_cmd(["git", "pull"], cwd=CHROMASCAPE)
    if args.browser:
        if platform.system() == "Windows":
            os.startfile("http://localhost:8080")
        else:
            subprocess.Popen(["xdg-open", "http://localhost:8080"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    gradle(["bootRun"])


def copy_images(sid: str, image_paths: list[str]) -> list[str]:
    """Copy images to the spec directory, return relative paths."""
    spec_dir = SPECS / sid
    spec_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for p in image_paths:
        src = Path(p).expanduser().resolve()
        if not src.exists():
            print(f"  ⚠ Image not found: {p}", file=sys.stderr)
            continue
        dest = spec_dir / src.name
        # Avoid collisions with a counter
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
    """Add a bug to the tracker, optionally with log errors and images."""
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker:
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

    tracker[sid]["bugs"].append(bug)
    save_tracker(tracker)
    print(f"✓ Bug added to {sid}: {desc}")
    if errors:
        print(f"  Attached {len(errors)} error/warn lines from log")
    if args.image:
        for p in bug.get("images", []):
            print(f"  📎 {p}")


def cmd_note(args):
    """Add a note to the tracker."""
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker:
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

    tracker[sid]["notes"].append(note)
    save_tracker(tracker)
    print(f"✓ Note added to {sid}")
    if args.image:
        for p in note.get("images", []):
            print(f"  📎 {p}")


def cmd_resolve(args):
    """Mark the latest unresolved bug as resolved."""
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker:
        print(f"Unknown script '{sid}'", file=sys.stderr)
        sys.exit(1)

    for bug in reversed(tracker[sid]["bugs"]):
        if not bug["resolved"]:
            bug["resolved"] = True
            save_tracker(tracker)
            print(f"✓ Resolved: {bug['description']}")
            return
    print(f"No unresolved bugs for {sid}")


def cmd_complete(args):
    """Mark a script as complete."""
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker:
        print(f"Unknown script '{sid}'", file=sys.stderr)
        sys.exit(1)

    tracker[sid]["status"] = "complete"
    save_tracker(tracker)
    sync_script(sid, tracker)
    print(f"✓ {sid} marked complete")


def cmd_sync(args):
    """Regenerate SETUP.md for a script (or all dev scripts)."""
    tracker = load_tracker()
    if args.script_id:
        if args.script_id not in tracker:
            print(f"Unknown script '{args.script_id}'", file=sys.stderr)
            sys.exit(1)
        sync_script(args.script_id, tracker)
        print(f"✓ Synced {args.script_id}")
    else:
        count = 0
        for sid, entry in tracker.items():
            if entry.get("status") == "dev":
                sync_script(sid, tracker)
                count += 1
        print(f"✓ Synced {count} dev script(s)")


def cmd_logs_pull(args):
    if not LOG_FILE.exists():
        print(f"No log file at {LOG_FILE}", file=sys.stderr)
        sys.exit(1)
    LOCAL_LOGS.mkdir(parents=True, exist_ok=True)
    dest = LOCAL_LOGS / f"{args.script_id}.log"
    shutil.copy2(LOG_FILE, dest)
    print(f"✓ Copied log to {dest.relative_to(ROOT)} (local only, gitignored)")


def cmd_logs_tail(args):
    if not LOG_FILE.exists():
        print(f"No log file at {LOG_FILE}", file=sys.stderr)
        sys.exit(1)
    lines = LOG_FILE.read_text().splitlines()
    for line in lines[-args.n:]:
        print(line)


def cmd_logs_summary(args):
    """Extract errors from log and save as a note."""
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker:
        print(f"Unknown script '{sid}'", file=sys.stderr)
        sys.exit(1)

    errors = extract_log_errors(args.n)
    if not errors:
        print("No errors/warnings found in log")
        return

    summary = "\n".join(errors)
    tracker[sid]["notes"].append({
        "date": today(),
        "from": "windows" if platform.system() == "Windows" else "linux",
        "text": f"Log summary ({len(errors)} errors/warnings):\n{summary}",
    })
    save_tracker(tracker)
    print(f"✓ Added {len(errors)} error/warn lines as note to {sid}")


def cmd_upstream(args):
    print("Fetching upstream...")
    run_cmd(["git", "fetch", "upstream"], cwd=CHROMASCAPE)
    run_cmd(["git", "merge", "upstream/main"], cwd=CHROMASCAPE)
    run_cmd(["git", "push"], cwd=CHROMASCAPE)
    print("✓ Merged and pushed upstream updates")


def cmd_lint(args):
    sig_re = re.compile(r"private\s+\w+\s+(\w+)\(")
    methods: dict[str, set[str]] = {}
    for f in SCRIPTS_DIR.glob("*.java"):
        for m in sig_re.findall(f.read_text()):
            methods.setdefault(m, set()).add(f.stem)
    dupes = {m: files for m, files in methods.items() if len(files) > 1}
    if dupes:
        print(f"⚠ {len(dupes)} duplicate private method(s) found:")
        for m, files in sorted(dupes.items()):
            print(f"  {m}() — {', '.join(sorted(files))}")
        sys.exit(1)
    print("✓ No duplicate private methods")


def cmd_delta(args):
    run_cmd(["git", "diff", "--stat", "upstream/main..HEAD"], cwd=CHROMASCAPE)


# === Python Framework Commands ===

PY_SCRIPTS_DIR = ROOT / "scripts"
PY_GENERATOR_REQUESTS = ROOT / "generator" / "requests"
LESSONS_PATH = ROOT / "knowledge" / "script-generation-lessons-learned.md"


def cmd_py_generate(args):
    """Generate a Python bot script from a Script Generation Request."""
    sys.path.insert(0, str(ROOT))
    from generator.pipeline import GeneratorPipeline
    pipeline = GeneratorPipeline()
    result = pipeline.generate_from_sgr(args.id)
    if result.success:
        print(f"\n✓ Script generated: {result.script_path}")
    else:
        print(f"\n✗ Generation completed with warnings")
        sys.exit(1)


def cmd_py_fix(args):
    """Fix a Python bot script using logged bugs."""
    sys.path.insert(0, str(ROOT))
    from generator.pipeline import GeneratorPipeline
    pipeline = GeneratorPipeline()
    result = pipeline.fix_script(args.id)
    if result.success:
        print(f"\n✓ Fix applied: {result.script_path}")
    else:
        print(f"\n✗ Fix completed with warnings")


def cmd_py_lesson(args):
    """Extract a lesson from a resolved bug and add to lessons-learned.md."""
    tracker = load_tracker()
    sid = args.id
    if sid not in tracker:
        print(f"Unknown script '{sid}'. Run: osrs-bot init {sid}", file=sys.stderr)
        sys.exit(1)

    entry = tracker[sid]
    bugs = entry.get("bugs", [])
    resolved_bugs = [b for b in bugs if b.get("resolved", False)]

    if not resolved_bugs:
        print(f"No resolved bugs for {sid}")
        return

    # Pick the bug to extract a lesson from
    if args.bug is not None:
        if args.bug < 0 or args.bug >= len(bugs):
            print(f"Bug index {args.bug} out of range (0-{len(bugs)-1})")
            sys.exit(1)
        target_bug = bugs[args.bug]
        if not target_bug.get("resolved"):
            print(f"Bug {args.bug} is not resolved yet")
            sys.exit(1)
    else:
        target_bug = resolved_bugs[-1]  # most recently resolved

    # Try to use Claude to distill a lesson
    try:
        sys.path.insert(0, str(ROOT))
        from generator.client import ClaudeClient

        # Read the current script if it exists
        script_name = sid.replace("-", "_") + "_bot.py"
        script_path = PY_SCRIPTS_DIR / script_name
        script_context = ""
        if script_path.exists():
            script_context = f"\n\nCurrent script ({script_name}):\n```python\n{script_path.read_text()}\n```"

        client = ClaudeClient()
        prompt = (
            f"A bot script had this bug:\n"
            f"  Description: {target_bug['description']}\n"
            f"  Date: {target_bug.get('date', 'unknown')}\n"
            f"{script_context}\n\n"
            f"The bug has been resolved. Distill a concise lesson (2-4 sentences) that would "
            f"help future script generation avoid this mistake. Format as:\n"
            f"## [Short Title]\n[Lesson text]\n\n"
            f"Focus on the general principle, not the specific script."
        )
        response = client.generate_script(
            "You are a bot development expert. Extract concise, actionable lessons from resolved bugs.",
            prompt,
        )
        lesson_text = response.strip()

    except Exception as e:
        # Fallback: manual lesson from bug description
        lesson_text = (
            f"## {target_bug['description'][:60]}\n"
            f"Resolved bug from script '{sid}'. "
            f"Review the fix to understand the root cause."
        )
        print(f"(Could not use Claude API: {e}. Using fallback lesson.)")

    # Show for review
    critical_tag = " [critical]" if args.critical else ""
    print(f"\nProposed lesson:{critical_tag}")
    print("─" * 60)
    print(lesson_text)
    print("─" * 60)
    answer = input("Add this lesson? [y/n/edit/critical]: ").strip().lower()

    if answer == "critical":
        args.critical = True
        answer = "y"

    if answer == "edit":
        print("Enter your edited lesson (end with a blank line):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        lesson_text = "\n".join(lines)
        answer = "y"

    if answer == "y":
        if args.critical and "[critical]" not in lesson_text:
            lesson_text = lesson_text.rstrip() + " [critical]"

        LESSONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LESSONS_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n\n{lesson_text}\n")
        print(f"✓ Lesson appended to {LESSONS_PATH.relative_to(ROOT)}")
    else:
        print("Lesson discarded.")


def cmd_status(args):
    tracker = load_tracker()

    dev = {k: v for k, v in tracker.items() if v.get("status") == "dev"}
    done = {k: v for k, v in tracker.items() if v.get("status") == "complete"}

    print("=== Dev ===")
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
            print(f"  {sid}{suffix}")
    else:
        print("  (none)")

    print("\n=== Complete ===")
    if done:
        for sid in sorted(done):
            print(f"  {sid}")
    else:
        print("  (none)")

    # Scripts in ChromaScape
    if SCRIPTS_DIR.exists():
        scripts = sorted(f.stem for f in SCRIPTS_DIR.glob("*Script.java"))
        print(f"\n=== Scripts ({len(scripts)}) ===")
        for s in scripts:
            print(f"  {s}")

    # Uncommitted changes
    for label, cwd in [("parent", ROOT), ("ChromaScape", CHROMASCAPE)]:
        result = subprocess.run(["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True)
        dirty = result.stdout.strip()
        if dirty:
            print(f"\n=== Uncommitted ({label}) ===")
            print(dirty)


def cmd_show(args):
    """Show details for a script — bugs, notes, status."""
    tracker = load_tracker()
    sid = args.script_id
    if sid not in tracker:
        print(f"Unknown script '{sid}'", file=sys.stderr)
        sys.exit(1)

    entry = tracker[sid]
    print(f"Script:  {sid}")
    print(f"Class:   {entry['class']}")
    print(f"Status:  {entry['status']}")

    bugs = entry.get("bugs", [])
    if bugs:
        print(f"\nBugs ({len(bugs)}):")
        for i, b in enumerate(bugs, 1):
            resolved = "✓" if b["resolved"] else "✗"
            print(f"  {resolved} [{b['date']}] {b['description']}")
            for img in b.get("images", []):
                print(f"      📎 {img}")

    notes = entry.get("notes", [])
    if notes:
        print(f"\nNotes ({len(notes)}):")
        for n in notes:
            src = f"({n['from']})" if n.get("from") else ""
            text = n["text"]
            if "\n" in text:
                text = text.split("\n")[0] + " ..."
            print(f"  [{n['date']}] {src} {text}")
            for img in n.get("images", []):
                print(f"      📎 {img}")


def main():
    parser = argparse.ArgumentParser(prog="osrs-bot")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize a new script")
    p_init.add_argument("script_id", help="Script ID (kebab-case)")

    sub.add_parser("build", help="Compile ChromaScape")
    sub.add_parser("lint", help="Find duplicate private methods")
    sub.add_parser("delta", help="Show ChromaScape diff from upstream")

    p_deploy = sub.add_parser("deploy", help="Compile, sync, commit, push")
    p_deploy.add_argument("--dry-run", action="store_true")

    p_run = sub.add_parser("run", help="Pull latest and launch ChromaScape")
    p_run.add_argument("--browser", action="store_true")

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

    p_sync = sub.add_parser("sync", help="Regenerate SETUP.md from Java source")
    p_sync.add_argument("script_id", nargs="?", help="Script ID (or omit for all dev)")

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

    sub.add_parser("upstream", help="Fetch and merge upstream ChromaScape")
    sub.add_parser("status", help="Show all scripts and their state")

    # Python framework commands
    p_pygen = sub.add_parser("py-generate", help="Generate a Python bot from an SGR file")
    p_pygen.add_argument("id", help="SGR ID (e.g. catherby-lobster-fisher)")

    p_pyfix = sub.add_parser("py-fix", help="Fix a Python bot using logged bugs")
    p_pyfix.add_argument("id", help="Script ID")

    p_pylesson = sub.add_parser("py-lesson", help="Extract a lesson from a resolved bug")
    p_pylesson.add_argument("id", help="Script ID")
    p_pylesson.add_argument("--bug", type=int, default=None, help="Bug index to extract from")
    p_pylesson.add_argument("--critical", action="store_true", help="Tag lesson as [critical]")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "build": cmd_build,
        "lint": cmd_lint,
        "delta": cmd_delta,
        "deploy": cmd_deploy,
        "run": cmd_run,
        "bug": cmd_bug,
        "note": cmd_note,
        "resolve": cmd_resolve,
        "complete": cmd_complete,
        "sync": cmd_sync,
        "show": cmd_show,
        "upstream": cmd_upstream,
        "status": cmd_status,
        "py-generate": cmd_py_generate,
        "py-fix": cmd_py_fix,
        "py-lesson": cmd_py_lesson,
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
