#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 27/01/2025
Last modified on 12/02/2025

Author: Alexis Sauvageon
Email: alexis.sauvageon@gmail.com

Description: This module defines the Elem class, a base class that encapsulates a vtkUnstructuredGrid.
It provides fundamental geometric transformations (translation, rotation, scaling) on the
grid points, as well as utility methods for cleaning up and inspecting the elem data.

The Elem class also supports a unique part ID (pid), which associates each element to a specific mesh 
entity. Each part may have different characteristics (e.g., material type, steel, synthetic, etc.), 
distinguishing it from others within a larger mesh structur
"""

import vtk
import inspect
import numpy as np
from vtk.util import numpy_support
from pybmesh.utils.constants import _MAX_HEAD_TAIL, _TOL
from pybmesh.utils.colors import mapcolor


# -------------------------------------------------------------------------
# Elem Base Class with vtkUnstructuredGrid Storage
# -------------------------------------------------------------------------

class Elem:
    """
    Elem Base Class
    ---------------
    A base class that encapsulates a vtkUnstructuredGrid (stored in self._ugrid) and
    provides basic transformation operations such as translation, rotation, and scaling.
    Additionally, it includes methods to merge duplicate nodes, reverse the orientation
    of elements, create a deep copy of the elem, and generate a string representation.
    
    The class associates a **part ID (pid)** to each element, which represents a mesh entity. 
    This part ID is used to categorize and differentiate parts with unique characteristics (e.g., 
    material type, function, etc.), facilitating the management of complex meshes in simulation contexts.
    """

    def __init__(self, pid = 0):
        """
        Initialize an Elem instance.

        Parameters:
            pid (int): The **part ID** that identifies the mesh entity represented by this element.
                       Default is 0, but the ID can be set to any unique integer to differentiate 
                       the element in a mesh (e.g., for material types or other properties).
        """
        self._pid = pid
        self.color = mapcolor(pid)
        self._ugrid = vtk.vtkUnstructuredGrid()  # Each subclass must construct and populate this grid

    def translate(self, dx, dy, dz):
        """
        Translate all points in the elem's unstructured grid by (dx, dy, dz)
        using vtkTransform for better performance.
    
        Parameters:
            dx (float): Translation distance along the X-axis.
            dy (float): Translation distance along the Y-axis.
            dz (float): Translation distance along the Z-axis.
        """
        points = self._ugrid.GetPoints()
        if points is None:
            return
    
        # Create a vtkTransform for translation
        transform = vtk.vtkTransform()
        transform.Translate(dx, dy, dz)
    
        # Apply the transformation to all points
        transformFilter = vtk.vtkTransformFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputData(self._ugrid)
        transformFilter.Update()
    
        # Update the grid's points with the transformed points
        self._ugrid = transformFilter.GetOutput()
        
        # Mark the grid as modified
        self._ugrid.Modified()

    def rotate(self, center=None, axis=None, angle=None, angles=None, pA=None, pB = None):
        """
        Rotate all points in the elem's unstructured grid.
        
        Parameters:
            center (tuple): The center of rotation (default to origin).
            axis (tuple or str, optional): The rotation axis (x, y, z) as a tuple or a string ("x", "y", "z").
            angle (float): The rotation angle in degrees.
            angles (tuple): Tuple of three angles for rotation along X, Y, and Z axes.
            points (tuple): Two points defining the rotation axis and angle.
        """
        points = self._ugrid.GetPoints()
        if points is None:
            return
    
        # Create a vtkTransform for rotation
        transform = vtk.vtkTransform()
    
        if pA and pB is not None:
            if isinstance(pA,Elem):
                pA = pA.coords[0]
            if isinstance(pB,Elem):
                pB = pB.coords[0] 
            center = pA
                
        # Default center of rotation is (0, 0, 0) if not provided
        if center is None:
            center = (0, 0, 0)
        else :
            if isinstance(center,Elem):
                center=center.coords[0]
    
        transform.Translate(center[0], center[1], center[2])  # Translate to the origin
        
        # Convert axis from string to tuple if necessary
        if isinstance(axis, str):
            if axis.lower() == "x":
                axis = (1, 0, 0)
            elif axis.lower() == "y":
                axis = (0, 1, 0)
            elif axis.lower() == "z":
                axis = (0, 0, 1)
            else:
                raise ValueError("Axis must be 'x', 'y', 'z' or a tuple of 3 numbers.")
        
        if axis and angle is not None:
            # Rotate around a given axis and angle
            transform.RotateWXYZ(angle, axis[0], axis[1], axis[2])
        
        elif angles is not None:
            # Rotate by specified angles along X, Y, and Z axes
            transform.RotateX(angles[0])
            transform.RotateY(angles[1])
            transform.RotateZ(angles[2])
            
        elif pA and pB is not None:
            # Rotate around an axis defined by two points and a given angle
            axis = (pB[0] - pA[0], pB[1] - pA[1], pB[2] - pA[2])
            transform.RotateWXYZ(angle, axis[0], axis[1], axis[2])
        
        transform.Translate(-center[0], -center[1], -center[2])  # Translate back to the original center
        
        # Apply the transformation to all points
        transformFilter = vtk.vtkTransformFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputData(self._ugrid)
        transformFilter.Update()
    
        # Update the grid's points with the transformed points
        self._ugrid = transformFilter.GetOutput()
    
        # Mark the grid as modified
        self._ugrid.Modified()

    def scale(self, center=None, sx=1, sy=1, sz=1):
        """
        Scale all points in the elem's unstructured grid by the factors (sx, sy, sz)
        about the origin (0, 0, 0).
    
        Parameters:
            center (tuple): The center of rotation (default to center of mass).
            sx (float): Scaling factor along the X-axis.
            sy (float): Scaling factor along the Y-axis.
            sz (float): Scaling factor along the Z-axis.
        """
        points = self._ugrid.GetPoints()
        if points is None:
            return

        if center is None:
            center_of_mass = vtk.vtkCenterOfMass()
            center_of_mass.SetInputData(self._ugrid)  # Set the mesh data
            center_of_mass.Update()  # Compute the center of mass
            
            # Get the centroid (center of mass)
            center = center_of_mass.GetCenter()

        elif isinstance(center,Elem):
            center=center.coords[0]
    
        # Create a vtkTransform for scaling
        transform = vtk.vtkTransform()
        transform.Translate(center[0], center[1], center[2])
        transform.Scale(sx, sy, sz)
        transform.Translate(-center[0], -center[1], -center[2])
        # Apply the transformation to all points using vtkTransformFilter
        transformFilter = vtk.vtkTransformFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputData(self._ugrid)
        transformFilter.Update()
    
        # Update the grid's points with the transformed points
        self._ugrid = transformFilter.GetOutput()
    
        # Mark the grid as modified
        self._ugrid.Modified()

    def get_vtk_unstructured_grid(self):
        """
        Retrieve the underlying vtkUnstructuredGrid.

        Returns:
            vtkUnstructuredGrid: The elem's internal unstructured grid.
        """
        return self._ugrid
    
    def _set_vtk_unstructured_grid(self, ugrid):
        """
        Manually Set the underlying vtkUnstructuredGrid.

        Parameters:
            vtkUnstructuredGrid: A vtk unstructured grid.
        """
        self._ugrid = ugrid    

    def merge_duplicate_nodes(self, verbose=False, tol=_TOL):
        """
        Merge duplicate (coincident) nodes in the elem using VTK's vtkCleanUnstructuredGrid filter.

        This method identifies and merges points that are closer than the specified tolerance,
        and then updates the cell connectivity accordingly.

        Parameters:
            verbose (bool): If True, prints the number of duplicate nodes merged.
            tol (float) : The tolerance value for merging points (default is TOL from constants).

        Note:
            If no points are found in the grid, the method will print a message (if verbose) and return.
        """
        # Retrieve the current points from the grid
        old_points = self._ugrid.GetPoints()
        if old_points is None:
            if verbose:
                print("No points found in the elem.")
            return

        num_old_points = old_points.GetNumberOfPoints()

        # Set up the VTK cleaner to merge duplicate points
        cleaner = vtk.vtkCleanUnstructuredGrid()
        cleaner.SetInputData(self._ugrid)
        cleaner.SetTolerance(tol)
        cleaner.Update()

        # Retrieve the cleaned grid and its points
        new_grid = cleaner.GetOutput()
        new_points = new_grid.GetPoints()
        num_new_points = new_points.GetNumberOfPoints()
        duplicates_count = num_old_points - num_new_points

        # Replace the current grid with the cleaned grid and mark it as modified
        self._ugrid = new_grid
        self._ugrid.Modified()

        if verbose:
            print(f"Merged {duplicates_count} duplicate nodes (reduced from {num_old_points} to {num_new_points} unique nodes).")

    def reverse_orientation(self):
        """
        Reverse the orientation of all elements (1D, 2D, and 3D) in the unstructured grid.

        For each cell, the order of its point IDs is reversed, which has the effect of:
          - Reversing the direction of 1D elements (lines).
          - Flipping the normal of 2D elements (surfaces).
          - Reversing the orientation of 3D elements (volumes).
        """
        num_cells = self._ugrid.GetNumberOfCells()
        if num_cells == 0:
            return  # No cells to process

        # Create a new vtkCellArray to store cells with reversed connectivity
        modified_cells = vtk.vtkCellArray()

        # Process each cell individually
        for i in range(num_cells):
            cell = self._ugrid.GetCell(i)
            npts = cell.GetNumberOfPoints()

            # Reverse the order of point IDs in the cell
            cell_points = cell.GetPointIds()
            for j in range(npts // 2):
                id1 = cell_points.GetId(j)
                id2 = cell_points.GetId(npts - 1 - j)
                cell_points.SetId(j, id2)
                cell_points.SetId(npts - 1 - j, id1)

            # Insert the modified cell into the new cell array
            modified_cells.InsertNextCell(cell_points)

        # Update the grid with the modified cell connectivity and mark it as modified
        self._ugrid.SetCells(self._ugrid.GetCellTypesArray(), modified_cells)
        self._ugrid.Modified()

    def _generate_pid_field(self):
        """
        Create a field to associate the **part ID (pid)** with each cell in the grid.

        The part ID is stored in the unstructured grid's cell data, and it can be used to 
        identify or manipulate the element based on its mesh entity characteristics (such as material).

        The pid field is updated whenever the pid changes, ensuring consistency across the grid.
        """
        pidField = np.full(self._ugrid.GetNumberOfCells(), self.pid)
        vtk_pidField = numpy_support.numpy_to_vtk(pidField, deep=True, array_type=vtk.VTK_INT)
        vtk_pidField.SetName("pid")
        self._ugrid.GetCellData().AddArray(vtk_pidField)
        self._ugrid.Modified()

    def copy(self):
        """
        Create a deep copy of the elem.

        The method clones the internal vtkUnstructuredGrid and reinitializes a new instance
        of the current class with the copied grid and attributes.

        Returns:
            Elem: A new instance of the Elem (or subclass) that is a deep copy of the original.
        """
        # Create a new instance of the same type with the same color
        new_elem = type(self)(pid=self._pid)
        # Deep copy the unstructured grid
        new_ugrid = vtk.vtkUnstructuredGrid()
        new_ugrid.DeepCopy(self._ugrid)
        new_elem._ugrid = new_ugrid
        new_elem.pid = self._pid
        new_elem.color = self.color
        # If there are subclass-specific attributes, they should be copied here as needed.

        return new_elem

    def __repr__(self):
        """
        Generate a string representation of the Elem.

        The representation includes:
          - The number of nodes (points) in the grid.
          - The number of elements (cells) in the grid.
          - A list of nodes with their indices and coordinates.
          - A list of elements with their indices and connected point indices.

        If there are many nodes or elements, only the head and tail are shown.

        Returns:
            str: A formatted string representation of the Elem.
        """
        # Retrieve node and element counts
        num_nodes = self._ugrid.GetNumberOfPoints()
        num_elements = self._ugrid.GetNumberOfCells()

        # Collect node information
        vtk_points = self._ugrid.GetPoints()
        nodes_str = []
        for idx in range(num_nodes):
            pt = vtk_points.GetPoint(idx)
            nodes_str.append(f" {idx} ({pt[0]:.3f}, {pt[1]:.3f}, {pt[2]:.3f})")

        # Collect element (cell) information
        elements_str = []
        for idx in range(num_elements):
            cell = self._ugrid.GetCell(idx)
            point_ids = cell.GetPointIds()
            element_str = f" {idx} ("
            element_str += ", ".join(str(point_ids.GetId(i)) for i in range(point_ids.GetNumberOfIds()))
            element_str += ")"
            elements_str.append(element_str)

        # Condense the list if it exceeds the maximum head/tail display count
        if num_nodes > 2 * _MAX_HEAD_TAIL:
            nodes_str = nodes_str[:_MAX_HEAD_TAIL] + ["..."] + nodes_str[-_MAX_HEAD_TAIL:]
        if num_elements > 2 * _MAX_HEAD_TAIL:
            elements_str = elements_str[:_MAX_HEAD_TAIL] + ["..."] + elements_str[-_MAX_HEAD_TAIL:]

        # Build the final string representation
        repr_str = f"Elem\nNumber of Nodes: {num_nodes}\nNumber of Elements: {num_elements}\n"
        repr_str += "Nodes:\n" + "\n".join(nodes_str) + "\n"
        repr_str += "Elements:\n" + "\n".join(elements_str)

        return repr_str

    @property
    def pid(self):
        """
        Accessor for the part ID (pid) of the elem.

        The **part ID (pid)** represents a specific mesh entity and is used for categorization 
        and managing different parts within a mesh. This ID could be linked to material properties, 
        structural characteristics, or any other distinguishing feature for simulation or analysis.

        Returns:
            int: The part ID (pid).
        """
        return self._pid 

    @pid.setter
    def pid(self, value):
        """
        Setter for the part ID (pid).

        Sets the **part ID (pid)**, which identifies the mesh entity represented by this element.
        When the part ID is updated, the associated color and pid field in the grid are also updated.
        
        Parameters:
            value (int): The new part ID to be assigned to the elem. This ID must be unique to the mesh.
        """
        self._pid = value 
        self.color = mapcolor(self._pid)  
        self._generate_pid_field()  


    @classmethod
    def help(cls):
        """
        Return helpful information about the Elem class and its methods.
    
        The help text includes usage details for the constructor and all public methods,
        as well as an explanation of the part ID (pid), which is used to identify the mesh entity
        and its unique characteristics (e.g., material, function).
    
        Returns:
            str: A multi-line string with usage instructions.
        """
        help_text = """
Elem Class
-----------
A base class that encapsulates a vtkUnstructuredGrid and provides fundamental
transformations and utilities for elem manipulation. Each element is associated with a
unique **part ID (pid)** that identifies the mesh entity.

Constructor:
-------------
\033[1;32mElem(pid=0)\033[0m
  - \033[1;32mpid\033[0m: The part ID representing the mesh entity (default: 0). 

Public Attributes:
------------------
\033[1;32mcolor\033[0m
    The RGB color associated with the element. The color is determined by the pid
    and can be used for visualization purposes.  

Public Methods:
---------------
\033[1;34mtranslate(dx, dy, dz)\033[0m
    Translate all points in the elem by the vector (dx, dy, dz).
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
\033[1;34mmerge_duplicate_nodes(verbose=False, tol=TOL)\033[0m
    Merge duplicate nodes in the elem using VTK's cleaning filter.
\033[1;34mreverse_orientation()\033[0m
    Reverse the orientation of all elements in the elem.
\033[1;34mcopy()\033[0m
    Create a deep copy of the elem.
\033[1;34mpid\033[0m
    Accessor and setter for the part ID (pid). The pid uniquely identifies the element
    as a mesh entity with its own characteristics (e.g., material, function).
\033[1;34mget_vtk_unstructured_grid()\033[0m
    Retrieve the underlying vtkUnstructuredGrid.
    
Usage Example:
---------------
  elem = Elem(pid=1, color=(1, 0, 0))
  elem.translate(1, 2, 3)
  elem.rotate('z', 45)
  print(elem)

In the example above, the element is initialized with a part ID of 1, which could correspond
to a specific material (e.g., steel). The part ID allows differentiation of elements with
different properties within a mesh, such as their material type or structural behavior.
"""
        return help_text

class MeshComponent:
    global_region_counter = 0

    def __init__(self):
        """
        Initialize the MeshComponent instance.

        This instance manages mesh elements in two dictionaries:
          - 'internal': holds internal mesh elements.
          - 'boundary': holds boundary mesh elements.
        
        It also maintains:
          - A region mapping (regionMapping) that links a unique region ID to a descriptive string.
          - An internal counter (_auto_name_counter) for auto-generated names.
          - A placeholder (mesh) for a unified vtkUnstructuredGrid generated by compute().
        """
        self.internal = {}
        self.boundary = {}
        self._auto_name_counter = 0
        self.regionMapping = {}  # Maps region id to a string describing the element and its type.
        self._ugrid = None
        self.computed = False

    def add_internal(self, elem, name=None):
        """
        Add an element to the internal mesh dictionary.

        Parameters:
            elem (Elem): The mesh element to add.
            name (str, optional): The name to associate with the element.
                                  If omitted, the variable name will be deduced automatically.
        """
        if name is None:
            name = self._get_variable_name(elem)
        self.internal[name] = elem
        self.internal[name].pid = elem.pid
        self.computed = False

    def add_boundary(self, elem, name=None):
        """
        Add an element to the boundary mesh dictionary.

        Parameters:
            elem (Elem): The mesh element to add.
            name (str, optional): The name to associate with the element.
                                  If omitted, an attempt is made to deduce the variable name.
                                  If that fails, an auto-generated name is used.
        """
        if name is None:
            name = self._get_variable_name(elem)
            if name == "Unnamed":
                # Fallback: auto-generate a boundary name if no suitable name is found.
                name = f"boundary_{self._auto_name_counter}"
                self._auto_name_counter += 1
        self.boundary[name] = elem
        self.computed = False

    def _get_variable_name(self, obj):
        """
        Retrieve the variable name for a given object from the caller's local scope.

        Parameters:
            obj: The object for which to deduce the variable name.

        Returns:
            str: The deduced variable name, or "Unnamed" if not found.
        """
        # Traverse back two frames: current frame -> add_internal/add_boundary -> caller.
        frame = inspect.currentframe().f_back.f_back
        for var_name, var_val in frame.f_locals.items():
            if var_val is obj:
                return var_name
        return "Unnamed"

    def compute(self):
        """
        Merge all internal and boundary mesh elements into a single vtkUnstructuredGrid.

        For each mesh element:
          - Retrieve its vtkUnstructuredGrid representation.
          - Assign a unique region id (stored in a cell data array 'idRegion').
          - Update the regionMapping dictionary with a description (internal or boundary) and name.
          - Add the grid to a vtkAppendFilter to combine all elements.
        
        After merging:
          - Use vtkIdFilter to generate point and cell ID arrays ("pointID" and "cellID").
          - Preserve all existing cell data by reattaching the 'idRegion' array.

        The final merged grid is stored in self.ugrid.
        """
        self._ugrid_inside = self._compute_inside()
        
        
    def _compute_inside(self):
        """
        Merge all internal and boundary mesh elements into a single vtkUnstructuredGrid.

        For each mesh element:
          - Retrieve its vtkUnstructuredGrid representation.
          - Assign a unique region id (stored in a cell data array 'idRegion').
          - Update the regionMapping dictionary with a description (internal or boundary) and name.
          - Add the grid to a vtkAppendFilter to combine all elements.
        
        After merging:
          - Use vtkIdFilter to generate point and cell ID arrays ("pointID" and "cellID").
          - Preserve all existing cell data by reattaching the 'idRegion' array.

        The final merged grid is stored in self.ugrid.
        """
        append_filter = vtk.vtkAppendFilter()
        # region_id here is locally redefined for clarity, but global_region_counter is used for uniqueness.
        region_id = 0

        # Process internal mesh elements
        for name, elem in self.internal.items():
            ugrid = vtk.vtkUnstructuredGrid()  # create a new grid
            ugrid.DeepCopy(elem.get_vtk_unstructured_grid())              # copy the contents from ugrid
            num_cells = ugrid.GetNumberOfCells() 
            # Use the global region counter to ensure a unique region id.
            region_id = MeshComponent.global_region_counter
            MeshComponent.global_region_counter += 1

            # Create a NumPy array filled with the region id for all cells
            region_ids = np.full(num_cells, region_id, dtype=np.int32)
            vtk_region_ids = numpy_support.numpy_to_vtk(
                region_ids, deep=True, array_type=vtk.VTK_INT)
            vtk_region_ids.SetName("idRegion")

            # Add the region id array to the cell data and set it as the active scalars
            ugrid.GetCellData().AddArray(vtk_region_ids)
            ugrid.GetCellData().SetScalars(vtk_region_ids)

            # Record the mapping: region id to a descriptive string
            self.regionMapping[region_id] = f"internal: {name}"

            # Add this grid to the append filter for merging
            append_filter.AddInputData(ugrid)

        # Process boundary mesh elements
        for name, elem in self.boundary.items():
            ugrid = vtk.vtkUnstructuredGrid()  # create a new grid
            ugrid.DeepCopy(elem.get_vtk_unstructured_grid())     
            num_cells = ugrid.GetNumberOfCells()
            # Assign a new unique region id for boundary elements
            region_id = MeshComponent.global_region_counter
            MeshComponent.global_region_counter += 1

            region_ids = np.full(num_cells, region_id, dtype=np.int32)
            vtk_region_ids = numpy_support.numpy_to_vtk(
                region_ids, deep=True, array_type=vtk.VTK_INT)
            vtk_region_ids.SetName("idRegion")

            ugrid.GetCellData().AddArray(vtk_region_ids)
            ugrid.GetCellData().SetScalars(vtk_region_ids)

            # Record the mapping for this boundary element
            self.regionMapping[region_id] = f"boundary: {name}"

            # Add the boundary grid to the append filter
            append_filter.AddInputData(ugrid)

        # Configure the append filter to merge coincident points
        append_filter.MergePointsOn()
        append_filter.SetTolerance(_TOL)  # _TOL should be defined as a suitable tolerance value

        # Create an id filter to generate point and cell ID arrays without looping
        idFilter = vtk.vtkIdFilter()
        idFilter.SetInputConnection(append_filter.GetOutputPort())
        idFilter.PointIdsOn()      # Enable creation of point ID array
        idFilter.CellIdsOn()       # Enable creation of cell ID array
        idFilter.SetPointIdsArrayName("pointID")
        idFilter.SetCellIdsArrayName("cellID")
        idFilter.Update()

        # Retrieve the 'idRegion' array from the appended output.
        newCellRegionArray = append_filter.GetOutput().GetCellData().GetArray("idRegion")

        # Store the final merged grid with new ID arrays.
        self._ugrid = idFilter.GetOutput()
        # Reattach the region id array to ensure original cell data is preserved.
        self._ugrid.GetCellData().AddArray(newCellRegionArray)
        self.computed = True

    def retrieve_connectivity_by_region(self, region_identifier):
        """
        Retrieve the connectivity (cell data/point data) corresponding to a specific region.

        The region is identified either by:
          - An integer region id.
          - A string (or substring) that matches part of the region's description.

        Parameters:
            region_identifier (int or str): The region identifier.

        Returns:
            vtkUnstructuredGrid: A filtered mesh containing only the cells with the specified region id.

        Raises:
            ValueError: If the region_identifier type is not int or str, or if no matching region is found.
        """
        # Determine the numeric region id from the identifier
        region_id = None
        if isinstance(region_identifier, int):
            region_id = region_identifier
        elif isinstance(region_identifier, str):
            # Search the mapping for a region whose description contains the provided string
            for rid, desc in self.regionMapping.items():
                if region_identifier in desc:
                    region_id = rid
                    break
            if region_id is None:
                raise ValueError(
                    f"No region found with a description containing '{region_identifier}'")
        else:
            raise ValueError("region_identifier must be an int or str")

        # Ensure the merged mesh has been computed
        if self._ugrid is None:
            self.compute()

        # Use a threshold filter to extract cells corresponding to the specified region id.
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(self._ugrid)
        threshold.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "idRegion")
        # Use a narrow range around the region_id to isolate the cells.
        threshold.SetLowerThreshold(region_id - 0.01)
        threshold.SetUpperThreshold(region_id + 0.01)
        threshold.Update()

        return threshold.GetOutput()

    def __repr__(self):
        """
        Generate a string representation of the Mesh.

        Returns:
            str: A formatted string representation of the Mesh, including the internal and boundary elements.
        """
        repr_str  = "------------------\n"
        repr_str += "Internal Elements:\n"
        repr_str += "------------------\n"
        for name, elem in self.internal.items():
            repr_str += f"+++ {name}: {elem}\n"
            repr_str +='\n'
        repr_str += "------------------\n"
        repr_str += "Boundary Elements:\n"
        repr_str += "------------------\n"
        for name, elem in self.boundary.items():
            repr_str += f"+++ {name}: {elem}\n"
            repr_str +='\n'
        return repr_str

    def get_vtk_unstructured_grid(self):
        """
        Retrieve the underlying vtkUnstructuredGrid.

        Returns:
            vtkUnstructuredGrid: The elem's internal unstructured grid.
        """
        return self._ugrid
    
    @classmethod
    def help(cls):
        """
        Return helpful information about the MeshComponent class and its methods.

        The help text includes usage details for the constructor and all public methods,
        as well as explanations of the primary attributes used for managing mesh elements.

        Returns:
            str: A multi-line string with usage instructions.
        """
        help_text = """
MeshComponent Class
---------------------
A class that encapsulates a collection of mesh elements by dividing them into 
two groups: internal and boundary. This class provides utilities to add elements, 
merge them into a single vtkUnstructuredGrid, and retrieve connectivity based on 
a unique region identifier. Nodes are merged.

Constructor:
-------------
\033[1;32mMeshComponent()\033[0m
    Initializes a new MeshComponent with empty 'internal' and 'boundary' dictionaries.

Public Attributes:
------------------
\033[1;32minternal\033[0m
    Dictionary storing internal mesh elements.
\033[1;32mboundary\033[0m
    Dictionary storing boundary mesh elements.
\033[1;32mregionMapping\033[0m
    Dictionary mapping unique region IDs to descriptive strings indicating the 
    element's name and whether it is internal or boundary.

Public Methods:
---------------
\033[1;34madd_internal(elem, name=None)\033[0m
    Add a mesh element to the internal collection. If no name is provided, the 
    variable name is automatically deduced.
\033[1;34madd_boundary(elem, name=None)\033[0m
    Add a mesh element to the boundary collection. If no name is provided, the 
    variable name is deduced or an auto-generated name is used.
\033[1;34mcompute()\033[0m
    Merge all internal and boundary elements into a single vtkUnstructuredGrid ith node merging. 
    Each element is assigned a unique region ID stored in the cell data array 'idRegion', 
    and the merged grid includes automatically generated 'pointID' and 'cellID' arrays.
\033[1;34mretrieve_connectivity_by_region(region_identifier)\033[0m
    Retrieve a filtered vtkUnstructuredGrid containing only the cells with the 
    specified region ID. The region identifier can be an integer or a descriptive string.
\033[1;34mget_vtk_unstructured_grid()\033[0m
    Retrieve the underlying vtkUnstructuredGrid.

Usage Example:
---------------
  comp = MeshComponent()
  comp.add_internal(mesh1, "mesh1")
  comp.add_boundary(mesh2, "mesh2")
  comp.compute()
  grid = comp.retrieve_connectivity_by_region("mesh1")
  print(grid)

In this example, 'mesh1' is added as an internal element and 'mesh2' as a boundary element.
After merging, the MeshComponent provides a unified vtkUnstructuredGrid where each cell 
carries region information that can be used for further analysis or visualization.
"""
        return help_text
  
class MeshAssembly:
    def __init__(self):
        """
        Initialize the MeshAssembly instance.

        This instance aggregates MeshComponent objects by merging their mesh data.
        It maintains:
          - internal: Aggregated internal mesh elements.
          - boundary: Aggregated boundary mesh elements.
          - regionMapping: A mapping of unique region IDs to descriptive strings.
          - _lgrid: A list of vtkUnstructuredGrid objects from each MeshComponent.
        """
        self.internal = {}
        self.boundary = {}
        self._auto_name_counter = 0
        self.regionMapping = {}  # Maps region id to descriptive strings.
        self._lgrid = []         # List to store each MeshComponent's vtkUnstructuredGrid
        self._ugrid = None
        self.computed = False

    def add_component(self, component):
        """
        Add a MeshComponent to the assembly.

        This method:
          - Calls compute() on the component to ensure its vtkUnstructuredGrid is generated.
          - Updates the assembly's 'internal' and 'boundary' dictionaries using the component's elements.
          - Merges the component's regionMapping into the assembly's regionMapping.
          - Appends the component's computed vtkUnstructuredGrid (component.ugrid) to self._lgrid.

        Parameters:
            component (MeshComponent): A MeshComponent instance to incorporate into the assembly.
        """
        # Ensure the component has generated its vtkUnstructuredGrid.
        if not component.computed : component.compute()

        # Update the assembly dictionaries with the component's data.
        self.internal.update(component.internal)
        self.boundary.update(component.boundary)
        self.regionMapping.update(component.regionMapping)

        # Append the component's unstructured grid to the assembly's list.
        self._lgrid.append(component.get_vtk_unstructured_grid())
        self.computed = False

    def compute(self):
        """
        Merge all internal and boundary mesh elements into a single vtkUnstructuredGrid.

        For each mesh element:
          - Retrieve its vtkUnstructuredGrid representation.
          - Assign a unique region id (stored in a cell data array 'idRegion').
          - Update the regionMapping dictionary with a description (internal or boundary) and name.
          - Add the grid to a vtkAppendFilter to combine all elements.
        
        After merging:
          - Use vtkIdFilter to generate point and cell ID arrays ("pointID" and "cellID").
          - Preserve all existing cell data by reattaching the 'idRegion' array.

        The final merged grid is stored in self.ugrid.
        """
        append_filter = vtk.vtkAppendFilter()

        # Process internal mesh elements
        for ugrid in self._lgrid:
            append_filter.AddInputData(ugrid)
            
        # Configure the append filter to NOT merge coincident points
        append_filter.MergePointsOff()

        # Create an id filter to generate point and cell ID arrays without looping
        idFilter = vtk.vtkIdFilter()
        idFilter.SetInputConnection(append_filter.GetOutputPort())
        idFilter.PointIdsOn()      # Enable creation of point ID array
        idFilter.CellIdsOn()       # Enable creation of cell ID array
        idFilter.SetPointIdsArrayName("pointID")
        idFilter.SetCellIdsArrayName("cellID")
        idFilter.Update()
        # Retrieve the 'idRegion' array from the appended output.
        newCellRegionArray = append_filter.GetOutput().GetCellData().GetArray("idRegion")
        # Store the final merged grid with new ID arrays.
        self._ugrid = idFilter.GetOutput()
        # Reattach the region id array to ensure original cell data is preserved.
        self._ugrid.GetCellData().AddArray(newCellRegionArray)
        self.computed = True

    def retrieve_connectivity_by_region(self, region_identifier):
        """
        Retrieve the connectivity (cell data/point data) corresponding to a specific region.

        The region is identified either by:
          - An integer region id.
          - A string (or substring) that matches part of the region's description.

        Parameters:
            region_identifier (int or str): The region identifier.

        Returns:
            vtkUnstructuredGrid: A filtered mesh containing only the cells with the specified region id.

        Raises:
            ValueError: If the region_identifier type is not int or str, or if no matching region is found.
        """
        # Determine the numeric region id from the identifier
        region_id = None
        if isinstance(region_identifier, int):
            region_id = region_identifier
        elif isinstance(region_identifier, str):
            # Search the mapping for a region whose description contains the provided string
            for rid, desc in self.regionMapping.items():
                if region_identifier in desc:
                    region_id = rid
                    break
            if region_id is None:
                raise ValueError(
                    f"No region found with a description containing '{region_identifier}'")
        else:
            raise ValueError("region_identifier must be an int or str")

        # Ensure the merged mesh has been computed
        if self._ugrid is None:
            self.compute()

        # Use a threshold filter to extract cells corresponding to the specified region id.
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(self._ugrid)
        threshold.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "idRegion")
        # Use a narrow range around the region_id to isolate the cells.
        threshold.SetLowerThreshold(region_id - 0.01)
        threshold.SetUpperThreshold(region_id + 0.01)
        threshold.Update()

        return threshold.GetOutput()

    def __repr__(self):
        """
        Generate a string representation of the Mesh.

        Returns:
            str: A formatted string representation of the Mesh, including the internal and boundary elements.
        """
        repr_str  = "------------------\n"
        repr_str += "Internal Elements:\n"
        repr_str += "------------------\n"
        for name, elem in self.internal.items():
            repr_str += f"+++ {name}: {elem}\n"
            repr_str +='\n'
        repr_str += "------------------\n"
        repr_str += "Boundary Elements:\n"
        repr_str += "------------------\n"
        for name, elem in self.boundary.items():
            repr_str += f"+++ {name}: {elem}\n"
            repr_str +='\n'
        return repr_str

    def get_vtk_unstructured_grid(self):
        """
        Retrieve the underlying vtkUnstructuredGrid.

        Returns:
            vtkUnstructuredGrid: The elem's internal unstructured grid.
        """
        return self._ugrid
    
    @classmethod
    def help(cls):
        """
        Return helpful information about the MeshComponent class and its methods.

        The help text includes usage details for the constructor and all public methods,
        as well as explanations of the primary attributes used for managing mesh elements.

        Returns:
            str: A multi-line string with usage instructions.
        """
        help_text = """
MeshAssembly Class
---------------------
A class that encapsulates a collection of mesh components. This class provides utilities to add elements, 
merge them into a single vtkUnstructuredGrid, and retrieve connectivity based on 
a unique region identifier. Nodes are NOT merged.

Constructor:
-------------
\033[1;32mMeshComponent()\033[0m
    Initializes a new MeshAssembly with empty 'internal' and 'boundary' dictionaries.

Public Attributes:
------------------
\033[1;32minternal\033[0m
    Dictionary storing internal mesh elements.
\033[1;32mboundary\033[0m
    Dictionary storing boundary mesh elements.
\033[1;32mregionMapping\033[0m
    Dictionary mapping unique region IDs to descriptive strings indicating the 
    element's name and whether it is internal or boundary.

Public Methods:
---------------
\033[1;34madd_component(component\033[0m
    Add a mesh component to the assembly.
\033[1;34mcompute()\033[0m
    Merge all  components into a single vtkUnstructuredGrid with no node merging
\033[1;34mretrieve_connectivity_by_region(region_identifier)\033[0m
    Retrieve a filtered vtkUnstructuredGrid containing only the cells with the 
    specified region ID. The region identifier can be an integer or a descriptive string.
\033[1;34mget_vtk_unstructured_grid()\033[0m
    Retrieve the underlying vtkUnstructuredGrid.

Usage Example:
---------------
  comp = MeshComponent()
  comp.add_component(comp1)
  comp.add_component(comp2)
  comp.compute()
  grid = comp.retrieve_connectivity_by_region("mesh1")
  plot(comp)
"""
        return help_text