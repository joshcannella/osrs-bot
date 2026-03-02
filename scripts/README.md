# Development Scripts

## Quick Reference

### Deploy (sync + compile, ready for Windows pull)
```bash
./scripts/deploy.sh
```
Syncs scripts to ChromaScape, compiles, and prepares for `git pull` on Windows.

### Sync and compile only
```bash
./scripts/sync-and-compile.sh
```
Copies scripts from `scriptgen/` to `ChromaScape/`, fixes package names and imports, syncs image resources, and compiles in ChromaScape.

### Check if scriptgen compiles
```bash
./scripts/check-scriptgen.sh
```
Verifies that all scripts in `scriptgen/` compile successfully.

### Sync and compile to ChromaScape
```bash
./scripts/sync-and-compile.sh
```
Copies scripts from `scriptgen/` to `ChromaScape/`, syncs image resources, and compiles ChromaScape.

## Workflow

1. Generate/edit scripts in `scriptgen/src/main/java/com/scriptgen/scripts/`
2. Run `./scripts/sync-and-compile.sh` to deploy and compile in ChromaScape
3. Start ChromaScape and test your script

**Important**: Always use `sync-and-compile.sh` instead of manually copying files. It automatically:
- Copies scripts from scriptgen to ChromaScape
- Updates package declarations (com.scriptgen.behavior → com.chromascape.scripts)
- Updates import statements
- Syncs image resources
- Compiles and verifies the code works in ChromaScape

## Troubleshooting

**"No pom.xml found"**: Run from project root, not from scripts/ directory

**Compilation errors**: Check that scriptgen compiles first with `check-scriptgen.sh`

**Note**: Both scriptgen and ChromaScape use Gradle. The sync script handles copying and recompiling automatically.

**Missing images**: Ensure images are in `scriptgen/src/main/resources/images/user/`

### Mark a script as complete
```bash
./scripts/complete-script.sh <script-id>
```
Moves the script from `dev/` to a completed directory with a merged SETUP.md (setup + changelog). Removes the dev directory.
