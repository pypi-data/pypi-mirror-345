from myreze.viz.threejs.threejs import ThreeJSRenderer
from myreze.viz.threejs.trimesh_utilities import attach_texture_to_mesh
from typing import Dict, Any
import numpy as np
import trimesh


@ThreeJSRenderer.register
class FlatOverlayRenderer(ThreeJSRenderer):
    """Render a flat overlay."""

    def render(self, data: "MyrezeDataPackage", params: Dict[str, Any]) -> str:
        """Render the data package as a Three.js object."""

        texture = np.array(data)

        # Create a 2d horizontal GLB plane with alpha channel texture
        plane = trimesh.Trimesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0], [0, 0, 1], [1, 0, 1]]),
            faces=np.array([[2, 1, 0], [3, 1, 2]]),
        )
        plane = attach_texture_to_mesh(plane, texture)

        return plane.export(file_type="glb")


@ThreeJSRenderer.register
class Planar4channelTextureRenderer(ThreeJSRenderer):
    """Render a flat overlay with a 4 channel texture."""

    def render(self, data: "MyrezeDataPackage", params: Dict[str, Any]) -> str:
        """Render the data package as a Three.js object."""

        texture = np.array(data["texture"])

        # Create a 2d horizontal GLB plane with alpha channel texture
        plane = trimesh.Trimesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0], [0, 0, 1], [1, 0, 1]]),
            faces=np.array([[2, 1, 0], [3, 1, 2]]),
        )
        plane = attach_texture_to_mesh(plane, texture)

        return plane.export(file_type="glb")


@ThreeJSRenderer.register
class DummyRenderer(ThreeJSRenderer):
    """Render a flat overlay with a 4 channel texture."""

    def render(self, data: "MyrezeDataPackage", params: Dict[str, Any]) -> str:
        """Render the data package as a Three.js object."""

        texture = np.random.rand(100, 100, 4)

        # Create a 2d horizontal GLB plane with alpha channel texture
        plane = trimesh.Trimesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0], [0, 0, 1], [1, 0, 1]]),
            faces=np.array([[2, 1, 0], [3, 1, 2]]),
        )
        plane = attach_texture_to_mesh(plane, texture)

        return plane.export(file_type="glb")
