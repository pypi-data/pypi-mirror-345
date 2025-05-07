from .geom.mesh import Elem, MeshComponent, MeshAssembly
from .geom.d0 import Point
from .geom.d1 import Line, PolyLine, Arc, Circle
from .geom.d2 import Surface
from .geom.d3 import Volume
from .io.viewer import Viewer, plot
from .io.write import WriteFOAM
from .utils.maths import (
    normalize,
    get_rotation_matrix,
    compute_tetrahedron_volume,
    get_permutation_function,
    genericFunction,
    ragged_to_matrix,
    matrix_to_ragged
)
from .utils.vtkquery import (
    nbEl,
    nbPt,
    elSize,
    findPoints,
    findElems,
    get_data,
)
from .io.vtk2numpy import (
    to_array,
    vtk_to_numpy_connectivity,
    mesh_to_numpy_connectivity,
    numpy_to_vtk_connectivity
)
from .utils.vtkcorrection import (
    are_dupNodes,
    are_id_oriented,
    check_mesh_quality,
    check_mesh_validity,
    fix_pyramid_connectivity,
    fix_wedge_connectivity,
    regen
)
from .utils.miscutils import (
    help,
    strip_brackets,
    sort_points,
    format_math_output
)
from .utils.meshtools import (
    save_to_vtk,
    translate,
    rotate,
    syme,
    scale,
    fuse,
    remove,
    get_closest_point,
    extract_point,
    extract_element,
    extrudeLinear,
    extrudeRotational,
    getBoundaries,
    _extract_bc_from_line,
    _extract_bc_from_surface,
    _extract_bc_from_volume,
    _reorganize_cells_into_edges,
    _reorganize_cells_into_sides
)
from .utils.detection import (
    auto_reduce_dim,
    cyclic_diff,
    find_nearest,
    select_four_hulls,
    corner_mask_auto
)
from .utils.constants import (
    _POINTSIZE, _FONTSIZE, 
    _MAX_HEAD_TAIL, _MAX_ITEM_DISPLAYED, _TOL, 
    _NB_SPACE_COLOR_DIM, 
    _ICON_DICT
)
from .utils.debug import plot_points_with_corners
from .utils.colors import (
    mapcolor,
    _BLACK, _WHITE, _BLUE, _GOLD, _RED, _PINK, _GREEN, _ORANGE,
    _PURPLE, _YELLOW, _CYAN, _MAGENTA, _BROWN, _GRAY, _TURQUOISE, 
    _LIME, _INDIGO, _VIOLET, _NAVY, _TEAL, _TOMATO, _SALMON, _TAN, 
    _CORAL, _PEACH, _MINT, _LEMON, _CHARTREUSE, _TURQUOISE_BLUE, 
    _SLATE, _ROSE, _PLUM
)
from .cython import (
	numpy_to_vtkIdList,
	extract_cells,
	Face,
	FaceExtractor
)
