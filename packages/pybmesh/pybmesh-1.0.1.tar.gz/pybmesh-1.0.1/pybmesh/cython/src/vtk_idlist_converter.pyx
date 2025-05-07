# vtk_idlist_converter.pyx
# cython: language_level=3, boundscheck=False, wraparound=False
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION

import numpy as np
cimport numpy as np

def numpy_to_vtkIdList(np.ndarray[np.int64_t, ndim=1] cell_ids):
    """
    Convert a 1D NumPy array of cell IDs (int64) to a vtkIdList,
    using the Python VTK wrapper but with a Cython-compiled loop.
    """
    import vtk  # use the Python-wrapped VTK
    cdef int n = cell_ids.shape[0]
    # Create a vtkIdList using the Python API:
    id_list = vtk.vtkIdList()
    id_list.SetNumberOfIds(n)
    cdef Py_ssize_t i
    # Use np.intp_t to match the pointer-sized integer type
    cdef np.intp_t* data = <np.intp_t*> cell_ids.data
    for i in range(n):
        id_list.SetId(i, data[i])
    return id_list
