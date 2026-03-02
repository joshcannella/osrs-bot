"""osrs-bot CLI — manage scripts, deployments, logs, and bugs."""

import click
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
    click.echo("Error: could not find project root (.kiro/ directory)", err=True)
    sys.exit(1)


ROOT = get_root()
SCRIPTGEN_SCRIPTS = ROOT / "scriptgen/src/main/java/com/scriptgen/scripts"
SCRIPTGEN_BEHAVIOR = ROOT / "scriptgen/src/main/java/com/scriptgen/behavior"
SCRIPTGEN_RESOURCES = ROOT / "scriptgen/src/main/resources/images/user"
CHROMASCAPE = ROOT / "ChromaScape"
CHROMASCAPE_SCRIPTS = CHROMASCAPE / "src/main/java/com/chromascape/scripts"
CHROMASCAPE_RESOURCES = CHROMASCAPE / "src/main/resources/images/user"
SPECS_DEV = ROOT / ".kiro/specs/scripts/dev"
SPECS_COMPLETED = ROOT / ".kiro/specs/scripts"
BUG_TEMPLATE = SPECS_DEV / "BUG-TEMPLATE.md"
LOG_FILE = CHROMASCAPE / "logs/chromascape.log"


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess command."""
    return subprocess.run(cmd, cwd=cwd or ROOT, check=check, capture_output=False)


def get_manifest(script_id: str) -> dict | None:
    """Load manifest.json for a script ID from dev or completed."""
    for base in [SPECS_DEV, SPECS_COMPLETED]:
        manifest = base / script_id / "manifest.json"
        if manifest.exists():
            return json.loads(manifest.read_text())
    return None


def get_active_dev_ids() -> list[str]:
    """Return script IDs currently under development."""
    if not SPECS_DEV.exists():
        return []
    return [
        d.name for d in sorted(SPECS_DEV.iterdir())
        if d.is_dir() and d.name not in ("TEMPLATE.md", "BUG-TEMPLATE.md")
        and (d / "requirements.md").exists()
    ]


def get_completed_ids() -> list[str]:
    """Return completed script IDs."""
    if not SPECS_COMPLETED.exists():
        return []
    return [
        d.name for d in sorted(SPECS_COMPLETED.iterdir())
        if d.is_dir() and d.name != "dev" and (d / "SETUP.md").exists()
    ]


def id_to_class(script_id: str) -> str:
    """Convert kebab-case ID to PascalCase class name. e.g. restless-ghost -> RestlessGhostScript."""
    return "".join(w.capitalize() for w in script_id.split("-")) + "Script"


def sync_script(script_class: str, images: list[str] | None = None):
    """Sync a single script + its images to ChromaScape."""
    src = SCRIPTGEN_SCRIPTS / f"{script_class}.java"
    dst = CHROMASCAPE_SCRIPTS / f"{script_class}.java"

    if not src.exists():
        click.echo(f"  ✗ {src} not found", err=True)
        return False

    CHROMASCAPE_SCRIPTS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    # Rewrite package and imports
    text = dst.read_text()
    text = text.replace("package com.scriptgen.scripts;", "package com.chromascape.scripts;")
    text = text.replace("import com.scriptgen.behavior.HumanBehavior;", "import com.chromascape.scripts.HumanBehavior;")
    dst.write_text(text)
    click.echo(f"  ✓ {script_class}.java")

    # Sync images
    if images:
        CHROMASCAPE_RESOURCES.mkdir(parents=True, exist_ok=True)
        for img in images:
            img_src = SCRIPTGEN_RESOURCES / img
            if img_src.exists():
                shutil.copy2(img_src, CHROMASCAPE_RESOURCES / img)
                click.echo(f"  ✓ {img}")
    return True


def sync_human_behavior():
    """Sync HumanBehavior.java to ChromaScape."""
    src = SCRIPTGEN_BEHAVIOR / "HumanBehavior.java"
    if not src.exists():
        return
    dst = CHROMASCAPE_SCRIPTS / "HumanBehavior.java"
    shutil.copy2(src, dst)
    text = dst.read_text()
    text = text.replace("package com.scriptgen.behavior;", "package com.chromascape.scripts;")
    dst.write_text(text)
    click.echo("  ✓ HumanBehavior.java")


def sync_all():
    """Sync everything from scriptgen to ChromaScape."""
    click.echo("Syncing all scripts...")
    sync_human_behavior()
    for f in sorted(SCRIPTGEN_SCRIPTS.glob("*.java")):
        script_class = f.stem
        sync_script(script_class)
    # Sync all images
    if SCRIPTGEN_RESOURCES.exists():
        CHROMASCAPE_RESOURCES.mkdir(parents=True, exist_ok=True)
        for img in sorted(SCRIPTGEN_RESOURCES.glob("*")):
            shutil.copy2(img, CHROMASCAPE_RESOURCES / img.name)
        click.echo(f"  ✓ {len(list(SCRIPTGEN_RESOURCES.glob('*')))} images synced")


def patch_logging():
    """Run the logging patcher."""
    script = ROOT / "scripts/patch-logging.sh"
    if script.exists():
        run(["bash", str(script)])


def compile_chromascape():
    """Compile ChromaScape."""
    click.echo("Compiling ChromaScape...")
    result = run(["gradle", "compileJava"], cwd=CHROMASCAPE, check=False)
    if result.returncode != 0:
        click.echo("✗ Compilation failed", err=True)
        sys.exit(1)
    click.echo("  ✓ Compiled")


def dry_run():
    """Verify boot task graph."""
    click.echo("Dry-run verification...")
    result = run(["gradle", "bootRun", "--dry-run"], cwd=CHROMASCAPE, check=False)
    if result.returncode != 0:
        click.echo("✗ Dry-run failed", err=True)
        sys.exit(1)
    click.echo("  ✓ Dry-run passed")


def push_submodule():
    """Commit and push ChromaScape submodule."""
    click.echo("Pushing ChromaScape submodule...")
    run(["git", "add", "-A"], cwd=CHROMASCAPE)
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=CHROMASCAPE, check=False
    )
    if result.returncode == 0:
        click.echo("  No submodule changes")
        return
    run(["git", "commit", "-m", "deploy: sync scripts and resources"], cwd=CHROMASCAPE)
    run(["git", "push"], cwd=CHROMASCAPE)
    click.echo("  ✓ Submodule pushed")


def push_parent():
    """Commit and push parent repo."""
    click.echo("Pushing parent repo...")
    run(["git", "add", "-A"])
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    if result.returncode == 0:
        click.echo("  No changes")
        return
    run(["git", "commit", "-m", "deploy: sync scripts to ChromaScape"])
    run(["git", "push"])
    click.echo("  ✓ Pushed")


@click.group()
def cli():
    """osrs-bot — manage scripts, deployments, logs, and bugs."""
    pass


@cli.command()
@click.argument("script_id", required=False)
def deploy(script_id):
    """Sync, compile, verify, and push. Optionally target a single script."""
    if script_id:
        click.echo(f"Deploying: {script_id}")
        manifest = get_manifest(script_id)
        script_class = manifest["script_class"] if manifest else id_to_class(script_id)
        images = manifest.get("images", []) if manifest else []
        sync_human_behavior()
        if not sync_script(script_class, images):
            sys.exit(1)
    else:
        sync_all()

    patch_logging()
    compile_chromascape()
    dry_run()
    push_submodule()
    push_parent()
    click.echo("\n✓ Deploy complete")


@cli.command("run")
@click.option("--browser", is_flag=True, help="Open the UI in your default browser.")
def run_app(browser):
    """Pull latest and launch ChromaScape."""
    run(["git", "pull"])
    run(["git", "submodule", "update", "--init", "--recursive"])

    if browser:
        if platform.system() == "Windows":
            os.startfile("http://localhost:8080")
        else:
            subprocess.Popen(["xdg-open", "http://localhost:8080"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    gradle = "gradlew.bat" if platform.system() == "Windows" else "gradle"
    run([gradle, "clean", "bootRun"], cwd=CHROMASCAPE)


@cli.group()
def logs():
    """Manage runtime logs."""
    pass


@logs.command("pull")
@click.argument("script_id")
def logs_pull(script_id):
    """Copy the runtime log to a script's spec directory."""
    if not LOG_FILE.exists():
        click.echo(f"No log file at {LOG_FILE}", err=True)
        sys.exit(1)

    dest_dir = SPECS_DEV / script_id
    if not dest_dir.exists():
        click.echo(f"No dev spec for '{script_id}'", err=True)
        sys.exit(1)

    dest = dest_dir / "runtime.log"
    shutil.copy2(LOG_FILE, dest)
    click.echo(f"✓ Copied log to {dest.relative_to(ROOT)}")


@logs.command("tail")
@click.option("-n", default=50, help="Number of lines to show.")
def logs_tail(n):
    """Show the last N lines of the runtime log."""
    if not LOG_FILE.exists():
        click.echo(f"No log file at {LOG_FILE}", err=True)
        sys.exit(1)

    lines = LOG_FILE.read_text().splitlines()
    for line in lines[-n:]:
        click.echo(line)


@cli.command()
@click.argument("script_id")
def bug(script_id):
    """Pull log, create bug report, commit and push — ready for the agent to fix."""
    dest_dir = SPECS_DEV / script_id
    if not dest_dir.exists():
        click.echo(f"No dev spec for '{script_id}'", err=True)
        sys.exit(1)

    # Copy log
    if LOG_FILE.exists():
        shutil.copy2(LOG_FILE, dest_dir / "runtime.log")
        click.echo(f"✓ Copied runtime log")
    else:
        click.echo("⚠ No log file found, continuing without it")

    # Create bug report from template
    bug_report = dest_dir / "bug-report.md"
    if not bug_report.exists() and BUG_TEMPLATE.exists():
        shutil.copy2(BUG_TEMPLATE, bug_report)

    # Open in editor
    editor = os.environ.get("EDITOR", "notepad" if platform.system() == "Windows" else "nano")
    subprocess.run([editor, str(bug_report)])

    # Commit and push
    run(["git", "add", str(dest_dir)])
    run(["git", "commit", "-m", f"bug report: {script_id}"], check=False)
    run(["git", "push"], check=False)
    click.echo(f"✓ Bug report pushed for {script_id}")


@cli.command()
@click.argument("script_id")
def complete(script_id):
    """Move a script from dev to completed."""
    dev_dir = SPECS_DEV / script_id
    dest_dir = SPECS_COMPLETED / script_id

    if not dev_dir.exists():
        click.echo(f"No dev spec for '{script_id}'", err=True)
        sys.exit(1)
    if dest_dir.exists():
        click.echo(f"'{script_id}' already completed", err=True)
        sys.exit(1)

    dest_dir.mkdir(parents=True)

    # Merge SETUP.md + changelog.md
    setup_text = ""
    setup_file = dev_dir / "SETUP.md"
    changelog_file = dev_dir / "changelog.md"
    if setup_file.exists():
        setup_text = setup_file.read_text()
    if changelog_file.exists():
        setup_text += "\n\n---\n\n# Changelog\n\n" + changelog_file.read_text()
    (dest_dir / "SETUP.md").write_text(setup_text)

    # Copy manifest if present
    manifest_file = dev_dir / "manifest.json"
    if manifest_file.exists():
        shutil.copy2(manifest_file, dest_dir / "manifest.json")

    # Copy script source
    script_class = id_to_class(script_id)
    script_file = SCRIPTGEN_SCRIPTS / f"{script_class}.java"
    if script_file.exists():
        shutil.copy2(script_file, dest_dir / f"{script_class}.java")
        click.echo(f"  ✓ Copied {script_class}.java")

    # Remove dev directory
    shutil.rmtree(dev_dir)
    click.echo(f"✓ {script_id} marked complete → {dest_dir.relative_to(ROOT)}")

    # Commit and push
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", f"complete: {script_id}"])
    run(["git", "push"])


@cli.command()
def upstream():
    """Fetch and merge upstream ChromaScape updates."""
    click.echo("Fetching upstream...")
    run(["git", "fetch", "upstream"], cwd=CHROMASCAPE)
    run(["git", "merge", "upstream/main"], cwd=CHROMASCAPE)
    click.echo("✓ Merged upstream")

    # Push updated submodule
    run(["git", "push"], cwd=CHROMASCAPE)
    run(["git", "add", "ChromaScape"])
    run(["git", "commit", "-m", "merge upstream ChromaScape"])
    run(["git", "push"])
    click.echo("✓ Pushed")


@cli.command()
def status():
    """Show active/completed scripts and pending bugs."""
    dev_ids = get_active_dev_ids()
    completed_ids = get_completed_ids()

    click.echo("=== Active (dev) ===")
    if dev_ids:
        for sid in dev_ids:
            has_bug = (SPECS_DEV / sid / "bug-report.md").exists()
            marker = " [BUG]" if has_bug else ""
            click.echo(f"  {sid}{marker}")
    else:
        click.echo("  (none)")

    click.echo("\n=== Completed ===")
    if completed_ids:
        for sid in completed_ids:
            click.echo(f"  {sid}")
    else:
        click.echo("  (none)")

    # Check for uncommitted changes
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True
    )
    dirty = result.stdout.strip()
    if dirty:
        click.echo(f"\n=== Uncommitted files ===")
        click.echo(dirty)


def main():
    cli()
