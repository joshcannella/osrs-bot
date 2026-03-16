# Project Conventions

## Script Spec Lifecycle

Script specifications live under `.kiro/specs/scripts/` and follow a lifecycle:

- **`dev/`** — Scripts under active development. These are works in progress, may have bugs, and are being iterated on. Requirements, runtime logs, and bug reports live here during development.
- **`complete/`** — Finished scripts considered working. These have been tested, are stable, and are ready for use. Moving a spec from `dev/` to `complete/` marks it as done.

When referencing script status:
- Scripts listed under `dev/` are NOT finished — they need work.
- Scripts listed under `complete/` are finished — treat them as working products.
- To mark a script complete, move its entire folder from `dev/` to `complete/`.
