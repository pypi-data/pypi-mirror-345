# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True

from vtk.util import numpy_support
import numpy as np
import vtk

cdef class Face:
    """
    Represents a face of a 3D cell.
    Stores the face's point IDs (unsorted as given) and a sorted tuple (key) used for identification.
    """
    cdef public list points      # original face point IDs (in order returned by VTK)
    cdef public list owners      # list of owning cell IDs
    cdef public bint isPatch     # True if face belongs to one cell (boundary)
    cdef public object patchName # name for patch if applicable
    cdef public tuple key        # sorted tuple of point IDs used as dictionary key

    def __init__(self, list points, list owners):
        # Store a copy of points and owners
        self.points = points[:]       
        self.owners = owners          
        self.isPatch = (len(owners) == 1)
        self.patchName = None
        # Compute a sorted tuple to serve as a unique key (avoids Python string operations)
        self.key = tuple(sorted(points))
        
    def __repr__(self):
        return f"<Face key={self.key} points={self.points} owners={self.owners} patchName={self.patchName}>"

cdef class FaceExtractor:
    """
    Extracts faces from a vtkUnstructuredGrid.
    Uses a dictionary with tuple keys to avoid costly string operations.
    """
    cdef public list faces           # list of Face objects
    cdef dict _face_map              # maps tuple key -> Face

    def __init__(self, unstructured_grid):
        self.faces = []
        self._face_map = {}
        grid = self.get3dMesh(unstructured_grid)
        self._extract_faces(grid)

    cpdef _extract_faces(self, grid):
        """
        Identify all unique faces in the grid and store their owners.
        The key is now a tuple of sorted point IDs.
        """

        cdef int num_cells = grid.GetNumberOfCells()
        cdef int cell_id, j, k, num_face_ids, n_faces
        cdef object cell, face_cell, pts, face_obj, face
        cdef list face_pts
        cdef tuple key_tuple


        for cell_id in range(num_cells):
            cell = grid.GetCell(cell_id)
            n_faces = cell.GetNumberOfFaces()
            for j in range(n_faces):
                face_cell = cell.GetFace(j)
                pts = face_cell.GetPointIds()
                num_face_ids = pts.GetNumberOfIds()
                # Preallocate list for face point IDs
                face_pts = [0] * num_face_ids
                for k in range(num_face_ids):
                    face_pts[k] = pts.GetId(k)
                # Use tuple of sorted point IDs as the unique key
                key_tuple = tuple(sorted(face_pts))
                face_obj = self._face_map.get(key_tuple)
                if face_obj is None:
                    face = Face(face_pts, [cell_id])
                    if face.isPatch:
                        face.patchName = "Boundary"
                    self.faces.append(face)
                    self._face_map[key_tuple] = face
                else:
                   face_obj = self._face_map[key_tuple]
                   face_obj.owners.append(cell_id)
                   if len(face_obj.owners) > 1:
                       face_obj.isPatch = False


    cpdef list filter_faces(self, bint is_patch=True):
        """Return a list of faces filtered by patch status."""
        return [face for face in self.faces if face.isPatch == is_patch]

    cpdef object find_face(self, tuple key):
        """Efficiently find and return a face by its tuple key."""
        return self._face_map.get(key)

    cpdef object get3dMesh(self, object ugrid):
        """
        Extract only the 3D cells from the unstructured grid.
        Uses a threshold filter on a computed 'Is3D' cell data array.
        """
        cellTypesVtk = ugrid.GetCellTypesArray()
        cellTypes = numpy_support.vtk_to_numpy(cellTypesVtk)
        
        # Define common 3D VTK cell type codes.
        three_d_types = {10, 11, 12, 13, 14, 42, 24, 25}
        
        # Create a boolean mask: 1 if the cell type is in three_d_types, else 0.
        is3D = np.isin(cellTypes, np.array(list(three_d_types))).astype(np.uint8)
        is3D_vtk = numpy_support.numpy_to_vtk(is3D, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        is3D_vtk.SetName("Is3D")
        ugrid.GetCellData().AddArray(is3D_vtk)
        
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(ugrid)
        threshold.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "Is3D")
        threshold.SetLowerThreshold(1)
        threshold.SetUpperThreshold(1)
        threshold.Update()
        
        return threshold.GetOutput()

    def __repr__(self):
        return "\n".join([str(face) for face in self.faces])
