#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 04/02/2025
Last modified on 04/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module defines the Volume class, a subclass of Elem that represents a 3D mesh
stored in vtkUnstructuredGrid. The class is designed to generate and manipulate 3D meshes such 
as hex meshes or tetrahedral meshes. It works by interpolating between two given surfaces (s0 
and s1) and building an unstructured grid based on these interpolated points. The class supports 
advanced mesh generation techniques, including element size progression and grading for adaptive meshing.
"""

import numpy as np
from pybmesh.geom.mesh import Elem
from pybmesh.io.vtk2numpy import mesh_to_numpy_connectivity, numpy_to_vtk_connectivity
from pybmesh.utils.vtkquery import nbPt, nbEl
from pybmesh.utils.miscutils import sort_points
from scipy.optimize import fsolve


class Volume(Elem):
    """
    Volume Class
    ------------
    A 3D mesh representation stored in vtkUnstructuredGrid. This class is designed to create
    and manipulate 3D meshes, such as hex meshes or tetrahedral meshes, by interpolating between
    two given surfaces (s0 and s1) to generate the corresponding 3D mesh grid.
    """

    def __init__(self, s0=None, s1=None, n=None, size=None, grading=1, progression = 'linear', pid=0):
        """
        Initialize a Volume object using two surfaces (s0 and s1) and generate the corresponding 3D mesh.

        Parameters:
            s0, s1 (Mesh): The two surfaces to interpolate between, must be homeomorphic (same topology).
            n (int, optional): The number of interpolation layers between s0 and s1. Default is None.
            size (float, optional): Size of the elements along the mesh. Overrides `n` if provided.
            grading (float, optional): The grading factor for mesh element size progression.
            progression (str, optional): Defines the progression type, either 'linear' or 'geometric'.
            pid (int, optional): Part ID for the element, identifying its unique properties or material.

        Raises:
            ValueError: If s0 and s1 are not homeomorphic.
        """
        super().__init__(pid=pid)
        if (s0,s1) != (None, None):
            # Check if s0 and s1 are homeomorphic
            if not self._check_homeomorphism(s0, s1):
                raise ValueError("The surfaces s0 and s1 are not homeomorphic.")
            
            # Build unstructured grid
            self._build_ugrid(s0, s1, n, size, grading, progression)

    def _check_homeomorphism(self, s0, s1):
        """
        Check if the two surfaces are homeomorphic (i.e., have the same topology).

        Parameters:
            s0, s1 (Mesh): The surfaces to check.

        Returns:
            bool: True if surfaces are homeomorphic, otherwise False.
        """
        return ((nbEl(s0) == nbEl(s1)) and (nbPt(s0) == nbPt(s1)))

    # def _sort_points(self, pts0, pts1, epsilon=1e-8):
    #     """
    #     Sort two sets of points (pts0, pts1) while considering numerical tolerance.
    #     Ensures that sorting order is consistent across both point sets.

    #     Parameters:
    #         pts0, pts1 (np.ndarray): Point sets to be sorted.
    #         epsilon (float, optional): Numerical tolerance for rounding.

    #     Returns:
    #         tuple: Sorted points (sorted_pts0, sorted_pts1) and the sorted indices.
    #     """
    #     pts0_rounded = np.round(pts0, decimals=int(-np.log10(epsilon)))
    #     pts1_rounded = np.round(pts1, decimals=int(-np.log10(epsilon)))

    #     sorted_indices1 = np.lexsort(
    #         (pts1_rounded[:, 2], pts1_rounded[:, 1], pts1_rounded[:, 0])
    #     )
    #     sorted_indices0 = np.lexsort( 
    #          (pts0_rounded[:, 2], pts0_rounded[:, 1], pts0_rounded[:, 0])
    #     )
    #     sorted_pts0 = pts0[sorted_indices0]
    #     sorted_pts1 = pts1[sorted_indices1]
        
    #     return sorted_pts0, sorted_pts1, sorted_indices0

    def _update_cell_connectivity(self, cells, sorted_indices):
        """
        Update cell connectivity based on sorted point indices.

        Parameters:
            cells (list): List of cells with original point indices.
            sorted_indices (list): List of sorted point indices.

        Returns:
            list: Updated list of cells with re-mapped point indices.
        """
        index_map = {original_idx: sorted_idx for sorted_idx, original_idx in enumerate(sorted_indices)}
        
        updated_cells = []
        for cell in cells:
            updated_cells.append([index_map[idx] for idx in cell])
        
        return updated_cells

    def _interpolate_points(self, pts0, pts1, n, grading=1, progression = 'linear'):
        """
        Interpolate points between pts0 and pts1 using linear or geometric progression.

        Parameters:
            pts0, pts1 (np.ndarray): The two sets of points between which to interpolate.
            n (int): The number of interpolation layers between the two surfaces.
            grading (float): The grading factor for the mesh.
            progression (str): Defines whether to use linear or geometric progression.

        Returns:
            np.ndarray: Interpolated points.
        """
        t = np.linspace(0, 1, n + 1)  # Linear interpolation factors
        
        if grading < 1:
            coeff = 1/grading
        else:
            coeff = grading
        
        if progression == 'geometric':
            # Geometric progression: elements follow a geometric sequence
            t = t ** coeff  # Apply grading factor to t (power law)
            
        elif progression == 'linear':
            # Linear progression: element sizes increase linearly from size_0 to size_0 * grading
            def equation(x):
                t_x = t ** x
                return t_x[-1] - t_x[-2] - coeff * (t_x[1] - t_x[0])
            
            x_value = fsolve(equation, 1.0)  # Initial guess is 1.0
            t = t ** x_value[0]
        
        t = t / t[-1]  # Normalize the grading
            
        pts0 = np.array(pts0).reshape(1, -1)
        pts1 = np.array(pts1).reshape(1, -1)
        
        if grading < 1 :
            interpolated_pts = pts0 * t[:, None] + pts1 * ( 1- t[:, None])  # Broadcast interpolation
        else:
            interpolated_pts = pts0 * (1 - t[:, None]) + pts1 * t[:, None]  # Broadcast interpolation
        
        interpolated_pts = interpolated_pts.reshape(n + 1, -1, 3)
        
        return interpolated_pts

    def _merge_meshes(self, meshes):
        """
        Merge multiple meshes with shared connectivity using efficient NumPy operations.

        Parameters:
            meshes (list): List of meshes to merge.

        Returns:
            tuple: Merged points and updated cell connectivity.
        """
        sorted_point0 = np.vstack([mesh[0] for mesh in meshes])
        updated_cells = []
        point_offset = 0
        
        for points, cells in meshes:
            updated_cells_i = [np.array(cell) + point_offset for cell in cells]
            updated_cells.append(updated_cells_i)
            point_offset += len(points)
        
        fused_cells = []
        for i in range(len(updated_cells) - 1):
            for cell0, cell1 in zip(updated_cells[i], updated_cells[i + 1]):
                fused_cells.append(np.concatenate([cell0, cell1]))
        
        return sorted_point0, fused_cells

    def _merge_interpolated_meshes(self, pts0, pts1, updated_cells0, n, grading=1, progression = 'linear'):
        """
        Merge meshes with interpolated points between pts0 and pts1.

        Parameters:
            pts0, pts1 (np.ndarray): Two sets of points between which to interpolate.
            updated_cells0 (list): Updated cell connectivity for the first set of points.
            n (int): Number of interpolation layers.
            grading (float): Grading factor.
            progression (str): Progression type.

        Returns:
            tuple: Merged points and cells.
        """
        interpolated_pts = self._interpolate_points(pts0, pts1, n, grading, progression)
        meshes = [[interp_pts, updated_cells0] for interp_pts in interpolated_pts]
        return self._merge_meshes(meshes)

    def _build_ugrid(self, s0, s1, n, size,  grading, progression):
        """
        Build unstructured grid by interpolating between two surfaces (s0 and s1).

        Parameters:
            s0, s1 (Mesh): The two surfaces to interpolate between.
            n (int): The number of interpolation layers.
            size (float): Size of the mesh elements.
            grading (float): Grading factor for mesh element size progression.
            progression (str): Type of progression ('linear' or 'geometric').
        """
        # Step 3: Convert the surfaces to numpy connectivity
        pts0, cells0, _ = mesh_to_numpy_connectivity(s0)
        pts1, _, _ = mesh_to_numpy_connectivity(s1)
        
        if (n, size) == (None, None):
            n = 1
        elif size is not None :
            distances = np.linalg.norm(pts0 - pts1, axis=1)
            largest_distance = np.max(distances)
            n = int(largest_distance / size)
        
        # Step 4: Sort the points
        sorted_pts0, sorted_pts1, sorted_indices, _ = sort_points(pts0, pts1)
        
        # Step 5: Update the connectivity based on the sorted points
        updated_cells0 = self._update_cell_connectivity(cells0, sorted_indices)
        
        # Step 6: Interpolate between surfaces and merge
        merged_point, merged_cells = self._merge_interpolated_meshes(sorted_pts0, sorted_pts1, updated_cells0, n, grading, progression = 'linear')
        
        # Step 7: Convert to vtk and store in the unstructured grid
        ugrid = numpy_to_vtk_connectivity(merged_point, merged_cells)
        self._set_vtk_unstructured_grid(ugrid)
        self._generate_pid_field()
    @classmethod
    def help(cls):
        """
        Return helpful information about the Volume class and its methods.

        The help text includes usage details for the constructor, attributes, public methods,
        and the functionality of the class to create and manipulate 3D meshes.

        Returns:
            str: A multi-line string with usage instructions.
        """
        help_text = """
Volume Class
------------
A class for creating and manipulating 3D meshes such as hex meshes or tetrahedral meshes. 
The Volume class interpolates between two surfaces to generate a 3D unstructured grid.

Constructor:
-------------
\033[1;32mVolume(s0, s1, n=None, size=None, grading=1, progression='linear', pid=0)\033[0m
  - \033[1;32ms0, s1\033[0m: Two surfaces (Mesh objects) used for interpolation. Must be homeomorphic.
  - \033[1;32mn\033[0m: Number of interpolation layers. Defaults to None.
  - \033[1;32msize\033[0m: Size of the mesh elements. If provided, overrides `n`.
  - \033[1;32mgrading\033[0m: Grading factor for mesh element size progression (default: 1).
  - \033[1;32mprogression\033[0m: Type of progression ('linear' or 'geometric').
  - \033[1;32mpid\033[0m: Part ID, used to differentiate mesh entities (default: 0).

Inherited Methods:
------------------
\033[1;34mtranslate(dx, dy, dz)\033[0m
    Translate all points in the line by the vector (dx, dy, dz).
\033[1;34mrotate(center, pA, pB, axis, angle, angles, points)\033[0m
    \033[1;34mrotate(center=(0, 0, 0), axis=(0, 0, 1), angle=45)\033[0m
    Rotate all points around the specified axis ('x', 'y', or 'z') by a given angle in degrees.
    \033[1;34mrotate(center, angles=(30, 45, 60))\033[0m
    Rotate all points by specified angles around the X, Y, and Z axes, respectively.
    \033[1;34mrotate(pA=(1, 1, 1), pB=(2, 2, 2), angle=90)\033[0m
    Rotate all points around an axis defined by two points (pA and pB), by a given angle in degrees.
    
    \033[1;34mcenter\033[0m default to (0, 0, 0)
    Point class or tuple may be used for \033[1;34mcenter\033[0m, \033[1;34mpA\033[0m, \033[1;34mpB\033[0m
\033[1;34mscale(center, sx, sy, sz)\033[0m
    Scale all points by factors (sx, sy, sz) about the center (default to center of mass).
\033[1;34mget_vtk_unstructured_grid()\033[0m
    Retrieve the underlying vtkUnstructuredGrid.
\033[1;34mreverse_orientation()\033[0m
    Reverse the orientation.
\033[1;34mmerge_duplicate_nodes(verbose=False, tol=1e-5)\033[0m
    Merge duplicate nodes in the line within a specified tolerance (default: 1e-5).
\033[1;34mpid\033[0m
    Accessor and setter for the part ID (pid). The pid uniquely identifies the element
    as a mesh entity with its own characteristics (e.g., material, function).
"""
        return help_text
