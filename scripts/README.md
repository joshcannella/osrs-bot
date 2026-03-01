# Development Scripts

## Quick Reference

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
