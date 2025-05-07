#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 14:38:23 2025

@author: sauvagea
"""
from pybmesh.utils.maths import genericFunction
import numpy as np
import matplotlib.pyplot as plt

def format_result(value):
    if value >= 1:
        return int(round(value))
    else:
        # Find number of decimal places until the first significant digit
        precision = abs(int(np.floor(np.log10(abs(value)))))
        return round(value, precision + 1)




if __name__ == "__main__":
    # Define three points (order does not matter)
    points = np.array([
                       [0,0],
                       [6325, 0.2], 
                       [864, 0.007], 
                       [1722, 0.1],
                       [119850, 2.04], 
                       [522500, 9.1],
                       [4887500, 91],
                       [38300000,1124],
                       ])

    # Instantiate the function object
    func = genericFunction(path="f_compute_time.pkl")

    # Identify and save the quadratic function that passes through the points
    func.identify(points)

    # Evaluate the function at x = 5 using the callable instance
    x_value = 8*4887500
    formatted_result = format_result(func(x_value))


    # Sort points by x-values for better visualization
    points = points[points[:, 0].argsort()]

    # Extract x and y
    x_points = points[:, 0]
    y_points = points[:, 1]

    # Generate a larger domain for plotting the function
    x_domain = np.linspace(min(x_points) - 2, max(x_points) + 4, 200)
    y_domain = func(x_domain)  # Use the already identified instance here

    # Plot
    plt.figure(figsize=(8, 6))
    # Plot the original points as crosses
    plt.plot(x_points, y_points, 'x', label='Reference Points', markersize=10, markeredgewidth=2)
    # Plot the identified function as a line
    plt.plot(x_domain, y_domain, '-', label='Identified Function')
    # Highlight the point at x = 5
    plt.plot(x_value, formatted_result, 'ro', label=f'f({x_value}) = {formatted_result:.2f}')

    # Labels and title
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('Quadratic Function Identification')
    plt.grid(True)
    plt.legend()
    plt.show()

    # Display function result again clearly
    print(f"f({x_value}) = {formatted_result}")
