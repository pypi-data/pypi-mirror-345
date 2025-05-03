import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from experimentalTreatingIsiPol.linearSearchMethod import getLinearSearchMethods

class TestLinearShearchMethod(unittest.TestCase):

    def test_get_methodos(self):
        """Tests if the rights methods are returned"""

        res = getLinearSearchMethods()

        expected_res = [
            'Deterministic',
            'Custom'
        ]

        for each_res, each_expected_res in zip(res, expected_res):
            self.assertEqual(each_res, each_expected_res)
