"""Plugin loading functionality for Agent ToolTree."""

from importlib.metadata import entry_points
from typing import Any


class ToolsetLoadError(Exception):
    """Raised when a toolset fails to load."""

    pass


class ToolsetRegistry:
    """Registry for managing toolsets."""

    def __init__(self):
        self._toolsets: dict[str, Any] = {}
        self._instances: dict[str, Any] = {}

    def load_toolsets(self) -> None:
        """Load all registered toolsets from entry points."""
        for entry_point in entry_points(group="agent_tooltree.toolsets"):
            try:
                toolset_class = entry_point.load()
                self._toolsets[entry_point.name] = toolset_class
            except Exception as e:
                raise ToolsetLoadError(
                    f"Failed to load toolset {entry_point.name}: {e}"
                )

    def get_toolset(self, name: str) -> Any:
        """Get a toolset instance by name."""
        if name not in self._instances:
            if name not in self._toolsets:
                raise KeyError(f"Toolset {name} not found")
            self._instances[name] = self._toolsets[name]()
        return self._instances[name]

    def get_all_toolsets(self) -> dict[str, Any]:
        """Get all registered toolsets."""
        return self._toolsets.copy()

    def get_all_instances(self) -> dict[str, Any]:
        """Get all toolset instances."""
        return {name: self.get_toolset(name) for name in self._toolsets}
