#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import unittest

import numpy as np

from ..support import array_assert


class ResampleTests(unittest.TestCase):
    def test_fast_resample_int_factor(self):
        """Test that we properly resample data with an integer factor"""
        from ..utils import fast_resample

        # Create a 10Hz signal sampled at 500Hz for 2s
        t = np.linspace(0, 2-(1/1000), 1000)
        s = np.sin(2*np.pi*t*10)

        # Reformat to [nchannels, nsamples]
        s = s[np.newaxis, :]

        # Re-sample by a factor of 2 (to 250Hz)
        res = fast_resample(s, 2)

        # We should still have 20 peaks
        # Find them by looking for points where the derivative reverses sign
        diff_res = np.diff(res)[0, :]
        peaks = []
        for idx in range(1, diff_res.shape[0]):
            if diff_res[idx-1] > 0 and diff_res[idx] < 0:
                peaks.append(idx)

        assert(len(peaks) == 20)

        # And each peak should be 25 samples apart starting at sample 6
        assert(peaks[0] == 6)
        diff = np.array([peaks[x] - peaks[x-1] for x in range(1, len(peaks))])
        assert(np.sum(diff == 25) == 19)

    def test_fast_resample_alt_dim(self):
        """Test that we properly resample data with an alternate dimension"""
        from ..utils import fast_resample

        # Create a 10Hz signal sampled at 500Hz for 2s
        t = np.linspace(0, 2-(1/1000), 1000)
        s = np.sin(2*np.pi*t*10)

        # Re-sample by a factor of 2 (to 250Hz)
        res = fast_resample(s, 2, axis=0)

        # We should still have 20 peaks
        # Find them by looking for points where the derivative reverses sign
        diff_res = np.diff(res)
        peaks = []
        for idx in range(1, diff_res.shape[0]):
            if diff_res[idx-1] > 0 and diff_res[idx] < 0:
                peaks.append(idx)

        assert(len(peaks) == 20)

        # And each peak should be 25 samples apart starting at sample 6
        assert(peaks[0] == 6)
        diff = np.array([peaks[x] - peaks[x-1] for x in range(1, len(peaks))])
        assert(np.sum(diff == 25) == 19)

    def test_fast_resample_float_factor(self):
        """Test that we properly resample data with an float factor"""
        from ..utils import fast_resample

        # Create a 10Hz signal sampled at 500Hz for 2s
        t = np.linspace(0, 2-(1/1000), 1000)
        s = np.sin(2*np.pi*t*10)

        # Reformat to [nchannels, nsamples]
        s = s[np.newaxis, :]

        # Re-sample by a factor of 2.5 (to 200Hz)
        res = fast_resample(s, 2.5)

        # We should still have 20 peaks
        # Find them by looking for points where the derivative reverses sign
        diff_res = np.diff(res)[0, :]
        peaks = []
        for idx in range(1, diff_res.shape[0]):
            if diff_res[idx-1] > 0 and diff_res[idx] < 0:
                peaks.append(idx)

        assert(len(peaks) == 20)

        # And each peak should be 19 or 20 samples apart starting at sample 5
        # (there is some inevitable rounding error)
        assert(peaks[0] == 5)
        diff = np.array([peaks[x] - peaks[x-1] for x in range(1, len(peaks))])
        assert(np.sum((diff == 20) | (diff == 19)) == 19)

    def test_fast_resample_multi_dim(self):
        """Test that we properly resample data in multi dimension mode"""
        from ..utils import fast_resample

        # Create a 10Hz signal sampled at 500Hz for 2s
        t = np.linspace(0, 2-(1/1000), 1000)
        s = np.sin(2*np.pi*t*10)

        # Reformat to [nchannels, nsamples]
        s = s[:, np.newaxis, np.newaxis]

        s = np.tile(s, (1, 1, 2))

        # Re-sample by a factor of 2 (to 250Hz)
        res = fast_resample(s, 2, axis=0)

        # For each of our two copies, perform our tests
        for idx in range(2):
            test_data = res[:, 0, idx]
            # We should still have 20 peaks
            # Find them by looking for points where the derivative reverses sign
            diff_res = np.diff(test_data)
            peaks = []
            for idx in range(1, diff_res.shape[0]):
                if diff_res[idx-1] > 0 and diff_res[idx] < 0:
                    peaks.append(idx)

            assert(len(peaks) == 20)

            # And each peak should be 25 samples apart starting at sample 6
            assert(peaks[0] == 6)
            diff = np.array([peaks[x] - peaks[x-1] for x in range(1, len(peaks))])
            assert(np.sum(diff == 25) == 19)


class EpochingTests(unittest.TestCase):

    def test_seglen_epoching(self):
        X = np.arange(10 * 1000).reshape(10, 1000)

        from ..utils import epoch_data

        Xout = epoch_data(X, segment_len=15)
        # Check basic shape
        assert(Xout.shape[1] == 15)
        assert(Xout.shape[2] == 66)

        # Check trial lengths are as expected
        assert(np.all(np.diff(Xout[0, 0, :]) == 15))
        # Check first trial values are as expected
        assert(np.all(Xout[0, :, 0] == np.arange(15)))
        assert(np.all(Xout[0, :, 20] == np.arange(300, 315)))

    def test_trials_epoching(self):
        X = np.arange(10 * 1000).reshape(10, 1000)

        trials = np.repeat([40, 100, 150, 210, 300], 2).reshape(-1, 2)
        trials[:, 1] += 40

        from ..utils import epoch_data

        Xout = epoch_data(X, trials=trials)
        # Check basic shape
        assert(Xout.shape[1] == 40)
        assert(Xout.shape[2] == 5)

        # Check first trial values are as expected
        assert(np.all(Xout[0, :, 1] == np.arange(trials[1, 0], trials[1, 1])))


class ValidSamplesTests(unittest.TestCase):
    def test_valid_samples(self):
        """Test that we properly compute the indices for valid samples"""
        from ..utils import get_valid_samples

        # Create some test data: 2 chans, 100 samples, 10 trials
        # Set up data as (trial_num*100) + (chan_no * 2000) + (sample_num)
        num_chans = 2
        num_samples = 100
        num_trials = 10

        data = np.zeros((num_chans, num_samples, num_trials))
        for k in range(num_chans):
            for l in range(num_trials):
                data[k, :, l] = (k * 2000) + (l * 100) + np.arange(num_samples)

        # Assume that we have an order 5 model
        delay_vect = np.arange(5 + 1)

        # Check that in the 'full' case we just get back our data
        array_assert(data, get_valid_samples(data, delay_vect, mode='full', backwards=False))
        array_assert(data, get_valid_samples(data, delay_vect, mode='full', backwards=True))

        # Check that in the 'valid' forward case, we get back our data offset by 6 samples (order + 1)
        array_assert(data[:, 6:, :],
                     get_valid_samples(data, delay_vect, mode='valid', backwards=False))

        # Check that in the 'valid' backwards case, we get back our data with 6 samples taken from
        # the end
        array_assert(data[:, :-6, :],
                     get_valid_samples(data, delay_vect, mode='valid', backwards=True))

        # Check that in the 'full_nan' forward case, we get back our data where the first 6 samples
        # are NaN
        nan_data = data.copy()
        nan_data[:, 0:6, :] = np.nan

        valid = get_valid_samples(data, delay_vect, mode='full_nan', backwards=False)
        # Check NaNs
        assert(np.sum(np.isnan(valid[:, 0:6, :])) == 120)
        # Check rest of array
        array_assert(nan_data[:, 6:, :], valid[:, 6:, ])

        # Check that in the 'full_nan' backward case, we get back our data where the last 6 samples
        # are NaN
        nan_data = data.copy()
        nan_data[:, -6:, :] = np.nan

        valid = get_valid_samples(data, delay_vect, mode='full_nan', backwards=True)
        # Check NaNs
        assert(np.sum(np.isnan(valid[:, -6:, :])) == 120)
        # Check rest of array
        array_assert(nan_data[:, :-6, :], valid[:, :-6, ])

        # Check that we raise on a bad mode
        self.assertRaises(ValueError, get_valid_samples,
                          data, delay_vect, mode='notreal', backwards=True)


class ArtefactDetectionTests(unittest.TestCase):
    def test_gesd(self):
        from ..utils import gesd
        np.random.seed(43)

        # Create some random data
        X = np.random.randn(100, 1)

        # Check that we don't detect outliers in normally distributed random
        # data
        bads, cleanX = gesd(X)
        # No bad samples
        assert(np.all(bads == False))  # noqa: E712
        # Clean data is the same as data
        assert(np.all(X == cleanX))

        # and on an outlier side -1 test
        bads, cleanX = gesd(X, outlier_side=-1)
        # No bad samples
        assert(np.all(bads == False))  # noqa: E712
        # Clean data is the same as data
        assert(np.all(X == cleanX))

        # and on an outlier side 1 test
        bads, cleanX = gesd(X, outlier_side=1)
        # No bad samples
        assert(np.all(bads == False))  # noqa: E712
        # Clean data is the same as data
        assert(np.all(X == cleanX))

        # and that we deal with passing a list
        bads, cleanX = gesd(list(X))
        # No bad samples
        assert(np.all(bads == False))  # noqa: E712
        # Clean data is the same as data
        assert(np.all(X == cleanX))

        # An an obviously bad sample
        X[50] = 10
        bads, cleanX = gesd(X)
        # Check correct sample is identified
        assert(np.where(bads == True)[0][0] == 50)  # noqa: E712
        # Bad sample is identified
        assert(cleanX.shape[0] == X.shape[0]-1)

    def test_detect_artefacts(self):
        from ..utils import detect_artefacts

        # Create random data
        np.random.seed(42)
        X = np.random.randn(50, 1000, 10)

        # Check no bads detected
        assert(np.sum(detect_artefacts(X, 0)) == 0)
        assert(np.sum(detect_artefacts(X, 1)) == 0)
        assert(np.sum(detect_artefacts(X, 2)) == 0)

        X[10, :, :] *= 5

        # Check one bad detected
        assert(np.sum(detect_artefacts(X, 0)) == 1)
        # Check it it at index 10
        assert(np.where(detect_artefacts(X, 0))[0] == 10)

        # Check one bad detected
        assert(np.sum(detect_artefacts(X, 0, ret_mode='good_inds')) == 49)
        # Check it it at index 10
        assert(np.where(detect_artefacts(X, 0, ret_mode='good_inds') == False)[0][0] == 10)  # noqa: E712

        # Check it all works with dim 3
        X[:, :, 2] *= 8

        # Check one bad detected
        assert(np.sum(detect_artefacts(X, 2)) == 1)
        # Check it it at index 10
        assert(np.where(detect_artefacts(X, 2))[0] == 2)

        # Check one bad detected
        assert(np.sum(detect_artefacts(X, 2, ret_mode='good_inds')) == 9)
        # Check it it at index 10
        assert(np.where(detect_artefacts(X, 2, ret_mode='good_inds') == False)[0][0] == 2)  # noqa: E712

        # Check nan outputs are sensible
        assert(np.isnan(detect_artefacts(X, 2, ret_mode='nan_bads')).sum() == 50000)
        assert(np.isnan(detect_artefacts(X, 0, ret_mode='nan_bads')).sum() == 10000)

        # Create random data
        np.random.seed(42)
        X = np.random.randn(50, 1000, 10)
        # Add high variance epoch
        X[:, 650:750, :] *= 10

        # Check that correct number of samples are rejected
        assert(np.sum(detect_artefacts(X, 1, reject_mode='segments', segment_len=50)) == 100)
        # Check that start and end of epoch are correctly identified
        assert(detect_artefacts(X, 1, reject_mode='segments', segment_len=50)[649] == False)  # noqa: E712
        assert(detect_artefacts(X, 1, reject_mode='segments', segment_len=50)[650] == True)  # noqa: E712
        assert(detect_artefacts(X, 1, reject_mode='segments', segment_len=50)[749] == True)  # noqa: E712
        assert(detect_artefacts(X, 1, reject_mode='segments', segment_len=50)[750] == False)  # noqa: E712

    def test_bad_params(self):
        from ..utils import detect_artefacts

        np.random.seed(43)

        # Create a dataset in sails format with 32 channels, 500 samples and
        # 128 epochs.
        X = np.random.randn(32, 500, 128)

        # No axis passed
        self.assertRaises(ValueError, detect_artefacts, X)

        # Bad reject mode
        self.assertRaises(ValueError, detect_artefacts, X, reject_mode='unknown')
