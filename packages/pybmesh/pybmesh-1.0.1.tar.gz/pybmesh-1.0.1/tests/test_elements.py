import unittest
import math
import numpy as np

# Import classes from your module.
from pybmesh import Point
from pybmesh import Line, PolyLine, Arc, Circle
from pybmesh import Surface, Volume

# ================================================================
# Tests for 0D elements: Point
# ================================================================
class TestPoint(unittest.TestCase):
    def test_creation(self):
        # Create a point with explicit coordinates.
        p = Point(1, 2, 3)
        coords = p.coords
        # coords should be a NumPy array of shape (1, 3)
        self.assertEqual(coords.shape, (1, 3))
        np.testing.assert_allclose(coords[0], [1, 2, 3], atol=1e-6)
    
    def test_default(self):
        # Creating without arguments should yield (0,0,0)
        p = Point()
        coords = p.coords
        self.assertEqual(coords.shape, (1, 3))
        np.testing.assert_allclose(coords[0], [0, 0, 0], atol=1e-6)
    
    def test_translation(self):
        p = Point(1, 2, 3)
        p.translate(1, -1, 2)
        np.testing.assert_allclose(p.coords[0], [2, 1, 5], atol=1e-6)
    
    def test_copy(self):
        p = Point(1, 2, 3)
        p_copy = p.copy()
        # The copy should have the same coordinates...
        np.testing.assert_allclose(p_copy.coords[0], p.coords[0], atol=1e-6)
        # ...but modifying it should not change the original.
        p_copy.translate(5, 5, 5)
        np.testing.assert_allclose(p.coords[0], [1, 2, 3], atol=1e-6)
    
    def test_repr(self):
        p = Point(1, 2, 3)
        rep = repr(p)
        self.assertIn("Point", rep)
        self.assertIn("Number of Points", rep)


# ================================================================
# Tests for 1D elements: Line, PolyLine, Arc, Circle
# ================================================================
class TestLine(unittest.TestCase):
    def setUp(self):
        self.p1 = Point(0, 0, 0)
        self.p2 = Point(1, 0, 0)
    
    def test_line_creation(self):
        # Create a line with 10 elements -> 11 nodes.
        line = Line(self.p1, self.p2, n=10)
        pts = line.get_points()
        self.assertEqual(len(pts), 11)
        # Check first and last nodes
        np.testing.assert_allclose(pts[0], self.p1.coords[0], atol=1e-6)
        np.testing.assert_allclose(pts[-1], self.p2.coords[0], atol=1e-6)
    
    def test_get_start_and_end(self):
        line = Line(self.p1, self.p2, n=5)
        start = line.get_start_point()
        end = line.get_end_point()
        np.testing.assert_allclose(start, self.p1.coords[0], atol=1e-6)
        np.testing.assert_allclose(end, self.p2.coords[0], atol=1e-6)
    
    def test_translation(self):
        line = Line(self.p1, self.p2, n=10)
        pts_before = line.get_points()
        line.translate(1, 2, 3)
        pts_after = line.get_points()
        for before, after in zip(pts_before, pts_after):
            np.testing.assert_allclose(after, np.array(before) + np.array([1, 2, 3]), atol=1e-6)
    
    def test_copy(self):
        line = Line(self.p1, self.p2, n=10)
        line_copy = line.copy()
        pts_line = line.get_points()
        pts_copy = line_copy.get_points()
        for a, b in zip(pts_line, pts_copy):
            np.testing.assert_allclose(a, b, atol=1e-6)
        # Translate copy; original must remain unchanged.
        line_copy.translate(2, 0, 0)
        pts_copy_after = line_copy.get_points()
        pts_line_after = line.get_points()
        for a, b in zip(pts_line_after, pts_copy_after):
            self.assertFalse(np.allclose(a, b, atol=1e-6))
    
    def test_reverse_orientation(self):
        line = Line(self.p1, self.p2, n=10)
        pts_before = line.get_points()
        line.reverse_orientation()
        pts_after = line.get_points()
        pts_before_reversed = pts_before[::-1]
        for a, b in zip(pts_before_reversed, pts_after):
            np.testing.assert_allclose(a, b, atol=1e-6)


class TestPolyLine(unittest.TestCase):
    def setUp(self):
        self.p1 = Point(0, 0, 0)
        self.p2 = Point(1, 0, 0)
        self.p3 = Point(1, 1, 0)
    
    def test_polyline_creation(self):
        polyline = PolyLine(self.p1, self.p2, self.p3, n=5)
        pts = polyline.get_points()
        # We expect at least the three original nodes (possibly with additional interpolated points)
        self.assertTrue(len(pts) >= 3)
        np.testing.assert_allclose(pts[0], self.p1.coords[0], atol=1e-6)
        np.testing.assert_allclose(pts[-1], self.p3.coords[0], atol=1e-6)
    
    def test_copy(self):
        polyline = PolyLine(self.p1, self.p2, self.p3, n=5)
        poly_copy = polyline.copy()
        pts_original = polyline.get_points()
        pts_copy = poly_copy.get_points()
        for a, b in zip(pts_original, pts_copy):
            np.testing.assert_allclose(a, b, atol=1e-6)
        poly_copy.translate(1, 1, 0)
        pts_copy_after = poly_copy.get_points()
        pts_original_after = polyline.get_points()
        for a, b in zip(pts_original_after, pts_copy_after):
            self.assertFalse(np.allclose(a, b, atol=1e-6))


class TestArc(unittest.TestCase):
    def setUp(self):
        # Define a center and two boundary points.
        self.center = Point(0, 0, 0)
        self.pA = Point(1, 0, 0)
        self.pB = Point(0, 1, 0)
    
    def test_from_center_angles(self):
        # Create an arc from center, radius, start and end angles.
        radius = 1.0
        angle_start = 0
        angle_end = math.pi / 2
        arc = Arc.from_center_angles(center=self.center.coords[0],
                                     radius=radius,
                                     angle_start=angle_start,
                                     angle_end=angle_end,
                                     n=5)
        pts = arc.get_points()
        for pt in pts:
            dist = np.linalg.norm(np.array(pt) - np.array(self.center.coords[0]))
            self.assertAlmostEqual(dist, radius, places=4)
    
    def test_from_3_points(self):
        # Create an arc from three non-collinear points.
        p0 = Point(1, 0, 0)
        p1 = Point(1, 1, 0)
        p2 = Point(0, 1, 0)
        arc = Arc.from_3_points(p0, p1, p2, n=5)
        pts = arc.get_points()
        np.testing.assert_allclose(pts[0], p0.coords[0], atol=1e-6)
        np.testing.assert_allclose(pts[-1], p2.coords[0], atol=1e-6)
    
    def test_from_center_2points(self):
        # Create an arc using a center and two boundary points.
        arc = Arc.from_center_2points(center=self.center.coords[0],
                                      radius=1.0,
                                      pA=self.pA.coords[0],
                                      pB=self.pB.coords[0],
                                      n=5)
        pts = arc.get_points()
        for pt in pts:
            dist = np.linalg.norm(np.array(pt) - np.array(self.center.coords[0]))
            self.assertAlmostEqual(dist, 1.0, places=4)
    
    def test_from_center_1point(self):
        # Create an arc from a center, one boundary point and an angle.
        arc = Arc.from_center_1point(center=self.center.coords[0],
                                     p0=self.pA.coords[0],
                                     angle=math.pi / 2,
                                     n=5)
        pts = arc.get_points()
        expected_radius = np.linalg.norm(np.array(self.pA.coords[0]) - np.array(self.center.coords[0]))
        for pt in pts:
            dist = np.linalg.norm(np.array(pt) - np.array(self.center.coords[0]))
            self.assertAlmostEqual(dist, expected_radius, places=4)
    
    def test_copy_and_translation(self):
        arc = Arc.from_center_2points(center=self.center.coords[0],
                                      radius=1.0,
                                      pA=self.pA.coords[0],
                                      pB=self.pB.coords[0],
                                      n=3)
        arc_copy = arc.copy()
        pts_original = arc.get_points()
        arc_copy.translate(1, 1, 0)
        pts_copy = arc_copy.get_points()
        for orig, new in zip(pts_original, pts_copy):
            np.testing.assert_allclose(new, np.array(orig) + np.array([1, 1, 0]), atol=1e-6)


class TestCircle(unittest.TestCase):
    def test_circle_points(self):
        center = [0, 0, 0]
        radius = 5.0
        circle = Circle(center=center, radius=radius, n=50)
        pts = circle.get_points()
        for pt in pts:
            dist = np.linalg.norm(np.array(pt) - np.array(center))
            self.assertAlmostEqual(dist, radius, places=4)
    
    def test_copy_and_translation(self):
        center = [0, 0, 0]
        circle = Circle(center=center, radius=5.0, n=50)
        circle_copy = circle.copy()
        pts_original = circle.get_points()
        circle_copy.translate(2, 3, 0)
        pts_copy = circle_copy.get_points()
        for orig, new in zip(pts_original, pts_copy):
            np.testing.assert_allclose(new, np.array(orig) + np.array([2, 3, 0]), atol=1e-6)



# ================================================================
# Tests for 2D elements: Surface
# ================================================================
class TestSurface(unittest.TestCase):
    def setUp(self):
        # Four points forming a square in the XY-plane.
        self.p1 = Point(0, 0, 0)
        self.p2 = Point(1, 0, 0)
        self.p3 = Point(1, 1, 0)
        self.p4 = Point(0, 1, 0)
    
    def test_surface_from_points(self):
        # Build a surface directly from points.
        surface = Surface(self.p1, self.p2, self.p3, self.p4, n=1, quad=True)
        num_points = surface._ugrid.GetNumberOfPoints()
        self.assertGreater(num_points, 0)
    
    def test_surface_from_lines(self):
        # Build boundary lines and create a surface.
        l1 = Line(self.p1, self.p2, n=1)
        l2 = Line(self.p2, self.p3, n=1)
        l3 = Line(self.p3, self.p4, n=1)
        l4 = Line(self.p4, self.p1, n=1)
        surface = Surface(l1, l2, l3, l4, quad=True)
        num_points = surface._ugrid.GetNumberOfPoints()
        self.assertGreater(num_points, 0)
    
    def test_surface_from_contour(self):
        # Create a closed contour using PolyLine and build a surface.
        polyline = PolyLine(self.p1, self.p2, self.p3, self.p4, self.p1, n=1)
        surface = Surface(polyline, quad=True)
        num_points = surface._ugrid.GetNumberOfPoints()
        self.assertGreater(num_points, 0)
    
    def test_surface_from_two_lines(self):
        # Create two lines (with the same number of elements) and generate a surface between them.
        l1 = Line(self.p1, self.p2, n=2)
        l2 = Line(self.p4, self.p3, n=2)
        surface = Surface(l1, l2, n=1, quad=True)
        num_points = surface._ugrid.GetNumberOfPoints()
        self.assertGreater(num_points, 0)
    
    def test_copy(self):
        surface = Surface(self.p1, self.p2, self.p3, self.p4, n=1, quad=True)
        surface_copy = surface.copy()
        num_original = surface._ugrid.GetNumberOfPoints()
        num_copy = surface_copy._ugrid.GetNumberOfPoints()
        self.assertEqual(num_original, num_copy)
        # Translate the copy and verify the original remains unchanged.
        surface_copy.translate(1, 1, 0)
        pts_original = np.array([surface._ugrid.GetPoints().GetPoint(i) for i in range(num_original)])
        pts_copy = np.array([surface_copy._ugrid.GetPoints().GetPoint(i) for i in range(num_copy)])
        self.assertFalse(np.allclose(pts_original, pts_copy, atol=1e-6))

# ================================================================
# Tests for 3D elements: Volume
# ================================================================
class TestVolume(unittest.TestCase):
    def create_square_surface(self, z=0):
        """
        Helper to create a square surface in the XY-plane at a given z-level.
        """
        p1 = Point(0, 0, z)
        p2 = Point(1, 0, z)
        p3 = Point(1, 1, z)
        p4 = Point(0, 1, z)
        # Create a surface from 4 points (quad) with one element.
        return Surface(p1, p2, p3, p4, n=1, quad=True)
    
    def get_ugrid_points(self, volume):
        """
        Helper function to extract all points from the volume's vtkUnstructuredGrid.
        """
        num_points = volume._ugrid.GetNumberOfPoints()
        return np.array([volume._ugrid.GetPoints().GetPoint(i) for i in range(num_points)])
    
    def test_volume_creation(self):
        """
        Test that a Volume can be created from two homeomorphic surfaces.
        """
        s0 = self.create_square_surface(z=0)
        s1 = self.create_square_surface(z=1)
        vol = Volume(s0, s1, n=2, grading=1, progression='linear', pid=42)
        # Ensure the generated unstructured grid has points.
        num_points = vol._ugrid.GetNumberOfPoints()
        self.assertGreater(num_points, 0)
        # Check that the part id is set as expected.
        self.assertEqual(vol.pid, 42)
    
    def test_volume_translation(self):
        """
        Test that translating a Volume moves all mesh points by the same vector.
        """
        s0 = self.create_square_surface(z=0)
        s1 = self.create_square_surface(z=1)
        vol = Volume(s0, s1, n=2, grading=1, progression='linear')
        pts_before = self.get_ugrid_points(vol)
        translation_vector = np.array([2, 3, 4])
        vol.translate(*translation_vector)
        pts_after = self.get_ugrid_points(vol)
        np.testing.assert_allclose(pts_after, pts_before + translation_vector, atol=1e-6)
    
    def test_volume_copy(self):
        """
        Test that copying a Volume produces an independent object.
        """
        s0 = self.create_square_surface(z=0)
        s1 = self.create_square_surface(z=1)
        vol = Volume(s0, s1, n=2, grading=1, progression='linear')
        vol_copy = vol.copy()
        pts_original = self.get_ugrid_points(vol)
        pts_copy = self.get_ugrid_points(vol_copy)
        np.testing.assert_allclose(pts_original, pts_copy, atol=1e-6)
        # Translate the copy and verify the original remains unchanged.
        vol_copy.translate(1, 0, 0)
        pts_copy_after = self.get_ugrid_points(vol_copy)
        pts_original_after = self.get_ugrid_points(vol)
        # They should now differ.
        with self.assertRaises(AssertionError):
            np.testing.assert_allclose(pts_original_after, pts_copy_after, atol=1e-6)
    
    def test_non_homeomorphic_surfaces(self):
        """
        Test that creating a Volume with non-homeomorphic surfaces raises a ValueError.
        Here we simulate non-homeomorphism by modifying the point count in one surface.
        """
        s0 = self.create_square_surface(z=0)
        s1 = self.create_square_surface(z=1)
        # Save the original GetNumberOfPoints method.
        original_get_num_pts = s1._ugrid.GetNumberOfPoints
        # Override it to simulate a different number of points.
        s0_num_pts = s0._ugrid.GetNumberOfPoints()
        s1._ugrid.GetNumberOfPoints = lambda: s0_num_pts + 1
        with self.assertRaises(ValueError):
            Volume(s0, s1, n=2, grading=1, progression='linear')
        # Restore the original method.
        s1._ugrid.GetNumberOfPoints = original_get_num_pts

if __name__ == '__main__':
    unittest.main()
