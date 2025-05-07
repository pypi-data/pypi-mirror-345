#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 03/02/2025
Last modified on 07/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module defines geometrical classes and functions for managing 
1D mesh elements within a 3D space. It provides classes for creating and manipulating 
line meshes, polylines, arcs, and circles. These classes include functionalities for 
discretizing segments using linear or geometric progressions, generating points along 
curves, and constructing VTK unstructured grids for visualization and further processing 
in computational geometry applications.
"""

import vtk
import math
import numpy as np
from scipy.optimize import fsolve
from pybmesh.geom.mesh import Elem
from pybmesh.geom.d0 import Point
from pybmesh.io.vtk2numpy import to_array
from pybmesh.utils.maths import normalize
from pybmesh.utils.constants import _TOL

# -------------------------------------------------------------------------
# 1) LineMesh Class
# -------------------------------------------------------------------------
class Line(Elem):
    """
    A 1D mesh stored as one or more vtkLine / vtkPolyLine cells.
    """

    def __init__(self, p1=None, p2=None, n=None, size=None, grading=1, progression='linear', pid = 0):
        """
        Initializes a line based on different input configurations.

        p1, p2: Points or tuples specifying the start and end points.
        n: Number of elements (ignored if size or size_at_start, size_at_end are provided).
        size: Element size if a fixed element size is desired.
        grading: Grading factor for element size at the end.
        progression: 'linear' or 'geometric' progression for element size change.
        """
        super().__init__(pid = pid)
        # Only build the unstructured grid if p1 and p2 are provided
        if p1 is not None and p2 is not None:
            self._build_ugrid(p1, p2, n, size, grading, progression)
        else:
            self._ugrid = None  # Or set to a default value if desired

    def _build_ugrid(self, p1, p2, n, size, grading, progression):
        """
        Generates the points and elements (lines) for the unstructured grid.
        This method calls different private methods based on the inputs.
        """
        # Ensure p1 and p2 are numpy arrays (or Points)
        p1 = p1.coords if isinstance(p1, Point) else np.array(p1)
        p2 = p2.coords if isinstance(p2, Point) else np.array(p2)
        
        # Generate points based on the provided arguments
        points = self.generate_points(p1, p2, n, size, grading, progression)
        points = np.array(points, dtype=float).reshape(-1, 3)

        # Create vtkPoints directly from the numpy array, avoiding a loop
        vtk_points = vtk.vtkPoints()
        vtk_points.SetNumberOfPoints(len(points))
        for i, pt in enumerate(points):
            vtk_points.SetPoint(i, pt)

        self._ugrid.SetPoints(vtk_points)

        # Create cells efficiently by pre-allocating a vtkCellArray
        cell_array = vtk.vtkCellArray()
        for i in range(len(points) - 1):
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, i)
            line.GetPointIds().SetId(1, i + 1)
            cell_array.InsertNextCell(line)

        self._ugrid.SetCells(vtk.VTK_LINE, cell_array)
        self._generate_pid_field()

    def generate_points(self, p1, p2, n, size, grading, progression):
        """
        Select the appropriate method to generate points based on the input parameters.
        """
        if size is not None:
            return self._generate_points_from_size(p1, p2, size, grading, progression)
        if n is not None:
            return self._generate_points_from_number(p1, p2, n, grading, progression)

    def _generate_points_from_size(self, p1, p2, size, grading, progression):
        """
        Generates points based on the size of elements.
        """
        total_distance = np.linalg.norm(p2 - p1)
        n_points = int(total_distance // size)
        return self._generate_points_from_number(p1, p2, n_points, grading, progression)

    def _generate_points_from_number(self, p1, p2, n, grading, progression):
        """
        Generates points based on the number of desired elements.
        """
        # vector = p2 - p1
        # distance = np.linalg.norm(vector)

        if n == 1:
            return np.array([p1, p2])
        elif (progression == 'linear') or (grading == 1):
            return self._linear_spacing(p1, p2, n, grading)
        elif progression == 'geometric':
            return self._geometric_spacing(p1, p2,  n, grading)
        else:
            raise ValueError("Progression must be 'linear' or 'geometric'.")


    def _linear_spacing(self, p1, p2, n, grading):
        """
        Generates points using linear spacing between p1 and p2 with grading.
        Uses interpolation factors similar to _interpolate_points.
        """
        t = np.linspace(0, 1, n + 1)  # Linear interpolation factors
        
        if grading < 1:
            coeff = 1/grading
        else:
            coeff = grading
            
        # Apply grading to the interpolation factors
        def equation(x):
            t_x = t ** x
            return t_x[-1] - t_x[-2] - coeff * (t_x[1] - t_x[0])
        
        x_value = fsolve(equation, 1.0)  # Initial guess is 1.0
        t = t ** x_value[0]
        
        t = t / t[-1]  # Normalize the grading
    
        # Interpolate the points between p1 and p2 using the computed t
        p1 = np.array(p1)
        p2 = np.array(p2)
        if grading < 1 :
            positions = p1 * t[:, None] + p2 * (1 - t[:, None])
            positions = positions[::-1]
        else:
            positions = p1 * (1 - t[:, None]) + p2 * t[:, None]
        
        return positions

    def _geometric_spacing(self, p1, p2, n, grading):
        """
        Generates points using geometric spacing between p1 and p2 with grading.
        Uses interpolation factors similar to _interpolate_points.
        """
        t = np.linspace(0, 1, n + 1)  # Linear interpolation factors
        
        if grading < 1:
            coeff = 1/grading
        else:
            coeff = grading
            
        # Apply grading to the interpolation factors (geometric progression)
        t = t ** coeff  # Apply the geometric progression to the interpolation factors
        
        t = t / t[-1]  # Normalize the grading
    
        # Interpolate the points between p1 and p2 using the computed t
        p1 = np.array(p1)
        p2 = np.array(p2)
        if grading < 1 :
            positions = p1 * t[:, None] + p2 * (1 - t[:, None])
            positions = positions[::-1]
        else:
            positions = p1 * (1 - t[:, None]) + p2 * t[:, None]
        
        return positions

    # def _linear_spacing(self, p1, p2, vector, distance, n, grading):
    #     """
    #     Generates points using linear spacing between p1 and p2.
    #     """
    #     vector = vector / np.linalg.norm(vector)
    #     x0 = 2 * distance / ((n - 1) * (grading + 1))
    #     positions = np.zeros((n, 3), dtype=float)
    #     positions[0] = p1
    #     positions[-1] = p2

    #     for i in range(1, n - 1):
    #         size = x0 + (i - 1) * (grading - 1) * x0 / (n - 2)
    #         positions[i] = positions[i - 1] + size * vector

    #     return positions

    # def _geometric_spacing(self, p1, p2, vector, distance, n, grading):
    #     """
    #     Generates points using geometric spacing between p1 and p2.
    #     """
    #     vector = vector / np.linalg.norm(vector)
    #     alpha = np.exp(np.log(grading) / (n - 1))
    #     x0 = distance * (1 - alpha) / (1 - alpha ** (n - 1))
    #     positions = np.zeros((n, 3), dtype=float)
    #     positions[0] = p1
    #     positions[-1] = p2

    #     for i in range(1, n - 1):
    #         size = x0 * (alpha ** (i - 1))
    #         positions[i] = positions[i - 1] + size * vector

    #     return positions

    def _compute_ordered_points(self):
        """
        Compute self.points from the unstructured grid (self._ugrid) by ordering the points
        according to the connectivity of the line cells. The points will be arranged from the
        starting point to the ending point of the polyline.
        """
        ugrid = self._ugrid
        vtk_points = ugrid.GetPoints()
        n_points = vtk_points.GetNumberOfPoints()
    
        # Build a connectivity dictionary: point ID -> list of connected point IDs
        connectivity = {i: [] for i in range(n_points)}
        cell_array = ugrid.GetCells()
        cell_array.InitTraversal()
        id_list = vtk.vtkIdList()
        while cell_array.GetNextCell(id_list):
            if id_list.GetNumberOfIds() == 2:
                id0 = id_list.GetId(0)
                id1 = id_list.GetId(1)
                connectivity[id0].append(id1)
                connectivity[id1].append(id0)
        
        # Find endpoints: points with exactly one neighbor.
        endpoints = [pid for pid, neighbors in connectivity.items() if len(neighbors) == 1]
        # Choose the first element created (smallest ID) among the endpoints as the start point.
        start = min(endpoints) if endpoints else 0
    
        # Traverse the connectivity starting at the identified start point
        ordered_ids = []
        visited = set()
        current = start
        while True:
            ordered_ids.append(current)
            visited.add(current)
            # Select the next neighbor that hasn't been visited
            next_candidates = [nb for nb in connectivity[current] if nb not in visited]
            if not next_candidates:
                break
            current = next_candidates[0]
    
        # If the contour is closed (i.e. no endpoints) and the first and last points differ,
        # append the starting point to the end to close the loop.
        if not endpoints and ordered_ids and ordered_ids[0] != ordered_ids[-1]:
            ordered_ids.append(start)
        
        # Update self.points with the coordinates ordered according to the connectivity
        points = []
        for pid in ordered_ids:
            pt = vtk_points.GetPoint(pid)
            points.append(np.array(pt))
        return points


    def get_points(self):
        """
        Returns the list of points in the line.
        """
        return self._compute_ordered_points()

    def get_start_point(self):
        """
        Returns the start point of the line.
        """
        return self._compute_ordered_points()[0]

    def get_end_point(self):
        """
        Returns the end point of the line.
        """
        return self._compute_ordered_points()[-1]

    def copy(self):
        """
        Creates a copy of the current Line object with the same parameters.
        """
        p0=Point(0,0,0)
        p1=Point(1,0,0)
        new_line = Line(p0,p1, n=1)
        new_ugrid = vtk.vtkUnstructuredGrid()
        new_ugrid.DeepCopy(self._ugrid)
        new_line._ugrid = new_ugrid
        new_line.pid = self.pid
        new_line.color = self.color
        return new_line

    def reverse_orientation(self):
        """
        Reverses the orientation of this Line and updates its connectivity.
        """
        points = self._compute_ordered_points()
        points = points[::-1].copy()
        vtk_points = vtk.vtkPoints()
        num_points = len(points)
        vtk_points.SetNumberOfPoints(num_points)
        for i, pt in enumerate(points):
            vtk_points.SetPoint(i, pt)

        cell_array = vtk.vtkCellArray()
        for i in range(num_points - 1):
            line_cell = vtk.vtkLine()
            line_cell.GetPointIds().SetId(0, i)
            line_cell.GetPointIds().SetId(1, i + 1)
            cell_array.InsertNextCell(line_cell)

        self._ugrid.SetPoints(vtk_points)
        self._ugrid.SetCells(vtk.VTK_LINE, cell_array)
        self._ugrid.Modified()

    def __repr__(self):
        """
        Custom string representation for the Line class.
        """
        repr_str = super().__repr__()
        repr_str = repr_str.replace("Elem", "Line", 1)
        return repr_str

    @staticmethod
    def help():
        """
        Returns helpful information about the Line class and its methods.
        """
        help_text = """
Line Class
----------
A class to represent a 1D line mesh, constructed using two points (p1, p2).

Constructor:
-------------
\033[1;32mLine(p1, p2, n=None, size=None, grading=1, progression='linear', color=(0, 1, 0))\033[0m
  - \033[1;32mp1, p2\033[0m: Points or tuples specifying the start and end points of the line.
  - \033[1;32mn\033[0m: Number of elements along the line (ignored if size or size_at_start/size_at_end is provided).
  - \033[1;32msize\033[0m: Fixed element size (if specified, `n` is ignored).
  - \033[1;32mgrading\033[0m: Grading factor to control element size variation along the line.
  - \033[1;32mprogression\033[0m: Type of size variation, either 'linear' or 'geometric'.
  - \033[1;32mpid\033[0m: The part ID representing the mesh entity (default: 0).

Public Attributes:
------------------
\033[1;32mcolor\033[0m
    The RGB color associated with the element. The color is determined by the part ID (pid)
    and can be used for visualization purposes.                      

Public Methods:
---------------
\033[1;34mget_points()\033[0m
    Retrieve the list of points defining the line.
\033[1;34mget_start_point()\033[0m
    Get the starting point of the line.
\033[1;34mget_end_point()\033[0m
    Get the endpoint of the line.
\033[1;34mcopy()\033[0m
    Create a deep copy of the Line object.
\033[1;34mreverse_orientation()\033[0m
    Reverse the orientation of the line.

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
\033[1;34mmerge_duplicate_nodes(verbose=False, tol=1e-5)\033[0m
    Merge duplicate nodes in the line within a specified tolerance (default: 1e-5).
\033[1;34mpid\033[0m
    Accessor and setter for the part ID (pid). The pid uniquely identifies the element
    as a mesh entity with its own characteristics (e.g., material, function).
    
Usage Example:
---------------
  line = Line(p1, p2, n=10, color=(0, 0, 1))
  line.translate(1, 2, 0)
  line.reverse_orientation()
  print(line)
        """
        return help_text

# -------------------------------------------------------------------------
# 2) PolyLine Class (Derived from Line)
# -------------------------------------------------------------------------
class PolyLine(Line):
    """
    A class to represent a polyline, derived from the Line class.
    A polyline is a series of connected line segments, forming a continuous path.
    """

    def __init__(self, *elements, n=None, size=None, pid=0):
        """
        Constructor for the PolyLine class. This initializes a polyline based on multiple points or lines.

        If all provided elements are Point objects (or convertible to points), a polyline is created by connecting these points.
        If all provided elements are Line objects (or a single list of Line objects is provided), a polyline is constructed by fusing these lines.

        Keyword Args:
            n: Number of elements (ignored if size is provided or if elements are Line).
            size: Element size if a fixed element size is desired (ignored if elements are Line).
            pid: The part ID representing the mesh entity (default: 0).
        """
        # Check if a single argument is a list of Line objects.
        if len(elements) == 1 and isinstance(elements[0], list) and all(isinstance(item, Line) for item in elements[0]):
            lines = elements[0]
        # If all provided elements are Line instances, use them directly.
        elif all(isinstance(el, Line) for el in elements):
            lines = list(elements)
        else:
            if len(elements) < 2:
                raise ValueError("At least two points are required to form a polyline.")
            
            # Store points as numpy arrays (or as Point objects)
            points = [p.coords if isinstance(p, Point) else np.array(p) for p in elements]
            
            # Create a line between each pair of consecutive points
            lines = []
            for i in range(len(points) - 1):
                # Create a Line between each pair of points and add it to the lines list
                line = Line(points[i], points[i + 1], n=n, size=size, grading=1, progression='linear', pid=pid)
                lines.append(line)


        # Call the constructor of the parent (Line), but we manage the points ourselves
        Elem.__init__(self, pid=pid)
        
        # Generate the unstructured grid based on the lines
        self._build_ugrid(lines)

    def _build_ugrid(self, lines):
        """
        Creates an unstructured grid from the list of lines (self.lines) without duplicate nodes.
        This method ensures that all points in the polyline are unique and mapped correctly.
        """
        all_points = []
        point_map = {}

        # Collect all unique points and map them to unique indices
        for line in lines:
            for pt in line.get_points():
                pt_tuple = tuple(pt)  # Convert to tuple to use as a key in point_map
                if pt_tuple not in point_map:
                    point_map[pt_tuple] = len(all_points)
                    all_points.append(pt)

        # Create vtkPoints from the unique points
        vtk_points = vtk.vtkPoints()
        vtk_points.SetNumberOfPoints(len(all_points))
        for i, pt in enumerate(all_points):
            vtk_points.SetPoint(i, pt)

        # Create vtkCellArray and add line cells to it
        cell_array = vtk.vtkCellArray()
        for line in lines:
            points = line.get_points()
            for i in range(len(points) - 1):
                id1 = point_map[tuple(points[i])]
                id2 = point_map[tuple(points[i + 1])]
                line_cell = vtk.vtkLine()
                line_cell.GetPointIds().SetId(0, id1)
                line_cell.GetPointIds().SetId(1, id2)
                cell_array.InsertNextCell(line_cell)

        # Set the points and cells for the unstructured grid
        self._ugrid.SetPoints(vtk_points)
        self._ugrid.SetCells(vtk.VTK_LINE, cell_array)

        clean_filter = vtk.vtkStaticCleanUnstructuredGrid()
        clean_filter.SetTolerance(_TOL) 
        clean_filter.SetInputData(self._ugrid)
        clean_filter.RemoveUnusedPointsOn()
        clean_filter.Update()
    
        self._ugrid=clean_filter.GetOutput()
        self._generate_pid_field()


    @staticmethod
    def help():
        """
        Returns helpful information about the PolyLine class and its methods.
        """
        help_text = """
PolyLine Class
--------------
A class to represent a polyline, which is a series of connected Line objects.

Constructor:
-------------
\033[1;32mPolyLine(*points, n=None, size=None, color=(0, 1, 0))\033[0m
  - \033[1;32mpoints\033[0m: A sequence of Point objects defining the polyline.
  - \033[1;32mn\033[0m: Number of elements (ignored if size is provided).
  - \033[1;32msize\033[0m: Element size for uniform segmentation.
  - \033[1;32mpid\033[0m: The part ID representing the mesh entity (default: 0). 

Public Attributes:
------------------
\033[1;32mcolor\033[0m
    The RGB color associated with the element. The color is determined by the part ID (pid)
    and can be used for visualization purposes.
                      

Inherited Methods:
---------------
\033[1;34mtranslate(dx, dy, dz)\033[0m
    Translate all points in the polyline by the vector (dx, dy, dz).
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
    Retrieve the underlying vtkUnstructuredGrid representation.
\033[1;34mmerge_duplicate_nodes(verbose=False, tol=1e-5)\033[0m
    Merge duplicate nodes in the polyline within the given tolerance.
\033[1;34mget_points()\033[0m
    Retrieve the list of points defining the polyline.
\033[1;34mget_start_point()\033[0m
    Return the starting point of the polyline.
\033[1;34mget_end_point()\033[0m
    Return the endpoint of the polyline.
\033[1;34mcopy()\033[0m
    Create a deep copy of the polyline.
\033[1;34mreverse_orientation()\033[0m
    Reverse the order of points in the polyline.
\033[1;34mpid\033[0m
    Accessor and setter for the part ID (pid). The pid uniquely identifies the element
    as a mesh entity with its own characteristics (e.g., material, function).
    
Usage Example:
---------------
  polyline = PolyLine(p1, p2, p3, n=10, color=(1, 0, 0))
  polyline.translate(1, 0, 0)
  polyline.reverse_orientation()
  print(polyline.get_start_point(), polyline.get_end_point())                
        """
        return help_text

    def __repr__(self):
        """
        Custom string representation for the PolyLine class.
        """
        repr_str = super().__repr__()
        repr_str = repr_str.replace("Line", "PolyLine", 1)
        return repr_str

# -------------------------------------------------------------------------
# 3) Arc Class
# -------------------------------------------------------------------------
class Arc(PolyLine):
    """
    Represents an arc in 3D space, constructible via various class methods.

    The arc is defined by seven parameters:
      (center, radius, angle_start, angle_end, normal, n, pid)
    """

    # --------------------------------------------------------------------------
    # Core Constructor: from center, radius, start and end angles, and normal.
    # --------------------------------------------------------------------------
    @classmethod
    def from_center_angles(cls, center=None, radius=None, angle_start=None,
                           angle_end=None, n=None, size=None,
                           plane_normal=(0, 0, 1), pid=0):
        """
        Create an Arc from a center, radius, start/end angles, and plane normal.

        Args:
            center: 3D coordinates of the arc's center.
            radius: Scalar radius of the arc.
            angle_start: Starting angle in radians.
            angle_end: Ending angle in radians.
            n: Number of segments.
            size: Size of each segment (used to compute n if n is None).
            plane_normal: Normal vector of the plane (default: (0, 0, 1)).
            pid: The part ID representing the mesh entity (default: 0).

        Returns:
            An instance of Arc.
        """
        return cls(center, radius, angle_start, angle_end,
                   plane_normal, n, size, pid)

    # --------------------------------------------------------------------------
    # Generator: Create an Arc from three non-collinear points.
    # --------------------------------------------------------------------------
    @classmethod
    def from_3_points(cls, p0=None, p1=None, p2=None, n=None, size=None,
                      pid=0):
        """
        Create an Arc that passes through three non-collinear 3D points.

        The arc is defined from p0 to p2 (passing through p1 in a counter-clockwise
        direction as viewed from the side of the computed normal).

        Args:
            p0: First point (3D).
            p1: Second point (3D).
            p2: Third point (3D).
            n: Number of segments.
            size: Size of each segment (used to compute n if n is None).
            pid: The part ID representing the mesh entity (default: 0).

        Returns:
            An instance of Arc.
        """
        p0_arr = to_array(p0)
        p1_arr = to_array(p1)
        p2_arr = to_array(p2)

        # Compute the plane normal via cross product.
        v01 = p1_arr - p0_arr
        v02 = p2_arr - p0_arr
        normal = np.cross(v01, v02)
        norm_len = np.linalg.norm(normal)
        if norm_len < 1e-14:
            raise ValueError("Points are collinear or too close. No unique arc can be formed.")
        normal = normalize(normal)

        # Build local 2D coordinate system.
        u, v = cls._get_local_basis(normal)

        def to_local(P):
            """Convert a 3D point to local 2D coordinates with origin at p0_arr."""
            Q = P - p0_arr
            return np.array([np.dot(Q, u), np.dot(Q, v)], dtype=float)

        p0_2d = to_local(p0_arr)  # Expected to be [0, 0]
        p1_2d = to_local(p1_arr)
        p2_2d = to_local(p2_arr)

        # Compute the 2D circumcenter from p0_2d, p1_2d, p2_2d.
        x1, y1 = p1_2d
        x2, y2 = p2_2d
        d = 2 * (x1 * y2 - y1 * x2)
        if abs(d) < 1e-14:
            raise ValueError("Points are collinear; cannot form unique arc.")
        xC = ((x1**2 + y1**2) * y2 - (x2**2 + y2**2) * y1) / d
        yC = ((x2**2 + y2**2) * x1 - (x1**2 + y1**2) * x2) / d

        center_3D = p0_arr + xC * u + yC * v
        radius = np.linalg.norm(center_3D - p0_arr)

        def angle_of_point_2d(x, y):
            return math.atan2(y - yC, x - xC)

        a0 = angle_of_point_2d(p0_2d[0], p0_2d[1])
        a1 = angle_of_point_2d(p1_2d[0], p1_2d[1])
        a2 = angle_of_point_2d(p2_2d[0], p2_2d[1])

        def ccw_angle_diff(start, end):
            diff = end - start
            while diff < 0:
                diff += 2 * math.pi
            return diff

        total_diff = ccw_angle_diff(a0, a2)

        def in_ccw_range(th, start, end):
            def norm(x):
                while x < 0:
                    x += 2 * math.pi
                while x >= 2 * math.pi:
                    x -= 2 * math.pi
                return x
            th_n = norm(th)
            s_n = norm(start)
            e_n = norm(end)
            if s_n <= e_n:
                return s_n <= th_n <= e_n
            else:
                return not (e_n < th_n < s_n)

        if not in_ccw_range(a1, a0, a0 + total_diff):
            total_diff -= 2 * math.pi

        angle_start = a0
        angle_end = a0 + total_diff

        return cls(center_3D, radius, angle_start, angle_end,
                   normal, n, size, pid)

    # --------------------------------------------------------------------------
    # Generator: Create an Arc from a center, radius, and two boundary points.
    # --------------------------------------------------------------------------
    @classmethod
    def from_center_2points(cls, center=None, radius=None, pA=None, pB=None,
                            n=None, size=None, use_short_arc=True,
                            pid=0):
        """
        Create an Arc from a center, radius, and two points on the circle.

        The arc goes from pA to pB in a counter-clockwise direction relative
        to the plane defined by the cross product of (pA - center) and (pB - center).
        If use_short_arc is True, the smaller arc is chosen.

        Args:
            center: 3D center of the arc.
            radius: Provided radius (recomputed using center and pA).
            pA: First boundary point on the arc.
            pB: Second boundary point on the arc.
            n: Number of segments.
            size: Size of each segment (used to compute n if n is None).
            use_short_arc: If True, use the shorter arc.
            pid: The part ID representing the mesh entity (default: 0).
            
        Returns:
            An instance of Arc.
        """
        center_arr = to_array(center)
        a_arr = to_array(pA)
        b_arr = to_array(pB)
        radius = np.linalg.norm(center_arr - a_arr)

        vCA = a_arr - center_arr
        vCB = b_arr - center_arr
        normal = np.cross(vCA, vCB)
        if np.linalg.norm(normal) < 1e-14:
            raise ValueError("pA and pB are collinear with center or identical. No unique arc.")
        normal = normalize(normal)

        u, v = cls._get_local_basis(normal)

        def local_angle_of_point_3d(P):
            Px = np.dot(P - center_arr, u)
            Py = np.dot(P - center_arr, v)
            return math.atan2(Py, Px)

        angleA = local_angle_of_point_3d(a_arr)
        angleB = local_angle_of_point_3d(b_arr)

        def ccw_diff(a1, a2):
            d = a2 - a1
            while d < 0:
                d += 2 * math.pi
            return d

        ccw_span = ccw_diff(angleA, angleB)
        if not use_short_arc:
            ccw_span -= 2 * math.pi

        angle_start = angleA
        angle_end = angleA + ccw_span

        return cls(center_arr, radius, angle_start, angle_end,
                   normal, n, size, pid)

    # --------------------------------------------------------------------------
    # Generator: Create an Arc from a center, a boundary point, and an angle.
    # --------------------------------------------------------------------------
    @classmethod
    def from_center_1point(cls, center=None, p0=None, angle=None, n=None,
                           size=None, plane_normal=(0, 0, 1), pid=0):
        """
        Create an Arc from a center, one boundary point, and an angle.

        The arc starts at p0 and extends counter-clockwise by the given angle
        (in radians). The plane of the arc is determined by plane_normal.

        Args:
            center: 3D center of the arc.
            p0: Boundary point on the arc.
            angle: Angle (in radians) through which the arc extends.
            n: Number of segments.
            size: Size of each segment (used to compute n if n is None).
            plane_normal: Normal vector of the plane (default: (0, 0, 1)).
            pid: The part ID representing the mesh entity (default: 0).

        Returns:
            An instance of Arc.
        """
        center_arr = to_array(center)
        p0_arr = to_array(p0)
        radius = np.linalg.norm(center_arr - p0_arr)

        def angle_in_plane(p):
            u, v = cls._get_local_basis(np.array(plane_normal, dtype=float))
            local_point = p - center_arr
            return math.atan2(np.dot(local_point, v), np.dot(local_point, u))

        angle_start = angle_in_plane(p0_arr)
        angle_end = angle_start + angle

        return cls(center_arr, radius, angle_start, angle_end,
                   plane_normal, n, size, pid)

    # --------------------------------------------------------------------------
    # Initialization and Representation
    # --------------------------------------------------------------------------
    def __init__(self, center, radius, angle_start, angle_end, normal,
                 n, size, pid):
        """
        Master constructor. Usually called by one of the generator methods.

        Args:
            center: 3D center of the arc.
            radius: Radius of the arc.
            angle_start: Start angle in radians.
            angle_end: End angle in radians.
            normal: Normal vector defining the arc's plane.
            n: Number of segments.
            size: Segment size (used to compute n if n is None).
            pid: The part ID representing the mesh entity (default: 0).
        """
        segments = self._discretize(radius, angle_start, angle_end, n, size)
        points = self._create_3d_arc_points(center, normal, radius, angle_start,
                                            angle_end, segments)
        super().__init__(*points, n=1, pid=pid)

    def __repr__(self):
        repr_str = super().__repr__()
        return repr_str.replace("PolyLine", "Arc", 1)

    # --------------------------------------------------------------------------
    # Private Methods
    # --------------------------------------------------------------------------
    @staticmethod
    def _get_local_basis(normal):
        """
        Return an orthonormal basis (u, v) for the plane perpendicular to 'normal'.

        Args:
            normal: A 3D vector representing the normal.

        Returns:
            A tuple (u, v) where both u and v are normalized and span the plane.
        """
        test = np.array([1, 0, 0], dtype=float)
        if abs(np.dot(test, normal)) > 0.99:
            test = np.array([0, 1, 0], dtype=float)
        u = normalize(np.cross(normal, test))
        v = normalize(np.cross(normal, u))
        return u, v

    def _create_3d_arc_points(self, center, normal, radius, angle_start,
                              angle_end, n):
        """
        Generate a list of 3D points along the arc.

        Args:
            center: 3D center of the arc.
            normal: Normal vector defining the arc's plane.
            radius: Radius of the arc.
            angle_start: Start angle in radians.
            angle_end: End angle in radians.
            n: Number of segments.

        Returns:
            A list of Point instances representing the arc.
        """
        center = to_array(center)
        normal = normalize(to_array(normal))
        u, v = self._get_local_basis(normal)

        angles = np.linspace(angle_start, angle_end, n) #n+1 for n is element and nodes are made
        points = []
        for a in angles:
            local_pt = radius * (math.cos(a) * u + math.sin(a) * v)
            world_pt = center + local_pt
            points.append(Point(world_pt[0], world_pt[1], world_pt[2]))
        return points

    def _discretize(self, radius, angle_start, angle_end, n, size):
        """
        Determine the number of segments for the arc discretization.

        Args:
            radius: Radius of the arc.
            angle_start: Start angle in radians.
            angle_end: End angle in radians.
            n: Predefined number of segments.
            size: Desired segment length (if n is None).

        Returns:
            An integer number of segments.
        """
        angle_span = abs(angle_end - angle_start)
        arc_length = radius * angle_span

        if n is not None:
            return n
        else:
            if size is not None:
                if size <= 0:
                    raise ValueError("size must be positive if used to compute n.")
                return max(1, math.ceil(arc_length / size))
            else:
                return 1

    @classmethod
    def help(cls):
        """
        Return help text describing the Arc class and its usage.
        """
        help_text = """
Arc Class
--------------
A class to represent an Arc of circle as a polyline.

Constructor:
-------------
\033[1;32mArc(*args, **kwargs)\033[0m
  Constructs an Arc using one of the following class methods:

\033[1;32mfrom_center_angles(center, radius, theta_start, theta_end, n=None, size=None, plane_normal=(0, 0, 1), color=(0, 1, 0))\033[0m
  - \033[1;32mcenter\033[0m: 3D center of the arc.
  - \033[1;32mradius\033[0m: Radius (scalar).
  - \033[1;32mtheta_start\033[0m: Starting angle (radians).
  - \033[1;32mtheta_end\033[0m: Ending angle (radians).
  - \033[1;32mplane_normal\033[0m: Normal of the plane (default: (0, 0, 1)).
  - \033[1;32mn\033[0m: Number of segments (optional).
  - \033[1;32msize\033[0m: Segment length (optional, used if n is None).
  - \033[1;32mpid\033[0m: The part ID (pid) representing the mesh entity (default: 0). 

\033[1;32mfrom_3_points(p0, p1, p2, n=None, size=None, color=(0, 1, 0))\033[0m
  - \033[1;32mp0, p1, p2\033[0m: Three non-collinear 3D points.
  - \033[1;32mn\033[0m: Number of segments (optional).
  - \033[1;32msize\033[0m: Segment length (optional).
  - \033[1;32mpid\033[0m: The part ID (pid) representing the mesh entity (default: 0). 

\033[1;32mfrom_center_2points(center, radius, pA, pB, n=None, size=None, use_short_arc=True, color=(0, 1, 0))\033[0m
  - \033[1;32mcenter\033[0m: 3D center of the arc.
  - \033[1;32mradius\033[0m: Radius (scalar; recalculated from center and pA).
  - \033[1;32mpA, pB\033[0m: Two boundary points on the arc.
  - \033[1;32mn\033[0m: Number of segments (optional).
  - \033[1;32msize\033[0m: Segment length (optional).
  - \033[1;32muse_short_arc\033[0m: If True, uses the shorter arc.
  - \033[1;32mpid\033[0m: The part ID (pid) representing the mesh entity (default: 0). 

\033[1;32mfrom_center_1point(center, p0, theta, n=None, size=None, plane_normal=(0, 0, 1), color=(0, 1, 0))\033[0m
  - \033[1;32mcenter\033[0m: 3D center of the arc.
  - \033[1;32mp0\033[0m: A boundary point on the arc.
  - \033[1;32mtheta\033[0m: Angle (radians) to extend the arc.
  - \033[1;32mn\033[0m: Number of segments (optional).
  - \033[1;32msize\033[0m: Segment length (optional).
  - \033[1;32mplane_normal\033[0m: Normal of the plane (default: (0, 0, 1)).
  - \033[1;32mpid\033[0m: The part ID (pid) representing the mesh entity (default: 0). 

Public Attributes:
------------------
\033[1;32mcolor\033[0m
    The RGB color associated with the element. The color is determined by the part ID (pid)
    and can be used for visualization purposes.                      

Inherited Methods:
---------------
\033[1;34mtranslate(dx, dy, dz)\033[0m
    Translate all points in the polyline by the vector (dx, dy, dz).
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
    Retrieve the underlying vtkUnstructuredGrid representation.
\033[1;34mmerge_duplicate_nodes(verbose=False, tol=1e-5)\033[0m
    Merge duplicate nodes in the polyline within the given tolerance.
\033[1;34mget_points()\033[0m
    Retrieve the list of points defining the polyline.
\033[1;34mget_start_point()\033[0m
    Return the starting point of the polyline.
\033[1;34mget_end_point()\033[0m
    Return the endpoint of the polyline.
\033[1;34mcopy()\033[0m
    Create a deep copy of the polyline.
\033[1;34mreverse_orientation()\033[0m
    Reverse the order of points in the polyline.
\033[1;34mpid\033[0m
    Accessor and setter for the part ID (pid). The pid uniquely identifies the element
    as a mesh entity with its own characteristics (e.g., material, function).
    
Usage Example:
---------------
  arc = Arc.from_center_angles((0, 0, 0), 5, 0, 3.14, n=10)
  arc.translate(1, 2, 3)
  arc.rotate('z', 45)
  print(arc)
"""

        return help_text

# -------------------------------------------------------------------------
# 4) Circle Class
# -------------------------------------------------------------------------
class Circle(PolyLine):
    """
    A class to represent a circle in 3D space, derived from PolyLine.
    The circle is defined by its center, radius, and the normal vector to the plane.
    """

    def __init__(self, center=(0, 0, 0), radius=1, normal=(0, 0, 1), n=None, size=None, pid=0):
        """
        Constructor to initialize a circle using its center, radius, and normal.

        center: 3D coordinates of the center of the circle (default: (0, 0, 0)).
        radius: Scalar radius of the circle (default: 1).
        normal: Normal vector defining the plane of the circle (default: (0, 0, 1)).
        n: Number of segments (optional).
        size: Size of each segment (optional, used to compute n if n is None).
        pid: The part ID representing the mesh entity (default: 0).
        """
        # Generate the circle points using the given parameters
        center = to_array(center)
        radius = radius
        normal = normalize(np.array(normal))

        # Generate points based on the number of segments or segment size
        n_segments = self._discretize(radius, n, size)
        points = self._generate_circle_points(center, normal, radius, n_segments)

        # Call parent constructor (PolyLine)
        super().__init__(*points, n=1, pid=pid)
        #self.merge_duplicate_nodes(verbose=False)

    def _generate_circle_points(self, center, normal, radius, n):
        """
        Generate points for the circle.

        center: 3D center of the circle.
        normal: Normal vector defining the plane.
        radius: Radius of the circle.
        n: Number of segments.

        Returns:
            A list of 3D points representing the circle.
        """
        # Create an orthonormal basis for the plane
        u, v = self._get_local_basis(normal)
        # Generate points along the circle's circumference
        angles = np.linspace(0, 2 * np.pi, n+1)
        points = []
        for angle in angles:
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            point = center + x * u + y * v
            points.append(Point(point[0], point[1], point[2]))
        return points

    def _discretize(self, radius, n, size):
        """
        Determine the number of segments for discretizing the circle.

        radius: Radius of the circle.
        n: Predefined number of segments.
        size: Desired segment size (used to compute n if n is None).

        Returns:
            The number of segments.
        """
        if n is not None:
            return n
        elif size is not None:
            circumference = 2 * np.pi * radius
            return max(1, int(circumference // size))
        else:
            return 1

    @staticmethod
    def _get_local_basis(normal):
        """
        Return an orthonormal basis (u, v) for the plane perpendicular to the given normal vector.

        normal: A 3D vector representing the normal of the plane.

        Returns:
            A tuple (u, v) representing the orthonormal basis for the plane.
        """
        # Find a vector orthogonal to the normal
        test = np.array([1, 0, 0], dtype=float)
        if abs(np.dot(test, normal)) > 0.99:
            test = np.array([0, 1, 0], dtype=float)
        u = normalize(np.cross(normal, test))
        v = np.cross(normal, u)
        return u, v

    def __repr__(self):
        repr_str = super().__repr__()
        return repr_str.replace("PolyLine", "Circle", 1)

    @classmethod
    def help(cls):
        """
        Returns helpful information about the Circle class and its methods.
        """
        help_text = """
Circle Class
-------------
A class to represent a circle in 3D space, defined by its center, radius, and normal.

Constructor:
-------------
\033[1;32mCircle(center=(0, 0, 0), radius=1, normal=(0, 0, 1), n=None, size=None, color=(0, 1, 0))\033[0m
  - \033[1;32mcenter\033[0m: 3D coordinates of the center of the circle (default: (0, 0, 0)).
  - \033[1;32mradius\033[0m: Scalar radius of the circle (default: 1).
  - \033[1;32mnormal\033[0m: Normal vector defining the plane of the circle (default: (0, 0, 1)).
  - \033[1;32mn\033[0m: Number of segments (optional).
  - \033[1;32msize\033[0m: Size of each segment (optional, used to compute n if n is None).
  - \033[1;32mpid\033[0m: The part ID (pid) representing the mesh entity (default: 0). 

Public Attributes:
------------------
\033[1;32mcolor\033[0m
    The RGB color associated with the element. The color is determined by the part ID (pid)
    and can be used for visualization purposes.
                      

Inherited Methods:
---------------
\033[1;34mtranslate(dx, dy, dz)\033[0m
    Translate all points in the polyline by the vector (dx, dy, dz).
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
    Retrieve the underlying vtkUnstructuredGrid representation.
\033[1;34mmerge_duplicate_nodes(verbose=False, tol=1e-5)\033[0m
    Merge duplicate nodes in the polyline within the given tolerance.
\033[1;34mget_points()\033[0m
    Retrieve the list of points defining the polyline.
\033[1;34mget_start_point()\033[0m
    Return the starting point of the polyline.
\033[1;34mget_end_point()\033[0m
    Return the endpoint of the polyline.
\033[1;34mcopy()\033[0m
    Create a deep copy of the polyline.
\033[1;34mreverse_orientation()\033[0m
    Reverse the order of points in the polyline.
\033[1;34mpid\033[0m
    Accessor and setter for the part ID (pid). The pid uniquely identifies the element
    as a mesh entity with its own characteristics (e.g., material, function).
               
Usage Example:
---------------
  circle = Circle(center=(0, 0, 0), radius=2, normal=(0, 0, 1), n=50, color=(1, 0, 0))
  circle.translate(1, 2, 0)
  circle.rotate('z', 30)
  print(circle.get_points())
"""
        return help_text


