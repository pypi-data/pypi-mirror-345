#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import unittest

import numpy as np

from ..support import array_assert


class DelayDiagnosticTests(unittest.TestCase):
    def test_constructor(self):
        """Test that we can initialise a DelayDiagnostics object"""
        from ..diags import DelayDiagnostics

        d = DelayDiagnostics()

        assert(d.MI is None)
        assert(d.MI_diff is None)
        assert(d.delay_vect_samples is None)
        assert(d.delay_vect_ms is None)
        assert(d.time_vect is None)
        assert(d.autocorrelation is None)
        assert(d.maxdelay is None)
        assert(d.first_zero is None)

    def test_delay_assessment_constant(self):
        """Test that we can assess delay with a constant window (default)"""
        from ..diags import DelayDiagnostics
        # assert_raises(ValueError, mutual_information, np.zeros(1000,),
        #               np.zeros(1000, ))
        # array_assert(ret, array([1.50009220434754353413]))

        # Create a simple sine/cosine set to test with
        t = np.linspace(0, 1, 1000)
        dat = np.array([[np.sin(2 * np.pi * t * 10).T],
                        [np.cos(2 * np.pi * t * 10).T]])
        # Needs to be signals / timepts / epochs
        dat = dat.transpose(0, 2, 1)

        d = DelayDiagnostics.delay_search(dat, 100, 1, 1000.0)

        # TODO: Ideally, we'd have a better test to fully check the
        # returned values based on the analytic version.
        array_assert(d.delay_vect_samples, np.arange(1, 100))
        array_assert(d.delay_vect_ms, np.arange(1, 100) * (1/1000.0))
        # This should be at time == 25ms
        # So in samples:
        assert(d.first_zero == 24)
        assert(d.delay_vect_ms[d.first_zero] == 0.025)
        assert(d.autocorrelation.shape == (2, 1, 1000))
        assert(d.MI.shape == (2, 99))
        assert(d.MI_diff.shape == (2, 98))

    def test_delay_search_nonconstant(self):
        """Test that we can assess delay with a non-constant window"""
        from ..diags import DelayDiagnostics

        # Create a simple sine/cosine set to test with
        t = np.linspace(0, 1, 1000)
        dat = np.array([[np.sin(2*np.pi * t * 10).T],
                        [np.cos(2*np.pi * t * 10).T]])
        # Needs to be signals / timepts / epochs
        dat = dat.transpose(0, 2, 1)

        d = DelayDiagnostics.delay_search(dat, 100, 1, 1000.0, False)

        # TODO: Ideally, we'd have a better test for the non-constant window
        # code.
        array_assert(d.delay_vect_samples, np.arange(1, 100))
        array_assert(d.delay_vect_ms, np.arange(1, 100) * (1/1000.0))
        # This should be at time == 25ms
        # So in samples:
        assert(d.first_zero == 24)
        assert(d.delay_vect_ms[d.first_zero] == 0.025)
        assert(d.autocorrelation.shape == (2, 1, 1000))
        assert(d.MI.shape == (2, 99))
        assert(d.MI_diff.shape == (2, 98))
