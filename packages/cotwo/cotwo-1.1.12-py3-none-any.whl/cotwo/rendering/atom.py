from copy import copy
from dataclasses import asdict
from typing import Optional

import numpy as np
import plotly.graph_objects as go
from numpy.typing import NDArray

from cotwo.rendering.meshes import Mesh
from cotwo.resources import PERIODIC_TABLE

ATOM_MESH_TEMPLATE = Mesh.unit_sphere()


class Coords:
    def __init__(self, x, y, z) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @property
    def as_vec(self) -> NDArray:
        return np.array([self.x, self.y, self.z])


class Atom:
    """Represents an atom with its element and 3D coordinates."""

    def __init__(self, symbol: str, coords: Coords):
        self.element: dict = PERIODIC_TABLE.get_element(symbol)
        self.coords: Coords = coords

    def to_str(self) -> str:
        """Convert atom to string representation in XYZ format (e.g. "H 0.0000 0.0000 0.0000")."""
        return f"{self.element['symbol']} {self.coords.x:.4f} {self.coords.y:.4f} {self.coords.z:.4f}"

    @classmethod
    def from_str(cls, line: str) -> "Atom":
        """Create an Atom instance from a string representation (e.g., "H 0.0 0.0 0.0")."""
        element, x, y, z = line.split()
        return cls(element, coords=Coords(x, y, z))

    @property
    def is_metal(self) -> bool:
        return True if self.element["group_block"][0] == "Transition metal" else False

    def to_mesh(self, scale: float = 0.25, color: Optional[str] = None) -> go.Mesh3d:
        mesh = copy(ATOM_MESH_TEMPLATE)

        # Scale and translate
        radius = self.element["atomic_radius"][0] / 100 * scale
        mesh.x = mesh.x * radius + self.coords.x
        mesh.y = mesh.y * radius + self.coords.y
        mesh.z = mesh.z * radius + self.coords.z

        mesh_dict = asdict(mesh)
        mesh_dict["color"] = color or f"#{self.element['hex_color'][0]}"
        mesh_dict["lighting"] = dict(
            ambient=0.85,
            diffuse=0.2,
            specular=0.6,
            roughness=0.5,
            fresnel=0.5,
        )

        # I'm not sure if I want to display information
        # # Add hover information from the element dictionary
        # hover_text = f"Element: {self.element['name'][0]}<br>"
        # hover_text += f"Symbol: {self.element['symbol'][0]}<br>"
        # hover_text += f"Atomic Number: {self.element['atomic_number'][0]}<br>"
        # hover_text += f"Group: {self.element['group_block'][0]}<br>"

        # mesh_dict["hoverinfo"] = "text"
        # mesh_dict["hovertext"] = hover_text
        # mesh_dict["showlegend"] = False
        mesh_dict["hoverinfo"] = "skip"

        return go.Mesh3d(**mesh_dict)
