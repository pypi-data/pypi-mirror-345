#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import unittest

import numpy as np


class MorletBasisTests(unittest.TestCase):

    def test_morlet_basis_generation(self):
        sample_rate = 128
        freqs = np.linspace(1, 50, 49)
        ncycles = 5
        win_len = 5

        from ..wavelet import get_morlet_basis

        mlt = get_morlet_basis(freqs, ncycles, win_len, sample_rate)

        # Check we have same number of morlet basis waves as input freqs
        assert(len(mlt) == freqs.shape[0])

        # Check that each morlet basis wave is of shorter or equal length to
        # previous one (for strictly ascending freqs)
        assert(np.all(np.diff([len(m) for m in mlt]) <= 0))

        # Example with faster sample_rate
        mlt2 = get_morlet_basis(freqs, ncycles, win_len, sample_rate*2)
        check = np.c_[[len(m) for m in mlt], [len(m) for m in mlt2]]

        # Morlets from double sample rate should be twice as long (or off-by-one)
        maxdiff = np.max(check[:, 0] - check[:, 1]//2)
        assert(0 <= maxdiff and maxdiff < 2)


class MorletTransformTests(unittest.TestCase):

    def setUp(self):

        self.seconds = 10
        self.sample_rate = 512
        self.time = np.linspace(0, self.seconds, self.seconds*self.sample_rate)
        self.f1 = 10
        self.f2 = 3

        self.x1 = np.sin(2 * np.pi * self.f1 * self.time[:(self.seconds // 2) * self.sample_rate])
        self.x2 = 2 * np.sin(2 * np.pi * self.f2 * self.time[(self.seconds // 2) * self.sample_rate:])

        self.x = np.r_[self.x1, self.x2]

    def test_simple_morlet_norm(self):

        from ..wavelet import morlet

        freqs = np.linspace(1, 50, 49)

        cwt = morlet(self.x, freqs, self.sample_rate,
                     ret_mode='amplitude', normalise='simple')

        # Check that amplitude is close to 'true' value whilst each oscillation
        # is 'on' and close to zerom when it is 'off'

        # Early signal, check 10Hz is close to 1 and 3Hz is close to zero
        assert(cwt[9, 2000] > .97 and cwt[9, 2000] < 1.03)
        assert(cwt[2, 2000] < 0.03)

        # Late signal, check 3Hz is close to 2 and 10Hz is close to zero
        assert(cwt[9, 4000] < 0.03)
        assert(cwt[2, 4000] > 1.97 and cwt[2, 4000] < 2.03)
