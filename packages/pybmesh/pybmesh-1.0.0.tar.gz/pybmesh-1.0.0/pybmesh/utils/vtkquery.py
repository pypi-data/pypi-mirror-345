# -*- coding: utf-8 -*-
"""
Created on 10/02/2025
Last modified on 10/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module contains various utility functions for querying and processing mesh data using VTK.
It provides functions for retrieving mesh properties (such as the number of elements and points), computing
element sizes, mapping points and elements between meshes, and extracting data arrays from vtkUnstructuredGrid
objects. These utilities facilitate mesh analysis and visualization in VTK-based applications.
"""

import vtk
import warnings
import numpy as np
from vtk.util import numpy_support
from pybmesh.io.vtk2numpy import vtk_to_numpy_connectivity


def nbEl(mesh):
    """
    Return the number of elements (cells) in the mesh.

    Args:
        mesh (Mesh): The mesh object to query.

    Returns:
        int: The number of cells in the mesh.

    Example:
        >>> nbEl(mesh)
        100
    """
    ug = mesh.get_vtk_unstructured_grid()
    n = ug.GetNumberOfCells()
    if n == 0:
        warnings.warn("No elements found in the mesh.", UserWarning)
    return n

def nbPt(mesh):
    """
    Return the number of points in the mesh.

    Args:
        mesh (Mesh): The mesh object to query.

    Returns:
        int: The number of points in the mesh.

    Example:
        >>> nbPt(mesh)
        200
    """
    return mesh.get_vtk_unstructured_grid().GetNumberOfPoints()

def elSize(mesh, opt='average'):
    """
    Return a size metric for the mesh elements.

    Parameters:
        mesh (Mesh): The mesh object.
        opt (str): One of 'min', 'max', or 'average' to choose the metric.

    Returns:
        float: The chosen size metric computed from each cell's GetLength2().

    Example:
        >>> elSize(mesh, opt='average')
        1.23
    """
    ug = mesh.get_vtk_unstructured_grid()
    n = ug.GetNumberOfCells()
    if n == 0:
        warnings.warn("No elements found in the mesh.", UserWarning)
        return np.nan

    # Compute sizes using each cell's GetLength2() as a measure
    sz = np.array([ug.GetCell(i).GetLength2() for i in range(n)])
    ops = {'min': np.min, 'max': np.max, 'average': np.mean}
    if opt not in ops:
        raise ValueError("Invalid option. Choose from 'min', 'max', or 'average'.")
    return ops[opt](sz)
    
def findPoints(mesh1, mesh2):
    """
    Maps points from the submesh (mesh1) to the main mesh (mesh2) using the vtkPointLocator 
    to find the closest points in the main mesh. The function checks the size of the meshes 
    to ensure proper mapping.

    Parameters:
    mesh1 (vtk.vtkUnstructuredGrid or your custom mesh): The submesh whose points are being mapped.
    mesh2 (vtk.vtkUnstructuredGrid or your custom mesh): The main mesh to which the points from the submesh are mapped.

    Returns:
    dict: A dictionary where keys are the indices of points in mesh1 (the submesh), 
          and values are the indices of the closest points in mesh2 (the main mesh).
    """

    # Ensure that mesh1 and mesh2 are vtkUnstructuredGrid objects
    if not isinstance(mesh1, vtk.vtkUnstructuredGrid):
        mesh1 = mesh1.get_vtk_unstructured_grid()
    if not isinstance(mesh2, vtk.vtkUnstructuredGrid):
        mesh2 = mesh2.get_vtk_unstructured_grid()
    
    # Swap mesh1 and mesh2 if mesh2 has fewer points than mesh1 to ensure proper mapping
    if mesh2.GetNumberOfPoints() < mesh1.GetNumberOfPoints():
        mesh1, mesh2 = mesh2, mesh1

    # Create a vtkPointLocator for mesh2 and build the locator
    point_locator = vtk.vtkPointLocator()
    point_locator.SetDataSet(mesh2)
    point_locator.BuildLocator()
    
    # Extract points from mesh1 (submesh)
    points, _, _ = vtk_to_numpy_connectivity(mesh1)
    
    # Map each point in mesh1 (submesh) to its closest point in mesh2 (main mesh)
    return {i: point_locator.FindClosestPoint(pt) for i, pt in enumerate(points)}

def findElems(mesh1, mesh2):
    """
    Maps points from the submesh (mesh1) to the main mesh (mesh2) using the vtkPointLocator 
    to find the closest points in the main mesh. The function checks the size of the meshes 
    to ensure proper mapping.

    Parameters:
    mesh1 (vtk.vtkUnstructuredGrid or your custom mesh): The submesh whose points are being mapped.
    mesh2 (vtk.vtkUnstructuredGrid or your custom mesh): The main mesh to which the points from the submesh are mapped.

    Returns:
    dict: A dictionary where keys are the indices of points in mesh1 (the submesh), 
          and values are the indices of the closest points in mesh2 (the main mesh).
    """
    # Ensure that mesh1 and mesh2 are vtkUnstructuredGrid objects
    if not isinstance(mesh1, vtk.vtkUnstructuredGrid):
        mesh1 = mesh1.get_vtk_unstructured_grid()
    if not isinstance(mesh2, vtk.vtkUnstructuredGrid):
        mesh2 = mesh2.get_vtk_unstructured_grid()
    
    # Swap mesh1 and mesh2 if mesh2 has fewer points than mesh1 to ensure proper mapping
    if mesh2.GetNumberOfCells() < mesh1.GetNumberOfCells():
        mesh1, mesh2 = mesh2, mesh1

    # Extract element and point data from mesh1 (submesh)
    points, cells, _ = vtk_to_numpy_connectivity(mesh1)
    
    # Map points from mesh1 to mesh2
    map_points_id = findPoints(mesh1, mesh2)
    
    # Update cell connectivity in mesh1 based on mapped points
    updated_cells = [
        [map_points_id[point_id] for point_id in cell] for cell in cells
    ]

    # Extract element and point data from mesh2 (main mesh)
    _, ref_cells, _ = vtk_to_numpy_connectivity(mesh2)
    
    # Hash the reference cells for faster lookup
    ref_cells_hash = {tuple(cell): idx for idx, cell in enumerate(ref_cells)}
    
    # Create a dictionary to store the mapping
    cell_mapping = {
        i: ref_cells_hash.get(tuple(updated_cell), -1)
        for i, updated_cell in enumerate(updated_cells)
    }

    return cell_mapping

def get_data(mesh, array_name = None):
    """
    Returns the data values of a given array name from the vtkUnstructuredGrid.

    Args:
        ugrid (vtk.vtkUnstructuredGrid): The unstructured grid.
        array_name (str): The name of the data array.

    Returns:
        numpy.ndarray: The data values corresponding to the given array name.
    """
    if isinstance(mesh, vtk.vtkUnstructuredGrid):
        ugrid = mesh
    else:
        ugrid = mesh.get_vtk_unstructured_grid()
    
    
    if array_name is None:
        array_names = []
        point_data = ugrid.GetPointData()
        cell_data = ugrid.GetCellData()
    
        # Get point data arrays
        for i in range(point_data.GetNumberOfArrays()):
            array_names.append(point_data.GetArrayName(i))
    
        # Get cell data arrays
        for i in range(cell_data.GetNumberOfArrays()):
            array_names.append(cell_data.GetArrayName(i))
    
        return array_names
    else :
        point_data = ugrid.GetPointData()
        cell_data = ugrid.GetCellData()
    
        # Check if the array is in point data
        array = point_data.GetArray(array_name)
        if array:
            return numpy_support.vtk_to_numpy(array)
    
        # Check if the array is in cell data
        array = cell_data.GetArray(array_name)
        if array:
            return numpy_support.vtk_to_numpy(array)
    
        raise ValueError(f"Array with name '{array_name}' not found in the vtkUnstructuredGrid.")