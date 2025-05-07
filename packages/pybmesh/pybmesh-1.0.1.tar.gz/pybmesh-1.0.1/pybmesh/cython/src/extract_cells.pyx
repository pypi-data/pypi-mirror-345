# extract_cells.pyx
# cython: language_level=3, boundscheck=False, wraparound=False
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION

import numpy as np
cimport numpy as np

def extract_cells(np.ndarray[np.intp_t, ndim=1] off,
                  np.ndarray[np.int64_t, ndim=1] connectivity):
    """
    Given:
      - off: a 1D NumPy array of type np.intp containing cell boundary indices.
      - connectivity: a 1D NumPy array of type np.int64 containing the flat connectivity.
      
    Returns a Python list of NumPy array views, one per cell.
    """
    cdef Py_ssize_t n = off.shape[0] - 1
    cdef Py_ssize_t i, start, end
    cdef list cells_list = [None] * n
    for i in range(n):
        start = off[i]
        end = off[i+1]
        cells_list[i] = connectivity[start:end]
    return cells_list
