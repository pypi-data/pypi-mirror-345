import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from experimentalTreatingIsiPol.direction import get_directions

class TestDirections(unittest.TestCase):

    def test_get_directions(self):
        """Tests if the returned directions are correct."""

        res = get_directions()

        exp_res = ['11', '22']

        for each_r, each_exp_res in zip(res, exp_res):
            self.assertEqual(each_r, each_exp_res)
