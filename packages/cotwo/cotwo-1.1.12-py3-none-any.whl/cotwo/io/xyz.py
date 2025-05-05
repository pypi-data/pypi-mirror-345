from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem

from cotwo.rendering.atom import Atom


class Xyz:
    """
    Represents a molecular structure with atoms and properties.

    Instanciate with .from_smiles, .from_file, or .from_str

    Attributes:
    -----------
    atoms : list[Atom]
        List of atoms in the molecule
    charge : int
        Total molecular charge
    mult : int
        Spin multiplicity
    spin: float
        Total spin
    """

    def __init__(self, atoms: list[Atom], charge: int = 0, mult: int = 1) -> None:
        """
        Initialize a Xyz instance.

        Parameters:
        -----------
        atoms : list[Atom]
            List of atoms comprising the molecule
        charge : int, optional
            Molecular charge. Defaults to 0
        mult : int, optional
            Spin multiplicity. Defaults to 1 (singlet)
        """
        self.atoms = atoms
        self.charge = charge
        self.mult = mult

    def __str__(self) -> str:
        """
        String representation of molecule in XYZ format.

        Returns:
        --------
        str
            XYZ format string of the molecule
        """
        xyz_str = f"{len(self.atoms)}\n\n"
        xyz_str += "\n".join((atom.to_str() for atom in self.atoms))
        return xyz_str

    @property
    def spin(self) -> float:
        """
        Calculate the spin of the molecule.

        Returns:
        --------
        float
            Spin multiplicity
        """
        return (self.mult - 1) / 2

    @classmethod
    def from_str(cls, xyz: str) -> "Xyz":
        """
        Create a Xyz instance from XYZ format string.

        Parameters:
        -----------
        xyz : str
            XYZ format string containing molecular structure

        Returns:
        --------
        Xyz
            New Xyz instance with parsed atoms
        """
        atoms = []
        for line in xyz.strip().split("\n")[2:]:
            atoms.append(Atom.from_str(line))
        return cls(atoms)

    @classmethod
    def from_file(cls, path: str | Path) -> "Xyz":
        path = Path(path).resolve()
        if path.suffix == ".xyz":
            return cls._from_xyz_file(path)
        elif path.suffix == ".out":
            return cls._from_output_file(path)
        else:
            raise ValueError("Unsupported file type")

    @classmethod
    def _from_xyz_file(cls, path: str | Path) -> "Xyz":
        return cls.from_str(Path(path).read_text())

    @classmethod
    def _from_output_file(cls, path: str | Path) -> "Xyz":
        lines = Path(path).read_text().splitlines()
        for i, line in enumerate(reversed(lines)):
            if "CARTESIAN COORDINATES (ANGSTROEM)" in line.strip():
                break
        else:
            raise ValueError("Failed to find cartesian coordinates in file")

        table_index = len(lines) - i

        rows = []
        for line in lines[table_index + 2 :]:
            if not line.strip():
                break
            rows.append(line)

        xyz_string = "\n".join(rows)
        return cls.from_str(f"{len(rows)}\n\n" + xyz_string)

    @classmethod
    def from_smiles(cls, smiles: str) -> "Xyz":
        """
        Deserialize a SMILES string using RDKit.

        Parameters:
        -----------
        smiles : str
            SMILES representation of molecule
        """
        # Convert SMILES string to a molecule object
        mol = Chem.MolFromSmiles(smiles)

        # Generate 3D conformer
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, useRandomCoords=False)  # type: ignore

        atoms = [atom.GetSymbol() for atom in mol.GetAtoms()]
        conf = mol.GetConformer()
        coords = [conf.GetAtomPosition(i) for i in range(mol.GetNumAtoms())]

        xyz_str = f"{len(atoms)}\nGenerated from SMILES: {smiles}\n"
        xyz_str += "\n".join(
            f"{atoms[i]} {coords[i].x:.4f} {coords[i].y:.4f} {coords[i].z:.4f}"
            for i in range(len(atoms))
        )

        return cls.from_str(xyz_str)
