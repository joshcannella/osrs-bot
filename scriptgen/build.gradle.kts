plugins {
    java
}

group = "com.chromascape"
version = "0.1.0"

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.chromascape:chromascape")

    implementation("org.bytedeco:javacv-platform:1.5.11")
    implementation("org.apache.commons:commons-math3:3.6.1")
    implementation("org.apache.logging.log4j:log4j-api:2.24.3")
    implementation("org.apache.logging.log4j:log4j-core:2.24.3")
}
