#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import unittest

import numpy as np

from numpy.testing import assert_raises

from ..support import array_assert


class MITests(unittest.TestCase):
    def test_mutual_information_bad(self):
        """Test that we raise an exception with bad MI input"""
        from ..stats import mutual_information
        assert_raises(ValueError, mutual_information,
                      np.zeros(1000,), np.zeros(1000, ))

    def test_mutual_information(self):
        """Test that we calculate a test MI value correctly (log2)"""
        from ..stats import mutual_information

        x1 = np.sin(2 * np.pi * np.linspace(0, 2, 1000))[..., np.newaxis].T
        x2 = np.cos(2 * np.pi * np.linspace(0, 2, 1000))[..., np.newaxis].T

        ret = mutual_information(x1, x2, r=(-1.0, 1.0), nbins=10)

        array_assert(ret, np.array([1.50009220434754353413]))

    def test_mutual_information_calc_range(self):
        """Test that we calculate MI value correctly when using auto range"""
        from ..stats import mutual_information

        x1 = np.sin(2 * np.pi * np.linspace(0, 2, 1000))[..., np.newaxis].T
        x2 = np.cos(2 * np.pi * np.linspace(0, 2, 1000))[..., np.newaxis].T

        ret = mutual_information(x1, x2, nbins=10)

        array_assert(ret, np.array([1.50011373288843841145]), decimal=5)


class DWTests(unittest.TestCase):
    def test_durbin_watson_1d(self):
        """Test Durbin-Watson calculation from 1D data"""
        from ..stats import durbin_watson

        dat = np.arange(1, 101)
        ret = durbin_watson(dat)
        correct = np.array([2.9259642382148664261e-04])
        array_assert(ret.real, correct)

    def test_durbin_watson_2d(self):
        """Test Durbin-Watson calculation from 2D data"""
        from ..stats import durbin_watson

        dat = np.arange(1, 101)[np.newaxis, slice(None)]
        ret = durbin_watson(dat)
        correct = np.array([2.9259642382148664261e-04])

        array_assert(ret.real, correct)

    def test_durbin_watson_3d(self):
        """Test Durbin-Watson calculation from 3D data"""
        from ..stats import durbin_watson

        dat = np.zeros((1, 100, 2))
        dat[0, :, 0] = np.arange(1, 101)
        dat[0, :, 1] = np.arange(101, 201)
        ret = durbin_watson(dat)
        correct = np.array([2.9259642382148664261e-04,
                            4.2157259352311195991e-05])

        array_assert(ret.real, correct)

    def test_durbin_watson_nd(self):
        """Test Durbin-Watson calculation fails with > 3D data"""
        from ..stats import durbin_watson

        dat = np.zeros((1, 100, 1, 1))
        assert_raises(ValueError, durbin_watson, dat)


class ResidualsTests(unittest.TestCase):
    def test_rsquared_from_residuals_bad_input(self):
        """Test rsquared_from_residuals calculation with bad input"""
        from ..stats import rsquared_from_residuals

        data = np.zeros((1, 100))
        residuals = np.zeros((2, 100))

        assert_raises(ValueError, rsquared_from_residuals, data, residuals)

    def test_rsquared_from_residuals_int(self):
        """Test rsquared_from_residuals calculation from 1D data (int)"""
        from ..stats import rsquared_from_residuals

        data = np.arange(1, 101)
        residuals = data * 0.5
        correct = 0.75

        # Both per_signal True and False should be the same here
        ret = rsquared_from_residuals(data, residuals, per_signal=True)
        assert(ret == correct)

        ret = rsquared_from_residuals(data, residuals, per_signal=False)
        assert(ret == correct)

    def test_rsquared_from_residuals_1d(self):
        """Test rsquared_from_residuals calculation from 1D data (float)"""
        from ..stats import rsquared_from_residuals

        data = np.arange(1, 101).astype(np.float64)
        residuals = data * 0.5
        correct = 0.75

        # Both per_signal True and False should be the same here
        ret = rsquared_from_residuals(data, residuals, per_signal=True)
        assert(ret == correct)

        ret = rsquared_from_residuals(data, residuals, per_signal=False)
        assert(ret == correct)

    def test_rsquared_from_residuals_2d(self):
        """Test rsquared_from_residuals calculation from 2D data"""
        from ..stats import rsquared_from_residuals

        data = np.zeros((2, 100))
        data[0, :] = np.arange(1, 101)
        data[1, :] = np.arange(1, 101)
        residuals = data.copy()
        residuals[0, :] *= 0.5
        residuals[1, :] *= 0.75

        # Check both combined and per-signal calculation
        correct_per = np.array([0.75, 0.4375])
        correct_comb = 0.59375
        ret = rsquared_from_residuals(data, residuals, per_signal=True)
        array_assert(ret, correct_per)

        ret = rsquared_from_residuals(data, residuals, per_signal=False)
        assert(ret == correct_comb)

    def test_rsquared_from_residuals_3d(self):
        """Test Durbin-Watson calculation from 3D data"""
        from ..stats import rsquared_from_residuals

        data = np.zeros((2, 100, 2))
        data[0, :, :] = np.arange(1, 101)[..., np.newaxis]
        data[1, :, :] = np.arange(1, 101)[..., np.newaxis]
        residuals = data.copy()
        residuals[0, :, :] *= 0.5
        residuals[1, :, :] *= 0.75

        # Check both combined and per-signal calculation
        correct_per = np.array([0.75, 0.4375])
        correct_comb = 0.59375
        ret = rsquared_from_residuals(data, residuals, per_signal=True)
        array_assert(ret, correct_per)

        ret = rsquared_from_residuals(data, residuals, per_signal=False)
        assert(ret == correct_comb)

    def test_rsquared_from_residuals_nd(self):
        """Test Durbin-Watson calculation fails with > 3D data"""
        from ..stats import rsquared_from_residuals

        data = np.zeros((1, 100, 1, 1))
        assert_raises(ValueError, rsquared_from_residuals, data, data)


class MahalnobisTests(unittest.TestCase):
    def test_mahalanobis_origin(self):
        """Test mahalanobis calculation to the origin"""
        from ..stats import mahalanobis

        # Set up a co-ordinate system
        dat = np.array([np.arange(1, 101),
                        np.sin(np.arange(1, 101)),
                        np.tan(np.arange(1, 301, 3))])

        # Pre-compute the covariance matrix
        sigma = np.cov(dat)

        # Feed in a couple of points of known distance
        pts = np.array([[1.0, 1, 1], [2, 2, 2]]).T

        correct = np.array([2.0136770397279, 8.0547081589117])

        ret = mahalanobis(pts, sigma=sigma)

        # An inverse is involved so allow for some difference
        array_assert(ret, correct, decimal=10)

    def test_mahalanobis_point(self):
        """Test mahalanobis calculation to another point"""
        from ..stats import mahalanobis

        # Set up a co-ordinate system
        dat = np.array([np.arange(1, 101),
                        np.sin(np.arange(1, 101)),
                        np.tan(np.arange(1, 301, 3))])

        # Pre-compute the covariance matrix
        sigma = np.cov(dat)

        # Feed in a couple of points of known distance
        pts_1 = np.array([[1.0, 1, 1], [2, 2, 2]]).T
        pts_2 = np.array([[1.0, 1, 1], [0, 0, 0]]).T

        correct = np.array([0.0, 8.0547081589117])

        ret = mahalanobis(pts_1, pts_2, sigma=sigma)

        # An inverse is involved so allow for some difference
        array_assert(ret, correct, decimal=8)

    def test_mahalanobis_point_error(self):
        """Test mahalanobis calculation to another point"""
        from ..stats import mahalanobis

        # Feed in a couple of points of known distance
        pts_1 = np.array([[1.0, 1, 1], [2, 2, 2]]).T
        pts_2 = np.array([[1.0, 1, 1], [0, 0, 0], [3, 3, 3]]).T

        assert_raises(ValueError, mahalanobis, pts_1, pts_2)

    def test_mahalanobis_compute_sigma(self):
        """Test mahalanobis calculation when computing sigma"""
        from ..stats import mahalanobis

        # Set up some co-ordinates
        dat = np.array([np.arange(1, 5),
                        np.sin(np.arange(1, 5)),
                        np.tan(np.arange(1, 12, 3))])

        ret = mahalanobis(dat)

        correct = np.array([46738.68983456, 47169.93175778,
                            46209.49548723, 47068.83525808])

        # An inverse is involved so allow for some difference
        array_assert(ret, correct, decimal=5)


class ProfileLikelihoodTests(unittest.TestCase):
    def test_profile_likelihood(self):
        """Test profile likelihood function"""
        from ..stats import profile_likelihood
        # TODO: This could do with a better external validation

        dat = np.zeros((10, 1))
        dat[0:5, 0] = np.arange(5, 0, -1)
        dat[5:,  0] = np.arange(0.8, -0.1, -0.2)

        correct = np.array([0.00000000000000000000,
                            0.00000000000000000000,
                            3.21859683762712212030,
                            5.06387510343866775742,
                            4.36930553905676788418,
                            2.50420226265147682909,
                            1.67250106964246647578,
                            1.15155564748249972240,
                            0.76855251039401584201,
                            0.00000000000000000000])

        ret = profile_likelihood(dat)

        array_assert(ret, correct, decimal=10)

    def test_profile_likelihood_bad_input(self):
        """Test profile likelihood function with bad input"""
        from ..stats import profile_likelihood

        dat = np.zeros((10, 1, 2))

        assert_raises(ValueError, profile_likelihood, dat)

    def test_find_cov(self):
        """Test find_cov"""
        from ..stats import find_cov

        # Datasets should be signals, samples)
        d1 = np.array([[0, 4, 6, 8],
                       [-1, 1, 3, 5]])

        d2 = np.array([[1, -1, 1, -1],
                       [3, -3, 3, -3]])

        expected = np.array([[-1.5+0j, -4.5+0j],
                             [-1.0+0j, -3.0+0j]])

        res = find_cov(d1, d2, ddof=0)

        array_assert(res, expected)

        # Routine should demean the data across samples, so add an offset
        # and compare

        d1 += 100

        res = find_cov(d1, d2, ddof=0)

        array_assert(res, expected)

        # DDOF of None should multiply by 4 (number of time points)
        res = find_cov(d1, d2, ddof=None)

        array_assert(res, expected * 4.0)

    def test_find_cov_multitrial(self):
        """Test find_cov_multitrial"""
        from ..stats import find_cov_multitrial

        # Datasets should be signals, samples, trials)
        d1 = np.array([[[0, 2, 4, 6], [-1, 1, 3, 5]],
                       [[0, 2, 4, 8], [8, -8, 8, -8]]])

        d2 = np.array([[[0, 1, 2, 3], [-1, 0, 1, 2]],
                       [[9, -9, 9, -9], [11, -11, 11, -11]]])

        expected = np.array([[0.50+0j, 0.0+0j], [1.75+0j, 9.50+0j]])

        res = find_cov_multitrial(d1, d2)

        array_assert(res, expected)

        # Routine should demean the data across samples, so add an offset
        # and compare

        d1 += 100

        res = find_cov_multitrial(d1, d2)

        array_assert(res, expected)

        # DDOF of None should be the same as 1 (default) in this case
        res = find_cov_multitrial(d1, d2, ddof=None)

        array_assert(res, expected)

        # Changing the DDOF to 0 should just scale by 2 in this case
        res = find_cov_multitrial(d1, d2, ddof=0)

        array_assert(res, expected / 2.0)

    def test_stability_index(self):
        """Test the stability index routine"""
        from ..stats import stability_index

        # The SI of an A matrix which is identity at lag 0
        # and zero everywhere else should be 0

        A1 = np.eye(2)
        A2 = np.zeros((2, 2))
        A = np.stack([A1, A2, A2], 2)

        res = stability_index(A)

        assert(res == 0.0)

        # The SI of an A matrix which is identity at lag 1
        # and zero everywhere else should be 1.0

        A = np.stack([A2, A1, A2], 2)

        res = stability_index(A)

        assert(res == 1.0)
