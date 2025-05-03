#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import unittest

import numpy as np

from ..support import array_assert

__all__ = []


class test_model_fits(unittest.TestCase):

    def run_fit_checks(self, freq, fitfunc, extraargs=None):
        from ..modal import MvarModalDecomposition

        if extraargs is None:
            extraargs = {}

        sample_rate = 100
        seconds = 50
        time_vect = np.linspace(0, seconds, sample_rate * seconds)
        x = np.sin(2*np.pi*freq*time_vect)

        model = fitfunc.fit_model(x[None, :, None], np.arange(3), **extraargs)
        modes = MvarModalDecomposition.initialise(model, sample_rate=sample_rate)

        # Compute analytic modes
        mode_theta = (freq/(sample_rate/2.0)) * np.pi
        mode_poles = np.array([np.cos(mode_theta) + 1j*np.sin(mode_theta),
                               np.cos(mode_theta) - 1j*np.sin(mode_theta)])

        # Check fitted parameters are close to analytic parameters
        array_assert(-np.poly(mode_poles),
                     model.parameters[0, 0, :].real,
                     decimal=3)

        # Check fitted poles are close to analytic poles
        array_assert(mode_poles,
                     modes.evals[:, 0],
                     decimal=3)

    def test_ols(self):
        """Test the Ordinary Least Squares model fits"""

        from ..modelfit import OLSLinearModel
        fit = OLSLinearModel

        self.run_fit_checks(24, fit)
        self.run_fit_checks(10, fit)
        self.run_fit_checks(40, fit)

    def test_ols_sklearn(self):
        """Test the Ordinary Least Squares model fits using sklearn"""

        import sklearn.linear_model

        from ..modelfit import OLSLinearModel

        fit = OLSLinearModel
        estimator = sklearn.linear_model.LinearRegression(fit_intercept=False)
        extraargs = {'estimator': estimator}

        self.run_fit_checks(24, fit, extraargs=extraargs)
        self.run_fit_checks(10, fit, extraargs=extraargs)
        self.run_fit_checks(40, fit, extraargs=extraargs)

    def test_vieiramorf(self):
        """Test the Vieira-Morf model fits"""

        from ..modelfit import VieiraMorfLinearModel
        fit = VieiraMorfLinearModel

        self.run_fit_checks(24, fit)
        self.run_fit_checks(10, fit)
        self.run_fit_checks(40, fit)
