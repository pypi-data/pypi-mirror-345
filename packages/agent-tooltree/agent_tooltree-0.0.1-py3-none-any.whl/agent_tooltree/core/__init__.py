from .plugin_loader import ToolsetRegistry

# Create a global toolset registry
toolset_registry = ToolsetRegistry()

# Load toolsets on module import
toolset_registry.load_toolsets()

__all__ = ["toolset_registry"]
