 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 10/02/2025
Last modified on 10/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module handles conversion between VTK and NumPy formats for mesh I/O.
It includes functions for converting vtkUnstructuredGrid objects to NumPy arrays (e.g., vtk_to_numpy_connectivity,
mesh_to_numpy_connectivity) and converting NumPy arrays back to VTK meshes (e.g., numpy_to_vtk_connectivity),
facilitating mesh processing and visualization.
"""

import vtk
import numpy as np
from vtk.util import numpy_support
from pybmesh.utils.constants import _TOL
from pybmesh.utils.maths import compute_tetrahedron_volume

def to_array(pt):
    """
    Convert a point (which may be an instance with a 'coords' attribute,
    or a list/tuple/array) into a flattened numpy array with 3 elements.
    If the point has only 2 coordinates, a zero is appended as the third.

    Args:
        pt (Point or list/tuple/array): The point to convert.

    Returns:
        np.ndarray: A flattened numpy array with 3 elements.

    Example:
        >>> to_array(Point([1, 2]))
        array([1., 2., 0.])
    """
    if hasattr(pt, 'coords'):
        arr = np.array(pt.coords, dtype=float).flatten()
    else:
        arr = np.asarray(pt, dtype=float).flatten()
    if arr.size == 2:
        arr = np.hstack([arr, 0.0])
    elif arr.size != 3:
        raise ValueError("Point must have 2 or 3 coordinates")
    return arr

def vtk_to_numpy_connectivity(ugrid):
    """
    Convert the connectivity and points data from a vtkUnstructuredGrid to numpy arrays.

    This function extracts the points and connectivity (cells) from the given vtkUnstructuredGrid,
    converting the points to a numpy array and structuring the cell connectivity into a list of 
    lists, where each sublist represents the point indices for a given cell.

    Parameters:
        ugrid (vtkUnstructuredGrid): The unstructured grid containing points and cells.

    Returns:
        tuple: A tuple containing:
            - points_array (np.ndarray): A numpy array of the points (coordinates).
            - cells (list): A list of numpy arrays, each containing the indices of points that form a cell.
    """
    # Get points and cells from the grid
    points = ugrid.GetPoints()
    cell_array_obj = ugrid.GetCells()
    types = ugrid.GetCellTypesArray()

    # Convert points to numpy array
    points_array = numpy_support.vtk_to_numpy(points.GetData())
    
    # Convert cells (type) to numpy array
    cell_types = numpy_support.vtk_to_numpy(types)

    offsets = numpy_support.vtk_to_numpy(cell_array_obj.GetOffsetsArray())
    connectivity = numpy_support.vtk_to_numpy(cell_array_obj.GetConnectivityArray())
    # Build the cells list by slicing the connectivity array with the offsets.
    cells_array = [connectivity[offsets[i]:offsets[i+1]] for i in range(len(offsets) - 1)]

    # Return points and cells as numpy arrays
    return points_array, cells_array, cell_types

def mesh_to_numpy_connectivity(mesh):
    """
    Convert the mesh's connectivity and points to numpy arrays.

    This function retrieves the vtkUnstructuredGrid from the mesh and uses 
    `vtk_to_numpy_connectivity` to extract the points and cells in numpy format.

    Parameters:
        mesh (Elem): The mesh object containing the unstructured grid.

    Returns:
        tuple: A tuple containing:
            - points_array (np.ndarray): A numpy array of the points (coordinates).
            - cells (list): A list of numpy arrays, each containing the indices of points that form a cell.
    """
    # Get points and cells from vtkUnstructuredGrid
    ugrid = mesh.get_vtk_unstructured_grid()
    return vtk_to_numpy_connectivity(ugrid)

def numpy_to_vtk_connectivity(points_array, cells, cell_type = None, dime = None):
    """
    Convert the connectivity and points data from numpy arrays to a vtkUnstructuredGrid.
    """
    # Create vtkPoints from the input points_array
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_support.numpy_to_vtk(points_array, deep=True))
    
    # Loop through cells to check for tetrahedron or quad
    cell_lengths = np.array(list(map(len, cells)), dtype=np.int64)
    offsets = np.concatenate(([0], np.cumsum(cell_lengths)))
    
    # Prepare cell connectivity data
    cell_connectivity = np.concatenate(cells).astype(np.int64)
    
    if cell_type is None:
    
        # Map cell lengths to VTK cell types
        cell_type_map = {
            1: vtk.VTK_VERTEX,      
            2: vtk.VTK_LINE,         
            3: vtk.VTK_TRIANGLE,
            4: vtk.VTK_QUAD,
            5: vtk.VTK_PYRAMID,
            6: vtk.VTK_WEDGE,
            8: vtk.VTK_HEXAHEDRON
        }
        
        
        # Determine the cell type for each element
        cell_types = []
        for i, cell in enumerate(cells):
            if len(cell) == 4:
                if dime is None:
                    volume = compute_tetrahedron_volume(points_array[cell])
                    if volume > _TOL:
                        cell_types.append(vtk.VTK_TETRA)
                    else:
                        cell_types.append(vtk.VTK_QUAD)
                elif dime == 2:
                    cell_types.append(vtk.VTK_QUAD)
                elif dime == 3:
                    cell_types.append(vtk.VTK_TETRA)
            else:
                # For other cases, directly use the mapping
                cell_types.append(cell_type_map.get(len(cell), vtk.VTK_EMPTY))
        
        vtk_cell_types = numpy_support.numpy_to_vtk(cell_types, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        
    else:
        cell_type = np.array(cell_type, dtype=np.int64)
        vtk_cell_types = numpy_support.numpy_to_vtk(cell_type, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)

    # Create vtkCellArray from cell connectivity
    vtk_cell_connectivity = numpy_support.numpy_to_vtkIdTypeArray(cell_connectivity, deep=True)
    vtk_offsets = numpy_support.numpy_to_vtkIdTypeArray(offsets, deep=True)
    vtk_cells = vtk.vtkCellArray()
    vtk_cells.SetData(vtk_offsets, vtk_cell_connectivity)
    
    # Create vtkUnstructuredGrid
    ugrid = vtk.vtkUnstructuredGrid()
    ugrid.SetPoints(vtk_points)
    ugrid.SetCells(vtk_cell_types, vtk_cells)
    
    return ugrid


# ---------------------------------------------------------------------
#   DEPRECATED
# ---------------------------------------------------------------------

# def numpy_to_vtk_connectivity(points_array, cells):
#     """
#     Convert the connectivity and points data from numpy arrays to a vtkUnstructuredGrid.

#     This function converts the provided numpy arrays for points and cells back into a vtkUnstructuredGrid.
#     The cell types are determined based on the number of points in each cell (e.g., triangle, quad).

#     Parameters:
#         points_array (np.ndarray): The numpy array of point coordinates.
#         cells (list): A list of numpy arrays, where each sublist contains the indices of points that form a cell.

#     Returns:
#         vtkUnstructuredGrid: A vtkUnstructuredGrid object constructed from the provided points and cells.
#     """ 
#     # Create vtkPoints from the input points_array
#     vtk_points = vtk.vtkPoints()
#     vtk_points.SetData(numpy_support.numpy_to_vtk(points_array, deep=True))
    
#     # Prepare cell connectivity data
#     cell_connectivity = np.concatenate(cells)


#     # Map cell lengths to VTK cell types
#     cell_type_map = {
#         1: vtk.VTK_VERTEX,      
#         2: vtk.VTK_LINE,         
#         3: vtk.VTK_TRIANGLE,
#         4: vtk.VTK_QUAD,
#         4: vtk.VTK_TETRA,
#         5: vtk.VTK_PYRAMID,
#         6: vtk.VTK_WEDGE,
#         8: vtk.VTK_HEXAHEDRON
#     }
#     cell_lengths = np.array(list(map(len, cells)), dtype=np.int64)
#     offsets = np.concatenate(([0], np.cumsum(cell_lengths)))
    
#     # Assign cell types
#     vectorized_map = np.vectorize(lambda length: cell_type_map.get(length, vtk.VTK_EMPTY))  # Default to VTK_EMPTY if not found
#     cell_types = vectorized_map(cell_lengths)
#     vtk_cell_types = numpy_support.numpy_to_vtk(cell_types, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)

#     # Create vtkCellArray from cell connectivity
#     vtk_cell_connectivity = numpy_support.numpy_to_vtkIdTypeArray(cell_connectivity, deep=True)
#     vtk_offsets = numpy_support.numpy_to_vtkIdTypeArray(offsets, deep=True)

#     # Create vtkUnstructuredGrid
#     ugrid = vtk.vtkUnstructuredGrid()
#     ugrid.SetPoints(vtk_points)

#     # Create vtkCellArray and set data
#     vtk_cells = vtk.vtkCellArray()
#     vtk_cells.SetData(vtk_offsets, vtk_cell_connectivity)

#     ugrid.SetCells(vtk_cell_types, vtk_cells)
    
#     return ugrid