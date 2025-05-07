#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 09:36:07 2025
Last modified on Fri Mar  7 09:36:07 2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module contains miscellaneous utility functions to support mesh processing and 
general operations. It provides a custom help display function, a utility to strip the outermost 
brackets from a string, and a function to sort two sets of points with numerical tolerance. These 
functions serve as common tools that enhance the functionality and maintainability of the codebase.
"""


import re
import builtins
import numpy as np

def help(obj):
    """
    Display help for an object.

    If the object has a 'help' method, it will be called. Otherwise, the built-in
    Python help() function will be invoked.

    Args:
        obj: The object for which help is to be displayed.

    Example:
        >>> help(my_object)
    """
    if hasattr(obj, 'help'):
        print(obj.help())
    else:
        _Helper = getattr(obj, '_Helper', None)  # Check if _Helper exists
        if _Helper:
            print(_Helper)
        else:
            builtins.help(obj)

def strip_brackets(aStr):
    """
    Removes only the outermost matching brackets, braces, or parentheses.

    Args:
        aStr (str): The input string to strip.

    Returns:
        str: The string without the outermost brackets, braces, or parentheses.

    Example:
        >>> strip_brackets("[example]")
        'example'
    """
    while True:
        stripped = re.sub(r'^[\[\(\{]\s*(.*?)\s*[\]\)\}]$', r'\1', aStr)
        if stripped == aStr:  # Stop if no further changes occur
            break
        aStr = stripped
    return aStr

def sort_points(pts0, pts1, epsilon=1e-8):
    """
    Sort two sets of points (pts0, pts1) while considering numerical tolerance.
    Ensures that sorting order is consistent across both point sets.

    Parameters:
        pts0, pts1 (np.ndarray): Point sets to be sorted.
        epsilon (float, optional): Numerical tolerance for rounding.

    Returns:
        tuple: Sorted points (sorted_pts0, sorted_pts1) and the respective sorted indices.
    """
    pts0_rounded = np.round(pts0, decimals=int(-np.log10(epsilon)))
    pts1_rounded = np.round(pts1, decimals=int(-np.log10(epsilon)))

    sorted_indices0 = np.lexsort( 
         (pts0_rounded[:, 2], pts0_rounded[:, 1], pts0_rounded[:, 0])
    )
    sorted_indices1 = np.lexsort(
        (pts1_rounded[:, 2], pts1_rounded[:, 1], pts1_rounded[:, 0])
    )
    
    sorted_pts0 = pts0[sorted_indices0]
    sorted_pts1 = pts1[sorted_indices1]
    
    return sorted_pts0, sorted_pts1, sorted_indices0, sorted_indices1

def format_math_output(value):
    """
    Format a numerical value according to specific precision rules.

    For values greater than or equal to 1, the number is rounded to the nearest integer.
    For values less than 1, the number is rounded to include digits up to and including
    the first non-zero digit after the decimal point.

    Parameters
    ----------
    value : float
        The numeric value to format.

    Returns
    -------
    int or float
        The formatted number as an integer if the input is >= 1, or as a float rounded
        appropriately if the input is < 1.

    Examples
    --------
    >>> format_math_output(12.345)
    12
    >>> format_math_output(0.002345)
    0.002
    >>> format_math_output(0.000034)
    3.4e-05
    """
    if value >= 1:
        return int(round(value))
    else:
        precision = abs(int(np.floor(np.log10(abs(value)))))
        return round(value, precision + 1)







