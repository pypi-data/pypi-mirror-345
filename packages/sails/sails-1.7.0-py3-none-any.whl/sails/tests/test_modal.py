#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import unittest

import numpy as np

__all__ = []


class test_modal_decomp(unittest.TestCase):

    def test_modal_decomp(self):
        """Test modal decomposition"""
        from ..modal import MvarModalDecomposition
        from ..modelfit import VieiraMorfLinearModel

        sample_rate = 128
        seconds = 10
        f = 20

        time_vect = np.linspace(0, seconds, seconds * sample_rate)
        X = np.sin(2 * np.pi * f * time_vect)[None, :, None]

        delay_vect = np.arange(3)
        m = VieiraMorfLinearModel.fit_model(X, delay_vect)
        mo = MvarModalDecomposition.initialise(m, sample_rate)

        # Check we have the right number of modes
        assert(mo.evals.shape[0] == 2)

        # Check peak frequency to 1 decimal place
        assert(np.round(mo.peak_frequency, 1)[0, 0] == f)
