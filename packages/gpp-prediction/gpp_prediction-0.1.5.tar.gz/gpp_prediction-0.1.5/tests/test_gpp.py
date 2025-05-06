import unittest
import numpy as np
import pandas as pd
from gpp_prediction import swrad2par, get_tmin_func, get_vpd_func, calc_gpp


class TestGppPrediction(unittest.TestCase):

    def test_swrad2par(self):
        # Test with scalar
        self.assertAlmostEqual(swrad2par(1.0), 38880.0)

        # Test with Series
        s = pd.Series([0.5, 1.0, 1.5])
        result = swrad2par(s)
        expected = pd.Series([19440.0, 38880.0, 58320.0])
        pd.testing.assert_series_equal(result, expected)

    def test_get_tmin_func(self):
        tmin_values = np.array([-5, 0, 5, 10, 15])
        tmin_min = 0
        tmin_max = 10

        result = get_tmin_func(tmin_values, tmin_min, tmin_max)
        expected = np.array([0.0, 0.0, 0.5, 1.0, 1.0])

        np.testing.assert_array_almost_equal(result, expected)

    def test_get_vpd_func(self):
        vpd_values = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
        vpd_min = 0.5
        vpd_max = 1.5

        result = get_vpd_func(vpd_values, vpd_min, vpd_max)
        expected = np.array([1.0, 1.0, 0.5, 0.0, 0.0])

        np.testing.assert_array_almost_equal(result, expected)

    def test_calc_gpp(self):
        # Sample inputs
        par = np.array([20000.0, 30000.0, 40000.0])
        fapar = np.array([0.6, 0.7, 0.8])
        tmin = np.array([5, 8, 11])
        vpd = np.array([0.8, 1.2, 1.6])

        # Parameters
        eps_max = 2.5
        tmin_min = 0
        tmin_max = 10
        vpd_min = 0.5
        vpd_max = 1.5

        result = calc_gpp(par, fapar, tmin, vpd, eps_max, tmin_min, tmin_max,
                          vpd_min, vpd_max)

        # Expected values (calculated manually)
        f_tmin = np.array([0.5, 0.8, 1.0])
        f_vpd = np.array([0.7, 0.3, 0.0])
        expected = par * fapar * eps_max * f_tmin * f_vpd

        np.testing.assert_array_almost_equal(result, expected)


if __name__ == "__main__":
    unittest.main()
