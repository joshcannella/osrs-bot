---
inclusion: manual
---

# DreamBot Javadocs Scraper

Repeatable tool to scrape the full DreamBot API from https://dreambot.org/javadocs/ into local markdown files for Kiro knowledge.

## How to Run

```bash
# Full scrape — writes all domain files + api-reference.md
uv run scripts/refresh-javadocs.py

# Dry run — list packages and classes without writing
uv run scripts/refresh-javadocs.py --dry-run

# Scrape + validate against local jar
uv run scripts/refresh-javadocs.py --validate

# Skip specific packages
uv run scripts/refresh-javadocs.py --skip 'input.event.*' --skip 'core'
```

## When to Re-Run

- After DreamBot updates the `client:4.0.0-SNAPSHOT` jar
- After adding new skip patterns
- Run `--validate` to check if javadocs and jar are still in sync

## Output Files

| File | Purpose |
|------|---------|
| `references/api-reference.md` | Lightweight index + key class signatures (loaded by default) |
| `references/api/*.md` | Full per-domain files with all methods and descriptions |
| `references/api/validation-report.md` | Cross-check results against the local jar |

## How the Agent Uses This

- `api-reference.md` is loaded automatically via the DreamBot skill — it has the index and most-used class signatures
- When the agent needs a specific API (e.g., `FairyRings`, `Trade`), it reads the relevant `api/*.md` file on demand
- The validation report helps identify stale docs or undocumented APIs

## Skip Patterns

The `--skip` flag takes glob patterns matched against the package name (minus `org.dreambot.api.` prefix). Examples:

```bash
--skip 'input.event.*'          # skip all input event internals
--skip 'walking.pathfinding.*'  # skip pathfinding internals
--skip 'core'                   # skip org.dreambot.core
```

## Validation

The `--validate` flag cross-checks scraped classes/methods against the actual `client-4.0.0-SNAPSHOT.jar` in the Gradle cache (`~/.gradle/caches/`). It reports:

- Classes in javadocs but missing from jar (stale docs)
- Classes in jar but missing from javadocs (undocumented)
- Methods in javadocs but not found in jar bytecode

Inner classes (e.g., `Quest.State`) show as "javadocs only" because the jar uses `$` notation — this is expected.

## Dependencies

Managed via the `uv` inline script header — no manual install needed. Uses:
- `httpx` — HTTP client
- `beautifulsoup4` — HTML parsing
