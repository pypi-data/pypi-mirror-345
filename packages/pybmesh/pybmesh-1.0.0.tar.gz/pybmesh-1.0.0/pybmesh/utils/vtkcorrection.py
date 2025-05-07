#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 09:47:46 2025
Last modified on Fri Mar  7 09:47:46 2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module provides correction utilities for VTK mesh connectivity.
It contains functions to check mesh quality and validity, correct pyramid and wedge connectivity issues,
and regenerate cleaned meshes. The module also includes helper functions for comparing duplicate nodes
and orientation of mesh elements, ensuring robust mesh processing for visualization and analysis.
"""

import vtk
from itertools import combinations
from skspatial.objects import Plane
from sklearn.cluster import KMeans
import numpy as np
from pybmesh.geom.d0 import Point
from pybmesh.utils.constants import _TOL
from pybmesh.utils.vtkquery import get_data
from pybmesh.utils.maths import get_permutation_function
from pybmesh.utils.miscutils import sort_points
from pybmesh.io.vtk2numpy import mesh_to_numpy_connectivity, numpy_to_vtk_connectivity

def are_dupNodes(pt1, pt2, tol=_TOL):
    """
    Return True if the distance between pt1 and pt2 is less than tol.

    Works for numpy arrays (e.g., a 3-element coordinate) or for Point objects.
    If a Point instance is provided, the first coordinate in its 'coords' attribute is used.

    Args:
        pt1 (Point or np.ndarray): First point.
        pt2 (Point or np.ndarray): Second point.
        tol (float): The tolerance threshold for comparison.

    Returns:
        bool: True if the points are within the tolerance, False otherwise.

    Example:
        >>> are_dupNodes(Point([1, 2, 3]), np.array([1, 2, 3]))
        True
    """
    if isinstance(pt1, Point):
        pt1 = pt1.coords[0]
    if isinstance(pt2, Point):
        pt2 = pt2.coords[0]
    return np.linalg.norm(pt1 - pt2) < tol

def are_id_oriented(obj1, obj2):
    """
    Check if two lines are oriented the same way.

    Args:
        obj1 (Line): First line object.
        obj2 (Line): Second line object.

    Returns:
        bool: True if lines are oriented the same, False otherwise.

    Example:
        >>> are_id_oriented(line1, line2)
        True
    """
    S1 = obj1.get_start_point()
    E1 = obj1.get_end_point()
    S2 = obj2.get_start_point()
    E2 = obj2.get_end_point()

    d0 = np.linalg.norm(S1 - S2) + np.linalg.norm(E1 - E2)
    d1 = np.linalg.norm(S1 - E2) + np.linalg.norm(E1 - S2)
    return d1 >= d0

def check_mesh_quality(mesh, bad = True):
    """
    Checks the quality of a vtkUnstructuredGrid mesh and identifies bad elements based on a quality threshold.

    Args:
        mesh  : The Elem object or vtkUnstructuredGrid  to evaluate.
        quality_threshold (float, optional): The threshold for quality assessment. Elements with quality below this value are considered bad. Default is 0.5.

    Returns:
        list: List of bad element indices (cell indices) that have quality below the threshold.
    """
    if isinstance(mesh, vtk.vtkUnstructuredGrid):
        ugrid = mesh
    else:
        ugrid = mesh.get_vtk_unstructured_grid()
    
    # Create a vtkCellQuality filter to evaluate the mesh quality
    cell_quality_filter = vtk.vtkMeshQuality()
    cell_quality_filter.SetInputData(ugrid)
    cell_quality_filter.SetTriangleQualityMeasureToArea() 
    cell_quality_filter.SetQuadQualityMeasureToArea()
    cell_quality_filter.SetTetQualityMeasureToJacobian()
    cell_quality_filter.SetPyramidQualityMeasureToJacobian()
    cell_quality_filter.SetWedgeQualityMeasureToJacobian() 
    cell_quality_filter.SetHexQualityMeasureToJacobian()
    cell_quality_filter.Update()
    
    
    # Get the quality values for each cell in the mesh)
    quality_array = get_data(cell_quality_filter.GetOutput(),"Quality")

    # filter bad cells
    valid_cells_mask = quality_array > 0
    valid_cells_idx = np.array(np.where(valid_cells_mask)[0], dtype=int)  # Returns indices where the condition is True
    invalid_cells_idx = np.array(np.where(~valid_cells_mask)[0], dtype=int)
    
    return valid_cells_idx, invalid_cells_idx, quality_array

def check_mesh_validity(mesh):
    """
    Checks the validity of a vtkUnstructuredGrid mesh using vtkCellValidator.
    
    This function uses `vtkCellValidator` to identify invalid cells in a VTK mesh.
    The validity status is obtained via the "ValidityState" array from the filter's
    output. Cells with a "ValidityState" value of 0 are considered valid; otherwise,
    they are deemed invalid.

    Args:
        mesh: Either an `Elem`-like object (which provides a `get_vtk_unstructured_grid` method)
              or a `vtkUnstructuredGrid` instance.
    
    Returns:
        tuple:
            - valid_cells_idx (numpy.ndarray): The indices of cells identified as valid.
            - invalid_cells_idx (numpy.ndarray): The indices of cells identified as invalid.
            - quality_array (numpy.ndarray): The "ValidityState" array indicating the validity
              state of each cell in the mesh. Values of 0 indicate valid cells; non-zero
              values indicate invalid cells.
    
    Example:
        >>> valid_indices, invalid_indices, validity = check_mesh_validity(my_mesh)
        >>> print("Valid cell indices:", valid_indices)
        >>> print("Invalid cell indices:", invalid_indices)
    """
    if isinstance(mesh, vtk.vtkUnstructuredGrid):
        ugrid = mesh
    else:
        ugrid = mesh.get_vtk_unstructured_grid()


    # step 1 = fin errors in mesh
    vtk.vtkOutputWindow.GetInstance().SetDisplayModeToNever() #deactivate vtk stdout
    cell_quality_filter = vtk.vtkCellValidator()
    cell_quality_filter.SetInputData(ugrid)
    cell_quality_filter
    cell_quality_filter.Update()
    vtk.vtkOutputWindow.GetInstance().SetDisplayModeToDefault() # ractivate vtk stdout
    quality_array = get_data(cell_quality_filter.GetOutput(),"ValidityState")

    # filter bad cells
    valid_cells_mask = quality_array == 0
    valid_cells_idx = np.array(np.where(valid_cells_mask)[0], dtype=int)  # Returns indices where the condition is True
    invalid_cells_idx = np.array(np.where(~valid_cells_mask)[0], dtype=int)
    
    # cells_array = np.array(cells, dtype=object)
    # invalid_cells = cells_array[list(invalid_cells_idx)]
    # valid_cells = cells_array[list(valid_cells_idx)]
    return valid_cells_idx, invalid_cells_idx, quality_array

def fix_pyramid_connectivity(cell, points):
    """
    Reorders the nodes of a pyramid cell so that the base nodes (4 nodes) are 
    arranged in counterclockwise order and the apex node is appended at the end.
    
    Parameters:
        cell: list or array-like of 5 node indices representing a pyramid.
        point: numpy array of shape (N, 3) containing the 3D coordinates of all nodes.
               (The node indices in 'cell' index into this array.)
    
    Returns:
        sorted_cell: list of node indices, with the first 4 being the base (ordered 
                     counterclockwise) and the last one being the apex.
    """
    
    def plane_error(plane, pts):
        """
        Calculate the sum of squared signed distances from points to the plane.
        """
        distances = [plane.distance_point_signed(pt) for pt in pts]
        return np.sum(np.array(distances)**2)
    
    # Iterate through all combinations of 4 nodes from the cell
    combs = list(combinations(cell, 4))
    min_error = np.inf
    best_plane = None
    best_combination = None

    for comb in combs:
        selected_points = points[list(comb)]
        # Fit a plane through the selected 4 points
        plane = Plane.best_fit(selected_points)
        error = plane_error(plane, selected_points)
        if error < min_error:
            min_error = error
            best_plane = plane
            best_combination = comb

    # The best combination is taken as the base of the pyramid.
    base = best_combination
    # The apex is the remaining node not in the base.
    apex = list(set(cell) - set(best_combination))
    
    # Project the base points onto the best-fit plane.
    base_points = points[list(base)]
    projected_pts = best_plane.project_points(base_points)
    
    # Compute the centroid of the projected points (reference for ordering)
    centroid = np.mean(projected_pts, axis=0)
    
    # Get the normal vector of the plane.
    normal_vector = best_plane.normal
    
    # Create a local coordinate system on the plane.
    # Choose an arbitrary vector that's not parallel to the normal.
    v1 = np.random.rand(3)
    v1 -= np.dot(v1, normal_vector) * normal_vector  # make it perpendicular to the normal
    v1 /= np.linalg.norm(v1)
    # v2 is perpendicular to both normal and v1.
    v2 = np.cross(normal_vector, v1)
    
    def transform_to_local(pts, origin, v1, v2):
        # Translate the points by subtracting the origin.
        translated = pts - origin
        # Project the points onto the local basis.
        x_local = np.dot(translated, v1)
        y_local = np.dot(translated, v2)
        return np.vstack((x_local, y_local)).T

    # Transform projected base points into the local 2D coordinate system.
    local_pts = transform_to_local(projected_pts, centroid, v1, v2)
    
    # Define an angle function relative to the centroid.
    def angle_from_centroid(pt):
        return np.arctan2(pt[1], pt[0])
    
    # Sort the local points by their angle (counterclockwise order).
    sorted_indices = sorted(range(len(local_pts)), key=lambda i: angle_from_centroid(local_pts[i]))
    
    # Reorder the base nodes using the sorted order.
    sorted_base = [base[i] for i in sorted_indices]
    
    # Combine sorted base with the apex node.
    sorted_cell = sorted_base + apex
    return sorted_cell

def fix_wedge_connectivity(cell, points):
    """
    Sort the points in a given cell into an anticlockwise order,
    after splitting them into two clusters along their major axis.
    
    This function assumes that:
      - 'cell' is an array-like of integer indices into 'points'.
      - 'points' is a NumPy array of shape (N, D) with D typically 2 or 3.
      - The points in the cell belong to a nearly coplanar set (e.g. a wedge base).
      - An external function 'sort_points' is defined and returns four values,
        where the third and fourth items are the sorted indices (relative to the
        respective groups) for group1 and group2.
    
    The algorithm works as follows:
      1. Extract the points corresponding to the indices in 'cell'.
      2. Compute their centroid and center the points.
      3. Use SVD to obtain the primary (major) axis of the point set.
      4. Project the centered points onto the major axis.
      5. Cluster the 1D projections into two groups using KMeans.
      6. For each group, sort the points using the externally defined
         'sort_points' function.
      7. Concatenate the sorted indices from both groups to obtain a full ordering,
         which can be used to fix the connectivity of the wedge.
    
    Parameters
    ----------
    cell : array-like of int
        The indices (e.g. from a cells array) corresponding to the points of interest.
    points : (N, D) np.ndarray of float
        The array of point coordinates.
    
    Returns
    -------
    connectivity : np.ndarray of int
        The sorted array of indices (from 'cell') in anticlockwise order.
    """
    # Ensure cell is a numpy array (of indices) and extract the corresponding points
    cell = np.asarray(cell)
    pts = points[cell]  
    
    # Compute the centroid of the points and center the data
    centroid = pts.mean(axis=0)
    pts_centered = pts - centroid

    # Compute SVD on the centered points to get the principal directions.
    # Setting full_matrices=False speeds up the computation.
    U, S, Vt = np.linalg.svd(pts_centered, full_matrices=False)
    # Try each principal axis candidate (up to the available dimensions)
    best_labels = None
    best_balance = float('inf')
    for i in range(Vt.shape[0]):
        axis_candidate = Vt[i]
        projections = pts_centered.dot(axis_candidate)
        # Cluster the 1D projections into two clusters
        kmeans = KMeans(n_clusters=2, random_state=0).fit(projections.reshape(-1, 1))
        labels = kmeans.labels_
        # Measure balance between the clusters
        counts = np.bincount(labels)
        # Skip if for some reason we don't get exactly two clusters
        if len(counts) < 2:
            continue
        balance = abs(counts[0] - counts[1])
        if balance < best_balance:
            best_balance = balance
            best_labels = labels

    # Use the best clustering obtained
    labels = best_labels
    # Split the points into groups using the selected labels
    group1 = pts[labels == 0]
    group2 = pts[labels == 1]
    grp1 = cell[labels == 0]
    grp2 = cell[labels == 1]
    # sort nodes according to position
    _, _, sorted_indices1, sorted_indices2 = sort_points(group1, group2)
    
    # Reorder the original indices of each group according to the sorted order.
    sorted_grp1 = grp1[sorted_indices1]
    sorted_grp2 = grp2[sorted_indices2]
    
    # Concatenate the sorted groups to form the complete connectivity order.
    connectivity = np.hstack([sorted_grp1, sorted_grp2])
    
    return connectivity

def regen(mesh, ncpu = 1):
    """
    Processes the input mesh by cleaning its connectivity data to remove duplicate points,
    and returns a new mesh with the cleaned connectivity.

    Parameters:
    mesh (Mesh): The input mesh object to be processed.

    Returns:
    Mesh: A new mesh object with cleaned connectivity data.
    """
    # filter bad cells

    _, invalid_cells_idx, _ = check_mesh_quality(mesh)

    # Remove duplicate cells by converting each cell list to a set and back to a list
    points, cells, types = mesh_to_numpy_connectivity(mesh)  

    [cells.__setitem__(i, list(dict.fromkeys(cells[i]))) for i in invalid_cells_idx]
    # cells = [list(dict.fromkeys(arr)) for arr in cells]
    ug = numpy_to_vtk_connectivity(points, cells)

    f_wedge = None

    for idx in invalid_cells_idx:
        if len(cells[idx]) == 5:
            cells[idx] = [cells[idx][1],cells[idx][2], cells[idx][4], cells[idx][3], cells[idx][0]]
        elif len(cells[idx]) == 6:
            if f_wedge is None :
                f_wedge, _ = get_permutation_function(cells[idx],
                                                   fix_wedge_connectivity(cells[idx],points))
            cells[idx] = f_wedge(cells[idx])
            #cells[idx] = [cells[idx][0],cells[idx][3], cells[idx][5], cells[idx][1], cells[idx][2],cells[idx][4]]


    ug = numpy_to_vtk_connectivity(points, cells) 
    
    mesh._set_vtk_unstructured_grid(ug)
    mesh.pid=mesh.pid