import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from experimentalTreatingIsiPol.docConfig import get_docconfig, print_docConfig

class testDocConfig(unittest.TestCase):

    def test_get_docconfig(self):
        """Tests the return of possible exp. data configurations."""
        res = get_docconfig()

        exp_res = [
            '_alpha',
            '_beta',
            '_gamma',
            '_delta',
            '_epsilon',
            '_zeta',
            '_eta',
            '_omicron',
            '_pi',
            '_rho',
            '_sigma'
        ]

        for each_r, each_exp_r in zip(res, exp_res):
            self.assertEqual(each_r, each_exp_r)

    def test_print_docConfig(self):
        """ Testing printing the docConfig example parameter."""
        self.assertEqual(type(print_docConfig()), str)
