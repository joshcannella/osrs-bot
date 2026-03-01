This guide will walk you through the complete setup process for ChromaScape.

## Prerequisites

### Java 17

ChromaScape requires **Java 17**.

1. Download the Java Development Kit 17 from the [official Oracle site](https://www.oracle.com/java/technologies/downloads/#java17-windows).
2. Locate the appropriate JDK 17 installer (Windows x64 `.msi` or `.exe`).
3. Complete the installation process.
4. Verify the installation by opening a terminal and running:

```bash
java -version
```
**Expected output:**
```
java version "17.x.x" 2025-01-21
Java(TM) SE Runtime Environment ...
```

---

### Git

- Download and install Git from [git-scm.com](https://git-scm.com).
- For Windows users, this will include **Git Bash**, which provides a Unix-style command line interface.

---

### IntelliJ IDEA

- Download IntelliJ IDEA from [JetBrains](https://www.jetbrains.com/idea/).
- Both **Community Edition** and **Ultimate Edition** are supported.

---

## Installation

### Clone the Repository

1. Open a terminal, command prompt, or Git Bash.
2. Navigate to your desired installation directory.
3. Clone the ChromaScape repository:

```bash
git clone https://github.com/StaticSweep/ChromaScape.git
```

---

### Configure the Project

1. Open the cloned project directory in **IntelliJ IDEA**.
2. If prompted, import the project as a **Gradle project**.
3. Allow IntelliJ to complete indexing and dependency resolution.
> Indexing may take a while, feel free to make a coffee

---

## Initial Setup

### Generate Computer Vision Templates

ChromaScape includes a utility script to prepare the computer vision templates required for RuneLite interaction.

1. Navigate to the project root directory (the same level as `/src`).
2. Locate the `CVTemplates.bat` file.
3. Execute the script by double-clicking `CVTemplates.bat`.

This process will generate the necessary template files for ChromaScape's visual recognition system.
> Ensure that you wait for all the files to be downloaded.

---

## Running ChromaScape

Once you have completed the above steps, you are ready to run ChromaScape from **IntelliJ IDEA**.

Next, you should check out [Making Your First Script](https://github.com/StaticSweep/ChromaScape/wiki/Making-your-first-script) and [Requirements](https://github.com/StaticSweep/ChromaScape/wiki/Requirements)