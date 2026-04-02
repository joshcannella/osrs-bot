"""
ClaudeClient — calls the Anthropic Claude API for script generation and fixing.
"""

import os
import re

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClaudeClient:
    def __init__(self, api_key: str | None = None, model: str = "claude-opus-4-6"):
        self._model = model
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Add it to .env or pass api_key="
            )
        self._client = Anthropic(api_key=key)

    def generate_script(self, system_prompt: str, user_message: str) -> str:
        """
        Generate a Python bot script from a user prompt.
        Returns the raw response text (should contain a ```python block).
        """
        response = self._client.messages.create(
            model=self._model,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def fix_script(
        self, system_prompt: str, script: str, bugs: list[dict]
    ) -> str:
        """
        Fix an existing script given a list of bug descriptions.
        Returns the raw response text with the corrected ```python block.
        """
        bug_text = "\n".join(
            f"- {b.get('description', str(b))}" for b in bugs
        )
        user_message = (
            "Fix the following Python bot script. Here are the bugs:\n\n"
            f"{bug_text}\n\n"
            "Here is the current script:\n\n"
            f"```python\n{script}\n```\n\n"
            "Return the complete fixed script in a ```python block."
        )
        response = self._client.messages.create(
            model=self._model,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text


def extract_python_code(response_text: str) -> str | None:
    """Extract the first ```python ... ``` code block from Claude's response."""
    match = re.search(r"```python\s*\n(.*?)```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
