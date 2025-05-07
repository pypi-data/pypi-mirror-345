#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 10/02/2025
Last modified on 10/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module provides utility functions for mesh manipulation using vtk and pybmesh.
It includes functions for reducing mesh geometry levels, extracting points, edges, and surfaces 
from meshes, and saving vtkUnstructuredGrid data to VTK files. The reduction of mesh levels can 
be applied to 1D, 2D, and 3D meshes, and the functions work by extracting geometry from existing 
mesh structures.
"""

import vtk
import numpy as np
#import awkward as ak
import multiprocessing
from scipy.spatial import ConvexHull
from sklearn.cluster import KMeans
from concurrent.futures import ProcessPoolExecutor, as_completed
from pybmesh.geom.mesh import Elem
from pybmesh.geom.d0 import Point
from pybmesh.geom.d1 import Line
from pybmesh.geom.d2 import Surface
from pybmesh.geom.d3 import Volume
from pybmesh.utils.constants import _TOL
from pybmesh.utils.detection import auto_reduce_dim
from pybmesh.utils.maths import get_rotation_matrix, ragged_to_matrix, matrix_to_ragged
from pybmesh.utils.vtkquery import nbEl, findPoints, findElems
from pybmesh.utils.vtkcorrection import regen
from pybmesh.io.vtk2numpy import  vtk_to_numpy_connectivity, mesh_to_numpy_connectivity, \
                                    numpy_to_vtk_connectivity

def save_to_vtk(mesh, filename):
    """
    Write a vtkUnstructuredGrid to a VTK XML file.
    
    Parameters:
        mesh (Elem): The mesh object containing the vtkUnstructuredGrid to write.
        filename (str): The filename where the VTK data will be saved.
    """
    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetFileName(filename)
    if isinstance(mesh,Elem):
        writer.SetInputData(mesh.get_vtk_unstructured_grid())
    else:
        writer.SetInputData(mesh)   
    writer.Write()
    print(f"VTK file written to: {filename}")

def translate(mesh, vector, pid=None):
    """
    Translate the mesh by the given vector and return a new translated mesh.
    
    Parameters:
        mesh (Elem): The mesh to be translated.
        vector (tuple): The translation vector (dx, dy, dz).
        pid (int, optional): A new part ID for the translated mesh (default: None, keeps original).
    
    Returns:
        Elem: A new mesh object with translated points.
    """
    newm = mesh.copy()
    newm.translate(*vector)
    if pid is not None:
        newm.pid = pid
    return newm

def rotate(mesh, center=None, axis=None, angle=None, angles=None, pA=None, pB = None, pid = None):
    """
    Rotate the mesh by the given parameters and return a new rotated mesh.
    
    Parameters:
        mesh (Elem): The mesh to be rotated.
        center (tuple, optional): The center of rotation (default is the origin (0, 0, 0)).
        axis (tuple or str, optional): The rotation axis (x, y, z) as a tuple or a string ("x", "y", "z").
        angle (float, optional): The rotation angle in degrees around the specified axis (default: None).
        angles (tuple, optional): A tuple of three angles for rotation along the X, Y, and Z axes, respectively (default: None).
        pA (Point, optional): A point defining the start of the rotation axis (used with `pB` to define the axis, default: None).
        pB (Point, optional): A point defining the end of the rotation axis (used with `pA` to define the axis, default: None).
        pid (int, optional): A new part ID for the rotated mesh (default: None, keeps original).
    
    Returns:
        Elem: A new mesh object with rotated points.
    """
    newm = mesh.copy()
    newm.rotate(center=center, axis=axis, angle=angle, angles=angles, pA=pA, pB = pB)
    if pid is not None:
        newm.pid = pid
    return newm

def syme(mesh, center=None, plane=None, pA=None, pB=None, pC=None, line=None, pid=None):
    """
    Reflect the mesh across the specified plane or axis and return a new reflected mesh.
    
    Parameters:
        mesh (vtk.vtkPolyData): The mesh to be reflected.
        center (tuple, optional): The center of reflection.
        plane (str, optional): The plane of reflection ('xy', 'yz', 'zx').
        pA (tuple, optional): A point defining reflection plane (used with `pA` and `pB` to define the plane).
        pB (tuple, optional): A point defining reflection plane (used with `pA` and `pB` to define the plane).
        pC (tuple, optional): A point defining reflection plane (used with `pA` and `pB` to define the plane).
        line (Line, optional): A line object defining the reflection plane.
        pid (int, optional): A new part ID for the reflected mesh (default: None, keeps original).
    
    Returns:
        vtk.vtkPolyData: A new mesh object with reflected points.
        
    Exemples:
        v1 = syme(v0, plane='yz', pid=10)
        v2 = syme(v0, pA=pA, pB=pB, pC=pC, pid=5)
        v3 = syme(v0, pA=pA, line=line)
    """
    if line is not None:
        # Extract points from the line object
        pA = line.get_start_point()
        pB = line.get_end_point()
        if pA is not None: pC = pA
        elif pB is not None: pC = pB
        elif pC is None : raise ValueError("One betwen pA, pB  and pC must be provided to define the reflection plane.")
   
    if plane is not None:
        if center is None :
            center = (0,0,0)
        pA = center
        if plane == 'xy':
            pB = (center[0] + 1, center[1], center[2])  # Example: pB is 1 unit along the x-axis from pA
            pC = (center[0], center[1] + 1, center[2])  # Example: pC is 1 unit along the z-axis from pA
        elif plane == 'yz':
            pB = (center[0], center[1] + 1, center[2])  # Example: pB is 1 unit along the y-axis from pA
            pC = (center[0], center[1], center[2] + 1)  # Example: pC is 1 unit along the z-axis from pA
        elif plane == 'zx':
            pB = (center[0] + 1, center[1], center[2])  # Example: pB is 1 unit along the x-axis from pA
            pC = (center[0], center[1], center[2] + 1)  # Example: pC is 1 unit along the y-axis from pA
        else:
            raise ValueError("Invalid plane specified. Choose from 'xy', 'yz', or 'zx'.")
        
   
    
    if pA is not None and isinstance(pA,Elem): pA = pA.coords[0]
    if pB is not None and isinstance(pB,Elem): pB = pB.coords[0]
    if pC is not None and isinstance(pC,Elem): pC = pC.coords[0]
    
    if pA is not None and pB is not None and pC is not None:
        pA = np.array(pA)
        pB = np.array(pB)
        pC = np.array(pC)
        AB = pB - pA
        AC = pC - pA
        normal = np.cross(AB, AC)
        normal_magnitude = np.linalg.norm(normal)
        if normal_magnitude == 0:
            raise ValueError("pA, pB  and pC are collinear; the normal vector cannot be computed.")
        normal_unit = normal / normal_magnitude
    else:
        raise ValueError("Both pA, pB  and pC must be provided to define the reflection plane.")
    
    # Compute the reflection matrix
    a, b, c = normal_unit 
    x0, y0, z0 = pA  # Using pA as a point on the plane
    d = -(a * x0 + b * y0 + c * z0)
    
    reflection_matrix = np.array([
        [1 - 2 * a**2, -2 * a * b, -2 * a * c, -2 * a * d],
        [-2 * a * b, 1 - 2 * b**2, -2 * b * c, -2 * b * d],
        [-2 * a * c, -2 * b * c, 1 - 2 * c**2, -2 * c * d],
        [0, 0, 0, 1]
    ])
    
    # Create a vtkMatrix4x4 from the reflection matrix
    vtk_matrix = vtk.vtkMatrix4x4()
    for i in range(4):
        for j in range(4):
            vtk_matrix.SetElement(i, j, reflection_matrix[i, j])
    
    # Create a vtkTransform and set the reflection matrix
    transform = vtk.vtkTransform()
    transform.SetMatrix(vtk_matrix)
    
    # Apply the transformation to the mesh
    transform_filter = vtk.vtkTransformFilter()
    transform_filter.SetInputData(mesh.get_vtk_unstructured_grid())
    transform_filter.SetTransform(transform)
    transform_filter.Update()
    
    # Retrieve the reflected mesh
    reflected_mesh = transform_filter.GetOutput()
    

    # Define the mesh (replace with actual mesh creation)
    nmesh = mesh.copy()
    nmesh._set_vtk_unstructured_grid(reflected_mesh)


    if pid is None : pid = mesh.pid
    nmesh.pid = pid
    
    return nmesh

def scale(mesh, sx=1, sy=1, sz=1, center=None, pid=None):
    """
    Rotate the mesh by the factors (sx, sy, sz) about center point
    by the given parameters and return a new rotated mesh.

    Parameters:
        center (tuple): The center of rotation (default to center of mass).
        sx (float): Scaling factor along the X-axis.
        sy (float): Scaling factor along the Y-axis.
        sz (float): Scaling factor along the Z-axis.
    """
    newm = mesh.copy()
    newm.scale(center=center, sx=sx, sy=sy, sz=sz)
    if pid is not None:
        newm.pid = pid
    return newm

def fuse(mesh1, mesh2, pid = None, merge = True, tol = _TOL,  verbose = True):
    """
    Merges two Elem objects into a single unstructured grid, with options to merge duplicate nodes and control verbosity.
    
    Parameters:
    - mesh1 (Elem): The first Elem object to be merged.
    - mesh2 (Elem): The second Elem object to be merged.
    - pid (int, optional): Process ID to assign to the merged mesh. If None, defaults to the minimum pid of mesh1 and mesh2.
    - merge (bool, optional): Flag indicating whether to merge duplicate nodes. Defaults to True.
    - tol (float, optional): Tolerance for merging points. Default is _TOL (a predefined constant).
    - verbose (bool, optional): Flag to control verbosity. If True, prints detailed information about the merging process. Defaults to True.
    
    Returns:
    - Elem: A new Elem object containing the merged unstructured grid.
    
    Notes:
    - The function combines the unstructured grids of mesh1 and mesh2.
    - If 'merge' is set to True, duplicate nodes (points with coincident coordinates) are merged based on the specified tolerance.
    - Verbosity can be enabled to print the number of nodes and elements before and after merging, along with the count of merged nodes and elements.
    """
    # Append the second grid to the first
    append_filter = vtk.vtkAppendFilter()
    append_filter.AddInputData(mesh1.get_vtk_unstructured_grid())
    append_filter.AddInputData(mesh2.get_vtk_unstructured_grid())
    if merge:
        append_filter.MergePointsOn()
        append_filter.SetTolerance(tol)
    append_filter.Update()
    
    # Get the combined unstructured grid
    ugrid = append_filter.GetOutput()
    
    if verbose : 
        num_points_before = mesh1.get_vtk_unstructured_grid().GetNumberOfPoints() + mesh2.get_vtk_unstructured_grid().GetNumberOfPoints()
        num_points_after = ugrid.GetNumberOfPoints()
        print(f"{num_points_before - num_points_after} nodes were merged.")

    
    if pid is None : pid = min(mesh1.pid, mesh2.pid)
    for cls in (Point, Line, Surface, Volume):
        if isinstance(mesh1, cls) and isinstance(mesh2, cls):
            output = cls(pid=pid)
            break
    else:
        output = Elem(pid)
    output._set_vtk_unstructured_grid(ugrid)
    return output

def remove(mesh1, mesh2, pid=None):
    if nbEl(mesh2) < nbEl(mesh1):
        mesh1, mesh2 = mesh2, mesh1

    cell_mapping = findElems(mesh1, mesh2)
    cells_to_remove = set(cell_mapping.values())
    cells_to_remove = np.array(list(cells_to_remove), dtype=int)

    points, cells, types = mesh_to_numpy_connectivity(mesh2)
    cells_array = np.array(cells, dtype=object)

    # Create a mask that is True for cells to keep.
    filtered_mask = np.ones(len(cells_array), dtype=bool)
    filtered_mask[cells_to_remove] = False

    remaining_cells = cells_array[filtered_mask].tolist()
    remaining_types = np.array(types)[filtered_mask].tolist()

    # If no cells remain, create an empty unstructured grid with the original points.
    if len(remaining_cells) == 0:
        ug = vtk.vtkUnstructuredGrid()
        pts = vtk.vtkPoints()
        for pt in points:
            pts.InsertNextPoint(pt)
        ug.SetPoints(pts)
    else:
        ug = numpy_to_vtk_connectivity(points, remaining_cells, remaining_types)

    clean_filter = vtk.vtkStaticCleanUnstructuredGrid()
    clean_filter.SetInputData(ug)
    clean_filter.RemoveUnusedPointsOn()
    clean_filter.Update()

    omesh = mesh2.copy()
    omesh._set_vtk_unstructured_grid(clean_filter.GetOutput())
    omesh.pid = mesh2.pid
    return omesh

def get_closest_point(mesh, pt):
    """
    Find the closest point in the mesh to a given point.
    Uses vtkKdTree for fast nearest neighbor search.
    
    Parameters:
        mesh (Elem): The mesh to search within.
        pt (vtk.vtkVector3d or np.ndarray or Point): The point to search for the closest neighbor.
    
    Returns:
        Point: The closest point found in the mesh.
    
    Raises:
        ValueError: If the provided point is not in a recognized format.
    """
    # Ensure pt is in the correct format
    if isinstance(pt, vtk.vtkVector3d):
        # pt is already a vtkVector3d
        point_coords = pt
    elif isinstance(pt, (tuple, list)) and len(pt) == 3:
        # pt is a numpy array (size 3)
        point_coords = vtk.vtkVector3d(pt[0], pt[1], pt[2]) 
    elif isinstance(pt, np.ndarray) and pt.shape == (3,):
        # pt is a numpy array (size 3)
        point_coords = vtk.vtkVector3d(pt[0], pt[1], pt[2])
    elif hasattr(pt, 'coords') and len(pt.coords) == 1:
        # pt is a custom Point class (assuming pt.coords[0] is a 3-element list/array)
        point_coords = vtk.vtkVector3d(pt.coords[0][0], pt.coords[0][1], pt.coords[0][2])
    else:
        raise ValueError("The point must be a VTK_POINT, numpy array, or a Point instance with 3 coordinates.")


    # Get the points of the unstructured grid
    ugrid = mesh.get_vtk_unstructured_grid()
    

    point_locator = vtk.vtkPointLocator()
    point_locator.SetDataSet(ugrid)
    point_locator.BuildLocator()
    closest_point_id = point_locator.FindClosestPoint(point_coords)

    # Retrieve the coordinates of the closest point from the ugrid using the point ID
    closest_point_coords = ugrid.GetPoint(closest_point_id)

    return Point(*closest_point_coords)

def extract_point(mesh,criterion, pid = None):
    """
    Extracts a subset of points from the mesh based on the specified criterion.

    Parameters:
    - mesh: The mesh object containing the points to be extracted.
    - criterion: A dictionary specifying the extraction criterion. The dictionary should include:
        - "type": A string indicating the type of extraction. Possible values include:
            - "all" : Extract all points
            - "plane": Extract points within a specified distance to a plane.
            - "closest": Extract the point closest to a specified point.
            - "line": Extract points within a specified distance to a line.
            - "sphere": Extract points within a spherical shell.
            - "cylinder": Extract points within a cylindrical shell.
            - "box": Extract points within a specified box.
            - "id": Extract points with specified IDs.
            - "pid": Extract points from elements with specified point IDs.
            - "condition": Extract points that satisfy a specific condition function.
        - Additional keys specific to each criterion type:
            - For "all":
                - no additional key
            - For "plane":
                - "p1": Tuple representing the first point (x1, y1, z1) on the plane.
                - "p2": Tuple representing the second point (x2, y2, z2) on the plane.
                - "p3": Tuple representing the third point (x3, y3, z3) on the plane.
                - "distance": Float representing the maximum distance from the plane.
            - For "closest":
                - "point": Tuple representing the point (x, y, z) to find the closest point to.
            - For "line":
                - "p1": Tuple representing the first point (x1, y1, z1) on the line.
                - "p2": Tuple representing the second point (x2, y2, z2) on the line.
                - "distance": Float representing the maximum distance from the line.
            - For "sphere":
                - "center": Tuple representing the center point (xc, yc, zc) of the sphere.
                - "inner_radius": Float representing the inner radius of the spherical shell.
                - "outer_radius": Float representing the outer radius of the spherical shell.
            - For "cylinder":
                - "p1": Tuple representing the base center point (x1, y1, z1) of the cylinder.
                - "p2": Tuple representing a point (x2, y2, z2) on the axis of the cylinder.
                - "inner_radius": Float representing the inner radius of the cylindrical shell.
                - "outer_radius": Float representing the outer radius of the cylindrical shell.
            - For "box":
                - "min_point": Tuple representing the minimum corner point (xmin, ymin, zmin) of the box.
                - "max_point": Tuple representing the maximum corner point (xmax, ymax, zmax) of the box.
            - For "id":
                - "value": Integer, list, tuple, or generator of point IDs to extract.
            - For "pid":
                - "value": Integer, list, tuple, or generator of element point IDs to extract.
            - For "condition":
                - "function": A lambda function that takes a point (x, y, z) and returns a boolean indicating whether the point satisfies the condition.

    - pid: Optional; a unique identifier for the points to be extracted.

    Returns:
    - A new PointSet instance containing the extracted points.

    Examples:
    - Extract points within a plane at a distance of 0.5 units:
        plane_dict = {
            "type": "plane",
            "p1": (0, 0, 0),
            "p2": (1, 0, 0),
            "p3": (0, 1, 0),
            "distance": 0.5
        }
        points = extract_point(mesh, plane_dict)

    - Extract the point closest to (0.5, 0.75, 0.123):
        closest_dict = {
            "type": "closest",
            "point": (0.5, 0.75, 0.123)
        }
        point = extract_point(mesh, closest_dict)

    - Extract points within a spherical shell with inner radius 0.3 and outer radius 0.7:
        sphere_dict = {
            "type": "sphere",
            "center": (0.5, 0.5, 0),
            "inner_radius": 0.3,
            "outer_radius": 0.7
        }
        points = extract_point(mesh, sphere_dict)

    - Extract points within a box defined by min and max points:
        box_dict = {
            "type": "box",
            "min_point": (0, 0, -0.001),
            "max_point": (1, 1, 0.001)
        }
        points = extract_point(mesh, box_dict)

    - Extract points that satisfy a specific condition:
        condition_dict = {
            "type": "condition",
            "function": lambda p: (
                (-10 < p[0] < 10) &
                (-10 < p[1] < 10) &
                (-0.001 < p[2] < 0.5)
            )
        }
        points = extract_point(mesh, condition_dict)
    """
    if pid is None : pid = mesh.pid
    if criterion["type"] == "all":
        # Extract the point closest to the specified point
        points, _ , _ = mesh_to_numpy_connectivity(mesh)
        return Point(points, pid=pid)
    if criterion["type"] == "closest":
        # Extract the point closest to the specified point
        pts = get_closest_point(mesh, criterion["point"])
        pts.pid = pid
        return pts
    elif criterion["type"] == "plane":
        # Extract points within a specified distance to the plane
        points, _, _ = mesh_to_numpy_connectivity(mesh)
        p1 = np.array(criterion["p1"].coords[0] if isinstance(criterion["p1"], Point) else criterion["p1"])
        p2 = np.array(criterion["p2"].coords[0] if isinstance(criterion["p2"], Point) else criterion["p2"])
        p3 = np.array(criterion["p3"].coords[0] if isinstance(criterion["p3"], Point) else criterion["p3"])
        normal = np.cross(p2 - p1, p3 - p1)
        normal = normal / np.linalg.norm(normal)
        distance_to_plane = np.dot(points - p1, normal)
        setPoint = points[np.abs(distance_to_plane) <= criterion["distance"]]
        return Point(setPoint, pid=pid)
    elif criterion["type"] == "line":
        # Extract points within a specified distance to the line
        points, _, _ = mesh_to_numpy_connectivity(mesh)
        p1 = np.array(criterion["p1"].coords[0] if isinstance(criterion["p1"], Point) else criterion["p1"])
        p2 = np.array(criterion["p2"].coords[0] if isinstance(criterion["p2"], Point) else criterion["p2"])
        line_direction = p2 - p1
        line_direction = line_direction / np.linalg.norm(line_direction)
        vector_to_points = points - p1
        projection_length = np.dot(vector_to_points, line_direction)
        projection = p1 + projection_length[:, None] * line_direction
        distances = np.linalg.norm(points - projection, axis=1)
        setPoint = points[distances <= criterion["distance"]]
        return Point(setPoint, pid=pid) 
    elif criterion["type"] == "sphere":
        # Extract points within a spherical shell
        points, _, _ = mesh_to_numpy_connectivity(mesh)
        center = np.array(criterion["center"].coords[0] if isinstance(criterion["center"], Point) else criterion["center"])
        inner_radius, outer_radius = criterion["inner_radius"], criterion["outer_radius"]
        distances = np.linalg.norm(points - center, axis=1)
        setPoint = points[(distances >= inner_radius) & (distances <= outer_radius)]
        return Point(setPoint, pid=pid)
    elif criterion["type"] == "cylinder":
        # Extract points within a cylindrical shell
        points, _, _ = mesh_to_numpy_connectivity(mesh)
        p1 = np.array(criterion["p1"].coords[0] if isinstance(criterion["p1"], Point) else criterion["p1"])
        p2 = np.array(criterion["p2"].coords[0] if isinstance(criterion["p2"], Point) else criterion["p2"])
        axis_direction = p2 - p1
        axis_direction  = axis_direction / np.linalg.norm(axis_direction)
        vector_to_points = points - p1
        projection_length = np.dot(vector_to_points, axis_direction)
        projection = p1 + projection_length[:, None] * axis_direction
        distances = np.linalg.norm(points - projection, axis=1)
        setPoint = points[(distances >= criterion["inner_radius"]) & (distances <= criterion["outer_radius"])]
        return Point(setPoint, pid=pid)
    elif criterion["type"] == "box":
        # Extract points within a specified box
        points, _, _ = mesh_to_numpy_connectivity(mesh)
        min_point = np.array(criterion["min_point"].coords[0] if isinstance(criterion["min_point"], Point) else criterion["min_point"])
        max_point = np.array(criterion["max_point"].coords[0] if isinstance(criterion["max_point"], Point) else criterion["max_point"])
        setPoint = points[np.all((points >= min_point) & (points <= max_point), axis=1)]
        return Point(setPoint, pid=pid)
    elif criterion["type"] == "id":
        # Extract points with specified IDs
        points, _, _ = mesh_to_numpy_connectivity(mesh)
        if isinstance(criterion["value"], (float, int)):
            ids =  np.array([criterion["value"]])
        else:
            ids = np.array(criterion["value"])
        setPoint = points[ids]
        return Point(setPoint, pid=pid)
    elif criterion["type"] == "pid":
        # Extract points from elements with specified point IDs
        
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(mesh.get_vtk_unstructured_grid())
        threshold.SetUpperThreshold(criterion["value"] + _TOL)
        threshold.SetLowerThreshold(criterion["value"] - _TOL)
        threshold.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, 'pid')
        threshold.Update()
        points, _,  _ = vtk_to_numpy_connectivity(threshold.GetOutput())
        return Point(points, pid=pid)
    elif criterion["type"] == "condition":
        # Extract points that satisfy a specific condition
        points, _, _ = mesh_to_numpy_connectivity(mesh)
        condition_function = criterion["function"]
        setPoint = [p for p in points if condition_function(p)]
        return Point(setPoint, pid=pid)

def extract_element(mesh, id=None, points=None, strict=True):
    """
    Extracts mesh elements based on specified criteria.

    Parameters:
    - mesh: The mesh object containing the elements to be extracted.
    - id: Integer, list, tuple, or numpy array of element IDs to extract. If None, this criterion is ignored.
    - points: point (cloud) to filter elements. If None, this criterion is ignored.
    - strict: Boolean indicating the strictness of point inclusion. If True, all points of the element must be in the specified points. If False, at least one point must be in the specified points.

    Returns:
    - A list of elements (each represented as a list of point IDs) that match the specified criteria.
    """
    
    if id is not None:
        if isinstance(id, (int, float)):
            id = [int(id)]
        iug = mesh.get_vtk_unstructured_grid()
        oug = vtk.vtkUnstructuredGrid()
        for cell_id in id:
            cell = iug.GetCell(cell_id)
            cell_type = cell.GetCellType()
            point_ids = cell.GetPointIds()
            nbpt = point_ids.GetNumberOfIds()
            ids=[point_ids.GetId(i) for i in range(nbpt)]
            # [oug_points.InsertNextPoint(iug.GetPoints().GetPoint(id)) for id in ids ]
            oug.InsertNextCell(cell_type, nbpt, ids)
        oug.SetPoints(iug.GetPoints())  
        clean_filter = vtk.vtkStaticCleanUnstructuredGrid()
        clean_filter.RemoveUnusedPointsOn()
        clean_filter.SetInputData(oug)
        clean_filter.Update()
        omesh = mesh.copy()
        omesh._set_vtk_unstructured_grid(clean_filter.GetOutput())

        omesh.pid = mesh.pid
        return omesh
    
    elif points is not None:
        
        ug0 = mesh.get_vtk_unstructured_grid()
        ug1 = points.get_vtk_unstructured_grid()
        
        map_dict = findPoints(ug0, ug1)
        map_values = set(map_dict.values())
        pts, cells, types = mesh_to_numpy_connectivity(mesh)
        
        # Convert cells and types to numpy arrays (if they aren't already)
        cells_array = np.array(cells, dtype=object)  # dtype=object allows for nested lists
        
        if strict:
            filtered_mask = np.array([all(node in map_values for node in cell) for cell in cells])
            # Apply the mask to filter the cells and types
        else:
            filtered_mask = np.array([any(node in map_values for node in cell) for cell in cells])
            #filtered_cells = [cell for cell in cells if any(node in map_values for node in cell)]
            
            # Apply the mask to filter the cells and types
        filtered_cells = cells_array[filtered_mask]
        filtered_type = types[filtered_mask]
        filtered_cells = filtered_cells.tolist()
        filtered_type  = filtered_type.tolist()
        
        oug = numpy_to_vtk_connectivity(pts, filtered_cells, filtered_type)

        clean_filter = vtk.vtkStaticCleanUnstructuredGrid()
        clean_filter.SetInputData(oug)
        clean_filter.RemoveUnusedPointsOn()
        clean_filter.Update()
        omesh = mesh.copy()
        omesh._set_vtk_unstructured_grid(clean_filter.GetOutput())

        omesh.pid = mesh.pid
        return omesh

def _process_layer_chunk(cells_chunk, n_layers, offsets, n_points):
    new_cells_local = []
    for cell in cells_chunk:
        for i in range(n_layers):
            l1 = cell + offsets[i]
            l2 = cell + offsets[i + 1]
            ncell = np.concatenate((l1, l2))
            
            if len(ncell) == 4:
                ncell[2], ncell[3] = ncell[3], ncell[2]
            
            new_cells_local.append(ncell)
    
    return new_cells_local

def _chunkify(data, n_chunks):
    avg_len = len(data) // n_chunks
    chunks = [data[i * avg_len: (i + 1) * avg_len] for i in range(n_chunks)]
    if len(data) % n_chunks != 0:
        chunks[-1] = np.concatenate((chunks[-1], data[n_chunks * avg_len:]))  # Append leftover items to the last chunk
    return chunks

# def extrudeLinear(basemesh, vector, pid=None, ncpu=None):
#     """
#     Extrudes a base mesh along a given vector (or vectors) and returns the resulting mesh with parallelism for performance improvement.

#     Parameters:
#     - basemesh: The mesh to extrude (e.g., a `Line` object).
#     - vector: The vector(s) used for extrusion. Vector should be a Line Object.
#     - pid (optional): Process ID for the new extruded mesh. Defaults to `None`, which uses the `pid` of the `base_mesh`.
#     - ncpu (optional): The number of CPUs/threads to use for parallel execution. Defaults to None, which will use all available cores.

#     Returns:
#     - A mesh object with the extruded points and cells.
#     """
#     # Use base mesh pid if not provided
#     if pid is None:
#         pid = basemesh.pid
        
#     # Set to serial if ncpu not provided
#     if ncpu is None:ncpu = 1
    
#     # Convert the base mesh to numpy connectivity (points and cells)
#     points, cells, _ = mesh_to_numpy_connectivity(basemesh)
    
#     # Get the points from the vector extraction and compute the extrusion vectors
#     pts = vector.get_points()
#     vextrude = np.diff(pts, axis=0)  # Compute the difference between consecutive points (extrusion vectors)
    
#     # Initialize the number of points and layers for extrusion
#     n_points = len(points)
#     n_layers = len(vextrude)

#     new_points = np.vstack([points] + [points + np.sum(vextrude[:i+1], axis=0) for i in range(n_layers)])
    
#     new_cells = []
#     offsets = np.arange(n_layers + 1) * n_points
    
    
#     # MPI case : Split flattened_cells into chunks
#     if ncpu > 1:
#         #print(f"...run into parallel with {ncpu} workers")
#         # flattened_cells = np.array(cells)
#         if ncpu > len(cells): ncpu = len(cells)
#         chunks = _chunkify(cells, ncpu)
#         # ctx = multiprocessing.get_context("spawn")
        
#         # Use ProcessPoolExecutor to parallelize the processing across chunks
#         new_cells = []
#         with ProcessPoolExecutor(max_workers=ncpu) as executor:
#             # Process each chunk in parallel
#             future_to_index = [executor.submit(_process_layer_chunk, chunk, n_layers, offsets, n_points) for chunk in chunks]
            
#             # Collect the results from each chunk as they complete
#             for future in as_completed(future_to_index):
#                 new_cells.extend(future.result())
#     else :
#     # Serial case 
#         cells_akarray = ak.Array(cells)
#         new_cells = ak.concatenate([ak.concatenate([cells_akarray+offsets[i],cells_akarray+offsets[i+1]], 1) for i in range(n_layers)], 0)
#         new_cells = new_cells.to_list()
#         for item in new_cells:
#             if len(item)==4:
#                 item[2], item[3] = item[3], item[2]
                
#     ug = numpy_to_vtk_connectivity(new_points, new_cells)
    
#     # Create the extruded mesh object and set its VTK grid and properties
#     if isinstance(basemesh, Point):
#         extruded_mesh = Line()
#     elif isinstance(basemesh, Line):
#         extruded_mesh = Surface()
#     elif isinstance(basemesh, Surface):
#         extruded_mesh = Volume()
    
#     extruded_mesh._set_vtk_unstructured_grid(ug)
#     extruded_mesh.pid = pid  # Set the process ID (pid) for the new mesh
    
#     # Return the extruded mesh object
#     return extruded_mesh

def extrudeLinear(basemesh, vector, pid=None):
    """
    Extrudes a base mesh along a given vector (or vectors) and returns the resulting mesh with parallelism for performance improvement.

    Parameters:
    - basemesh: The mesh to extrude (e.g., a `Line` object).
    - vector: The vector(s) used for extrusion. Vector should be a Line Object.
    - pid (optional): Process ID for the new extruded mesh. Defaults to `None`, which uses the `pid` of the `base_mesh`.
    - ncpu (optional): The number of CPUs/threads to use for parallel execution. Defaults to None, which will use all available cores.

    Returns:
    - A mesh object with the extruded points and cells.
    """
    # Use base mesh pid if not provided
    if pid is None:
        pid = basemesh.pid
        
    # Convert the base mesh to numpy connectivity (points and cells)
    points, cells, _ = mesh_to_numpy_connectivity(basemesh)
    
    # Get the points from the vector extraction and compute the extrusion vectors
    pts = vector.get_points()
    vextrude = np.diff(pts, axis=0)  # Compute the difference between consecutive points (extrusion vectors)
    
    # Initialize the number of points and layers for extrusion
    n_points = len(points)
    n_layers = len(vextrude)

    new_points = np.vstack([points] + [points + np.sum(vextrude[:i+1], axis=0) for i in range(n_layers)])

    new_cells = []
    offsets = np.arange(n_layers + 1) * n_points

    n_cols = max(len(row) for row in cells)
    quad_idx = [i for i, row in enumerate(cells) if len(row) == 2]
    
    matrix = ragged_to_matrix(cells, n_cols=n_cols, fill=np.iinfo(np.int64).min)  #np.iinfo(np.int64).min ~ nan
    n_cells, k = matrix.shape
    
    # Broadcast-add to get two (n_layers, n_cells, k) arrays in C
    m1 = matrix[None, :, :] + offsets[:-1 ][:, None, None]
    m2 = matrix[None, :, :] + offsets[1:  ][:, None, None]
    new_cells = np.concatenate((m1, m2), axis=2)
    new_cells = new_cells.reshape(-1, 2*k)
    
    bad_idx = np.where((matrix < 0).any(axis=1))[0] # remove nan
    bad_idx = np.add.outer(np.arange(len(offsets)-1)*matrix.shape[0],
                       bad_idx).ravel()
    quad_idx = np.add.outer(np.arange(len(offsets)-1)*matrix.shape[0],
                       quad_idx).ravel()

    #new_cells = new_cells.tolist()
    new_cells = list(new_cells) # speed up using view instead of pure python
    
    if  len(bad_idx) > 1:
        for i in bad_idx:
            new_cells[i] = [x for x in new_cells[i] if x > -1]
            
    if len(quad_idx) > 1:
        for idx in quad_idx:
            item = new_cells[idx]
            item[2], item[3] = item[3], item[2]

    ug = numpy_to_vtk_connectivity(new_points, new_cells)
    
    # Create the extruded mesh object and set its VTK grid and properties
    if isinstance(basemesh, Point):
        extruded_mesh = Line()
    elif isinstance(basemesh, Line):
        extruded_mesh = Surface()
    elif isinstance(basemesh, Surface):
        extruded_mesh = Volume()
    
    extruded_mesh._set_vtk_unstructured_grid(ug)
    extruded_mesh.pid = pid  # Set the process ID (pid) for the new mesh
    
    # Return the extruded mesh object
    return extruded_mesh
    # return points, cells, new_points, new_cells, offsets, matrix, bad_idx


# def extrudeRotational(basemesh, pA = None, pB = None, angle = None, n = 1, pid=None, ncpu = None):
#     """
#     Extrudes a base mesh by rotating it around an axis defined by two points and returns the resulting mesh.

#     Parameters:
#     - basemesh: The mesh to extrude (e.g., a `Line` object).
#     - axis_points: Two points defining the axis of rotation (e.g., (x1, y1, z1) and (x2, y2, z2)).
#     - angle: The angle of rotation (in degrees).
#     - n_layers: The number of layers (or steps) to rotate around the axis.
#     - pid (optional): Process ID for the new extruded mesh. Defaults to `None`, which uses the `pid` of the `base_mesh`.

#     Returns:
#     - A mesh object with the rotated points and cells.
#     """
#     # Use base mesh pid if not provided
#     if pid is None:
#         pid = basemesh.pid
        
#     # Set to serial if ncpu not provided
#     if ncpu is None:ncpu = 1

#     if angle is None:
#         raise ValueError("Angle must be provided.")
#     if abs(angle) == 0:
#         raise ValueError("No extrusion possible: angle cannot be zero.")
#     if abs(angle) > 360:
#         raise ValueError("Angle must be within 0 to 360 degrees.")
        
#     # Convert angle from degrees to radians for the rotation matrix
#     angle = angle * np.pi / 180.0

#     # Convert the base mesh to numpy connectivity (points and cells)
#     points, cells, types = mesh_to_numpy_connectivity(basemesh)
    
#     # Extract the axis of rotation defined by two points
#     p1 = pA.coords[0] if isinstance(pA, Point) else pA
#     p2 = pB.coords[0] if isinstance(pB, Point) else pB
    
#     axis = np.array(p2) - np.array(p1)
    
#     # Normalize the axis vector
#     axis = axis / np.linalg.norm(axis)
    
#     # Calculate the rotation matrix based on the axis and angle
#     rotation_matrix = get_rotation_matrix(axis, angle/n)
    
#     # Initialize the number of points and layers for rotation
#     n_points = len(points)
    
#     # Create new points by applying the rotation for each layer
#     new_points = points.tolist()
    
#     for i in range(n):
#         # Apply rotation to all points
#         rotated_points = np.dot(points - p1, rotation_matrix.T) + p1
#         new_points.append(rotated_points)
#         points = rotated_points  # Update points for the next layer

#     # Stack the points for all layers
#     new_points = np.vstack(new_points)
    
#     new_cells = []
#     offsets = np.arange(n + 1) * n_points
        
#     # MPI case : Split flattened_cells into chunks
#     if ncpu > 1:
#         # flattened_cells = np.array(cells)
#         if ncpu > len(cells): ncpu = len(cells)
#         chunks = _chunkify(cells, ncpu)
        
#         # Use ProcessPoolExecutor to parallelize the processing across chunks
#         new_cells = []
#         with ProcessPoolExecutor(max_workers=ncpu) as executor:
#             # Process each chunk in parallel
#             futures = [executor.submit(_process_layer_chunk, chunk, n, offsets, n_points) for chunk in chunks]
            
#             # Collect the results from each chunk as they complete
#             for future in futures:
#                 new_cells.extend(future.result())
#     else :
#     # Serial case 
#         cells_akarray = ak.Array(cells)
#         new_cells = ak.concatenate([ak.concatenate([cells_akarray+offsets[i],cells_akarray+offsets[i+1]], 1) for i in range(n)], 0)
#         new_cells = new_cells.to_list()
#         for item in new_cells:
#             if len(item)==4:
#                 item[2], item[3] = item[3], item[2]


#     ug = numpy_to_vtk_connectivity(new_points, new_cells)

    

#     # Step 1: Merge duplicate points
#     cleaner = vtk.vtkStaticCleanUnstructuredGrid()
#     cleaner.SetInputData(ug)
#     cleaner.SetTolerance(_TOL**3)
#     cleaner.Update()
#     cleaned_ug = cleaner.GetOutput()

    
#     # Create the rotated mesh object and set its VTK grid and properties
#     if isinstance(basemesh, Point): 
#         extruded_mesh = Line()
#     elif isinstance(basemesh, Line): 
#         extruded_mesh = Surface()
#     elif isinstance(basemesh, Surface): 
#         extruded_mesh = Volume()
    
#     extruded_mesh._set_vtk_unstructured_grid(cleaned_ug)
#     extruded_mesh.pid = pid  # Set the process ID (pid) for the new mesh
#     regen(extruded_mesh,ncpu=ncpu)


#     # Return the rotated mesh object
#     return extruded_mesh

def extrudeRotational(basemesh, pA = None, pB = None, angle = None, n = 1, pid=None, ncpu = 1):
    """
    Extrudes a base mesh by rotating it around an axis defined by two points and returns the resulting mesh.

    Parameters:
    - basemesh: The mesh to extrude (e.g., a `Line` object).
    - axis_points: Two points defining the axis of rotation (e.g., (x1, y1, z1) and (x2, y2, z2)).
    - angle: The angle of rotation (in degrees).
    - n_layers: The number of layers (or steps) to rotate around the axis.
    - pid (optional): Process ID for the new extruded mesh. Defaults to `None`, which uses the `pid` of the `base_mesh`.

    Returns:
    - A mesh object with the rotated points and cells.
    """
    # Use base mesh pid if not provided
    if pid is None:
        pid = basemesh.pid
        
    # Set to serial if ncpu not provided
    if ncpu is None:ncpu = 1

    if angle is None:
        raise ValueError("Angle must be provided.")
    if abs(angle) == 0:
        raise ValueError("No extrusion possible: angle cannot be zero.")
    if abs(angle) > 360:
        raise ValueError("Angle must be within 0 to 360 degrees.")
        
    # Convert angle from degrees to radians for the rotation matrix
    angle = angle * np.pi / 180.0

    # Convert the base mesh to numpy connectivity (points and cells)
    points, cells, types = mesh_to_numpy_connectivity(basemesh)
    
    # Extract the axis of rotation defined by two points
    p1 = pA.coords[0] if isinstance(pA, Point) else pA
    p2 = pB.coords[0] if isinstance(pB, Point) else pB
    
    axis = np.array(p2) - np.array(p1)
    
    # Normalize the axis vector
    axis = axis / np.linalg.norm(axis)
    
    # Calculate the rotation matrix based on the axis and angle
    rotation_matrix = get_rotation_matrix(axis, angle/n)
    
    # Initialize the number of points and layers for rotation
    n_points = len(points)
    
    # Create new points by applying the rotation for each layer
    new_points = points.tolist()
    
    for i in range(n):
        # Apply rotation to all points
        rotated_points = np.dot(points - p1, rotation_matrix.T) + p1
        new_points.append(rotated_points)
        points = rotated_points  # Update points for the next layer

    # Stack the points for all layers
    new_points = np.vstack(new_points)
    
    new_cells = []
    offsets = np.arange(n + 1) * n_points

    n_cols = max(len(row) for row in cells)
    quad_idx = [i for i, row in enumerate(cells) if len(row) == 2]
    
    matrix = ragged_to_matrix(cells, n_cols=n_cols, fill=np.iinfo(np.int64).min)  #np.iinfo(np.int64).min ~ nan
    n_cells, k = matrix.shape
    
    # Broadcast-add to get two (n_layers, n_cells, k) arrays in C
    m1 = matrix[None, :, :] + offsets[:-1 ][:, None, None]
    m2 = matrix[None, :, :] + offsets[1:  ][:, None, None]
    new_cells = np.concatenate((m1, m2), axis=2)
    new_cells = new_cells.reshape(-1, 2*k)
    
    bad_idx = np.where((matrix < 0).any(axis=1))[0] # remove nan
    bad_idx = np.add.outer(np.arange(len(offsets)-1)*matrix.shape[0],
                       bad_idx).ravel()
    quad_idx = np.add.outer(np.arange(len(offsets)-1)*matrix.shape[0],
                       quad_idx).ravel()

    #new_cells = new_cells.tolist()
    new_cells = list(new_cells) # speed up using view instead of pure python
    
    if  len(bad_idx) > 1:
        for i in bad_idx:
            new_cells[i] = [x for x in new_cells[i] if x > -1]
            
    if len(quad_idx) > 1:
        for idx in quad_idx:
            item = new_cells[idx]
            item[2], item[3] = item[3], item[2]


    ug = numpy_to_vtk_connectivity(new_points, new_cells)

    

    # Step 1: Merge duplicate points
    cleaner = vtk.vtkStaticCleanUnstructuredGrid()
    cleaner.SetInputData(ug)
    cleaner.SetTolerance(_TOL**3)
    cleaner.Update()
    cleaned_ug = cleaner.GetOutput()

    
    # Create the rotated mesh object and set its VTK grid and properties
    if isinstance(basemesh, Point): 
        extruded_mesh = Line()
    elif isinstance(basemesh, Line): 
        extruded_mesh = Surface()
    elif isinstance(basemesh, Surface): 
        extruded_mesh = Volume()
    
    extruded_mesh._set_vtk_unstructured_grid(cleaned_ug)
    extruded_mesh.pid = pid  # Set the process ID (pid) for the new mesh
    regen(extruded_mesh,ncpu=ncpu)


    # Return the rotated mesh object
    return extruded_mesh

def getBoundaries(mesh, level_type=None, pid=None, pick="all", n_faces = 6):
    """
    Reduces the mesh to the next lower level of geometry (e.g., points from lines, edges from surfaces, surfaces from volumes).
    
    Parameters:
        mesh (Mesh): The input mesh to reduce.
        level_type (str, optional): The type of element to reduce to ('1D', '2D', '3D'). 
                                    If None, it will automatically decide based on the mesh geometry.
    
    Returns:
        Elem: A new Elem object of reduced level geometry.
    
    Raises:
        ValueError: If the mesh contains only points or multiple geometry types.
    """
    
    # Check the number of cells in the mesh
    num_cells = mesh.get_vtk_unstructured_grid().GetNumberOfCells()
    if num_cells == 0:
        raise ValueError("The mesh contains no elements. Cannot reduce to a lower level.")
    
    cell_types = set()
    
    # Identify the types of cells present in the mesh
    for i in range(num_cells):
        cell = mesh.get_vtk_unstructured_grid().GetCell(i)
        cell_types.add(cell.GetCellType())
    
    # Check whether the mesh is 1D, 2D, or 3D
    is_1d = any(cell_type in [vtk.VTK_LINE] for cell_type in cell_types)
    is_2d = any(cell_type in [vtk.VTK_TRIANGLE, vtk.VTK_QUAD] for cell_type in cell_types)
    is_3d = any(cell_type in [vtk.VTK_WEDGE, vtk.VTK_HEXAHEDRON, vtk.VTK_POLYHEDRON, vtk.VTK_VOXEL] for cell_type in cell_types)
    
    # Handle cases based on the presence of 1D, 2D, or 3D elements
    if not any([is_1d, is_2d, is_3d]):
        raise ValueError("The mesh does not contain valid 1D, 2D, or 3D elements.")
    
    if len(cell_types) > 1 and level_type is None:
        raise ValueError(
            "The mesh contains multiple types of geometry (1D, 2D, 3D). Please specify a level type ('1D', '2D', '3D')."
        )
    
    # Determine the type of mesh reduction based on the geometry
    if level_type is None:
        if is_1d:
            level_type = '1D'
        elif is_2d:
            level_type = '2D'
        else:
            level_type = '3D'
    # Extract the appropriate mesh based on the level type
    if level_type == '1D':  # Extract points from a line
        return _extract_bc_from_line(mesh, pid=pid, pick = pick)
    elif level_type == '2D':  # Extract edges from a surface
        return _extract_bc_from_surface(mesh, pid=pid, pick = pick)
    elif level_type == '3D':  # Extract the envelope surface from a volume
        return _extract_bc_from_volume(mesh, pid=pid, pick = pick, n_faces = 6)
    else:
        raise ValueError("Invalid level_type specified. Must be '1D', '2D', or '3D'.")

# def extract_elem(mesh,criterion)

def _extract_bc_from_line(mesh, pid=None, pick="all"):
    """
    Extract points from a 1D line mesh.

    Parameters:
        mesh (Elem): The input line mesh to extract points from.
        pid (int, optional): The part ID for the new mesh (default: None, keeps original part ID).
    
    Returns:
        Elem: A new mesh containing only the points.
    """
    
    connectivity_filter = vtk.vtkConnectivityFilter()
    connectivity_filter.SetInputData(mesh.get_vtk_unstructured_grid())
    connectivity_filter.SetExtractionModeToAllRegions()
    connectivity_filter.ColorRegionsOn()
    connectivity_filter.Update()    
    
    # Get the output of the filter
    connected_mesh = connectivity_filter.GetOutput()
    # Get the number of extracted regions
    number_of_regions = connectivity_filter.GetNumberOfExtractedRegions()

    extremities = []
    
    if pid == None : pid=mesh.pid

    def __process_region(rid):
        """Process a single region to extract its extremities."""
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(connected_mesh)
        threshold.SetUpperThreshold(rid + _TOL)
        threshold.SetLowerThreshold(rid - _TOL)
        threshold.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, 'RegionId')
        threshold.Update()
        pl = Line()
        pl._set_vtk_unstructured_grid(threshold.GetOutput())
        return pl.get_start_point(), pl.get_end_point()

    if pick == 'all':
        for rid in range(number_of_regions):
            start_point, end_point = __process_region(rid)
            extremities.extend([start_point, end_point])

    elif isinstance(pick, int):
        if not (0 <= pick <= number_of_regions * 2 - 1):
            raise ValueError(f"Desired point index must be between 0 and {number_of_regions * 2 - 1}")
        for rid in range(number_of_regions):
            start_point, end_point = __process_region(rid)
            if pick == 2 * rid:
                extremities.append(start_point)
            elif pick == 2 * rid + 1:
                extremities.append(end_point)

    elif isinstance(pick, (list, tuple, np.ndarray)):
        if any(p < 0 or p > number_of_regions * 2 - 1 for p in pick):
            raise ValueError(f"Desired point indices must be between 0 and {number_of_regions * 2 - 1}")
        for rid in range(number_of_regions):
            start_point, end_point = __process_region(rid)
            if 2 * rid in pick:
                extremities.append(start_point)
            if 2 * rid + 1 in pick:
                extremities.append(end_point)
    
    new_mesh = Point(extremities, pid=pid)
    return new_mesh

    """
    Extract edges from a 2D surface mesh using vtkFeatureEdges.

    Parameters:
        mesh (Elem): The input surface mesh.
        pid (int, optional): The part ID for the new mesh (default: None, keeps original part ID).
    
    Returns:
        Elem: A new mesh containing only the edges.
    """
    if pid == None : pid=mesh.pid
    
    # Create a vtkDataSetSurfaceFilter to extract the surface from the unstructured grid
    surface_filter = vtk.vtkDataSetSurfaceFilter()
    surface_filter.SetInputData(mesh.get_vtk_unstructured_grid())
    surface_filter.Update()
    
    # Now use vtkFeatureEdges on the extracted surface (vtkPolyData)
    feature_edges = vtk.vtkFeatureEdges()
    feature_edges.SetInputData(surface_filter.GetOutput())
    
    # Optionally, you can choose to extract only the boundary edges, or all edges
    feature_edges.BoundaryEdgesOn()  # Only boundary edges
    feature_edges.FeatureEdgesOff()  # Do not extract non-boundary feature edges
    feature_edges.ManifoldEdgesOff()  # Do not extract edges shared by manifold surfaces
    feature_edges.NonManifoldEdgesOff()  # Exclude non-manifold edges
    
    feature_edges.Update()

    # convert back to ugrid
    edge_ugrid_filter = vtk.vtkPolyDataToUnstructuredGrid()
    edge_ugrid_filter.AddInputData(feature_edges.GetOutput())
    edge_ugrid_filter.Update()
    edge_ugrid = edge_ugrid_filter.GetOutput()
    
    # Create a new mesh for the extracted edges

    
    if pick != 'all':
        points, cells = vtk_to_numpy_connectivity(edge_ugrid)
        points_2d, _ = auto_reduce_dim(points)
        hull = ConvexHull(points)
        hv = sorted(hull.vertices)
        print(hv)


        
    new_mesh = Line(pid=pid)
    ugrid =vtk.vtkUnstructuredGrid()
    points = edge_ugrid.GetPoints()
    cell_array = edge_ugrid.GetCells()
    
    ugrid.SetPoints(points)
    ugrid.SetCells(vtk.VTK_LINE, cell_array)
    
    new_mesh._set_vtk_unstructured_grid(ugrid)
    new_mesh.pid=pid
    
    return new_mesh

def _extract_bc_from_surface(mesh, pid=None, pick='all'):
    """
    Extract edges from a 2D surface mesh using vtkFeatureEdges.

    Parameters:
        mesh (Elem): The input surface mesh.
        pid (int, optional): The part ID for the new mesh (default: None, keeps original part ID).
    
    Returns:
        Elem: A new mesh containing only the edges.
    """
    # # check regions
    # connectivity_filter = vtk.vtkConnectivityFilter()
    # connectivity_filter.SetInputData(mesh.get_vtk_unstructured_grid())
    # connectivity_filter.SetExtractionModeToAllRegions()
    # connectivity_filter.ColorRegionsOn()
    # connectivity_filter.Update()    
    
    # # Get the number of extracted regions
    # number_of_regions = connectivity_filter.GetNumberOfExtractedRegions()
    
   
    if pid == None : pid=mesh.pid
    
    # Create a vtkDataSetSurfaceFilter to extract the surface from the unstructured grid
    surface_filter = vtk.vtkDataSetSurfaceFilter()
    surface_filter.SetInputData(mesh.get_vtk_unstructured_grid())
    surface_filter.Update()
    
    # Now use vtkFeatureEdges on the extracted surface (vtkPolyData)
    feature_edges = vtk.vtkFeatureEdges()
    feature_edges.SetInputData(surface_filter.GetOutput())
    
    # Optionally, you can choose to extract only the boundary edges, or all edges
    feature_edges.BoundaryEdgesOn()  # Only boundary edges
    feature_edges.FeatureEdgesOff()  # Do not extract non-boundary feature edges
    feature_edges.ManifoldEdgesOff()  # Do not extract edges shared by manifold surfaces
    feature_edges.NonManifoldEdgesOff()  # Exclude non-manifold edges
    
    feature_edges.Update()

    # convert back to ugrid
    edge_ugrid_filter = vtk.vtkPolyDataToUnstructuredGrid()
    edge_ugrid_filter.AddInputData(feature_edges.GetOutput())
    edge_ugrid_filter.Update()
    edge_ugrid = edge_ugrid_filter.GetOutput()
    
    if pick != 'all':
        # if number_of_regions > 1:
        #     raise ValueError(f"Multiple surfaces detected ({number_of_regions} regions). Please extract one region before applying the function.")
            
        points, cells, _ = vtk_to_numpy_connectivity(edge_ugrid)
        edges = _reorganize_cells_into_edges(cells, points)
        if isinstance(pick, int):
            edge_ugrid = numpy_to_vtk_connectivity(points, edges[pick],dime=1) 
        elif isinstance(pick, (list, tuple, np.ndarray)):
            selected_edges = [edges[index] for index in pick]
            flattened_edges = [item for sublist in selected_edges for item in sublist]
            edge_ugrid = numpy_to_vtk_connectivity(points, flattened_edges,dime=1) 
    # Create a new mesh for the extracted edges
    new_mesh = Line(pid=pid)

        
    ugrid =vtk.vtkUnstructuredGrid()
    points = edge_ugrid.GetPoints()
    cell_array = edge_ugrid.GetCells()
    
    ugrid.SetPoints(points)
    ugrid.SetCells(vtk.VTK_LINE, cell_array)
    
    new_mesh._set_vtk_unstructured_grid(ugrid)
    new_mesh.pid=pid
    
    return new_mesh

def _extract_bc_from_volume(mesh, pid=None, pick='all', n_faces = 6):
    """
    Extract the envelope surface from a 3D volume mesh.

    Parameters:
        mesh (Elem): The input volume mesh.
        color (tuple, optional): The color for the extracted surface (default: red).

    Returns:
        Elem: A new mesh containing only the envelope surface.
    """    
    # extract surface
    surface_filter = vtk.vtkGeometryFilter()
    surface_filter.SetInputData(mesh.get_vtk_unstructured_grid())
    surface_filter.MergingOn()
    
    # convert PolyData to Unstructured Grid
    surf_ugrid_filter = vtk.vtkPolyDataToUnstructuredGrid()
    surf_ugrid_filter.SetInputConnection(surface_filter.GetOutputPort())
    surf_ugrid_filter.Update()
    surf_ugrid = surf_ugrid_filter.GetOutput() 
    
    if pid is None : pid=mesh.pid
    
    if pick != 'all':
        points, cells, _ = vtk_to_numpy_connectivity(surf_ugrid)
        sides = _reorganize_cells_into_sides(cells, points, n_faces = n_faces)
        if isinstance(pick, int):
            surf_ugrid = numpy_to_vtk_connectivity(points, sides[pick], dime=2) 
        elif isinstance(pick, (list, tuple, np.ndarray)):
            selected_sides = [sides[index] for index in pick]
            flattened_sides = [item for sublist in selected_sides for item in sublist]
            surf_ugrid = numpy_to_vtk_connectivity(points, flattened_sides, dime=2) 
    # Create a new mesh for the extracted edges
    
    new_mesh = Surface(pid=pid)
    new_mesh._set_vtk_unstructured_grid(surf_ugrid)
    new_mesh.pid=pid
    
    return new_mesh

def _reorganize_cells_into_edges(cells, points, angle_threshold=np.pi/8):
    """
    Reorganize cells into edges based on direction vectors and angle variation.

    Parameters:
    - cells: List of arrays representing cell connectivity.
    - points: Array of point coordinates.
    - angle_threshold: Threshold angle (in radians) to group cells into the same edge.

    Returns:
    - edges: List of edges, each containing a sequence of connected cells.
    """
    def compute_direction_vector(cell):
        """Compute the direction vector of a cell."""
        p1, p2 = points[cell[0]], points[cell[1]]
        return p2 - p1

    def angle_between_vectors(v1, v2):
        """Compute the angle between two vectors."""
        dot_product = np.dot(v1, v2)
        norms = np.linalg.norm(v1) * np.linalg.norm(v2)
        return np.arccos(np.clip(dot_product / norms, -1.0, 1.0))

    edges = []
    visited = set()

    for i, cell in enumerate(cells):
        if i in visited:
            continue

        edge = [cell]
        visited.add(i)
        current_direction = compute_direction_vector(cell)

        for j, next_cell in enumerate(cells):
            if j in visited:
                continue

            next_direction = compute_direction_vector(next_cell)
            angle = angle_between_vectors(current_direction, next_direction)

            if angle < angle_threshold:
                edge.append(next_cell)
                visited.add(j)
                current_direction = next_direction

        edges.append(edge)

    return edges

def _reorganize_cells_into_sides(cells, points, n_faces=6):
    """
    Organize the cells into groups (sides) based on their face normals using vectorized operations.

    Parameters:
        cells (list or np.ndarray): List/array of cell connectivity (each cell is assumed to be a triangle defined by 3 indices).
        points (np.ndarray): Array of point coordinates.
        n_faces (int): Number of clusters (sides) to create.
    
    Returns:
        list: A list of length n_faces where each element is a list of cells belonging to that side.
    """
    # Ensure cells is a NumPy array
    cells_arr = np.asarray(cells)  # shape (n_cells, 3)
    
    # Vectorized extraction of triangle vertices
    v0 = points[cells_arr[:, 0]]
    v1 = points[cells_arr[:, 1]]
    v2 = points[cells_arr[:, 2]]
    
    # Compute edge vectors
    edge1 = v1 - v0
    edge2 = v2 - v0
    
    # Compute cross product for all faces in one shot (normals)
    normals = np.cross(edge1, edge2)
    
    # Normalize the normals, avoid division by zero
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normals = normals / norms

    # Cluster normals using KMeans
    kmeans = KMeans(n_clusters=n_faces, random_state=0)
    labels = kmeans.fit_predict(normals)
    
    # Organize cells into clusters (sides)
    faces = [[] for _ in range(n_faces)]
    for i, label in enumerate(labels):
        faces[label].append(cells[i])
    
    return faces
