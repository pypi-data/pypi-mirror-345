
# PyBMesh

**Homepage:** https://gitlab.com/alexis.sauvageon/pybmesh

**PyBMesh** is a Python library for generating, manipulating, and exporting meshes using VTK. It supports a wide range of mesh types - from points (0D) to volumes (3D) - and provides advanced tools such as extrusion (both linear and rotational), mesh fusion, and boundary extraction. PyBMesh is designed to help users create high-quality meshes for computational simulations and CFD applications (e.g., for OpenFOAM).

## Prerequisites

- **C Compiler** (GCC or Clang)  
- **C++ Compiler** (GCC or MSVC 14.0+)

### Windows  
Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools":  
[Download Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Linux  
Install GCC and related build tools via your package manager:
```bash
sudo apt-get update
sudo apt-get install build-essential
```

## Installation

Install PyBMesh from pypi.org using pip:
`pip install pybmesh` 

Or clone the repository and install with:
`python pip install -e .` 

## Module Structure
A high-level view of the project layout:



    +-- examples/             # Example scripts illustrating common meshing workflows.
    +-- LICENSE               # MIT License.
    +-- pybmesh/              # Main package.
    ¦   +-- cython/         # Cython modules for performance-critical tasks.
    ¦   +-- geom/           # Definitions for 0D (points), 1D (lines, arcs, circles), 2D (surfaces), and 3D (volumes) elements.
    ¦   +-- io/             # I/O routines for VTK conversion and mesh writing.
    ¦   +-- utils/          # Utility modules including mesh manipulation tools (fusion, extrusion, boundary extraction).
    +-- pyproject.toml        # Build configuration.
    +-- README.md             # This documentation.
    +-- ressources/           # other useful files.
    +-- tests/                # Unit tests for verifying functionality.

## Quick Tutorial

### Creating Basic Mesh Elements

PyBMesh provides classes for each mesh dimension:

-   **0D - Points:**   
```python
from pybmesh import Point
p = Point(0, 0, 0)
```
    
-   **1D - Lines, Arcs, and Circles:**   
```python
from pybmesh import Point, Line, Arc, Circle
p1 = Point(0, 0, 0)
p2 = Point(1, 0, 0)
line = Line(p1, p2, n=10)

# Create an arc using a center and boundary points:
arc = Arc.from_center_2points(center=p1.coords[0], pA=p2.coords[0],
                               pB=Point(0, 1, 0).coords[0], n=10)``
```


-   **2D - Surfaces:**
    
```python
from pybmesh import Surface
p3 = Point(1, 1, 0)
p4 = Point(0, 1, 0)
surface = Surface(p1, p2, p3, p4, n=1, quad=True)` 
```
    
-   **3D - Volumes:**
    
```python
from pybmesh import Volume, translate
surface2 = surface.copy()
surface2.translate(0, 0, 1)
volume = Volume(surface, surface2, n=10)
```
    

### Mesh Manipulation

The `pybmesh.utils.meshtools` module offers several functions for transforming and combining meshes:

```python
from pybmesh import translate, rotate, syme, scale, fuse
```

-   **Translate a mesh (with copy):**
```python
translated = translate(surface, (2, 0, 0))
```

-   **Rotate 90° about the Z-axis (with copy):**
```python
rotated = rotate(surface, center=(0,0,0), axis=(0,0,1), angle=90)
```

-   **Reflect (symmetry) across the XY-plane (with copy):**
```python
reflected = syme(surface, plane='xy')
```

-   **Scale a mesh (with copy):**
```python
scaled = scale(surface, sx=2, sy=1, sz=1)
```

-   **Fuse two meshes:**
```python
fused = fuse(surface, translated)` 
```

### Extruding Meshes

Create higher-dimensional meshes via extrusion:

-   **Linear Extrusion:**
    
```python
from pybmesh.meshmanip import extrudeLinear
vector_line = Line(Point(0,0,0), Point(0,0,1), n=1)
extruded_surface = extrudeLinear(line, vector_line)` 
```

-   **Rotational Extrusion:**
```python
from pybmesh.meshmanip import extrudeRotational
rot_extruded = extrudeRotational(line, pA=(0,0,0), pB=(0,0,1), angle=45, n=10)` 
```

### Additional Tools

-   **Boundary Extraction:**  
    Use `getBoundaries` from `pybmesh.meshmanip` to extract faces, edges, or nodes from a mesh.
    
-   **Submesh Extraction:**  
    Use `extract_point` and `extract_element` functions for obtaining submeshes based on criteria.
    
-   **Assembly and Export:**  
    Combine mesh components using `MeshComponent` and `MeshAssembly`, and export meshes using VTK writers (e.g., in `FoamSave.py`).
    

## Examples

The `examples/` directory contains scripts that illustrate various workflows:

-   **Lines.py:** Demonstrates creation and manipulation of 1D elements.
-   **Surfaces.py:** Shows surface generation from curves and transfinite techniques.
-   **Volumes.py:** Illustrates volume creation by interpolating between surfaces.
-   **Extrude_Exemples.py:** Provides examples of linear and rotational extrusion.
-   **Extract_Boundaries.py & Extract_submeshes.py:** Demonstrate boundary and submesh extraction.
-   **FoamSave.py:** Exports meshes to VTK files for CFD applications.
-   **MeshComponent.py & MeshAssembly.py:** Show how to build a complete mesh from components.

## Help and Documentation

For complete descriptions of classes and functions, use Python's built-in help. 
For example, to view details about the `Volume` class:
```python
from pybmesh import Volume
help(Volume)` 
```
This will print a full explanation of the constructor, methods, and usage examples.

## License

PyBMesh is released under the BSD 3-Clause License(LICENSE).
