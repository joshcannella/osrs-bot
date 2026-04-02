import json
import os
from dataclasses import dataclass


@dataclass
class ColorRange:
    name: str
    hsv_min: tuple[int, int, int]
    hsv_max: tuple[int, int, int]


class ColorRegistry:
    def __init__(self, json_path: str | None = None):
        if json_path is None:
            json_path = os.path.join(os.path.dirname(__file__), "colors", "colors.json")
        with open(json_path, "r") as f:
            data = json.load(f)
        self._colors: dict[str, ColorRange] = {}
        for entry in data:
            name = entry["name"]
            self._colors[name.lower()] = ColorRange(
                name=name,
                hsv_min=tuple(entry["min"][:3]),
                hsv_max=tuple(entry["max"][:3]),
            )

    def get_by_name(self, name: str) -> ColorRange | None:
        return self._colors.get(name.lower())

    def names(self) -> list[str]:
        return [c.name for c in self._colors.values()]
