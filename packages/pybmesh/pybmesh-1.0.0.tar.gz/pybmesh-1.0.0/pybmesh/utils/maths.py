#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 09:36:07 2025
Last modified on Fri Mar  7 09:36:07 2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module contains mathematical utility functions for mesh processing and geometric calculations.
It includes functions for computing the volume of a tetrahedron from its 3D points, normalizing 3D vectors, and 
generating rotation matrices using Rodrigues' rotation formula. These functions facilitate various geometric 
transformations and analyses in mesh-related applications.
"""

import numpy as np
import pickle
from scipy.optimize import curve_fit


def compute_tetrahedron_volume(points):
    """
    Compute the volume of a tetrahedron based on its points in 3D.
    The points array should contain 4 points, and each point is a 3D coordinate.
    
    Returns the volume of the tetrahedron (positive value if it's valid, zero or negative if invalid).
    """
    # Create a matrix based on the coordinates of the 4 points
    matrix = np.ones((4, 4))
    for i in range(4):
        matrix[i, :3] = points[i]
    
    # The volume is the determinant of the matrix formed by the points
    volume = np.linalg.det(matrix)
    return abs(volume) / 6  # Volume of a tetrahedron is 1/6 * determinant

def normalize(v):
    """
    Normalize a 3D vector (returning a new array).

    Args:
        v (np.ndarray): The vector to normalize.

    Returns:
        np.ndarray: The normalized vector.

    Raises:
        ValueError: If the vector has zero length.

    Example:
        >>> normalize(np.array([1, 2, 3]))
        array([0.26726124, 0.53452248, 0.80178373])
    """
    norm = np.linalg.norm(v)
    if norm < 1e-14:
        raise ValueError("Cannot normalize a zero-length vector.")
    return v / norm

def get_rotation_matrix(axis, angle):
    """
    Generates a rotimport numpy as np

ation matrix for rotating points around a given axis by a specific angle.

    Parameters:
    - axis: The axis to rotate around (a 3D vector).
    - angle: The angle of rotation in radians.

    Returns:
    - A 3x3 rotation matrix.
    """
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)
    ux, uy, uz = axis

    # Rotation matrix (Rodrigues' rotation formula)
    rotation_matrix = np.array([
        [cos_angle + ux**2 * (1 - cos_angle), ux * uy * (1 - cos_angle) - uz * sin_angle, ux * uz * (1 - cos_angle) + uy * sin_angle],
        [uy * ux * (1 - cos_angle) + uz * sin_angle, cos_angle + uy**2 * (1 - cos_angle), uy * uz * (1 - cos_angle) - ux * sin_angle],
        [uz * ux * (1 - cos_angle) - uy * sin_angle, uz * uy * (1 - cos_angle) + ux * sin_angle, cos_angle + uz**2 * (1 - cos_angle)]
    ])
    return rotation_matrix   

def get_permutation_function(cella, cellb):
    """
    Given two lists (or arrays) cella and cellb (where cellb is a permutation of cella),
    returns a transformation function f such that f(cella) == cellb,
    along with the permutation indices for reference.
    
    Parameters:
    - cella: Original list of elements.
    - cellb: Permuted list of the same elements.
    
    Returns:
    - f: A function that transforms any sequence (list or numpy array) from the cella ordering
         to the cellb ordering.
    - perm_indices: The list of indices representing the permutation.
    """
    # Check that both cells contain the same elements
    if sorted(cella) != sorted(cellb):
        raise ValueError("cella and cellb must be permutations of each other.")
    
    # Create a mapping from each value in cella to its index
    mapping = {val: idx for idx, val in enumerate(cella)}
    
    # Compute the permutation indices for cellb:
    # For each value in cellb, find the corresponding index in cella.
    perm_indices = [mapping[val] for val in cellb]
    
    # Define the transformation function
    def f(x):
        # x is assumed to have the same order as cella.
        if isinstance(x, np.ndarray):
            return x[np.array(perm_indices)]
        else:
            return [x[i] for i in perm_indices]
    
    return f, perm_indices

    # # Example usage:
    # cella = [np.int64(191), np.int64(192), np.int64(202), np.int64(201), np.int64(401), np.int64(402)]
    # cellb = [201, 401, 191, 202, 402, 192]
    
    # # Get the transformation function and the permutation mapping.
    # f, perm = get_permutation_function(cella, cellb)
    

class genericFunction:
    def __init__(self, path="function.pkl"):
        """
        Instantiate a function object.
        
        Parameters:
            path (str): File path to save/load the function parameters.
        """
        self.path = path

    def __call__(self, x):
        """
        Evaluate the stored quadratic function at x.
        
        Parameters:
            x (float or array-like): The point(s) at which to evaluate the function.
            
        Returns:
            float or np.ndarray: The function value f(x).
        """
        # Load the polynomial coefficients from file
        with open(self.path, "rb") as f:
            coeffs = pickle.load(f)
        # Evaluate the quadratic: f(x) = a*x^2 + b*x + c
        return coeffs[0] * np.power(x, 2) + coeffs[1] * x + coeffs[2]

    def identify(self, points):
        """
        Identify the best quadratic function that passes through the given points using 
        an advanced curve-fitting method, and save its parameters.
        
        The quadratic function is defined as:
            f(x) = a*x^2 + b*x + c
        
        Parameters:
            points (list): A list of three points, each given as [x, y]. 
                           The points may be provided in any order.
        """
        # Sort points by x-value for consistency
        points = sorted(points, key=lambda p: p[0])
        xs = np.array([p[0] for p in points])
        ys = np.array([p[1] for p in points])
        
        # Define the quadratic function to fit
        def quadratic(x, a, b, c):
            return a * x**2 + b * x + c
        
        # Use curve_fit to find the best parameters (advanced fitting)
        popt, _ = curve_fit(quadratic, xs, ys, p0=[1, 1, 1])
        
        # Save the coefficients [a, b, c] to the specified path using pickle
        with open(self.path, "wb") as f:
            pickle.dump(popt, f)
        
        print(f"Function identified and saved to '{self.path}'.")


def ragged_to_matrix(data, n_cols=8, fill=0, dtype=None):
    """
    Turn a ragged list-of-lists into an (n_rows × n_cols) NumPy array,
    padding with `fill` (which may be np.nan) or truncating longer rows,
    without any Python-level loops in the hot path.

    Parameters
    ----------
    data : Sequence of sequences of scalars
        Your ragged input, e.g. list-of-lists of ints.
    n_cols : int
        Number of columns in the output matrix.
    fill : scalar
        Value to pad with (can be np.nan).
    dtype : np.dtype or type, optional
        If not provided, inferred from `fill`:  
          - `float` if `fill` is a float (or np.nan)  
          - otherwise `int`
    Returns
    -------
    mat : np.ndarray, shape (n_rows, n_cols)
    """
    # Ensure we have a simple Python list for iteration of lengths
    data = list(data)
    n_rows = len(data)

    # 1) Compute per-row lengths, clipped to n_cols
    lengths = np.fromiter((min(len(r), n_cols) for r in data),
                          dtype=np.intp, count=n_rows)

    # 2) Infer dtype if needed
    if dtype is None:
        dtype = float if isinstance(fill, float) else int

    # 3) Pre-allocate the output full of `fill`
    mat = np.full((n_rows, n_cols), fill, dtype=dtype)

    # 4) Build the 1D arrays of all real values + their (row, col) indices
    #     flat_vals: concatenated first `lengths[i]` elements of data[i]
    flat_vals = np.concatenate([
        np.array(r[:L], dtype=dtype)
        for r, L in zip(data, lengths)
    ])

    #     row_idx: repeats row i, lengths[i] times
    row_idx = np.repeat(np.arange(n_rows, dtype=np.intp), lengths)

    #     col_idx: 0,1,..,lengths[i]-1 for each row i
    col_idx = np.concatenate([np.arange(L, dtype=np.intp) for L in lengths])

    # 5) Bulk-assign in one C-loop
    mat[row_idx, col_idx] = flat_vals

    return mat


def matrix_to_ragged(mat: np.ndarray, fill=0):
    """
    Invert a padded (n_rows × n_cols) matrix back into
    a list-of-lists by stripping off trailing `fill` values,
    ensuring all entries are ints, and swapping elements 2 & 3
    whenever a row has exactly 4 real entries.
    """
    # Build boolean mask of real vs pad entries
    if isinstance(fill, float) and np.isnan(fill):
        mask = ~np.isnan(mat)
    else:
        mask = mat != fill

    result = []
    for row, m in zip(mat, mask):
        # 1) select only real entries, cast to int, convert to Python list
        vals = row[m].astype(int).tolist()
        # 2) if exactly four real entries, swap positions 2 and 3
        if len(vals) == 4:
            vals[2], vals[3] = vals[3], vals[2]
        result.append(vals)

    return result
    return [row[:L].tolist() for row, L in zip(mat, lengths)]