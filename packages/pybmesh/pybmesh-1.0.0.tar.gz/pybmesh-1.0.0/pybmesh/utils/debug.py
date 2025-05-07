#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 14:00:30 2025

@author: sauvagea
"""
import matplotlib.pyplot as plt


def plot_points_with_corners(points, corner_mask):
    """
    Plots the points, highlighting corners in a distinct color/marker.
    """
    plt.figure(figsize=(6, 5))
    
    # Plot all points
    plt.plot(points[:, 0], points[:, 1], 'ko', label='Points')
    
    # Highlight corners
    corners = points[corner_mask]
    plt.plot(corners[:, 0], corners[:, 1], 'ro', label='Corners', markersize=10)
    
    # Optionally: connect the points in their boundary order
    # (useful if they form a shape)
    plt.plot(points[:,0], points[:,1], 'k--', alpha=0.3)
    
    # Make it look nicer
    plt.axis('equal')
    plt.title("Points with Detected Corners")
    plt.legend()
    plt.show()