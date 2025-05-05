cotwo
=====

(like, carbon dioxide)

Render molecules with Plotly.

Installation
------------

```sh
pip install cotwo
```

or

```sh
uv add cotwo
```

Features
--------

+ Read and display structures from XYZ files
+ Read and display structures from SMILES strings
+ Plot smooth isosurfaces from cube files

Usage
-----

Use the "Molecule" class to instanciate an object from either an XYZ file (give the path) or a SMILES string:

```py
from cotwo import Molecule

# From an XYZ file
methane = Molecule.from_file("methane.xyz")

# From an output file
ethanol = Molecule.from_file("ethanol.out")

# From a SMILES string
caffeine = Molecule.from_smiles("CN1C=NC2=C1C(=O)N(C(=O)N2C)C")
```

```python
# Display a basic 3D visualization of the molecule
caffeine.show()

# Create a Plotly figure
fig = caffeine.create_fig()
```

The `Molecule` class can visualize molecular orbitals and spin densities by generating and displaying isosurfaces:

```python
# First, create the cube file for a specific molecular orbital
# (requires orca_plot to be installed)
mo_file = molecule.create_molecular_orbital("calculation.gbw", 42)  # HOMO orbital, for example

# Display the molecule with the molecular orbital isosurface
molecule.show_with_isosurface(
    mo_file,
    isovalue=0.03,  # Adjust the isosurface threshold
    colors=("#FF4081", "#1E88E5"),  # Custom colors for positive/negative phases
)
```

```python
# Load a molecule from an optimization calculation output
optimized = Molecule.from_file("optimized.xyz")

# Generate and visualize the HOMO-LUMO gap
homo_file = optimized.create_molecular_orbital("calculation.gbw", "42a")  # HOMO
lumo_file = optimized.create_molecular_orbital("calculation.gbw", "43a")  # LUMO

# View HOMO
optimized.show_with_isosurface(homo_file, colors=("#FF4081", "#1E88E5"))

# View LUMO
optimized.show_with_isosurface(lumo_file, colors=("#FF9800", "#2979FF"))
```


Roadmap
-------

Since creating the meshes and the isosurfaces is computationally heavy,
a neat feature would be the possibility to precompute several isosurfaces and keep them in memory.
This way multiple densities can be inspected in short succession without the computational overhead.

In the same vein, it would be cool to load a directory and then be able to select from the available `.cube` files. One could also compute the verticies and faces of the isosurfaces and store
them separately, then loading would be much faster.
That said, it's kind of beyond the scope of this project - best to keep it lightweigth and focused
on only the actual rendering.
