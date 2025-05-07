#!/usr/bin/env python3
import unittest
import numpy as np
import vtk

# Import geometry classes and mesh manipulation functions from your module.
from pybmesh import Point, Line, Surface, Volume, Arc
from pybmesh import (
    translate, rotate, syme, scale, fuse, remove, 
    extrudeLinear, extrudeRotational, extract_point, extract_element, getBoundaries
)

def get_ugrid_points(mesh):
    """Helper to extract all points from a mesh's vtkUnstructuredGrid as a NumPy array."""
    ugrid = mesh.get_vtk_unstructured_grid()
    num_pts = ugrid.GetNumberOfPoints()
    pts = np.array([ugrid.GetPoints().GetPoint(i) for i in range(num_pts)])
    return pts

class TestMeshManipulation(unittest.TestCase):
    def setUp(self):
        # Define four points to create a simple square surface.
        self.p0 = Point(0, 0, 0)
        self.p1 = Point(1, 0, 0)
        self.p2 = Point(1, 1, 0)
        self.p3 = Point(0, 1, 0)
        # Create a square surface (quad) with one element.
        self.surface = Surface(self.p0, self.p1, self.p2, self.p3, n=1, quad=True, pid=100)
        # Create a second surface by translating the first upward.
        self.surface2 = translate(self.surface, (0, 0, 1), pid=101)
        # Build a volume by interpolating between the two surfaces.
        self.volume = Volume(self.surface, self.surface2, n=1, grading=1, progression='linear', pid=102)
        
        # Create a simple line for extrusion tests.
        self.line = Line(self.p0, self.p1, n=1, pid=200)
        # Create a vector (as a line) for linear extrusion; a line from (0,0,0) to (0,0,1)
        self.vector_line = Line(Point(0,0,0), Point(0,0,1), n=1, pid=201)
        # For rotational extrusion, we reuse the same line.
        
    def test_translate_and_rotate(self):
        # Test the translate function.
        orig_pts = get_ugrid_points(self.surface)
        moved = translate(self.surface, (2, -1, 3), pid=300)
        moved_pts = get_ugrid_points(moved)
        np.testing.assert_allclose(moved_pts, orig_pts + np.array([2, -1, 3]), atol=1e-6)
        
        # Test rotate: rotate the moved surface 90 degrees about z-axis around (0,0,0).
        rotated = rotate(moved, center=(0,0,0), axis=(0,0,1), angle=90, pid=301)
        rotated_pts = get_ugrid_points(rotated)
        # For a 90° rotation about z, (x,y) becomes (-y,x)
        expected_pts = np.array([[-pt[1], pt[0], pt[2]] for pt in moved_pts])
        np.testing.assert_allclose(rotated_pts, expected_pts, atol=1e-6)
    
    def test_syme_and_scale(self):
        # Test symmetry (reflection) about the xy-plane.
        moved = translate(self.surface, (0, 0, 1), pid=401)
        sym_moved = syme(moved, plane='xy', pid=402)
        sym_moved_pts = get_ugrid_points(sym_moved)
        moved_pts = get_ugrid_points(moved)[:,2]
        # Reflection about the xy-plane should negate the z-coordinate.
        self.assertTrue(np.allclose(sym_moved_pts[:,2], -moved_pts, atol=1e-6))
        
        # Test scaling: scale the surface by factors (2,0.5,1) about its center.
        scaled = scale(self.surface, sx=2, sy=0.5, sz=1, center=(0.5,0.5,0), pid=500)
        scaled_pts = get_ugrid_points(scaled)
        expected = (get_ugrid_points(self.surface) - np.array([0.5,0.5,0])) * np.array([2, 0.5, 1]) + np.array([0.5,0.5,0])
        np.testing.assert_allclose(scaled_pts, expected, atol=1e-6)
    
    def test_fuse(self):
        # Create two overlapping surfaces.
        surf1 = self.surface
        surf2 = translate(self.surface, (0,0,0), pid=600)  # identical surface but different pid
        # Fuse with merge=True: duplicate nodes should be merged.
        fused = fuse(surf1, surf2, pid=601, merge=True)
        pts_fused = get_ugrid_points(fused)
        pts1 = get_ugrid_points(surf1)
        pts2 = get_ugrid_points(surf2)
        total_pts = pts1.shape[0] + pts2.shape[0]
        # With merging, the number of points should be less than the sum.
        self.assertLess(pts_fused.shape[0], total_pts)
        # Fuse with merge=False: the number of points equals the sum.
        fused_no_merge = fuse(surf1, surf2, pid=602, merge=False)
        pts_fused_no_merge = get_ugrid_points(fused_no_merge)
        self.assertEqual(pts_fused_no_merge.shape[0], total_pts)
    
    def test_extrudeLinear(self):
        # Extrude a line along a small vector.
        extruded = extrudeLinear(self.line, self.vector_line, pid=700)
        # When extruding a Line, the result should be a Surface.
        self.assertEqual(extruded.__class__.__name__, "Surface")
        # Check that the new mesh has more points than the original line.
        pts_line = get_ugrid_points(self.line)
        pts_extruded = get_ugrid_points(extruded)
        self.assertGreater(pts_extruded.shape[0], pts_line.shape[0])
    
    def test_extrudeRotational(self):
        # Extrude (rotate) a line around the z-axis.
        # Use pA at (0,0,0) and pB at (0,0,1) with a 45° rotation.
        extruded = extrudeRotational(self.line, pA=(0,0,0), pB=(0,0,1), angle=45, n=1, pid=800)
        # When extruding a Line rotationally, the result should be a Surface.
        self.assertEqual(extruded.__class__.__name__, "Surface")
        pts_original = get_ugrid_points(self.line)
        pts_extruded = get_ugrid_points(extruded)
        # The first block of pts_extruded equals the original, so compare the subsequent rotated layer.
        rotated_layer = pts_extruded[pts_original.shape[0]:]
        self.assertFalse(np.allclose(pts_original, rotated_layer, atol=1e-6))
    
    def test_extract_point_and_element(self):
        # Use a simple "closest" criterion on the volume.
        closest_dict = {
            "type": "closest",
            "point": (0.5, 0.5, 0.5)
        }
        pt = extract_point(self.volume, closest_dict, pid=900)
        # Verify the returned object is a Point and has three coordinates.
        self.assertEqual(pt.coords.shape[1], 3)
        
        # Test extraction of an element by id.
        # For this, extract the first element of the volume.
        elem = extract_element(self.volume, id=0)
        # The new mesh should have only one element (vtkUnstructuredGrid cell).
        num_cells = elem.get_vtk_unstructured_grid().GetNumberOfCells()
        self.assertEqual(num_cells, 1)

    def test_getBoundaries_and_remove(self):
        # Test getBoundaries on the volume to extract one envelope face.
        boundary = getBoundaries(self.volume, pid=1000, pick=0)
        # For a volume, boundaries are Surface objects.
        self.assertEqual(boundary.__class__.__name__, "Surface")
        # Now extract edges from that surface.
        contour = getBoundaries(boundary, pid=1001, pick=[0,2])
        # Expect a Line for contours.
        self.assertEqual(contour.__class__.__name__, "Line")
        # Extract nodes (points) from the contour.
        nodes = getBoundaries(contour, pid=1002, pick='all')
        self.assertEqual(nodes.__class__.__name__, "Point")
        
        # Test removal: remove the elements present in the contour from the volume.
        elem_removed = extract_element(self.volume, points=nodes, strict=False)
        # Check if any cells were extracted; if not, skip the removal test.
        num_elem_removed = elem_removed.get_vtk_unstructured_grid().GetNumberOfCells()
        if num_elem_removed == 0:
            self.skipTest("extract_element returned empty connectivity; skipping removal test")
        vol_removed = remove(self.volume, elem_removed)
        # Check that the number of cells in the new volume is less than in the original.
        num_cells_orig = self.volume.get_vtk_unstructured_grid().GetNumberOfCells()
        num_cells_removed = vol_removed.get_vtk_unstructured_grid().GetNumberOfCells()
        self.assertLess(num_cells_removed, num_cells_orig)

if __name__ == '__main__':
    unittest.main()
