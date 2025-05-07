#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 27/01/2025
Last modified on 07/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module defines geometrical classes and functions for managing 
0D mesh elements within a 3D space. It provides a class for creating and manipulating 
point meshes. This class includes functionalities for handling multiple points, applying 
geometric transformations, and constructing VTK unstructured grids for visualization and further 
processing in computational geometry applications.
"""
import vtk
import numpy as np
from vtk.util import numpy_support
from pybmesh.geom.mesh import Elem
from pybmesh.utils.constants import _MAX_HEAD_TAIL

# -------------------------------------------------------------------------
# 1) PointMesh
# -------------------------------------------------------------------------
class Point(Elem):
    """
    Represents one or multiple points as 0D "vertex" cell(s) in a VTK unstructured grid.

    Inherits from:
        Elem: Provides additional methods for geometric transformations and visualization.
    """

    def __init__(self, *points_coords, pid = 0):
        """
        Initialize a Point instance with one or more 3D points.

        The points are stored in a VTK unstructured grid with VTK_VERTEX cells (0D).

        Parameters
        ----------
        *points_coords : tuple or list of tuples
            A single (x, y, z) tuple, separate x, y, z values, or multiple (x, y, z) tuples.
            If no coordinates are provided, defaults to [(0, 0, 0)].
        pid (int): The **part ID** that identifies the mesh entity represented by this element.
        """
        super().__init__(pid = pid)
        # Handle input based on type and structure of points_coords.
        if not points_coords:
            points_coords = [(0, 0, 0)]
        elif isinstance(points_coords[0], (tuple, list, np.ndarray)):
            # If the first element is a tuple or list, assume a list of points was provided.
            points_coords = self._parse_from_list_of_coordinates(points_coords)
        else:
            # Otherwise, treat the inputs as separate coordinate values.
            points_coords = self._parse_from_coordinates(*points_coords)

        self._build_ugrid(points_coords)

    def _parse_from_coordinates(self, *coords):
        """
        Parse coordinates provided as separate values or a single tuple.

        Missing coordinate values default to 0.

        Parameters
        ----------
        *coords : numbers
            Coordinate values, e.g., (x, y, z).

        Returns
        -------
        list of tuple
            A list containing one tuple with three coordinates (x, y, z).
        """
        points_coords = [(coords[0] if len(coords) > 0 else 0,
                          coords[1] if len(coords) > 1 else 0,
                          coords[2] if len(coords) > 2 else 0)]
        return points_coords

    def _parse_from_list_of_coordinates(self, coords):
        """
        Parse a list or tuple of coordinate tuples.

        Each coordinate entry can be provided as a tuple/list of (x, y), (x, y, z), or as a single number.

        Parameters
        ----------
        coords : list or tuple
            A collection of coordinates in various formats.

        Returns
        -------
        list
            A list of parsed coordinate tuples.
        """
        points_coords = []
        coords = coords[0]
        for coord in coords:
            if isinstance(coord, (tuple, list, np.ndarray)):
                # Recursively parse each coordinate tuple/list.
                points_coords.append(self._parse_from_coordinates(*coord)[0])
            elif isinstance(coord, (int, float)):
                # If a single numeric value is provided, treat it as an x-coordinate.
                points_coords.append(self._parse_from_coordinates(coord)[0])
            else:
                raise ValueError(f"Unsupported coordinate format in list/tuple: {type(coord)}")
        return points_coords

    def _build_ugrid(self, coords):
        """
        Build the VTK unstructured grid from a list of coordinate tuples using
        NumPy for fast conversion. Each coordinate is added as a point in the grid,
        and a corresponding VTK_VERTEX cell is created in a vectorized manner.
        
        Parameters
        ----------
        coords : list of tuple
            List of (x, y, z) coordinates.
        """
        # Convert the list of coordinates to a numpy array
        np_coords = np.array(coords, dtype=np.float64)
        
        # Create vtkPoints from the numpy array directly
        vtk_points = vtk.vtkPoints()
        vtk_points.SetData(numpy_support.numpy_to_vtk(np_coords, deep=True))
        self._ugrid.SetPoints(vtk_points)
        
        # Number of points
        n = np_coords.shape[0]
        
        # For vertex cells, each cell is defined as: [1, point_id]
        # Build a 1D numpy array of length 2*n where:
        #  - Every even index is 1 (the number of points in the cell)
        #  - Every odd index is the point index.
        cell_array = np.empty(2 * n, dtype=np.int64)
        cell_array[0::2] = 1
        cell_array[1::2] = np.arange(n)
        
        # Convert the numpy array to a vtkIdTypeArray
        vtk_cell_ids = numpy_support.numpy_to_vtkIdTypeArray(cell_array, deep=True)
        
        # Create a vtkCellArray and set the cells
        vtk_cell_array = vtk.vtkCellArray()
        vtk_cell_array.SetCells(n, vtk_cell_ids)
        
        # Set the cells for the unstructured grid (VTK_VERTEX type)
        self._ugrid.SetCells(vtk.VTK_VERTEX, vtk_cell_array)
        
        # Generate the pid field once, after the full grid is built.
        self._generate_pid_field()

    @property
    def coords(self):
        """
        Get the current coordinates of all points in the unstructured grid.

        This property reflects any transformations that have been applied to the points.

        Returns
        -------
        numpy.ndarray
            An array of shape (n, 3) containing the (x, y, z) coordinates of each point.
        """
        vtk_points = self._ugrid.GetPoints()
        num_points = vtk_points.GetNumberOfPoints()
        updated_coords = np.array([vtk_points.GetPoint(i) for i in range(num_points)], dtype=float)
        return updated_coords

    def __repr__(self):
        """
        Return a string representation of the Point object.

        The representation includes:
          - The total number of points.
          - A list of points with their index and (x, y, z) coordinates.
          If the number of points exceeds a threshold, only the head and tail points are displayed.

        Returns
        -------
        str
            A formatted string describing the Point object.
        """
        # Retrieve the total number of points.
        num_nodes = self._ugrid.GetNumberOfPoints()

        # Build a list of string representations for each point.
        vtk_points = self._ugrid.GetPoints()
        nodes_str = []
        for idx in range(num_nodes):
            pt = vtk_points.GetPoint(idx)  # Retrieve the point's (x, y, z) coordinates.
            nodes_str.append(f" {idx} ({pt[0]:.2f}, {pt[1]:.2f}, {pt[2]:.2f})")

        # If there are too many points, show only the first and last few.
        if num_nodes > 2 * _MAX_HEAD_TAIL:
            nodes_str = nodes_str[:_MAX_HEAD_TAIL] + ["..."] + nodes_str[-_MAX_HEAD_TAIL:]

        # Format the final representation string.
        repr_str = f"Point\nNumber of Points: {num_nodes}\nPoints:\n" + "\n".join(nodes_str)
        return repr_str

    @classmethod
    def help(cls):
        """
        Returns helpful information about the Point class and its methods.
        """
        help_text = """
Point Class
------------------
A class to represent one or multiple 0D points in a 3D space, stored as VTK vertex cells.

Constructor:
------------------
\033[1;32mPoint(*points_coords, color=(1, 0, 0))\033[0m
  - \033[1;32m*points_coords\033[0m: Specifies the point coordinates, which can be provided as:
      - A single (x, y, z) tuple.
      - Separate x, y, z values.
      - A list or tuple of (x, y, z) tuples.
    If coordinates are missing, they default to (0, 0, 0).
  - \033[1;32mpid\033[0m: The part ID representing the mesh entity (default: 0). 

Public Attributes:
------------------
\033[1;32mcolor\033[0m
    The RGB color associated with the element. The color is determined by the pid
    and can be used for visualization purposes.                    

Public Methods:
------------------
\033[1;34mcoords()\033[0m
    Retrieve the current (x, y, z) coordinates of the points.

Inherited Methods :
------------------
\033[1;34mtranslate(dx, dy, dz)\033[0m
    Translate all points by the vector (dx, dy, dz).
\033[1;34mrotate(center, pA, pB, axis, angle, angles, points)\033[0m
    \033[1;34mrotate(center=(0, 0, 0), axis=(0, 0, 1), angle=45)\033[0m
    Rotate all points around the specified axis ('x', 'y', or 'z') by a given angle in degrees.
    \033[1;34mrotate(center, angles=(30, 45, 60))\033[0m
    Rotate all points by specified angles around the X, Y, and Z axes, respectively.
    \033[1;34mrotate(pA=(1, 1, 1), pB=(2, 2, 2), angle=90)\033[0m
    Rotate all points around an axis defined by two points (pA and pB), by a given angle in degrees.
    
    \033[1;34mcenter\033[0m default to (0, 0, 0)
    Point class or tuple may be used for \033[1;34mcenter\033[0m, \033[1;34mpA\033[0m, \033[1;34mpB\033[0m
\033[1;34mget_vtk_unstructured_grid()\033[0m
    Retrieve the underlying vtkUnstructuredGrid.
\033[1;34mmerge_duplicate_nodes(verbose=False, tol=1e-5)\033[0m
    Merge duplicate nodes within a specified tolerance (default: 1e-5).
\033[1;34mcopy()\033[0m
    Create a deep copy of the Point object.
\033[1;34mpid\033[0m
    Accessor and setter for the part ID (pid). The pid uniquely identifies the element
    as a mesh entity with its own characteristics (e.g., material, function).
    
Usage Example:
------------------
  p1 = Point(1, 2, 3)
  p2 = Point((0, 0, 0), (1, 1, 1), color=(0, 1, 0))
  p1.translate(1, 0, 0)
  print(p1.coords)
"""
        return help_text
