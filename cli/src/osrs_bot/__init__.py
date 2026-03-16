"""osrs-bot CLI — manage scripts, deployments, logs, and bugs."""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_root() -> Path:
    """Find the project root by walking up to find .kiro/."""
    p = Path(__file__).resolve()
    for parent in [p] + list(p.parents):
        if (parent / ".kiro").is_dir():
            return parent
    print("Error: could not find project root (.kiro/ directory)", file=sys.stderr)
    sys.exit(1)


ROOT = get_root()
SCRIPTGEN_SCRIPTS = ROOT / "scriptgen/src/main/java/com/scriptgen/scripts"
SCRIPTGEN_RESOURCES = ROOT / "scriptgen/src/main/resources/images/user"
CHROMASCAPE = ROOT / "ChromaScape"
CHROMASCAPE_SCRIPTS = CHROMASCAPE / "src/main/java/com/chromascape/scripts"
CHROMASCAPE_RESOURCES = CHROMASCAPE / "src/main/resources/images/user"
SPECS_DEV = ROOT / ".kiro/specs/scripts/dev"
SPECS_COMPLETED = ROOT / ".kiro/specs/scripts"
BUG_TEMPLATE = SPECS_DEV / "BUG-TEMPLATE.md"
LOG_FILE = CHROMASCAPE / "logs/chromascape.log"


def run_cmd(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd or ROOT, check=check)


def get_manifest(script_id: str) -> dict | None:
    for base in [SPECS_DEV, SPECS_COMPLETED]:
        manifest = base / script_id / "manifest.json"
        if manifest.exists():
            return json.loads(manifest.read_text())
    return None


def get_active_dev_ids() -> list[str]:
    if not SPECS_DEV.exists():
        return []
    return [
        d.name for d in sorted(SPECS_DEV.iterdir())
        if d.is_dir() and (d / "requirements.md").exists()
    ]


def get_completed_ids() -> list[str]:
    if not SPECS_COMPLETED.exists():
        return []
    return [
        d.name for d in sorted(SPECS_COMPLETED.iterdir())
        if d.is_dir() and d.name != "dev" and (d / "SETUP.md").exists()
    ]


def id_to_class(script_id: str) -> str:
    return "".join(w.capitalize() for w in script_id.split("-")) + "Script"


def dry_run():
    print("Dry-run verification...")
    result = run_cmd(["gradle", "bootRun", "--dry-run"], cwd=CHROMASCAPE, check=False)
    if result.returncode != 0:
        print("✗ Dry-run failed", file=sys.stderr)
        sys.exit(1)
    print("  ✓ Dry-run passed")


def push_submodule():
    print("Pushing ChromaScape submodule...")
    run_cmd(["git", "add", "-A"], cwd=CHROMASCAPE)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=CHROMASCAPE, check=False)
    if result.returncode == 0:
        print("  No submodule changes")
        return
    run_cmd(["git", "commit", "-m", "deploy: sync scripts and resources"], cwd=CHROMASCAPE)
    run_cmd(["git", "push"], cwd=CHROMASCAPE)
    print("  ✓ Submodule pushed")


def push_parent():
    print("Pushing parent repo...")
    run_cmd(["git", "add", "-A"])
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    if result.returncode == 0:
        print("  No changes")
        return
    run_cmd(["git", "commit", "-m", "deploy: sync scripts to ChromaScape"])
    run_cmd(["git", "push"])
    print("  ✓ Pushed")


def build():
    """Compile scripts, sync to ChromaScape, and compile ChromaScape."""
    result = run_cmd(["bash", str(ROOT / "scripts/sync-and-compile.sh")], check=False)
    if result.returncode != 0:
        print("✗ Build failed", file=sys.stderr)
        sys.exit(1)


def lint():
    """Warn about private methods duplicated across scripts."""
    import re, collections
    scripts_dir = ROOT / "scriptgen/src/main/java/com/chromascape/scripts"
    sig_re = re.compile(r"private\s+\w+\s+(\w+)\(")
    # map method name -> set of filenames
    methods: dict[str, set[str]] = collections.defaultdict(set)
    for f in scripts_dir.glob("*.java"):
        for m in sig_re.findall(f.read_text()):
            methods[m].add(f.stem)
    dupes = {m: files for m, files in methods.items() if len(files) > 1}
    if dupes:
        print(f"⚠ {len(dupes)} duplicate private method(s) found:")
        for m, files in sorted(dupes.items()):
            print(f"  {m}() — {', '.join(sorted(files))}")
        return 1
    print("✓ No duplicate private methods")
    return 0

def delta():
    """Show files in ChromaScape that differ from upstream."""
    result = run_cmd(
        ["git", "diff", "--stat", "upstream/main..HEAD"],
        cwd=CHROMASCAPE, check=False,
    )
    if result.returncode != 0:
        print("Run 'osrs-bot upstream' first to fetch upstream.", file=sys.stderr)
        sys.exit(1)


# === Commands ===

def cmd_build(args):
    build()

def cmd_lint(args):
    sys.exit(lint())

def cmd_delta(args):
    delta()


def cmd_deploy(args):
    if args.script_id:
        print(f"Deploying: {args.script_id}")
    build()
    dry_run()
    if args.dry_run:
        print("\n✓ Deploy complete (dry-run, no changes pushed)")
        return
    push_submodule()
    push_parent()
    print("\n✓ Deploy complete")


def cmd_run(args):
    run_cmd(["git", "pull"])
    run_cmd(["git", "submodule", "update", "--init", "--recursive"])
    if args.browser:
        if platform.system() == "Windows":
            os.startfile("http://localhost:8080")
        else:
            subprocess.Popen(["xdg-open", "http://localhost:8080"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_cmd(["gradle", "bootRun"], cwd=CHROMASCAPE)


def cmd_logs_pull(args):
    if not LOG_FILE.exists():
        print(f"No log file at {LOG_FILE}", file=sys.stderr)
        sys.exit(1)
    dest_dir = SPECS_DEV / args.script_id
    if not dest_dir.exists():
        print(f"No dev spec for '{args.script_id}'", file=sys.stderr)
        sys.exit(1)
    dest = dest_dir / "runtime.log"
    shutil.copy2(LOG_FILE, dest)
    print(f"✓ Copied log to {dest.relative_to(ROOT)}")


def cmd_logs_tail(args):
    if not LOG_FILE.exists():
        print(f"No log file at {LOG_FILE}", file=sys.stderr)
        sys.exit(1)
    lines = LOG_FILE.read_text().splitlines()
    for line in lines[-args.n:]:
        print(line)


def cmd_bug(args):
    dest_dir = SPECS_DEV / args.script_id
    if not dest_dir.exists():
        print(f"No dev spec for '{args.script_id}'", file=sys.stderr)
        sys.exit(1)
    if LOG_FILE.exists():
        shutil.copy2(LOG_FILE, dest_dir / "runtime.log")
        print("✓ Copied runtime log")
    else:
        print("⚠ No log file found, continuing without it")
    bug_report = dest_dir / "bug-report.md"
    if not bug_report.exists() and BUG_TEMPLATE.exists():
        shutil.copy2(BUG_TEMPLATE, bug_report)
    editor = os.environ.get("EDITOR", "notepad" if platform.system() == "Windows" else "nano")
    subprocess.run([editor, str(bug_report)])
    run_cmd(["git", "add", str(dest_dir)])
    run_cmd(["git", "commit", "-m", f"bug report: {args.script_id}"], check=False)
    run_cmd(["git", "push"], check=False)
    print(f"✓ Bug report pushed for {args.script_id}")


def cmd_complete(args):
    dev_dir = SPECS_DEV / args.script_id
    dest_dir = SPECS_COMPLETED / args.script_id
    if not dev_dir.exists():
        print(f"No dev spec for '{args.script_id}'", file=sys.stderr)
        sys.exit(1)
    if dest_dir.exists():
        print(f"'{args.script_id}' already completed", file=sys.stderr)
        sys.exit(1)
    dest_dir.mkdir(parents=True)
    setup_text = ""
    if (dev_dir / "SETUP.md").exists():
        setup_text = (dev_dir / "SETUP.md").read_text()
    if (dev_dir / "changelog.md").exists():
        setup_text += "\n\n---\n\n# Changelog\n\n" + (dev_dir / "changelog.md").read_text()
    (dest_dir / "SETUP.md").write_text(setup_text)
    if (dev_dir / "manifest.json").exists():
        shutil.copy2(dev_dir / "manifest.json", dest_dir / "manifest.json")
    script_class = id_to_class(args.script_id)
    script_file = SCRIPTGEN_SCRIPTS / f"{script_class}.java"
    if script_file.exists():
        shutil.copy2(script_file, dest_dir / f"{script_class}.java")
        print(f"  ✓ Copied {script_class}.java")
    shutil.rmtree(dev_dir)
    print(f"✓ {args.script_id} marked complete → {dest_dir.relative_to(ROOT)}")
    run_cmd(["git", "add", "-A"])
    run_cmd(["git", "commit", "-m", f"complete: {args.script_id}"])
    run_cmd(["git", "push"])


def cmd_upstream(args):
    print("Fetching upstream...")
    run_cmd(["git", "fetch", "upstream"], cwd=CHROMASCAPE)
    run_cmd(["git", "merge", "upstream/main"], cwd=CHROMASCAPE)
    print("✓ Merged upstream")
    run_cmd(["git", "push"], cwd=CHROMASCAPE)
    run_cmd(["git", "add", "ChromaScape"])
    run_cmd(["git", "commit", "-m", "merge upstream ChromaScape"])
    run_cmd(["git", "push"])
    print("✓ Pushed")


def cmd_status(args):
    dev_ids = get_active_dev_ids()
    completed_ids = get_completed_ids()
    print("=== Active (dev) ===")
    if dev_ids:
        for sid in dev_ids:
            has_bug = (SPECS_DEV / sid / "bug-report.md").exists()
            print(f"  {sid}{' [BUG]' if has_bug else ''}")
    else:
        print("  (none)")
    print("\n=== Completed ===")
    if completed_ids:
        for sid in completed_ids:
            print(f"  {sid}")
    else:
        print("  (none)")
    result = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
    dirty = result.stdout.strip()
    if dirty:
        print(f"\n=== Uncommitted files ===")
        print(dirty)


def main():
    parser = argparse.ArgumentParser(prog="osrs-bot", description="Manage scripts, deployments, logs, and bugs.")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("build", help="Compile scripts, sync to ChromaScape, and compile.")
    sub.add_parser("lint", help="Warn about private methods duplicated across scripts.")
    sub.add_parser("delta", help="Show ChromaScape files that differ from upstream.")

    p_deploy = sub.add_parser("deploy", help="Build, verify, and push.")
    p_deploy.add_argument("script_id", nargs="?", help="Deploy a single script by spec ID")
    p_deploy.add_argument("--dry-run", action="store_true", help="Test deploy locally without pushing to GitHub")

    p_run = sub.add_parser("run", help="Pull latest and launch ChromaScape.")
    p_run.add_argument("--browser", action="store_true", help="Open the UI in your default browser")

    p_logs = sub.add_parser("logs", help="Manage runtime logs.")
    logs_sub = p_logs.add_subparsers(dest="logs_command")
    p_logs_pull = logs_sub.add_parser("pull", help="Copy runtime log to script's spec directory.")
    p_logs_pull.add_argument("script_id", help="Script ID")
    p_logs_tail = logs_sub.add_parser("tail", help="Show last N lines of runtime log.")
    p_logs_tail.add_argument("-n", type=int, default=50, help="Number of lines")

    p_bug = sub.add_parser("bug", help="Pull log, create bug report, push.")
    p_bug.add_argument("script_id", help="Script ID")

    p_complete = sub.add_parser("complete", help="Move script from dev to completed.")
    p_complete.add_argument("script_id", help="Script ID")

    sub.add_parser("upstream", help="Fetch and merge upstream ChromaScape updates.")
    sub.add_parser("status", help="Show active/completed scripts and pending bugs.")

    args = parser.parse_args()

    commands = {
        "build": cmd_build,
        "lint": cmd_lint,
        "delta": cmd_delta,
        "deploy": cmd_deploy,
        "run": cmd_run,
        "logs": lambda a: cmd_logs_pull(a) if a.logs_command == "pull" else cmd_logs_tail(a) if a.logs_command == "tail" else p_logs.print_help(),
        "bug": cmd_bug,
        "complete": cmd_complete,
        "upstream": cmd_upstream,
        "status": cmd_status,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
