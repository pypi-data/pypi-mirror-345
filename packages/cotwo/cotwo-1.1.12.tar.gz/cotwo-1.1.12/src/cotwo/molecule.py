"""High-level class"""

import subprocess
from itertools import combinations
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from cotwo.io import Xyz
from cotwo.rendering.atom import Atom
from cotwo.rendering.bond import Bond
from cotwo.rendering.isosurface import Isosurface
from cotwo.resources.bond_types import BondType


class Molecule:
    """
    Represents a molecular structure with atoms and bonds.

    This class provides functionality to create, visualize and analyze molecules,
    including support for displaying isosurfaces of molecular orbitals and spin densities.
    """

    LAYOUT = dict(
        scene=dict(
            aspectmode="data",
            xaxis_visible=False,
            yaxis_visible=False,
            zaxis_visible=False,
            bgcolor="whitesmoke",
            dragmode="orbit",  # Ensures orbital rotation mode is active
        ),
        scene_camera=dict(
            up=dict(x=0, y=0, z=2),
            eye=dict(x=0, y=2.5, z=0),
            center=dict(x=0, y=0, z=0),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(dict(yanchor="top", y=0.99, xanchor="left", x=0.01)),
    )

    def __init__(self, atoms: list[Atom]) -> None:
        """
        Initialize a Molecule with a list of atoms.

        Args:
            atoms: List of Atom objects that make up the molecule

        Raises:
            AssertionError: If no atoms are provided
        """
        self.atoms = atoms
        assert len(self.atoms) != 0, "No atoms supplied!"
        self.bonds = self._detect_bonds_by_radius_overlap()

    @classmethod
    def from_file(cls, file: str | Path) -> "Molecule":
        """
        Create a Molecule from an .xyz or an .out file.

        Args:
            file: Path to the .xyz or .out file

        Returns:
            A new Molecule instance created from the file data
        """
        xyz = Xyz.from_file(Path(file))
        return cls(xyz.atoms)

    @classmethod
    def from_smiles(cls, smiles: str) -> "Molecule":
        """
        Create a Molecule from a SMILES string.

        Args:
            smiles: A valid SMILES string representing a molecule

        Returns:
            A new Molecule instance created from the SMILES string
        """
        xyz = Xyz.from_smiles(smiles)
        return cls(xyz.atoms)

    def _detect_bonds_by_radius_overlap(self, scale: float = 0.5) -> list[Bond]:
        """
        Detect bonds between atoms based on their atomic radii and distances.

        Uses atomic radii to determine if atoms are close enough to be bonded,
        with special handling for coordination bonds involving metals.

        Args:
            scale: Factor to scale the bond threshold distance (default: 0.5)

        Returns:
            List of detected Bond objects
        """
        bonds: list[Bond] = []
        for i, j in combinations(self.atoms, 2):
            bond_type = BondType.SINGLE
            bond_threshold = (
                i.element["atomic_radius"][0] + j.element["atomic_radius"][0]
            ) / 100
            bond_threshold *= scale

            # Coordination bonds are usually longer (same for hydrogen bonds etc)
            if i.is_metal or j.is_metal:
                bond_threshold *= BondType.COORDINATION.value.detection_threshold
                bond_type = BondType.COORDINATION

            distance = np.linalg.norm(j.coords.as_vec - i.coords.as_vec)

            if distance <= bond_threshold:
                bonds.append(Bond((i, j), bond_type))
        return bonds

    def create_fig(self) -> go.Figure:
        """
        Create a Plotly figure of the molecule.

        Renders atoms as spheres and bonds as cylinders.

        Returns:
            A Plotly Figure object containing the 3D representation of the molecule
        """
        fig = go.Figure()

        for atom in self.atoms:
            mesh = atom.to_mesh()
            fig.add_trace(mesh)

        for bond in self.bonds:
            mesh = bond.to_mesh()
            fig.add_trace(mesh)

        fig.update_layout(self.LAYOUT)
        return fig

    def create_fig_with_isosurface(
        self,
        file: str | Path,
        isovalue: float = 0.005,
        colors: tuple[str, str] = ("#1E88E5", "#004D40"),
        smoothness_factor: float = 1.0,
    ) -> go.Figure:
        """
        Create a Plotly figure of the molecule with an isosurface.

        Args:
            file: Path to cube file containing isosurface data
            isovalue: Value at which to render the isosurface (default: 0.005)
            colors: Tuple of two colors for positive and negative surfaces (default: blue and dark teal)
            smoothness_factor: Factor to control the smoothness of the isosurface (default: 1.0)

        Returns:
            A Plotly Figure object containing the molecule and isosurface
        """
        fig = self.create_fig()
        isosurface_meshes = Isosurface(file).to_meshes(
            isovalue, colors, smoothness_factor
        )
        for mesh in isosurface_meshes:
            fig.add_trace(mesh)
        return fig

    def show(self) -> None:
        """
        Display an interactive 3D visualization of the molecule.

        Creates and displays a Plotly figure in the current environment.
        """
        fig = self.create_fig()
        fig.show()

    def show_with_isosurface(
        self,
        file: str | Path,
        isovalue: float = 0.005,
        colors: tuple[str, str] = ("#1E88E5", "#004D40"),
        smoothness_factor: float = 1.0,
    ) -> None:
        """
        Display an interactive 3D visualization of the molecule with an isosurface.

        Difference density colors: ("#CCBE00", "#CC0022")

        Args:
            file: Path to cube file containing isosurface data
            isovalue: Value at which to render the isosurface (default: 0.005)
            colors: Tuple of two colors for positive and negative surfaces (default: blue and dark teal)
            smoothness_factor: Factor to control the smoothness of the isosurface (default: 1.0)
        """
        fig = self.create_fig_with_isosurface(file, isovalue, colors, smoothness_factor)
        fig.show()

    def create_molecular_orbital(
        self, orbital_file: str | Path, id: int | str, grid: int = 60
    ) -> Path:
        """
        Create a cube file for a specific molecular orbital.

        Uses orca_plot to generate a cube file representation of a molecular orbital.

        Args:
            orbital_file: Path to the ORCA output file containing orbital data
            id: Orbital identifier, either a number (defaults to alpha spin) or with spin suffix (e.g., "12b")
            grid: Grid resolution for the cube file (default: 60)

        Returns:
            Path to the generated cube file

        Raises:
            FileNotFoundError: If the cube file cannot be created
            AssertionError: If the orbital file does not exist
        """
        orbital_file = Path(orbital_file)
        assert orbital_file.exists(), f"Can't find {orbital_file}"

        # Either give "12b" to specifiy the spin explicitly,
        # or simply a number (assume alpha in that case)
        id = str(id).strip()
        id = id + "a" if id.isdigit() else id

        # Add an identifier where the density comes from,
        # e.g. ".gbw.mo21a.cube" and ".qro.mo21a.cube" can coexist.
        # Still need the unmodified name to check what `orca_plot` produces.
        raw_density_file = orbital_file.with_suffix(f".mo{id}.cube")
        density_file_with_identifier = orbital_file.with_suffix(
            f"{orbital_file.suffix}.mo{id}.cube"
        )

        if density_file_with_identifier.exists():
            # Check if the files grid is smaller
            existing_grid = 0
            lines = density_file_with_identifier.read_text().splitlines()
            existing_grid = int(lines[3].split()[0])
            if existing_grid >= grid:
                return density_file_with_identifier

        # You know, codified `orca_plot` stuff..
        instruction_set = (
            f"4\n{grid}\n5\n7\n3\n{1 if 'b' in id else 0}\n2\n{id[:-1]}\n11\n12\n"
        )
        result = subprocess.run(
            ["orca_plot", orbital_file, "-i"],
            text=True,
            cwd=orbital_file.parent,
            input=instruction_set,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if not raw_density_file.exists():
            print(f"orca_plot stdout: {result.stdout}")
            print(f"orca_plot stderr: {result.stderr}")
            raise FileNotFoundError(
                "Failed to create density file. Check what orca_plot is doing."
            )

        # Add the identifier to the density file
        raw_density_file.rename(density_file_with_identifier)

        return density_file_with_identifier

    def create_spin_density(self, orbital_file: str | Path, grid: int = 100) -> Path:
        """
        Create a cube file for the spin density.

        Uses orca_plot to generate a cube file representation of the spin density.

        Args:
            orbital_file: Path to the ORCA output file
            grid: Grid resolution for the cube file (default: 100)

        Returns:
            Path to the generated spin density cube file

        Raises:
            FileNotFoundError: If the cube file cannot be created
            AssertionError: If the orbital file does not exist
        """
        orbital_file = Path(orbital_file)
        assert orbital_file.exists(), f"Can't find {orbital_file}"

        # Add an identifier where the density comes from,
        # e.g. ".gbw.mo21a.cube" and ".qro.mo21a.cube" can coexist.
        # Still need the unmodified name to check what `orca_plot` produces.
        raw_density_file = orbital_file.with_suffix(".spindens.cube")
        density_file_with_identifier = orbital_file.with_suffix(
            f"{orbital_file.suffix}.spindens.cube"
        )

        if density_file_with_identifier.exists():
            # Check if the files grid is smaller
            existing_grid = 0
            lines = density_file_with_identifier.read_text().splitlines()
            existing_grid = int(lines[3].split()[0])
            if existing_grid >= grid:
                return density_file_with_identifier

        auxiliary_file = orbital_file.with_suffix(".scfr")

        # You know, codified `orca_plot` stuff..
        instruction_set = f"4\n{grid}\n5\n7\n1\n3\nn\n{auxiliary_file}\n11\n12\n"
        result = subprocess.run(
            ["orca_plot", orbital_file, "-i"],
            text=True,
            cwd=orbital_file.parent,
            input=instruction_set,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if not raw_density_file.exists():
            print(f"orca_plot stdout: {result.stdout}")
            print(f"orca_plot stderr: {result.stderr}")
            raise FileNotFoundError(
                "Failed to create density file. Check what orca_plot is doing."
            )

        # Add the identifier to the density file
        raw_density_file.rename(density_file_with_identifier)

        return density_file_with_identifier

    def create_difference_density(
        self, orbital_file: str | Path, state_vector: int, grid: int = 60
    ) -> Path:
        """
        Create a cube file for a difference density.

        Uses orca_plot to generate a cube file representation of a difference density.

        Args:
            orbital_file: Path to the ORCA output file
            grid: Grid resolution for the cube file (default: 100)

        Returns:
            Path to the generated difference density cube file

        Raises:
            FileNotFoundError: If the cube file cannot be created
            AssertionError: If the orbital file does not exist
        """
        orbital_file = Path(orbital_file)
        assert orbital_file.exists(), f"Can't find {orbital_file}"

        # Add an identifier where the density comes from,
        # e.g. ".gbw.mo21a.cube" and ".qro.mo21a.cube" can coexist.
        # Still need the unmodified name to check what `orca_plot` produces.
        density_file = orbital_file.with_suffix(f".cisdp{state_vector:02d}.cube")

        if density_file.exists():
            # Check if the files grid is smaller
            existing_grid = 0
            lines = density_file.read_text().splitlines()
            existing_grid = int(lines[3].split()[0])
            if existing_grid >= grid:
                return density_file

        auxiliary_file = orbital_file.with_suffix(".cis")

        # You know, codified `orca_plot` stuff..
        instruction_set = (
            f"4\n{grid}\n5\n7\n6\nn\n{auxiliary_file}\n{state_vector}\n12\n"
        )
        result = subprocess.run(
            ["orca_plot", orbital_file, "-i"],
            text=True,
            cwd=orbital_file.parent,
            input=instruction_set,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if not density_file.exists():
            print(f"orca_plot stdout: {result.stdout}")
            print(f"orca_plot stderr: {result.stderr}")
            raise FileNotFoundError(
                "Failed to create density file. Check what orca_plot is doing."
            )

        return density_file
