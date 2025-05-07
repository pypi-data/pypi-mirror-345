#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 12:46:23 2025

@author: sauvagea
"""

import numpy as np
from scipy.spatial import ConvexHull

def auto_reduce_dim(points):
    """
    Reduces the dimensions of the given 3D points by removing constant coordinates 
    (those where min == max).

    Args:
        points (np.ndarray): An Nx3 array of points where each point is (x, y, z).

    Returns:
        tuple: 
            - reduced_points (np.ndarray): An NxD array with non-constant dimensions.
            - kept_dims (list): List of indices of the original dimensions that remain.

    Example:
        >>> points = np.array([[1, 2, 3], [4, 5, 3], [7, 8, 3]])
        >>> auto_reduce_dim(points)
        (array([[1, 2], [4, 5], [7, 8]]), [0, 1])
    """
    mins = points.min(axis=0)
    maxs = points.max(axis=0)

    # A dimension is constant if min == max
    is_constant = (mins == maxs)

    # Keep only columns that are NOT constant
    kept_dims = np.where(~is_constant)[0]
    reduced_points = points[:, kept_dims]

    return reduced_points, kept_dims

def cyclic_diff(a, b, T):
    """
    Computes the cyclic difference between indices a and b within the range [0, T).

    Args:
        a (int): First index.
        b (int): Second index.
        T (int): The cyclic range, usually the length of a list.

    Returns:
        int: The cyclic difference between a and b.

    Example:
        >>> cyclic_diff(3, 1, 5)
        3
    """
    return (b - a) % T

def find_nearest(hull_vertices, target, T):
    """
    Finds the nearest hull vertex to a target index, considering a cyclic boundary.

    Args:
        hull_vertices (list): List of sorted hull vertex indices.
        target (int): Target index for which the nearest vertex is found.
        T (int): The cyclic range, usually the total number of vertices.

    Returns:
        int: The index of the hull vertex closest to the target.

    Example:
        >>> find_nearest([0, 1, 3, 4], 2, 5)
        1
    """
    best = hull_vertices[0]
    best_dist = T
    for v in hull_vertices:
        dist = min(cyclic_diff(target, v, T), cyclic_diff(v, target, T))
        if dist < best_dist:
            best_dist = dist
            best = v
    return best

def select_four_hulls(points):
    """
    Selects four hull vertices that approximately form a rectangle or square 
    by minimizing the error in the segment lengths.

    Args:
        points (np.ndarray): The points forming the convex hull.

    Returns:
        tuple: A tuple of four indices of the selected hull vertices.

    Example:
        >>> select_four_hulls(np.array([[0, 0], [1, 0], [1, 1], [0, 1], [2, 2]]))
        (0, 1, 2, 3)
    """
    points = np.asarray(points)
    T = len(points)
    hull = ConvexHull(points)
    hv = sorted(hull.vertices)

    best_error = float('inf')
    best_corners = None

    for i, c0 in enumerate(hv):
        # Compute the ideal positions (mod T) for the other three corners.
        target1 = (c0 + T // 4) % T
        target2 = (c0 + T // 2) % T
        target3 = (c0 + (3 * T) // 4) % T
        
        # Find the nearest hull vertices to these targets.
        c1 = find_nearest(hv, target1, T)
        c2 = find_nearest(hv, target2, T)
        c3 = find_nearest(hv, target3, T)
        
        # Compute segment lengths using cyclic differences.
        seg1 = cyclic_diff(c0, c1, T)
        seg2 = cyclic_diff(c1, c2, T)
        seg3 = cyclic_diff(c2, c3, T)
        seg4 = cyclic_diff(c3, c0, T)
        
        # Check for an exact match
        if seg1 == seg3 and seg2 == seg4:
            return (c0, c1, c2, c3)
        
        # Otherwise, compute an error metric.
        error = abs(seg1 - seg3) + abs(seg2 - seg4)
        if error < best_error:
            best_error = error
            best_corners = (c0, c1, c2, c3)

    return best_corners

def corner_mask_auto(points_3d):
    """
    Automatically detects corner points from a set of 3D points, reducing dimensions if necessary 
    and computing the convex hull.

    Args:
        points_3d (np.ndarray): An Nx3 array of 3D points.

    Returns:
        np.ndarray: A boolean mask where True indicates the points are corners.

    Raises:
        ValueError: If there are fewer than 3 points after dimensionality reduction.

    Example:
        >>> points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])
        >>> corner_mask_auto(points)
        array([ True,  True,  True,  True])
    """
    points_2d, _ = auto_reduce_dim(points_3d)
    
    if points_2d.shape[1] != 2:
        raise ValueError("Data is not 2D after removing constant dimensions. "
                         "Cannot compute a 2D hull. Possibly the shape is 1D or truly 3D.")
    
    hull = ConvexHull(points_2d)
    hv = hull.vertices

    if len(hv) < 3:
        raise ValueError("Less than 3 corner nodes in hull => shape is degenerate.")
    
    corner_mask_2d = np.zeros(len(points_2d), dtype=bool)
    if len(hv) <= 4:
        corner_mask_2d[hv] = True
    else:
        hv = np.array(select_four_hulls(points_2d))
        corner_mask_2d[hv] = True

    return corner_mask_2d

# ---------------------------------------------------------------------
#   DEPRECATED
# ---------------------------------------------------------------------

# def detect_3_corners(points):
#     """
#     If the convex hull is exactly 3 points, return those hull points.
#     Otherwise, raise an exception or handle differently.
    
#     NOTE: This is NOT a full minimal bounding triangle for an arbitrary shape.
#     It simply returns the 3 hull vertices if the shape is already a triangle.

#     Args:
#         points (np.ndarray): An Nx2 array of 2D points.

#     Returns:
#         np.ndarray: An array containing the 3 corner points of the triangle.

#     Raises:
#         ValueError: If the convex hull does not contain exactly 3 points.

#     Example:
#         >>> detect_3_corners(np.array([[0, 0], [1, 0], [0, 1]]))
#         array([[0, 0], [1, 0], [0, 1]])
#     """
#     hull = ConvexHull(points)
#     hull_vertices = hull.vertices
#     if len(hull_vertices) != 3:
#         raise ValueError("Shape is not a triangle (convex hull has != 3 vertices). "
#                          "Implement a minimal bounding triangle algorithm if needed.")
#     return points[hull_vertices]

# def detect_4_corners(points):
#     """
#     Computes the minimum area bounding rectangle of a set of 2D points.
#     Returns the 4 corner points (in order) of the rectangle.
    
#     Args:
#         points (np.ndarray): An (N,2) array of 2D points.
        
#     Returns:
#         np.ndarray: A (4,2) array of corner points.

#     Example:
#         >>> detect_4_corners(np.array([[0, 0], [1, 0], [1, 1], [0, 1]]))
#         array([[0, 0], [1, 0], [1, 1], [0, 1]])
#     """
#     hull = ConvexHull(points)
#     hull_points = points[hull.vertices]
#     n = len(hull_points)
    
#     best_area = np.inf
#     best_rect = None
#     best_angle = 0
#     for i in range(n):
#         p0 = hull_points[i]
#         p1 = hull_points[(i + 1) % n]
#         edge = p1 - p0
#         angle = np.arctan2(edge[1], edge[0])
#         R = np.array([[np.cos(-angle), -np.sin(-angle)],
#                       [np.sin(-angle),  np.cos(-angle)]])
#         rot_points = (R @ hull_points.T).T
#         min_x, max_x = np.min(rot_points[:, 0]), np.max(rot_points[:, 0])
#         min_y, max_y = np.min(rot_points[:, 1]), np.max(rot_points[:, 1])
#         area = (max_x - min_x) * (max_y - min_y)
#         if area < best_area:
#             best_area = area
#             best_angle = angle
#             best_rect = np.array([[min_x, min_y],
#                                   [min_x, max_y],
#                                   [max_x, max_y],
#                                   [max_x, min_y]])
    
#     return best_rect



    

# ---------------------------------------------------------------------
#   DEPRECATED
# ---------------------------------------------------------------------

# def detect_3_corners(points):
#     """
#     If the convex hull is exactly 3 points, return those hull points.
#     Otherwise, raise an exception or handle differently.
    
#     NOTE: This is NOT a full minimal bounding triangle for an arbitrary shape.
#     It simply returns the 3 hull vertices if the shape is already a triangle.
#     """
#     hull = ConvexHull(points)
#     hull_vertices = hull.vertices
#     if len(hull_vertices) != 3:
#         raise ValueError("Shape is not a triangle (convex hull has != 3 vertices). "
#                          "Implement a minimal bounding triangle algorithm if needed.")
#     return points[hull_vertices]

# def detect_4_corners(points):
#     """
#     Compute the minimum area bounding rectangle of a set of 2D points.
#     Returns the 4 corner points (in order) of the rectangle.
    
#     Parameters:
#         points (np.ndarray): An (N,2) array of 2D points.
        
#     Returns:
#         np.ndarray: A (4,2) array of corner points.
#     """
#     # Compute the convex hull of the points.
#     hull = ConvexHull(points)
#     hull_points = points[hull.vertices]
#     n = len(hull_points)
    
#     best_area = np.inf
#     best_rect = None
#     best_angle = 0
#     # Loop through all edges of the hull.
#     for i in range(n):
#         # Edge from hull_points[i] to hull_points[(i+1) % n]
#         p0 = hull_points[i]
#         p1 = hull_points[(i + 1) % n]
#         edge = p1 - p0
#         angle = np.arctan2(edge[1], edge[0])
#         # Rotate all points to align the edge with the x-axis.
#         R = np.array([[np.cos(-angle), -np.sin(-angle)],
#                       [np.sin(-angle),  np.cos(-angle)]])
#         rot_points = (R @ hull_points.T).T
#         min_x, max_x = np.min(rot_points[:, 0]), np.max(rot_points[:, 0])
#         min_y, max_y = np.min(rot_points[:, 1]), np.max(rot_points[:, 1])
#         area = (max_x - min_x) * (max_y - min_y)
#         if area < best_area:
#             best_area = area
#             best_angle = angle
#             best_rect = (min_x, max_x, min_y, max_y)
    
#     # Unpack the best rectangle parameters.
#     min_x, max_x, min_y, max_y = best_rect
#     # The rectangle corners in the rotated coordinate system:
#     rect = np.array([
#         [min_x, min_y],
#         [max_x, min_y],
#         [max_x, max_y],
#         [min_x, max_y]
#     ])
#     # Rotate the rectangle corners back to the original coordinate system.
#     R_inv = np.array([[np.cos(best_angle), -np.sin(best_angle)],
#                       [np.sin(best_angle),  np.cos(best_angle)]])
#     rect_corners = (R_inv @ rect.T).T
#     return rect_corners

# def detect_corners(points):
#     """
#     1) Check how many hull vertices the shape has.
#     2) If it has exactly 3, call min_area_triangle_if_triangle().
#     3) If it has >= 4, call min_area_rect().
    
#     Returns either 3 or 4 corner points.
#     """
#     points, _ = auto_reduce_dim(points)
#     hull = ConvexHull(points)
#     n_hull = len(hull.vertices)
#     if n_hull == 3:
#         #print("Shape has exactly 3 corners on its hull -> Using the triangle approach.")
#         return detect_3_corners(points)
#     elif n_hull == 4:
#         #print("Shape has 4 corners on its hull -> Using min_area_rect directly on hull.")
#         # If you want to treat *any* shape with 4 hull vertices as a rectangle, 
#         # you could just return the hull points themselves (which is *already* a quadrilateral).
#         # But if you specifically want the minimum bounding rectangle (which might not match the hull
#         # if the shape is a quadrilateral but tilted, etc.), call min_area_rect.
#         return detect_4_corners(points)
#     else:
#         #print(f"Shape hull has {n_hull} vertices, not 3 or 4. Using rectangle fallback.")
#         return detect_4_corners(points)

