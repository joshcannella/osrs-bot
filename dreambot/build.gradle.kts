plugins {
    java
}

repositories {
    maven {
        url = uri("https://maven.dreambot.org")
        content { includeGroup("org.dreambot") }
    }
    mavenCentral()
}

dependencies {
    compileOnly("org.dreambot:client:4.0.0-SNAPSHOT") { isTransitive = false }
}

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

tasks.withType<JavaCompile> {
    options.encoding = "UTF-8"
}

tasks.jar {
    archiveBaseName.set(project.findProperty("jarName") as? String ?: "osrs-scripts")
    archiveVersion.set(project.findProperty("jarVersion") as? String ?: "0.1")
}
