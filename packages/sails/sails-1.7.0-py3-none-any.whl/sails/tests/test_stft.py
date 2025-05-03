#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

"""Test STFT Module."""

import unittest

import numpy as np
from scipy import signal


class TestSTFTAgainstScipy(unittest.TestCase):
    """Compare simple periodogram outputs against scipy."""

    def test_simple_periodogram_nperseg(self):
        """Ensure nperseg results are consistent."""
        from ..stft import periodogram

        # Run test 5 times
        for ii in range(5):
            xx = np.random.randn(4096,)
            f, pxx = signal.welch(xx, nperseg=2**(4+ii))
            pxx2 = periodogram(xx, nperseg=2**(4+ii))

            assert(np.allclose(pxx, pxx2.spectrum))

    def test_simple_periodogram_window_type(self):
        """Ensure window type results are consistent."""
        from ..stft import periodogram

        window_tests = [None, 'hann', 'hamming', 'boxcar', 'tukey', 'blackman']

        for ii in range(5):
            xx = np.random.randn(4096,)
            win = window_tests[ii] if window_tests[ii] is not None else np.ones((128,)) / 128
            f, pxx = signal.welch(xx, nperseg=128, window=win)
            pxx2 = periodogram(xx, nperseg=128, window_type=window_tests[ii])

            assert(np.allclose(pxx, pxx2.spectrum))

    def test_simple_periodogram_nfft(self):
        """Ensure nfft results are consistent."""
        from ..stft import periodogram

        for ii in range(5):
            xx = np.random.randn(4096,)
            f, pxx = signal.welch(xx, nfft=2**(ii+4), nperseg=16)
            pxx2 = periodogram(xx, nfft=2**(ii+4), nperseg=16)

            assert(np.allclose(pxx, pxx2.spectrum))

    def test_simple_periodogram_scaling(self):
        """Ensure scaling results are consistent."""
        from ..stft import periodogram

        scaling_tests = ['density', 'spectrum']

        for ii in range(len(scaling_tests)):
            xx = np.random.randn(4096,)
            f, pxx = signal.welch(xx, nperseg=128, scaling=scaling_tests[ii])
            pxx2 = periodogram(xx, nperseg=128, scaling=scaling_tests[ii])

            assert(np.allclose(pxx, pxx2.spectrum))

    def test_simple_periodogram_sided(self):
        """Ensure scaling results are consistent."""
        from ..stft import periodogram

        side_tests = [True, False]

        for ii in range(len(side_tests)):
            print(side_tests[ii])
            xx = np.random.randn(4096,)
            f, pxx = signal.welch(xx, nperseg=128, return_onesided=side_tests[ii])
            pxx2 = periodogram(xx, nperseg=128, return_onesided=side_tests[ii])

            assert(np.allclose(pxx, pxx2.spectrum))

    def test_simple_periodogram_detrend(self):
        """Ensure scaling results are consistent."""
        from ..stft import periodogram

        detrend_tests = [None, 'linear', 'constant']

        for ii in range(len(detrend_tests)):
            print(detrend_tests[ii])
            xx = np.random.randn(4096,)
            f, pxx = signal.welch(xx, nperseg=128, detrend=detrend_tests[ii])
            pxx2 = periodogram(xx, nperseg=128, detrend=detrend_tests[ii])

            assert(np.allclose(pxx, pxx2.spectrum))

    def test_simple_periodogram_average(self):
        """Ensure scaling results are consistent."""
        from ..stft import periodogram

        average_tests = ['mean', 'median']

        for ii in range(len(average_tests)):
            print(average_tests[ii])
            xx = np.random.randn(4096,)
            f, pxx = signal.welch(xx, nperseg=128, average=average_tests[ii])

            # can't benchmark against scipy for median as they don't do a simple median,
            # they use a median with bias correction referencing a paper
            # https://github.com/scipy/scipy/blob/v1.11.3/scipy/signal/_spectral_py.py#L2037
            avg = average_tests[ii] if ii == 0 else average_tests[ii] + '_bias'
            pxx2 = periodogram(xx, nperseg=128, average=avg, verbose='DEBUG')

            assert(np.allclose(pxx, pxx2.spectrum))


class TestBasicIRASA(unittest.TestCase):
    """Test that IRASA functions run."""

    def test_canary_irasa(self):
        """Ensure irasa runs."""
        from ..stft import irasa, periodogram

        # Run test 5 times
        for ii in range(5):
            xx = np.random.randn(4096,)
            pxx = periodogram(xx, nperseg=2**(4+ii), average='mean')
            aperiodic, oscillatory = irasa(xx, nperseg=2**(4+ii), average='mean')
            assert(np.all(pxx.f == aperiodic.f))
            assert(np.allclose(pxx.spectrum, aperiodic.spectrum + oscillatory.spectrum))
