from copy import copy
from dataclasses import asdict
from typing import Optional

import numpy as np
import plotly.graph_objects as go

from cotwo.rendering.atom import Atom
from cotwo.rendering.meshes import Mesh
from cotwo.resources.bond_types import BondType

BOND_MESH_TEMPLATE = Mesh.unit_cylinder()


class Bond:
    """Represent a molecular bond between two atoms"""

    def __init__(
        self, atoms: tuple[Atom, Atom], type: BondType = BondType.SINGLE
    ) -> None:
        self.atoms = atoms
        self.type = type

    def to_mesh(self, radius: float = 0.2, color: Optional[str] = None) -> go.Mesh3d:
        """Transform a unit cylinder to connect two atoms.

        Returns:
            Transformed cylinder mesh as go.Mesh3d
        """
        mesh = copy(BOND_MESH_TEMPLATE)

        # Get coordinate vectors from atoms
        p0 = self.atoms[0].coords.as_vec
        p1 = self.atoms[1].coords.as_vec

        # Calculate bond direction and length
        direction = p1 - p0
        length = np.linalg.norm(direction)
        if length < 1e-12:
            raise ValueError("Degenerate case, both atoms are at the same position")

        # Normalize direction
        direction_normalized = direction / length

        # The cylinder initially points along the z-axis [0, 0, 1]
        z_axis = np.array([0, 0, 1])

        # Calculate rotation axis and angle using the cross product
        rotation_axis = np.cross(z_axis, direction_normalized)
        rotation_axis_norm = np.linalg.norm(rotation_axis)

        # If rotation_axis is very small, the bond is already aligned with z-axis
        # (or pointing in the opposite direction)
        if rotation_axis_norm < 1e-6:
            # If bond points along -z, we need to rotate 180 degrees around any
            # perpendicular axis (like x)
            if direction_normalized[2] < 0:
                rotation_matrix = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
            else:  # Bond already points along +z
                rotation_matrix = np.eye(3)
        else:
            # Normalize rotation axis
            rotation_axis = rotation_axis / rotation_axis_norm

            # Calculate rotation angle
            cos_angle = np.dot(z_axis, direction_normalized)
            sin_angle = rotation_axis_norm

            # Build rotation matrix using Rodrigues' rotation formula
            K = np.array(
                [
                    [0, -rotation_axis[2], rotation_axis[1]],
                    [rotation_axis[2], 0, -rotation_axis[0]],
                    [-rotation_axis[1], rotation_axis[0], 0],
                ]
            )
            rotation_matrix = np.eye(3) + sin_angle * K + (1 - cos_angle) * (K @ K)

        # Stack original mesh coordinates
        coords = np.vstack([mesh.x, mesh.y, mesh.z]).T

        # Scale x-, and y- coordinates by radius
        coords[:, 0] *= radius * self.type.value.radius_scale
        coords[:, 1] *= radius * self.type.value.radius_scale

        # Scale z-coordinate by length
        coords[:, 2] *= length

        # Apply rotation
        rotated_coords = np.dot(coords, rotation_matrix.T)

        # Apply translation and update mesh coordinates
        mesh.x = rotated_coords[:, 0] + p0[0]
        mesh.y = rotated_coords[:, 1] + p0[1]
        mesh.z = rotated_coords[:, 2] + p0[2]

        mesh_dict = asdict(mesh)
        mesh_dict["color"] = color or self.type.value.color
        mesh_dict["lighting"] = dict(
            ambient=0.85,
            diffuse=0.3,
            specular=0.4,
            roughness=0.5,
            fresnel=0.5,
        )

        mesh_dict["hoverinfo"] = "skip"

        return go.Mesh3d(**mesh_dict)
