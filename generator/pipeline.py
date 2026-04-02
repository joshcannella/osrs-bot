"""
GeneratorPipeline — orchestrates script generation and fixing.

Two entry points:
  - generate_from_sgr(sgr_id) — generate a new script from a Script Generation Request
  - fix_script(script_id)     — fix an existing script using logged bugs
"""

import difflib
import json
import os
import sys
from dataclasses import dataclass, field

from generator.client import ClaudeClient, extract_python_code
from generator.prompts import build_system_prompt
from generator.validator import PythonValidator

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_REQUESTS_DIR = os.path.join(_ROOT, "generator", "requests")
_SCRIPTS_DIR = os.path.join(_ROOT, "scripts")
_TRACKER_PATH = os.path.join(_ROOT, "scripts.json")


@dataclass
class GeneratorResult:
    success: bool
    python_code: str | None = None
    script_path: str | None = None
    validation_errors: list[str] = field(default_factory=list)


def _load_tracker() -> dict:
    if os.path.exists(_TRACKER_PATH):
        with open(_TRACKER_PATH) as f:
            return json.load(f)
    return {}


def _load_sgr(sgr_id: str) -> dict:
    path = os.path.join(_REQUESTS_DIR, f"{sgr_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"SGR not found: {path}")
    with open(path) as f:
        return json.load(f)


def _sgr_to_user_message(sgr: dict) -> str:
    """Convert a Script Generation Request JSON into a user prompt for Claude."""
    lines = [
        f"Generate a Python bot script for the following task:",
        f"",
        f"**Task:** {sgr.get('task', 'No task specified')}",
        f"**Skill:** {sgr.get('skill', 'N/A')}",
        f"**Location:** {sgr.get('location', 'N/A')}",
    ]

    entities = sgr.get("entities", {})
    if entities:
        lines.append("\n**Entities:**")
        for name, info in entities.items():
            if isinstance(info, dict):
                parts = [f"  - {name}:"]
                if "item_id" in info:
                    parts.append(f"item_id={info['item_id']}")
                if "color" in info:
                    parts.append(f"color={info['color']}")
                if "detection" in info:
                    parts.append(f"detection={info['detection']}")
                if "notes" in info:
                    parts.append(f"({info['notes']})")
                lines.append(" ".join(parts))

    if sgr.get("workflow"):
        lines.append(f"\n**Workflow:** {sgr['workflow']}")
    if sgr.get("bank_location"):
        lines.append(f"**Bank location:** {sgr['bank_location']}")

    stop_conditions = sgr.get("stop_conditions", [])
    if stop_conditions:
        lines.append("\n**Stop conditions:**")
        for sc in stop_conditions:
            lines.append(f"  - {sc}")

    if sgr.get("behavior_notes"):
        lines.append(f"\n**Behavior notes:** {sgr['behavior_notes']}")

    color_reqs = sgr.get("color_requirements", [])
    if color_reqs:
        lines.append("\n**Color requirements:**")
        for cr in color_reqs:
            lines.append(f"  - {cr['name']}: {cr.get('target', 'N/A')}")

    runelite_setup = sgr.get("runelite_setup", [])
    if runelite_setup:
        lines.append("\n**RuneLite setup required:**")
        for rs in runelite_setup:
            lines.append(f"  - {rs}")

    lines.append(
        "\n\nReturn the complete script in a ```python block. "
        "Include argparse with --debug flag and proper logging setup."
    )
    return "\n".join(lines)


class GeneratorPipeline:
    def __init__(self, api_key: str | None = None, model: str = "claude-opus-4-6"):
        self._client = ClaudeClient(api_key=api_key, model=model)
        self._validator = PythonValidator()

    def generate_from_sgr(self, sgr_id: str) -> GeneratorResult:
        """
        Generate a script from a Script Generation Request file.
        Writes the result to scripts/<id>_bot.py.
        """
        sgr = _load_sgr(sgr_id)
        user_message = _sgr_to_user_message(sgr)
        system_prompt = build_system_prompt()

        print(f"Generating script for '{sgr_id}'...")
        response = self._client.generate_script(system_prompt, user_message)
        code = extract_python_code(response)

        if code is None:
            return GeneratorResult(
                success=False,
                validation_errors=["Claude response did not contain a ```python block"],
            )

        # Validate
        errors = self._validator.validate(code)

        # One fix pass if validation fails
        if errors:
            print(f"Validation errors ({len(errors)}), attempting fix pass...")
            fix_prompt = (
                f"The generated script has these validation errors:\n"
                + "\n".join(f"- {e}" for e in errors)
                + "\n\nHere is the script:\n```python\n" + code + "\n```\n"
                + "\nFix all issues and return the complete corrected script in a ```python block."
            )
            fix_response = self._client.generate_script(system_prompt, fix_prompt)
            fixed_code = extract_python_code(fix_response)
            if fixed_code:
                code = fixed_code
                errors = self._validator.validate(code)

        # Write output
        os.makedirs(_SCRIPTS_DIR, exist_ok=True)
        script_name = sgr_id.replace("-", "_") + "_bot.py"
        script_path = os.path.join(_SCRIPTS_DIR, script_name)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code + "\n")

        if errors:
            print(f"WARNING: Script written with {len(errors)} validation warning(s):")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"Script generated and validated: {script_path}")

        return GeneratorResult(
            success=len(errors) == 0,
            python_code=code,
            script_path=script_path,
            validation_errors=errors,
        )

    def fix_script(self, script_id: str) -> GeneratorResult:
        """
        Fix an existing script using logged bugs from the tracker.
        Writes versioned output, shows diff, and prompts for confirmation.
        """
        script_name = script_id.replace("-", "_") + "_bot.py"
        script_path = os.path.join(_SCRIPTS_DIR, script_name)
        if not os.path.exists(script_path):
            return GeneratorResult(
                success=False,
                validation_errors=[f"Script not found: {script_path}"],
            )

        with open(script_path, encoding="utf-8") as f:
            current_code = f.read()

        # Load bugs from tracker
        tracker = _load_tracker()
        entry = tracker.get(script_id, {})
        bugs = [b for b in entry.get("bugs", []) if not b.get("resolved", False)]

        if not bugs:
            return GeneratorResult(
                success=False,
                validation_errors=["No open bugs found for this script"],
            )

        # Load SGR if available (for context)
        sgr_context = ""
        try:
            sgr = _load_sgr(script_id)
            sgr_context = f"\n\nOriginal task spec:\n{json.dumps(sgr, indent=2)}"
        except FileNotFoundError:
            pass

        system_prompt = build_system_prompt()
        response = self._client.fix_script(
            system_prompt, current_code + sgr_context, bugs
        )
        fixed_code = extract_python_code(response)

        if fixed_code is None:
            return GeneratorResult(
                success=False,
                validation_errors=["Claude fix response did not contain a ```python block"],
            )

        errors = self._validator.validate(fixed_code)

        # Write versioned file
        version = 1
        while True:
            versioned_name = script_id.replace("-", "_") + f"_bot_v{version}.py"
            versioned_path = os.path.join(_SCRIPTS_DIR, versioned_name)
            if not os.path.exists(versioned_path):
                break
            version += 1

        with open(versioned_path, "w", encoding="utf-8") as f:
            f.write(fixed_code + "\n")

        # Print diff
        diff = difflib.unified_diff(
            current_code.splitlines(keepends=True),
            fixed_code.splitlines(keepends=True),
            fromfile=script_name,
            tofile=versioned_name,
        )
        diff_text = "".join(diff)
        if diff_text:
            print("\n--- Changes ---")
            print(diff_text)
        else:
            print("No changes detected in fix.")

        if errors:
            print(f"\nWARNING: Fixed script has {len(errors)} validation warning(s):")
            for e in errors:
                print(f"  - {e}")

        # Prompt for confirmation
        print(f"\nFixed version saved to: {versioned_path}")
        answer = input("Apply this fix to the main script? (y/n): ").strip().lower()
        if answer == "y":
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(fixed_code + "\n")
            print(f"Applied fix to {script_path}")
        else:
            print(f"Fix saved as {versioned_path} — not applied to main script")

        return GeneratorResult(
            success=len(errors) == 0,
            python_code=fixed_code,
            script_path=versioned_path,
            validation_errors=errors,
        )
