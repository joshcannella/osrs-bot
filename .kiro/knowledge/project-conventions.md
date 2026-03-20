# Project Conventions

## Architecture

ChromaScape is a separate git repo (your fork) cloned inside the project root. It is NOT a submodule — it's listed in `.gitignore` and managed independently.

- **Scripts** go directly into `ChromaScape/src/main/java/com/chromascape/scripts/`
- **Images** go into `ChromaScape/src/main/resources/images/user/`
- **Custom utilities** go into `ChromaScape/src/main/java/com/chromascape/utils/actions/custom/`
- **Specs and knowledge** live in the parent repo under `.kiro/`

## Two-Repo Workflow

The parent repo (`osrs-bot`) and ChromaScape are pushed independently:
- `osrs-bot deploy` pushes both
- On Windows: `git pull` in both, then `osrs-bot run`

## Script Spec Lifecycle

Script specifications live under `.kiro/specs/scripts/` and follow a lifecycle:

- **`dev/`** — Scripts under active development. These are works in progress, may have bugs, and are being iterated on. Requirements, runtime logs, and bug reports live here during development.
- **`complete/`** — Finished scripts considered working. These have been tested, are stable, and are ready for use. Moving a spec from `dev/` to `complete/` marks it as done.

When referencing script status:
- Scripts listed under `dev/` are NOT finished — they need work.
- Scripts listed under `complete/` are finished — treat them as working products.
- To mark a script complete: `osrs-bot complete <script-id>`
