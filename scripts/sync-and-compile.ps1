## Sync scriptgen scripts to ChromaScape and compile (PowerShell)

$ErrorActionPreference = "Stop"

$ScriptgenScripts = "scriptgen\src\main\java\com\chromascape\scripts"
$ScriptgenBehavior = "scriptgen\src\main\java\com\chromascape\behavior"
$ChromascapeScripts = "ChromaScape\src\main\java\com\chromascape\scripts"
$ScriptgenResources = "scriptgen\src\main\resources\images\user"
$ChromascapeResources = "ChromaScape\src\main\resources\images\user"

Write-Host "=== Syncing scripts from scriptgen to ChromaScape ==="

# Copy all scripts
Copy-Item "$ScriptgenScripts\*.java" "$ChromascapeScripts\" -Force

# Copy HumanBehavior
if (Test-Path "$ScriptgenBehavior\HumanBehavior.java") {
    Copy-Item "$ScriptgenBehavior\HumanBehavior.java" "$ChromascapeScripts\" -Force
    $file = "$ChromascapeScripts\HumanBehavior.java"
    (Get-Content $file) -replace 'package com\.chromascape\.behavior;', 'package com.chromascape.scripts;' | Set-Content $file
    Write-Host "  > Copied and updated HumanBehavior.java"
}

# Update package and import declarations
Write-Host "  > Updating imports..."
Get-ChildItem "$ChromascapeScripts\*.java" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace 'package com\.chromascape\.scripts;', 'package com.chromascape.scripts;'
    $content = $content -replace 'import com\.chromascape\.behavior\.HumanBehavior;', 'import com.chromascape.scripts.HumanBehavior;'
    Set-Content $_.FullName $content
}

# Sync image resources
Write-Host "=== Syncing image resources ==="
if (!(Test-Path $ChromascapeResources)) { New-Item -ItemType Directory -Path $ChromascapeResources -Force | Out-Null }
if (Test-Path $ScriptgenResources) {
    Copy-Item "$ScriptgenResources\*" "$ChromascapeResources\" -Force -Recurse
}

# Patch log4j2.xml
Write-Host "=== Patching logging ==="
$log4jFile = "ChromaScape\src\main\resources\log4j2.xml"
$logDir = "ChromaScape\logs"
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

if (!(Select-String -Path $log4jFile -Pattern 'name="File"' -Quiet -ErrorAction SilentlyContinue)) {
    @'
<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN">
    <Appenders>
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="%d{HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n"/>
        </Console>
        <WebSocketLogAppender name="WebSocket"/>
        <RollingFile name="File" fileName="logs/chromascape.log"
                     filePattern="logs/chromascape-%d{yyyy-MM-dd}-%i.log">
            <PatternLayout pattern="%d{HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n"/>
            <Policies>
                <SizeBasedTriggeringPolicy size="10 MB"/>
            </Policies>
            <DefaultRolloverStrategy max="3"/>
        </RollingFile>
    </Appenders>
    <Loggers>
        <Root level="info">
            <AppenderRef ref="Console"/>
            <AppenderRef ref="WebSocket"/>
            <AppenderRef ref="File"/>
        </Root>
    </Loggers>
</Configuration>
'@ | Set-Content $log4jFile
    Write-Host "  > Patched log4j2.xml with file appender"
} else {
    Write-Host "  > File appender already present"
}

# Compile
Write-Host "=== Compiling ChromaScape ==="
Push-Location ChromaScape
& .\gradlew.bat compileJava
if ($LASTEXITCODE -eq 0) {
    Write-Host "> Sync and compile complete"
} else {
    Write-Host "x Compilation failed"
    exit 1
}
Pop-Location
