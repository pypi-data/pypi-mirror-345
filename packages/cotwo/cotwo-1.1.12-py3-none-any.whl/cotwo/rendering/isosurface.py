from collections import namedtuple
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from scipy.ndimage import zoom
from skimage import measure

from cotwo.rendering.atom import Atom, Coords
from cotwo.resources import PERIODIC_TABLE


class Isosurface:
    def __init__(
        self,
        file: str | Path,
    ) -> None:
        self.file = Path(file)

    def to_meshes(
        self,
        isovalue: float = 0.005,
        colors: tuple[str, str] = ("#1E88E5", "#004D40"),
        smoothness_factor: float = 1.0,
    ) -> tuple[go.Mesh3d, go.Mesh3d]:
        raw_density = self._read_cube()
        density = self._smooth_density(raw_density, smoothness_factor)

        MESH_DICT = dict(
            opacity=1,
            showlegend=True,
            hoverinfo="skip",
            lighting=dict(
                ambient=0.5,
                diffuse=0.7,
                specular=0.2,
                roughness=0.2,
                fresnel=0.1,
            ),
        )

        isosurfaces = (
            self._create_surface(density, isovalue),
            self._create_surface(density, -isovalue),
        )

        positive_mesh = go.Mesh3d(
            name="Positive",
            color=colors[0],
            x=isosurfaces[0][0][:, 0],
            y=isosurfaces[0][0][:, 1],
            z=isosurfaces[0][0][:, 2],
            i=isosurfaces[0][1][:, 0],
            j=isosurfaces[0][1][:, 1],
            k=isosurfaces[0][1][:, 2],
            **MESH_DICT,
        )

        negative_mesh = go.Mesh3d(
            name="Negative",
            color=colors[1],
            x=isosurfaces[1][0][:, 0],
            y=isosurfaces[1][0][:, 1],
            z=isosurfaces[1][0][:, 2],
            i=isosurfaces[1][1][:, 0],
            j=isosurfaces[1][1][:, 1],
            k=isosurfaces[1][1][:, 2],
            **MESH_DICT,
        )

        return (positive_mesh, negative_mesh)

    def _create_surface(self, density: dict, isovalue: float) -> tuple:
        try:
            verticies, faces, normales, values = measure.marching_cubes(
                density["values"], level=isovalue, spacing=density["spacing"]
            )
        except ValueError as e:
            raise ValueError(
                "Isovalue is too extreme, the isosurface would protrude the grid volume."
            ) from e
        # Center verticies to the origin
        verticies += density["origin"]
        return (verticies, faces)

    def _smooth_density(self, density: dict, smoothness_factor: float = 1.0) -> dict:
        density["values"] = zoom(
            input=density["values"], zoom=smoothness_factor, order=3
        )

        density["spacing"] = [
            basis_vec / smoothness_factor for basis_vec in density["spacing"]
        ]
        return density

    def _read_cube(self, smoothing_factor: float = 1.0) -> dict:
        """Parse a .cube density file into a dictionary.

        Interpolates the grid points for creating smoother isosurfaces.
        Control with the 'smoothing_factor' (default = 1.0)

        dict(
            origin,
            basis_vectors,
            grid,
            values
        )
        """
        lines = self.file.read_text().splitlines()

        _comments = lines[:2]
        n_atoms, *origin = lines[2].strip().split()
        n_atoms = int(n_atoms)

        # Cube files encode the unit (Bohrs or Angstroms) in the sign
        # of the number of atoms...
        #
        # If n_atoms is negative, the units are (supposed to be) in Angstroms,
        # but apparently it doesn't fucking matter - they are in Bohrs regardless.
        unit = "bohr"
        if n_atoms < 0:
            n_atoms = -n_atoms
            # unit = "angstrom"
        scale = 0.529177 if unit == "bohr" else 1.0

        origin = np.array([float(coord) * scale for coord in origin])

        BasisVector = namedtuple("BasisVector", ["n_voxels", "x", "y", "z"])
        basis_vectors = {
            "x": BasisVector(
                int(lines[3].split()[0]),
                *[float(coord) * scale for coord in lines[3].split()[1:]],
            ),
            "y": BasisVector(
                int(lines[4].split()[0]),
                *[float(coord) * scale for coord in lines[4].split()[1:]],
            ),
            "z": BasisVector(
                int(lines[5].split()[0]),
                *[float(coord) * scale for coord in lines[5].split()[1:]],
            ),
        }

        if (
            not basis_vectors["x"].n_voxels
            == basis_vectors["y"].n_voxels
            == basis_vectors["z"].n_voxels
        ):
            raise ValueError("Number of voxels in each direction must be equal")

        grid_resolution = basis_vectors["x"].n_voxels

        atoms = []
        for line in lines[6 : 6 + n_atoms]:
            atomic_number, _charge, x, y, z = line.split()
            symbol = PERIODIC_TABLE.get_symbol_by_id(int(atomic_number))
            atoms.append(Atom(symbol, Coords(x, y, z)))

        grid_values = []
        for line in lines[6 + n_atoms :]:
            grid_values.extend(map(float, line.split()))

        try:
            grid_values = np.array(grid_values).reshape(
                basis_vectors["x"].n_voxels,
                basis_vectors["y"].n_voxels,
                basis_vectors["z"].n_voxels,
            )
        except ValueError:
            # Sometimes ORCA writes an additional charge/multiplicity line after the coordinates
            # which goes against the cube file format :)
            grid_values = grid_values[2:]
            grid_values = np.array(grid_values).reshape(
                basis_vectors["x"].n_voxels,
                basis_vectors["y"].n_voxels,
                basis_vectors["z"].n_voxels,
            )

        spacing = (
            basis_vectors["x"].x,
            basis_vectors["y"].y,
            basis_vectors["z"].z,
        )

        return {
            "origin": origin,
            "basis_vectors": basis_vectors,
            "grid": grid_resolution,
            "values": grid_values,
            "spacing": spacing,
        }
