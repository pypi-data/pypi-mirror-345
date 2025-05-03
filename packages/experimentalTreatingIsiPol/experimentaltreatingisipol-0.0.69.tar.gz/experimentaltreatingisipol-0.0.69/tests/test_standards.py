import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from experimentalTreatingIsiPol.standards import get_standards

class TestStandard(unittest.TestCase):

    def test_return_standards(self):
        """Test if returns the right standards"""

        res = get_standards()
        expected_res = [
    'standard-ASTM-D7078'
    ,'standard-ASTM-D7264'
    ,'standard-ASTM-D3039'
    ,'standard-ASTM-D638'
]
        for each_r, each_expected_r in zip(res, expected_res):
            self.assertEqual(each_r, each_expected_r)
