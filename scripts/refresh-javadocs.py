# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx", "beautifulsoup4"]
# ///
"""Scrape DreamBot javadocs into local markdown for Kiro knowledge.

Usage:
    uv run scripts/refresh-javadocs.py              # full scrape + write
    uv run scripts/refresh-javadocs.py --dry-run    # list packages/classes only
    uv run scripts/refresh-javadocs.py --validate   # scrape + cross-check against jar
    uv run scripts/refresh-javadocs.py --skip 'input.event.*' --skip 'core'
"""

import argparse
import fnmatch
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://dreambot.org/javadocs"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_OUT = PROJECT_ROOT / ".kiro/skills/dreambot/references/api"
API_REF = PROJECT_ROOT / ".kiro/skills/dreambot/references/api-reference.md"
JAR_PATTERN = "org.dreambot/client/4.0.0-SNAPSHOT"
REQUEST_DELAY = 0.05  # seconds between requests

# Domain grouping: package substring → domain name
DOMAIN_MAP = [
    ("methods.interactive", "interactive"),
    ("methods.container", "containers"),
    ("methods.depositbox", "containers"),
    ("methods.grandexchange", "grandexchange"),
    ("methods.walking", "walking"),
    ("methods.map", "map"),
    ("methods.combat", "combat"),
    ("methods.magic", "magic"),
    ("methods.prayer", "prayer"),
    ("methods.dialogues", "dialogues"),
    ("methods.skills", "skills"),
    ("methods.tabs", "tabs"),
    ("methods.widget", "widgets"),
    ("methods.world", "world"),
    ("methods.settings", "settings"),
    ("methods.item", "items"),
    ("methods.quest", "quests"),
    ("methods.trade", "trade"),
    ("methods.login", "login"),
    ("methods.filter", "filters"),
    ("methods.clan", "clan"),
    ("methods.fairyring", "fairyring"),
    ("methods.favour", "favour"),
    ("methods.sailing", "sailing"),
    ("methods.emotes", "emotes"),
    ("methods.hint", "misc-methods"),
    ("methods.hotkeys", "misc-methods"),
    ("methods.ignore", "misc-methods"),
    ("methods.friend", "misc-methods"),
    ("methods.bond", "misc-methods"),
    ("methods.music", "misc-methods"),
    ("methods.diary", "misc-methods"),
    ("methods.minigame", "misc-methods"),
    ("methods.event", "misc-methods"),
    ("methods.cs2", "misc-methods"),
    ("methods.input", "input"),
    ("methods", "methods-base"),
    ("wrappers.interactive", "wrappers-entities"),
    ("wrappers.items", "wrappers-items"),
    ("wrappers.widgets", "wrappers-widgets"),
    ("wrappers.map", "wrappers-map"),
    ("wrappers.cache", "wrappers-cache"),
    ("wrappers.graphics", "wrappers-graphics"),
    ("wrappers", "wrappers-base"),
    ("script.frameworks", "script-frameworks"),
    ("script.listener", "script-listeners"),
    ("script.schedule", "script-schedule"),
    ("script.event", "script-events"),
    ("script", "script"),
    ("input.event", "input-events"),
    ("input.mouse", "input-mouse"),
    ("input.keyboard", "input-keyboard"),
    ("input", "input"),
    ("data", "data"),
    ("utilities", "utilities"),
    ("randoms", "randoms"),
    ("settings", "client-settings"),
    ("core", "core"),
]

# Priority order for combined api-reference.md (most-used first)
DOMAIN_PRIORITY = [
    "interactive", "containers", "walking", "map", "combat", "magic",
    "prayer", "dialogues", "skills", "grandexchange", "widgets", "world",
    "wrappers-entities", "wrappers-items", "wrappers-map", "wrappers-widgets",
    "script-frameworks", "script", "items", "settings", "input", "filters",
    "data", "utilities",
]


@dataclass
class MethodInfo:
    name: str
    return_type: str
    params: str
    description: str
    modifiers: str = ""

    @property
    def signature(self) -> str:
        mods = f"{self.modifiers} " if self.modifiers else ""
        return f"{mods}{self.return_type} {self.name}({self.params})"


@dataclass
class FieldInfo:
    name: str
    type: str
    modifiers: str = ""
    description: str = ""


@dataclass
class ClassInfo:
    name: str
    package: str
    url: str
    kind: str = "class"  # class, interface, enum, annotation
    hierarchy: str = ""
    methods: list[MethodInfo] = field(default_factory=list)
    fields: list[FieldInfo] = field(default_factory=list)
    inherited_from: dict[str, list[str]] = field(default_factory=dict)


# ── Scraping ──────────────────────────────────────────────────────────


def fetch(client: httpx.Client, url: str) -> BeautifulSoup:
    time.sleep(REQUEST_DELAY)
    resp = client.get(url, follow_redirects=True)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def discover_packages(client: httpx.Client) -> list[tuple[str, str]]:
    """Return list of (package_name, package_url)."""
    soup = fetch(client, f"{BASE_URL}/index.html")
    packages = []
    for a in soup.select("a[href*='package-summary.html']"):
        href = a.get("href", "")
        name = a.get_text(strip=True)
        if name.startswith("org.dreambot"):
            url = f"{BASE_URL}/{href}" if not href.startswith("http") else href
            packages.append((name, url))
    return packages


def discover_classes(client: httpx.Client, pkg_name: str, pkg_url: str) -> list[ClassInfo]:
    """Return list of ClassInfo for all classes in a package."""
    soup = fetch(client, pkg_url)
    classes = []
    base = pkg_url.rsplit("/", 1)[0]

    for table in soup.select("table"):
        caption = table.select_one("caption")
        if not caption:
            continue
        caption_text = caption.get_text(strip=True).lower()
        if "class" in caption_text:
            kind = "class"
        elif "interface" in caption_text:
            kind = "interface"
        elif "enum" in caption_text:
            kind = "enum"
        elif "annotation" in caption_text:
            kind = "annotation"
        else:
            continue

        for row in table.select("tbody tr"):
            link = row.select_one("a")
            if not link:
                continue
            name = link.get_text(strip=True)
            href = link.get("href", "")
            url = f"{base}/{href}" if not href.startswith("http") else href
            classes.append(ClassInfo(name=name, package=pkg_name, url=url, kind=kind))

    return classes


def _clean_type(text: str) -> str:
    """Clean up type text from javadoc HTML into concise Java-style types."""
    text = text.replace("\u200b", "").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text.strip())
    text = text.replace("@ NonNull ", "@NonNull ").replace("@ Nullable ", "@Nullable ")
    text = re.sub(r"@\s*(NonNull|Nullable)\s*", "", text)  # strip annotations
    text = text.replace(". ", ".").strip()
    # Simplify fully-qualified types to short names
    for fq, short in _TYPE_SIMPLIFICATIONS:
        text = text.replace(fq, short)
    # Clean up generic spacing: List< Item > → List<Item>
    text = re.sub(r"<\s+", "<", text)
    text = re.sub(r"\s+>", ">", text)
    # Fix varargs spacing: String...names → String... names
    text = re.sub(r"\.\.\.(\w)", r"... \1", text)
    return text.strip()


_TYPE_SIMPLIFICATIONS = [
    ("java.util.List", "List"),
    ("java.util.Collection", "Collection"),
    ("java.util.Map", "Map"),
    ("java.util.Set", "Set"),
    ("java.lang.String", "String"),
    ("java.lang.Integer", "Integer"),
    ("java.lang.Object", "Object"),
    ("java.lang.Class", "Class"),
    ("java.lang.Boolean", "Boolean"),
    ("java.lang.Long", "Long"),
    ("java.lang.Double", "Double"),
    ("java.awt.Rectangle", "Rectangle"),
    ("java.awt.Point", "Point"),
    ("java.awt.Color", "Color"),
    ("java.awt.Graphics2D", "Graphics2D"),
    ("java.awt.image.BufferedImage", "BufferedImage"),
    ("java.awt.Polygon", "Polygon"),
    ("net.runelite.api.", ""),  # strip runelite prefix
]


def _parse_method_cell(cell: Tag) -> tuple[str, str]:
    """Parse method name and params from the method column."""
    text = cell.get_text(" ", strip=True)
    # Clean unicode whitespace chars
    text = text.replace("\u200b", "").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    # Pattern: methodName (params) or methodName()
    m = re.match(r"(\w+)\s*\((.*)\)", text)
    if m:
        return m.group(1), _clean_type(m.group(2))
    return text.strip(), ""


def extract_class_details(client: httpx.Client, cls: ClassInfo) -> ClassInfo:
    """Fetch a class page and extract methods, fields, hierarchy."""
    soup = fetch(client, cls.url)

    # Hierarchy
    hier_el = soup.select_one("ul.inheritance")
    if hier_el:
        items = [li.get_text(strip=True).replace(". ", ".") for li in hier_el.select("li")]
        cls.hierarchy = " → ".join(items)

    # Method Summary table
    for table in soup.select("table"):
        caption = table.select_one("caption")
        if not caption:
            continue
        cap_text = caption.get_text(strip=True).lower()
        if "method" in cap_text:
            _parse_method_table(table, cls)
        elif "field" in cap_text:
            _parse_field_table(table, cls)
        elif "enum constant" in cap_text:
            _parse_enum_table(table, cls)

    # Inherited methods
    for section in soup.select("li.blockList"):
        heading = section.select_one("h3")
        if not heading:
            continue
        h_text = heading.get_text(strip=True)
        if "inherited" not in h_text.lower() or "method" not in h_text.lower():
            continue
        # Extract parent class name from heading text like "Methods inherited from class org.dreambot.api.wrappers.interactive.Character"
        parent = h_text.split("from")[-1].strip().removeprefix("class ").removeprefix("interface ").strip()
        codes = section.select("code a")
        method_names = [c.get_text(strip=True) for c in codes]
        if method_names and parent != "java.lang.Object":
            cls.inherited_from[parent] = method_names

    return cls


def _parse_method_table(table: Tag, cls: ClassInfo):
    for row in table.select("tr"):
        # Data rows have a td.colFirst (type) and th.colSecond (method)
        type_cell = row.select_one("td.colFirst")
        method_cell = row.select_one("th.colSecond")
        if not type_cell or not method_cell:
            continue

        type_text = _clean_type(type_cell.get_text(" ", strip=True))
        modifiers = ""
        ret_type = type_text
        if "static " in type_text:
            modifiers = "static"
            ret_type = type_text.replace("static ", "", 1).strip()

        method_name, params = _parse_method_cell(method_cell)
        desc_cell = row.select_one("td.colLast")
        desc = desc_cell.get_text(" ", strip=True) if desc_cell else ""
        desc = re.sub(r"\s+", " ", desc).strip()

        cls.methods.append(MethodInfo(
            name=method_name, return_type=ret_type, params=params,
            description=desc, modifiers=modifiers,
        ))


def _parse_field_table(table: Tag, cls: ClassInfo):
    for row in table.select("tr"):
        type_cell = row.select_one("td.colFirst")
        name_cell = row.select_one("th.colSecond")
        if not type_cell or not name_cell:
            continue
        type_text = _clean_type(type_cell.get_text(" ", strip=True))
        modifiers = ""
        ftype = type_text
        if "static " in type_text:
            modifiers = "static"
            ftype = type_text.replace("static ", "", 1).strip()
        name = name_cell.get_text(strip=True)
        desc_cell = row.select_one("td.colLast")
        desc = desc_cell.get_text(" ", strip=True) if desc_cell else ""
        cls.fields.append(FieldInfo(name=name, type=ftype, modifiers=modifiers, description=desc))


def _parse_enum_table(table: Tag, cls: ClassInfo):
    for row in table.select("tr"):
        name_cell = row.select_one("th.colFirst")
        if not name_cell or name_cell.get_text(strip=True) == "Enum Constant":
            continue
        name = name_cell.get_text(strip=True)
        desc_cell = row.select_one("td.colLast")
        desc = desc_cell.get_text(" ", strip=True) if desc_cell else ""
        cls.fields.append(FieldInfo(name=name, type="enum", modifiers="", description=desc))


# ── Domain grouping ───────────────────────────────────────────────────


def get_domain(package: str) -> str:
    # Strip the org.dreambot.api. prefix for matching
    short = package.removeprefix("org.dreambot.api.")
    if short == package:
        short = package.removeprefix("org.dreambot.")
    for pattern, domain in DOMAIN_MAP:
        if short.startswith(pattern):
            return domain
    return "other"


def group_by_domain(classes: list[ClassInfo]) -> dict[str, list[ClassInfo]]:
    domains: dict[str, list[ClassInfo]] = {}
    for cls in classes:
        domain = get_domain(cls.package)
        domains.setdefault(domain, []).append(cls)
    # Sort classes within each domain by name
    for domain in domains:
        domains[domain].sort(key=lambda c: c.name)
    return domains


# ── Markdown generation ───────────────────────────────────────────────


def class_to_markdown(cls: ClassInfo) -> str:
    lines = [f"### {cls.name}", f""]
    lines.append(f"**Package:** `{cls.package}`  ")
    lines.append(f"**Type:** {cls.kind}  ")
    if cls.hierarchy:
        lines.append(f"**Hierarchy:** {cls.hierarchy}  ")
    lines.append("")

    if cls.fields:
        if cls.kind == "enum":
            lines.append("**Constants:**")
        else:
            lines.append("**Fields:**")
        lines.append("```java")
        for f in cls.fields:
            mods = f"{f.modifiers} " if f.modifiers else ""
            if cls.kind == "enum":
                lines.append(f"{f.name}")
            else:
                lines.append(f"{mods}{f.type} {f.name}")
        lines.append("```")
        lines.append("")

    if cls.methods:
        lines.append("**Methods:**")
        lines.append("```java")
        for m in cls.methods:
            lines.append(f"{m.signature};")
        lines.append("```")
        lines.append("")
        # Method descriptions (only for those that have one)
        described = [m for m in cls.methods if m.description]
        if described:
            lines.append("| Method | Description |")
            lines.append("|--------|-------------|")
            for m in described:
                desc = m.description.replace("|", "\\|")
                lines.append(f"| `{m.name}({m.params})` | {desc} |")
            lines.append("")

    if cls.inherited_from:
        lines.append("**Inherited methods:**")
        for parent, methods in cls.inherited_from.items():
            short_parent = parent.rsplit(".", 1)[-1] if "." in parent else parent
            lines.append(f"- From `{short_parent}`: {', '.join(f'`{m}`' for m in methods[:15])}")
            if len(methods) > 15:
                lines.append(f"  ...and {len(methods) - 15} more")
        lines.append("")

    return "\n".join(lines)


def write_domain_file(domain: str, classes: list[ClassInfo], timestamp: str):
    path = API_OUT / f"{domain}.md"
    lines = [
        f"# DreamBot API — {domain}",
        f"",
        f"<!-- Auto-generated by scripts/refresh-javadocs.py on {timestamp} -->",
        f"<!-- Source: {BASE_URL} -->",
        f"",
    ]
    for cls in classes:
        lines.append(class_to_markdown(cls))
        lines.append("---\n")
    path.write_text("\n".join(lines))
    return path


def write_combined_reference(domains: dict[str, list[ClassInfo]], timestamp: str):
    """Write a lightweight index + commonly-used snippets. NOT the full dump."""
    lines = [
        "# DreamBot API Reference",
        "",
        f"<!-- Auto-generated by scripts/refresh-javadocs.py on {timestamp} -->",
        f"<!-- Source: {BASE_URL} -->",
        "<!-- Full details in references/api/*.md — load those for specific APIs -->",
        "",
        "## API Index",
        "",
        "Each domain has a dedicated file in `references/api/` with full method signatures.",
        "",
    ]

    ordered = []
    for d in DOMAIN_PRIORITY:
        if d in domains:
            ordered.append(d)
    for d in sorted(domains):
        if d not in ordered:
            ordered.append(d)

    for domain in ordered:
        classes = domains[domain]
        class_names = ", ".join(c.name for c in classes)
        method_count = sum(len(c.methods) for c in classes)
        lines.append(f"- **[{domain}](api/{domain}.md)** ({method_count} methods) — {class_names}")
    lines.append("")

    # Commonly-used quick reference for the most important classes
    KEY_CLASSES = [
        "GameObjects", "NPCs", "Players", "GroundItems",
        "Bank", "Inventory", "Equipment", "Shop", "DepositBox",
        "Walking", "Tile", "Area",
        "Combat", "Magic", "Prayers", "Dialogues",
        "Skills", "GrandExchange", "Widgets", "WorldHopper",
        "Sleep", "Keyboard", "Mouse", "ItemProcessing",
        "TreeScript", "Branch", "Leaf", "TaskScript", "AbstractScript", "TaskNode",
    ]
    class_lookup = {c.name: c for c in sum(domains.values(), [])}

    lines.append("## Quick Reference — Most-Used Classes\n")
    lines.append("Method signatures for the classes you'll use in almost every script.")
    lines.append("Redundant overloads trimmed — see domain files for full signatures.\n")

    for name in KEY_CLASSES:
        cls = class_lookup.get(name)
        if not cls or not cls.methods:
            continue
        lines.append(f"### {cls.name}")
        lines.append(f"`{cls.package}` · [full details](api/{get_domain(cls.package)}.md)\n")
        lines.append("```java")
        for m in _trim_overloads(cls.methods):
            lines.append(f"{m.signature};")
        lines.append("```")
        lines.append("")

    API_REF.write_text("\n".join(lines))


def _trim_overloads(methods: list[MethodInfo]) -> list[MethodInfo]:
    """Keep the most useful overload per method name. Prefer String params over int/Filter/Item."""
    from collections import defaultdict
    groups: dict[str, list[MethodInfo]] = defaultdict(list)
    for m in methods:
        groups[m.name].append(m)

    result = []
    for name, overloads in groups.items():
        if len(overloads) == 1:
            result.append(overloads[0])
            continue
        # Score each overload: prefer String params, then no-arg, then int+amount
        kept = []
        for m in overloads:
            p = m.params.lower()
            # Always keep: no-arg, String, String+int
            if not p:
                kept.append(m)
            elif "string" in p and "filter" not in p:
                kept.append(m)
            # Keep int+int (id, amount) but skip bare int id or int[] ids
            elif re.match(r"^int \w+,\s*int \w+$", p):
                kept.append(m)
            elif "filter" in p and not any("string" in k.params.lower() for k in kept):
                # Only keep Filter variant if no String variant exists
                kept.append(m)
        # Fallback: if nothing matched, keep first and last
        if not kept:
            kept = [overloads[0]]
        result.extend(kept)
    return result


# ── Jar validation ────────────────────────────────────────────────────


def find_jar() -> Path | None:
    gradle_cache = Path.home() / ".gradle/caches/modules-2/files-2.1"
    candidates = [
        p for p in gradle_cache.glob(f"{JAR_PATTERN}/*/client-*.jar")
        if "javadoc" not in p.name and "sources" not in p.name
    ]
    return candidates[0] if candidates else None


def get_jar_classes(jar_path: Path) -> set[str]:
    """Get all class names from the jar (as dotted names)."""
    result = subprocess.run(
        ["jar", "tf", str(jar_path)], capture_output=True, text=True, check=True,
    )
    classes = set()
    for line in result.stdout.splitlines():
        if line.endswith(".class") and not "$" in line:
            cls = line.removesuffix(".class").replace("/", ".")
            if cls.startswith("org.dreambot.api"):
                classes.add(cls)
    return classes


def get_jar_methods(jar_path: Path, fqcn: str) -> set[str]:
    """Get public method names from a class via javap."""
    result = subprocess.run(
        ["javap", "-public", "-cp", str(jar_path), fqcn],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return set()
    methods = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if "(" in line and not line.startswith("public class") and not line.startswith("public interface"):
            # Extract method name
            m = re.search(r"(\w+)\s*\(", line)
            if m:
                methods.add(m.group(1))
    return methods


def validate(scraped: list[ClassInfo], jar_path: Path) -> str:
    """Cross-check scraped classes/methods against jar. Returns markdown report."""
    jar_classes = get_jar_classes(jar_path)
    scraped_fqcns = {f"{c.package}.{c.name}" for c in scraped}

    # Classes in javadocs but not in jar
    docs_only = sorted(scraped_fqcns - jar_classes)
    # Classes in jar but not in javadocs (only org.dreambot.api, skip inner classes)
    jar_only = sorted(jar_classes - scraped_fqcns)

    # Method-level check for scraped classes that exist in jar
    method_issues = []
    common = scraped_fqcns & jar_classes
    checked = 0
    for cls in scraped:
        fqcn = f"{cls.package}.{cls.name}"
        if fqcn not in common or not cls.methods:
            continue
        jar_methods = get_jar_methods(jar_path, fqcn)
        if not jar_methods:
            continue
        checked += 1
        scraped_names = {m.name for m in cls.methods}
        missing_from_jar = scraped_names - jar_methods
        if missing_from_jar:
            method_issues.append((cls.name, sorted(missing_from_jar)))

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Validation Report",
        f"",
        f"Generated: {timestamp}  ",
        f"Jar: `{jar_path.name}`  ",
        f"Scraped classes: {len(scraped_fqcns)}  ",
        f"Jar classes (public, non-inner): {len(jar_classes)}  ",
        f"Method-checked classes: {checked}  ",
        "",
        "## Summary",
        f"- ✅ Classes in both: {len(common)}",
        f"- ⚠️  In javadocs only (stale docs?): {len(docs_only)}",
        f"- 📦 In jar only (undocumented): {len(jar_only)}",
        f"- 🔍 Method mismatches: {len(method_issues)}",
        "",
    ]

    if docs_only:
        lines.append("## Classes in Javadocs but NOT in Jar\n")
        for c in docs_only:
            lines.append(f"- `{c}`")
        lines.append("")

    if jar_only:
        lines.append("## Classes in Jar but NOT in Javadocs\n")
        for c in jar_only:
            lines.append(f"- `{c}`")
        lines.append("")

    if method_issues:
        lines.append("## Method Mismatches (in docs but not found in jar)\n")
        for cls_name, methods in method_issues:
            lines.append(f"### {cls_name}")
            for m in methods:
                lines.append(f"- `{m}`")
            lines.append("")

    if not docs_only and not jar_only and not method_issues:
        lines.append("✅ **All clear** — javadocs and jar are in sync.\n")

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────


def should_skip(pkg_name: str, skip_patterns: list[str]) -> bool:
    short = pkg_name.removeprefix("org.dreambot.api.")
    return any(fnmatch.fnmatch(short, p) for p in skip_patterns)


def main():
    parser = argparse.ArgumentParser(description="Scrape DreamBot javadocs into markdown")
    parser.add_argument("--dry-run", action="store_true", help="List packages/classes without writing")
    parser.add_argument("--validate", action="store_true", help="Cross-check against local jar")
    parser.add_argument("--skip", action="append", default=[], metavar="PATTERN",
                        help="Skip packages matching glob (e.g. 'input.event.*')")
    args = parser.parse_args()

    print("🔍 Discovering packages...")
    with httpx.Client(timeout=30) as client:
        packages = discover_packages(client)
        print(f"   Found {len(packages)} packages")

        # Filter
        packages = [(n, u) for n, u in packages if not should_skip(n, args.skip)]
        if args.skip:
            print(f"   After skip filters: {len(packages)} packages")

        if args.dry_run:
            for name, _ in packages:
                print(f"   📦 {name}")

        # Discover classes
        print("📋 Discovering classes...")
        all_classes: list[ClassInfo] = []
        for pkg_name, pkg_url in packages:
            classes = discover_classes(client, pkg_name, pkg_url)
            all_classes.extend(classes)
            if args.dry_run and classes:
                print(f"   📦 {pkg_name}: {', '.join(c.name for c in classes)}")

        print(f"   Found {len(all_classes)} classes total")

        if args.dry_run:
            return

        # Extract details for each class
        print("🔬 Extracting class details...")
        total = len(all_classes)
        for i, cls in enumerate(all_classes, 1):
            if i % 20 == 0 or i == total:
                print(f"   [{i}/{total}] {cls.package}.{cls.name}")
            extract_class_details(client, cls)

    # Group and write
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    domains = group_by_domain(all_classes)

    print(f"📝 Writing {len(domains)} domain files...")
    API_OUT.mkdir(parents=True, exist_ok=True)
    for domain, classes in sorted(domains.items()):
        path = write_domain_file(domain, classes, timestamp)
        method_count = sum(len(c.methods) for c in classes)
        print(f"   {path.name}: {len(classes)} classes, {method_count} methods")

    print("📝 Writing combined api-reference.md...")
    write_combined_reference(domains, timestamp)

    total_methods = sum(len(c.methods) for c in all_classes)
    print(f"✅ Done — {len(all_classes)} classes, {total_methods} methods")

    # Validation
    if args.validate:
        print("\n🔎 Validating against local jar...")
        jar_path = find_jar()
        if not jar_path:
            print("   ❌ Could not find client-4.0.0-SNAPSHOT.jar in Gradle cache")
            print(f"   Looked in: ~/.gradle/caches/modules-2/files-2.1/{JAR_PATTERN}/")
            sys.exit(1)
        print(f"   Jar: {jar_path}")
        report = validate(all_classes, jar_path)
        report_path = API_OUT / "validation-report.md"
        report_path.write_text(report)
        print(f"   Report: {report_path}")
        # Print summary
        for line in report.splitlines():
            if line.startswith("- "):
                print(f"   {line}")


if __name__ == "__main__":
    main()
