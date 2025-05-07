#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 16:35:38 2025

@author: sauvagea
"""
import os
import vtk
import numpy as np
import pandas as pd
from pybmesh.cython import FaceExtractor
from vtk.util import numpy_support
import vtkmodules.util.pickle_support
from importlib.resources import files, as_file
from pybmesh.geom.mesh import MeshComponent,MeshAssembly
from pybmesh.utils.miscutils import format_math_output
from pybmesh.utils.vtkquery import get_data
from pybmesh.utils.maths import genericFunction
from pybmesh.io.vtk2numpy import vtk_to_numpy_connectivity, mesh_to_numpy_connectivity, \
                                numpy_to_vtk_connectivity
                                                                           
class WriteFOAM:
    def __init__(self, mesh = None, output_dir = ".", patch_types ={}):
        self._mesh = mesh
        self.output_dir = output_dir+r"/constant/polyMesh"
        self.patch_types = patch_types
        
        # create repository
        os.makedirs(self.output_dir, exist_ok=True)
        open(os.path.join(output_dir, "mesh.foam"), "w").close()
        # retrieve connectivity data
        print("...retrieve connectivity data")
        self._ugrid  = self._mesh.get_vtk_unstructured_grid()
        self._points, self._cells, _ =  vtk_to_numpy_connectivity(self._ugrid)
        # make face connectivity
        print("...generate faces from cells")
        print("\x1B[3m   this step may take some time\x1B[0m")
        # evaluate time
        pkl_resource = files("pybmesh.ressources.foamTimeWriter").joinpath("f_compute_time.pkl")
        with as_file(pkl_resource) as pkl_path:
            f = genericFunction(path=str(pkl_path))
        formatted_time = format_math_output(f(len(self._cells)))
        print(f"\x1B[3m   ({len(self._cells)} cells ~{formatted_time}s)\x1B[0m")
        self._faces = self._make_face_connectivity()
        # save mesh files
        print("...saving files")
        self._make_points_file()
        self._faceMtrx = self._make_foam_df()
        self._make_faces_file()
        self._make_owner_file()
        self._make_neighbour_file()
        self._make_boundary_file()

    def _compute_key(self,points):
        """
        Compute a unique key for a face based on its points.
        The key is defined as a tuple of the sorted point IDs.
        """
        return tuple(sorted(points))
    
    def _compute_hashtag(self,key):
        """
        Given a key (a tuple of point IDs), return the hashtag string.
        """
        return "#" + "-".join(map(str, key))

    def _make_foam_df(self):
        """
        Optimized version for large number (~100M) of faces.
        Minimizes Python overhead and avoids storing the full face object 
        when building the DataFrame.
        """
        faces = self._faces.faces  # An iterable of face objects
        num_faces = len(faces)
    
        # First pass: count how many faces are internal vs boundary
        # so we can preallocate arrays of the correct size.
        internal_count = 0
        boundary_count = 0
        
        for face in faces:
            if len(face.owners) == 2:
                internal_count += 1
            else:
                boundary_count += 1
    
        # Preallocate NumPy arrays. Use object dtype for patchName since its a string.
        # If you want to store references to face objects, use object dtype for that column as well.
        internal_owner   = np.empty(internal_count, dtype=np.int64)
        internal_neighbor = np.empty(internal_count, dtype=np.int64)
        # If you need to store patch info for internal (you mention "internalCell"):
        internal_patch   = np.full(internal_count, "internalCell", dtype=object)
        boundary_patch   = np.empty(boundary_count, dtype=object)
        
        boundary_owner   = np.empty(boundary_count, dtype=np.int64)
        boundary_neighbor = np.full(boundary_count, np.nan)  # neighbor is NaN for boundary
    
        # If you need face references (be mindful of memory):       
        internal_point_list = np.empty(internal_count, dtype=object)
        boundary_point_list = np.empty(boundary_count, dtype=object)
        
        internal_nbpt_list = np.empty(internal_count, dtype=object)
        boundary_nbpt_list = np.empty(boundary_count, dtype=object)
        # internal_face_ref = np.empty(internal_count, dtype=object)
        # boundary_face_ref = np.empty(boundary_count, dtype=object)
    
        # Second pass: fill in the arrays
        i_int = 0
        i_bnd = 0
        for face in faces:
            o = face.owners  # owners array/list
            if len(o) == 2:
                internal_point_list[i_int] = "(" + " ".join(map(str, face.points)) + ")"  # if needed
                internal_nbpt_list[i_int] = len(face.points)
                internal_owner[i_int]   = min(o)
                internal_neighbor[i_int] = max(o)
                i_int += 1
            else:
                boundary_point_list[i_bnd] = "(" + " ".join(map(str, face.points)) + ")"
                boundary_nbpt_list[i_bnd] = len(face.points)
                boundary_patch[i_bnd]   = face.patchName or ""  # or some default
                boundary_owner[i_bnd]   = o[0]
                i_bnd += 1
    
        # --- Now we have two sets of columns for internal and boundary faces. ---
        # Build DataFrames from these arrays (much faster than building lists of tuples).
        df_internal = pd.DataFrame({
            'points' : internal_point_list,
            'nbpt' :   internal_nbpt_list,
            'patch': internal_patch,
            'owner': internal_owner,
            'neighbour': internal_neighbor
        })
    
        df_boundary = pd.DataFrame({
            'points' : boundary_point_list,
            'nbpt' :   boundary_nbpt_list,
            'patch': boundary_patch,
            'owner': boundary_owner,
            'neighbour': boundary_neighbor
        })
    
        # --- Sorting ---
        # 1) Sort internal faces by [owner, neighbour]
        df_internal.sort_values(by=['owner','neighbour'],
                                ascending=True, inplace=True)
    
        # 2) Sort boundary faces by [patch, owner, neighbour]
        df_boundary.sort_values(by=['patch','owner','neighbour'],
                                ascending=True, inplace=True)
    
        # 3) Concatenate
        df = pd.concat([df_internal, df_boundary], ignore_index=True)

        return df
        
    # Helper: OpenFOAM file header template
    def _make_header(f, cls, obj):
        return (
            "/*--------------------------------*- C++ -*----------------------------------*\\n"
            "| =========                 |                                                 |\n"
            "| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n"
            "|  \\    /   O peration     | Version:  2.3.0                                 |\n"
            "|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |\n"
            "|    \\/     M anipulation  |                                                 |\n"
            "\*---------------------------------------------------------------------------*/\n"
            "FoamFile\n{\n"
            "    version     2.0;\n"
            "    format      ascii;\n"
            f"    class       {cls};\n"
            "    location    \"constant/polyMesh\";\n"
            f"    object      {obj};\n"
            "}\n"
            "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n"
        ) 
        
    def _make_points_file(self):
        pstr = self._make_header("vectorField", "points")
        formatted_x = np.char.mod("%g", self._points[:, 0])
        formatted_y = np.char.mod("%g", self._points[:, 1])
        formatted_z = np.char.mod("%g", self._points[:, 2])
        rows = "(" + formatted_x + " " + formatted_y + " " + formatted_z + ")"
        pstr += f'{len(self._points)}\n'
        pstr += "(\n" + "\n".join(rows.tolist()) + "\n)"
        
        self._write_file("points", pstr)

    def _make_faces_file(self):
        """
        Create the 'faces' file.
        Order the faces so that internal faces (with 2 owners) come first,
        followed by boundary faces.
        Each face is written as: <nPoints>(pt0 pt1 ... pt(n-1))
        """
    
        # Build lines in a vectorized manner by concatenating columns
        # (nbpt might be numeric, so cast to string):
        face_lines = (
            self._faceMtrx['nbpt'].astype(str)
            + self._faceMtrx['points'].astype(str)
        ).tolist()
    
        # Prepare the final string
        pstr = self._make_header("faceList", "faces")
        pstr += (
            f"{len(face_lines)}\n(\n"
            + "\n".join(face_lines)
            + "\n)\n"
        )
    
        # Write the file
        self._write_file("faces", pstr)


    def _make_owner_file(self):
        """
        Create the 'owner' file.
        For each face (in the same order as in the faces file), the owner cell is:
          - For internal faces (2 owners): the lower-numbered cell (already stored in 'owner').
          - For boundary faces: the only cell (also in 'owner').
        """
        
        # Convert 'owner' column to int -> str in a vectorized way
        owner_str_list = self._faceMtrx['owner'].astype(int).astype(str).tolist()
        
        # Build output string
        nfaces = len(owner_str_list)
        pstr = self._make_header("labelList", "owner")
        pstr += f"{nfaces}\n(\n" + "\n".join(owner_str_list) + "\n)\n"
        
        # Write the file
        self._write_file("owner", pstr)

    def _make_neighbour_file(self):
        """
        Create the 'neighbour' file.
        Only internal faces (faces with 2 owners) are included.
        For each internal face, the neighbour is the cell that is not the owner
        (assuming owner = min(owner, neighbour), neighbour = max(owner, neighbour)).
        """
    
        # Select only rows that have a valid (non-null) neighbour
        _neighbourMtrx = self._faceMtrx[self._faceMtrx['neighbour'].notnull()]
    
        # Convert the 'neighbour' column to integers, then to strings (vectorized)
        neighbour_str_list = _neighbourMtrx['neighbour'].astype(int).astype(str).tolist()
    
        # Build the final string
        nfaces = len(neighbour_str_list)
        pstr = self._make_header("labelList", "neighbour")
        pstr += f"{nfaces}\n(\n" + "\n".join(neighbour_str_list) + "\n)\n"
    
        # Write the file
        self._write_file("neighbour", pstr)


    def _make_boundary_file(self):
        """
        Create the 'boundary' file more efficiently.
        We group once on the 'patch' column, then build the output in one pass.
        """
        # Filter out the 'internalCell' beforehand so we only group boundary faces
        boundary_df = self._faceMtrx.query("patch != 'internalCell'")
        
        # Group by patch
        patch_groups = boundary_df.groupby('patch')
        n_patches = len(patch_groups)
        
        # Use a list of strings and join at the end (faster than repeated concatenation)
        lines = []
        lines.append(self._make_header("polyBoundaryMesh", "boundary"))
        lines.append(f"{n_patches}\n(\n")
        
        # Build each patch entry
        for patch_name, patch_group in patch_groups:
            start_face = patch_group.index[0]  # first index as starting face
            n_faces = len(patch_group)         # number of faces in this patch
            # Assign patch type if specified, else default to "patch"
            patch_type = self.patch_types.get(patch_name, "patch")
            
            lines.append(f"    {patch_name}\n    {{\n")
            lines.append(f"        type            {patch_type};\n")
            if patch_type != "patch":
                lines.append(f"        inGroups        1({patch_type});\n")
            lines.append(f"        nFaces          {n_faces};\n")
            lines.append(f"        startFace       {start_face};\n")
            lines.append("    }\n")
        
        lines.append(")\n")
        
        # Join and write to file
        final_str = ''.join(lines)
        self._write_file("boundary", final_str)



    # def _make_faces_file(self):
    #     """
    #     Create the 'faces' file.
    #     Order the faces so that internal faces (with 2 owners) come first,
    #     followed by boundary faces.
    #     Each face is written as: <nPoints>(pt0 pt1 ... pt(n-1))
    #     """
    #     # Separate internal and boundary faces
    #     internal_faces = [face for face in self._faces.faces if len(face.owners) == 2]
    #     boundary_faces = [face for face in self._faces.faces if len(face.owners) == 1]
    #     boundary_faces = sorted(boundary_faces, key=lambda face: face.patchName or "")
    #     # Concatenate: internal faces first, then boundary
    #     self.ordered_faces = internal_faces + boundary_faces  
    #     nfaces = len(self.ordered_faces)
        
    #     face_lines = []
    #     for face in self.ordered_faces:
    #         line = f"{len(face.points)}(" + " ".join(map(str, face.points)) + ")"
    #         face_lines.append(line)
        
    #     pstr = self._make_header("faceList", "faces")
    #     pstr += f"{nfaces}\n(\n" + "\n".join(face_lines) + "\n)\n"
    #     self._write_file("faces", pstr)

    # def _make_owner_file(self):
    #     """
    #     Create the 'owner' file.
    #     For each face (in the same order as in the faces file), the owner cell is:
    #       - For internal faces (2 owners): the lower-numbered cell.
    #       - For boundary faces: the only cell.
    #     """
    #     owner_list = []
    #     for face in self.ordered_faces:
    #         if len(face.owners) == 2:
    #             owner = min(face.owners)
    #         else:
    #             owner = face.owners[0]
    #         owner_list.append(owner)
        
    #     nfaces = len(owner_list)
    #     pstr = self._make_header("labelList", "owner")
    #     pstr += f"{nfaces}\n(\n" + "\n".join(map(str, owner_list)) + "\n)\n"
    #     self._write_file("owner", pstr)

    # def _make_neighbour_file(self):
    #     """
    #     Create the 'neighbour' file.
    #     Only internal faces (faces with 2 owners) are included.
    #     For each internal face, the neighbour is the cell that is not the owner
    #     (assuming owner = min(owners), neighbour = max(owners)).
    #     """
    #     internal_faces = [face for face in self.ordered_faces if len(face.owners) == 2]
    #     neighbour_list = [max(face.owners) for face in internal_faces]
    #     nInternal = len(neighbour_list)
        
    #     pstr = self._make_header("labelList", "neighbour")
    #     pstr += f"{nInternal}\n(\n" + "\n".join(map(str, neighbour_list)) + "\n)\n"
    #     self._write_file("neighbour", pstr)

    # def _make_boundary_file(self):
    #     """
    #     Create the 'boundary' file.
    #     Group boundary faces (faces with 1 owner) by their patchName.
    #     Each patch entry includes the patch name, type (by default set to 'patch'
    #     or determined from self.patch_types), the number of faces in the patch,
    #     and the starting face index in the global faces list.
    #     """
    #     # Get indices of boundary faces from the ordered list.
    #     boundary_faces = [(i, face) for i, face in enumerate(self.ordered_faces) if len(face.owners) == 1]
    #     patch_groups = {}
    #     for idx, face in boundary_faces:
    #         patch = face.patchName if face.patchName is not None else "unknown"
    #         patch_groups.setdefault(patch, []).append(idx)
        
    #     nPatches = len(patch_groups)
    #     pstr = self._make_header("polyBoundaryMesh", "boundary")
    #     pstr += f"{nPatches}\n(\n"
    #     # It is assumed that the faces are already contiguous by patch.
    #     # For each patch, output its starting face index and number of faces.
    #     for patch in sorted(patch_groups.keys()):
    #         indices = sorted(patch_groups[patch])
    #         startFace = indices[0]
    #         nFaces = len(indices)
            
    #         # Determine patch type using the patch_types dict if provided.
    #         # If not provided or patch not in the dict, default to "patch".
    #         if self.patch_types and patch in self.patch_types:
    #             patch_type = self.patch_types[patch]
    #         else:
    #             patch_type = "patch"
            
    #         pstr += f"    {patch}\n"
    #         pstr += "    {\n"
    #         pstr += f"        type            {patch_type};\n"
    #         # If patch_type is not the default, include the inGroups line.
    #         if patch_type != "patch":
    #             pstr += f"        inGroups        1({patch_type});\n"
    #         pstr += f"        nFaces          {nFaces};\n"
    #         pstr += f"        startFace       {startFace};\n"
    #         pstr += "    }\n"
    #     pstr += ")\n"
    #     self._write_file("boundary", pstr)

    def _make_face_connectivity(self):
        """
        Generate connectivity for faces from a 3D unstructured grid.
        
        Optimizations:
          - Uses dictionary lookups for fast face retrieval.
          - Reduces unnecessary iterations.
          - Vectorized operations with NumPy for performance.
        
        Returns:
          - A list of Face objects.
        """
        # Extract face connectivity efficiently
        face_dict = FaceExtractor(self._ugrid)  # Extract all faces once
    
        # Convert cells array to NumPy for efficient slicing
        cells = np.array(self._cells, dtype=object)
        
        # Precompute boundary cell connectivity mappings to avoid redundant function calls
        boundary_mappings = {
            bc: self._mesh.retrieve_connectivity_by_region(bc) for bc in self._mesh.boundary.keys()
        }
    
        # Process boundary conditions efficiently
        for bc, ugbc in boundary_mappings.items():
            bc_cells_glob = get_data(ugbc, "cellID")  # Get global cell indices
            bc_cells = cells[bc_cells_glob]  # Slice all boundary cells at once
            
            # Generate keys for batch processing by computing key tuples.
            keys = [self._compute_key(bc_cells[i]) for i in range(len(bc_cells))]
            # # Generate hashtags for batch processing
            # hashtags = [
            #     "#" + "-".join(map(str, sorted(bc_cells[i]))) for i in range(len(bc_cells))
            # ]
        
            # Bulk update faces using dictionary lookups based on computed keys.
            for key in keys:
                face = face_dict.find_face(key)
                if face is not None:
                    face.patchName = str(bc)

        return face_dict

    def _write_file(self, filename, content):
        with open(self.output_dir+'/'+filename, "w") as file:
            file.write(content)         

    def __repr__(self):
        return f"Mesh with {len(self._cells)} cells written to {self.output_dir }"

# Now Coded in cython
# class Face:
#     """Data structure to represent a face of a 3D cell."""
#     def __init__(self, points, owners = None):
#         # Store face point IDs (sorted for consistency) and owners list
#         self.points = list(points)              # list of point IDs forming the face
#         self.owners = owners                   # list of owning cell IDs
#         self.isPatch = (len(owners) == 1)      # True if only one owner (boundary face)
#         self.patchName = None                  # name of patch if applicable (can be set later)
#         # Create a unique hashtag (independent of point order) for identification
#         sorted_ids = sorted(points)
#         self.hashtag = "#" + "-".join(map(str, sorted_ids))
        
#     def __repr__(self):
#         return f"<Face {self.hashtag} points={self.points} owners={self.owners} patchName={self.patchName}>"

# class FaceExtractor:
#     """Extracts faces from a vtkUnstructuredGrid and provides search/filter functionality."""
#     def __init__(self, unstructured_grid):
#         self.faces = []               # list of Face objects
#         self._face_map = {}           # dict mapping hashtag -> Face for quick lookup
#         a = time.time()
#         self._extract_faces(unstructured_grid)
#         b = time.time()
#         print("making face", b-a)

#     def _extract_faces(self, grid):
#         """
#         Identify all unique faces in the grid and store their owners.
#         This version creates Face objects on the fly.
#         """
#         grid = self.get3dMesh(grid)
#         num_cells = grid.GetNumberOfCells()
#         for cell_id in range(num_cells):
#             cell = grid.GetCell(cell_id)
#             n_faces = cell.GetNumberOfFaces()
#             for j in range(n_faces):
#                 face_cell = cell.GetFace(j)
#                 pts = face_cell.GetPointIds()
#                 # Get face vertices in their original order as returned by VTK
#                 face_pts = [pts.GetId(k) for k in range(pts.GetNumberOfIds())]
#                 # # Create key and hashtag from sorted point IDs
#                 face_key = tuple(sorted(face_pts))
#                 hashtag = "#" + "-".join(map(str, face_key))
#                 if hashtag in self._face_map:
#                     # Face already exists: update its owners list
#                     face_obj = self._face_map[hashtag]
#                     face_obj.owners.append(cell_id)
#                     # Update isPatch flag if now shared by more than one cell
#                     if len(face_obj.owners) > 1:
#                         face_obj.isPatch = False
#                 else:
#                     # Create a new Face on the fly
#                     face = Face(points=face_pts, owners=[cell_id])
#                     # Mark patch name if it is a boundary face
#                     if face.isPatch:
#                         face.patchName = "Boundary"
#                     self.faces.append(face)
#                     self._face_map[hashtag] = face
    
#     def filter_faces(self, is_patch=True):
#         """Return a list of faces filtered by patch status."""
#         return [face for face in self.faces if face.isPatch == is_patch]
    
#     def find_face(self, hashtag):
#         """Efficiently find and return a face by its hashtag identifier."""
#         return self._face_map.get(hashtag)

#     def get3dMesh(self, ugrid):
#         cellTypesVtk = ugrid.GetCellTypesArray()
#         cellTypes = numpy_support.vtk_to_numpy(cellTypesVtk)
        
#         # Define the set of VTK cell type codes considered 3D.
#         # Common 3D types: Tetra (10), Voxel (11), Hexahedron (12), Wedge (13), Pyramid (14)
#         # Some VTK versions also define Polyhedron (42) and higher order types.
#         three_d_types = {10, 11, 12, 13, 14, 42, 24, 25}  # adjust as needed
        
#         # Create a new numpy array: 1 if the cell type is in the 3D set, else 0.
#         is3D = np.isin(cellTypes, list(three_d_types)).astype(np.uint8)
        
#         # Convert the numpy array back to a VTK array.
#         is3D_vtk = numpy_support.numpy_to_vtk(is3D, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
#         is3D_vtk.SetName("Is3D")
#         ugrid.GetCellData().AddArray(is3D_vtk)
        
#         threshold = vtk.vtkThreshold()
#         threshold.SetInputData(ugrid)
        
#         # Specify the array to process: field "Is3D" from cell data.
#         threshold.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "Is3D")
        
#         # Set threshold to extract cells with Is3D value equal to 1.
#         threshold.SetLowerThreshold(1)
#         threshold.SetUpperThreshold(1)
#         threshold.Update()
        
#         # The output is a vtkUnstructuredGrid containing only 3D cells.
#         return threshold.GetOutput()
        

#     def __repr__(self):
#         return "\n".join([str(face) for face in self.faces])

