"""ref: phase 6 follow-up. great circle distance helper used by /api/geo/nearby."""

import math
import unittest

# direct import without django bootstrap so this stays runnable through unittest
from geo.services import haversine_km


class HaversineTests(unittest.TestCase):
    def test_zero_distance(self):
        self.assertAlmostEqual(haversine_km(38.72, -9.14, 38.72, -9.14), 0.0)

    def test_lisbon_new_york(self):
        # ~5440 km, accept a generous tolerance
        d = haversine_km(38.72, -9.14, 40.71, -74.0)
        self.assertGreater(d, 5300)
        self.assertLess(d, 5600)

    def test_antipodes_close_to_half_circumference(self):
        # opposite side of the globe: ~ pi * R = 20015 km
        d = haversine_km(0, 0, 0, 180)
        self.assertAlmostEqual(d, math.pi * 6371.0, delta=1.0)

    def test_symmetry(self):
        a = haversine_km(35.0, 139.0, 19.0, 72.0)
        b = haversine_km(19.0, 72.0, 35.0, 139.0)
        self.assertAlmostEqual(a, b)


if __name__ == "__main__":
    unittest.main()
