plugins {
    java
}

group = "com.osrsbot"
version = "0.1.0"

repositories {
    mavenCentral()
    maven { url = uri("https://repo.runelite.net") }
}

dependencies {
    compileOnly("net.runelite:client:latest.release")
    compileOnly("com.google.code.gson:gson:2.10.1")
    compileOnly("org.projectlombok:lombok:1.18.30")
    annotationProcessor("org.projectlombok:lombok:1.18.30")
}

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

tasks.jar {
    archiveBaseName.set("osrsbot-plugin")
}
