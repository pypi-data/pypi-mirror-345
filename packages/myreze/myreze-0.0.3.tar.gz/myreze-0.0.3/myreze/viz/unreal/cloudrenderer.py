from myreze.viz.unreal.unreal import UnrealRenderer
from typing import Dict, Any


@UnrealRenderer.register
class CloudRenderer(UnrealRenderer):
    """Render a CloudRenderer object."""

    def render(self, data: "MyrezeDataPackage", params: Dict[str, Any]) -> str:
        """Render the data package as a Unreal Engine object."""
        pass
