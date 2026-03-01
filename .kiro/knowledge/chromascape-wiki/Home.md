## Welcome to the ChromaScape wiki!

This project prioritizes code clarity, customizability, and full user control - offering an alternative to bloated or closed-source clients. It also serves as a practical way to learn and apply essential programming principles such as object-oriented design, dependency injection, the single responsibility principle, and more.

---

# Project Architecture

ChromaScape is split into clean modular layers:

- `controller`: Manages stateful core utilities and safely dispatches them.
- `base`: Abstract base for all user scripts.
- `utils.core`: Single-purpose utilities like VirtualMouseUtils, TemplateMatching, etc.
- `utils.domain`: Feature-level abstractions like ZoneManager, based on multiple core utilities.
- `utils.actions`: Reusable code snippets useful in any script.
- `web`: Hosts the local UI and handles script serving + the colour picker.
- `scripts`: This is where you keep your scripts.
- `api`: API connections such as DAX for the walker.

## Diagram

<img width="75%" height="75%" alt="ChromaScape" src="https://github.com/user-attachments/assets/4da7550d-b38e-48e6-8b27-72e9f43c9a14" />

