"""
PythonValidator — validates generated bot scripts using AST analysis.

Checks:
1. Syntax (ast.parse)
2. BaseBot subclass present
3. cycle() method defined
4. framework imports present
5. wait_random_millis used
6. stuck counter present
7. None checks on detection results
"""

import ast


# Known controller attributes that scripts may reference
_VALID_CONTROLLER_ATTRS = {
    "capture", "mouse", "keyboard", "zones", "detection",
    "actions", "colors", "game_state",
}


class PythonValidator:
    def validate(self, code: str) -> list[str]:
        """
        Validate a generated Python script.
        Returns a list of error messages. Empty list = valid.
        """
        errors = []

        # 1. Syntax check
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [f"Syntax error: {e}"]

        # 2. Find BaseBot subclass
        classes = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]
        bot_classes = [
            c for c in classes
            if any(
                (isinstance(b, ast.Name) and b.id == "BaseBot")
                or (isinstance(b, ast.Attribute) and b.attr == "BaseBot")
                for b in c.bases
            )
        ]
        if not bot_classes:
            errors.append("No class extending BaseBot found")
            return errors  # Can't check further without a bot class

        bot_class = bot_classes[0]

        # 3. cycle() method
        methods = [
            node for node in ast.walk(bot_class)
            if isinstance(node, ast.FunctionDef) and node.name == "cycle"
        ]
        if not methods:
            errors.append("BaseBot subclass missing cycle() method")

        # 4. Framework imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

        has_framework_import = any("framework" in m for m in imports)
        if not has_framework_import:
            errors.append("No 'framework' imports found")

        # 5. wait_random_millis usage
        source = code
        if "wait_random_millis" not in source:
            errors.append("No wait_random_millis() call found — bot timing will be non-human")

        # 6. Stuck counter
        has_stuck = any(
            kw in source for kw in ["stuck", "STUCK_LIMIT", "stuck_count", "_stuck"]
        )
        if not has_stuck:
            errors.append("No stuck detection found — bot may run indefinitely without progress")

        # 7. None checks on detection results
        if "get_random_point_in_color" in source:
            # Check if there's a "is None" or "is not None" or "if point" near the call
            if "is None" not in source and "is not None" not in source and "if point" not in source and "if not point" not in source:
                errors.append(
                    "get_random_point_in_color() used without None check — "
                    "detection can return None when nothing is found"
                )

        return errors
