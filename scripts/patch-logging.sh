#!/bin/bash
# Patch ChromaScape's log4j2.xml to add file logging
# Called by sync-and-compile.sh

LOG4J_FILE="ChromaScape/src/main/resources/log4j2.xml"
LOG_DIR="ChromaScape/logs"

mkdir -p "$LOG_DIR"

# Only patch if file appender isn't already present
if grep -q 'name="File"' "$LOG4J_FILE" 2>/dev/null; then
    echo "  ✓ File appender already present"
    exit 0
fi

cat > "$LOG4J_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN">
    <Appenders>
        <!-- Console appender for standard output -->
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="%d{HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n"/>
        </Console>

        <!-- Custom WebSocket appender -->
        <WebSocketLogAppender name="WebSocket"/>

        <!-- File appender for log capture -->
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
        <!-- Root logger sends logs to console, WebSocket, and file -->
        <Root level="info">
            <AppenderRef ref="Console"/>
            <AppenderRef ref="WebSocket"/>
            <AppenderRef ref="File"/>
        </Root>
    </Loggers>
</Configuration>
EOF

echo "  ✓ Patched log4j2.xml with file appender → logs/chromascape.log"
