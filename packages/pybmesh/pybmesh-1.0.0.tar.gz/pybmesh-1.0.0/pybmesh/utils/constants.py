#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 27/01/2025
Last modified on 07/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@arep.fr
Company: AREP

Description: This file defines constants used in meshing, including point and font sizes,
print options, tolerance values, and a dictionary for icons...
"""
import importlib.resources as resources

# Define point and font sizes
_POINTSIZE = 10
_FONTSIZE = 10

# Define print option
_MAX_HEAD_TAIL = 5
_MAX_ITEM_DISPLAYED = 500
_TOL = 1e-8 # geometric tolerance

# Space colors
_NB_SPACE_COLOR_DIM = 16

# ICONS
_ICON_DICT = {
    "global_axis": str(resources.files("pybmesh.ressources.images").joinpath("cos.png")),
    "reset_view": str(resources.files("pybmesh.ressources.images").joinpath("reset_view.png")),
    "top_view": str(resources.files("pybmesh.ressources.images").joinpath("top.png")),
    "left_view": str(resources.files("pybmesh.ressources.images").joinpath("left.png")),
    "front_view": str(resources.files("pybmesh.ressources.images").joinpath("front.png")),
    "isometric_view": str(resources.files("pybmesh.ressources.images").joinpath("iso.png")),
}
# _ICON_DICT = {
#     "global_axis":r"../ressources/images/cos.png",
#     "reset_view": r"../ressources/images/reset_view.png",
#     "top_view" : r"../ressources/images/top.png",
#     "left_view": r"../ressources/images/left.png",
#     "front_view": r"../ressources/images/front.png",
#     "isometric_view": r"../ressources/images/iso.png"
# }

