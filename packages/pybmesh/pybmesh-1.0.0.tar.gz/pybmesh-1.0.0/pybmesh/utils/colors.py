#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 12:26:44 2025
Last modified on 12/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module provides utility functions for color mapping and manipulation.
It includes a function `mapcolor(k)` that maps an integer to a color in a defined color chart.
The chart is structured with base colors and variations, allowing for a wide range of color outputs.
The function utilizes HSV-to-RGB conversion to generate colors, with gradual fading from base hues to black.
The module also imports predefined constants and color dimensions to handle color space efficiently.
"""
import numpy as np
import matplotlib.colors as mcolors
from pybmesh.utils.constants import _NB_SPACE_COLOR_DIM

# Define colors as individual variables (with RGB values between 0 and 1)
_BLACK = (0.0, 0.0, 0.0)
_WHITE = (1.0, 1.0, 1.0)
_BLUE = (83/255, 116/255, 181/255)
_GOLD = (199/255, 166/255, 116/255)
_RED = (205/255, 85/255, 87/255)
_PINK = (238/255, 119/255, 201/255)
_GREEN = (34/255, 139/255, 34/255)
_ORANGE = (255/255, 165/255, 0/255)
_PURPLE = (128/255, 0/255, 128/255)
_YELLOW = (255/255, 255/255, 0/255)
_CYAN = (0/255, 255/255, 255/255)
_MAGENTA = (255/255, 0/255, 255/255)
_BROWN = (139/255, 69/255, 19/255)
_GRAY = (169/255, 169/255, 169/255)
_TURQUOISE = (64/255, 224/255, 208/255)
_LIME = (0/255, 255/255, 0/255)
_INDIGO = (75/255, 0/255, 130/255)
_VIOLET = (238/255, 130/255, 238/255)
_NAVY = (0/255, 0/255, 128/255)
_TEAL = (0/255, 128/255, 128/255)
_TOMATO = (255/255, 99/255, 71/255)
_SALMON = (250/255, 128/255, 114/255)
_TAN = (210/255, 180/255, 140/255)
_CORAL = (255/255, 127/255, 80/255)
_PEACH = (255/255, 218/255, 185/255)
_MINT = (189/255, 252/255, 201/255)
_LEMON = (255/255, 247/255, 153/255)
_CHARTREUSE = (223/255, 255/255, 0/255)
_TURQUOISE_BLUE = (0/255, 199/255, 140/255)
_SLATE = (112/255, 128/255, 144/255)
_ROSE = (255/255, 102/255, 204/255)
_PLUM = (221/255, 160/255, 221/255)


def mapcolor(k):
    """
    Maps an integer k to a color in a color chart with j base colors and i variations per base color.
    Each column represents a base color, and each row represents a variation of that color.

    Parameters:
        k (int): The integer representing the color index to map.

    Returns:
        tuple: The RGB color corresponding to the given index k in the chart.
    
    Notes:
        - k == 0 maps to black (0, 0, 0).
        - k == -1 maps to white (1, 1, 1).
        - For other values of k, the function calculates a color using HSV to RGB conversion,
          distributing hues evenly across the spectrum and fading to black as the row index increases.
    """
    if k == 0:
        return (0, 0, 0)  # Black for k = -1
    elif k == -1:
        return (1, 1, 1)  # White for k = -2
    
    i = _NB_SPACE_COLOR_DIM  # Number of variations per base color
    j = _NB_SPACE_COLOR_DIM  # Number of base colors (columns)
    
    # Determine column (base color)
    k = k-1
    col = k % j
    # Determine row (variation of base color)
    row = (k - (k % j)) // j
    
    # Set base colors (Hues)
    base_hues = np.linspace(0, 1, j)  # Distribute base hues across the spectrum
    
    # Interpolate between base color and black based on the row
    hue = base_hues[col]
    saturation = 1  # Full saturation
    value = 1.1 - (row / (i - 1))  # Gradual fade to black (from 1 to 0)
    
    # Convert HSV to RGB
    rgb = mcolors.hsv_to_rgb([hue, saturation, value])
    
    return tuple(rgb)  # Return the color as an RGB tuple