#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import math
import numpy as np
from scipy import signal, stats

from .anam import AbstractAnam, register_class

__all__ = []


def fast_resample(X, ds_factor, axis=1):
    """Fast resampling of a timeseries array. This function pads the
    time-dimension to the nearest power of 2 to ensure that the resampling can
    use efficient FFT routines. The padding is removed before the downsampled
    data are returned.

    Parameters
    ----------
    X : ndarray
        Data to be resampled

    ds_factor : float
        Factor of downsampling to apply. Output sample rate will be sample_rate/ds_factor

    axis : int
        Axis along which to perform resampling.  Defaults to 1 for compatibility reasons

    Returns
    -------
    ndarray
        Resampled dataset, of size [nchannels x nsamples]

    """

    orig_size = X.shape[axis]
    target_size = int(X.shape[axis] // ds_factor)

    tmp_size = int(2**math.ceil(math.log(X.shape[axis], 2)))
    tmp_target_size = int(tmp_size // ds_factor)

    # We zero-pad the data in the time dimension up to the temporary size
    # Start by creating an array of appropriate shape
    new_shape = list(X.shape)
    new_shape[axis] = tmp_size

    tmp_X = np.zeros(new_shape, dtype=X.dtype)

    # Now we copy the data into the relevant part of the temporary array
    slic = [slice(None)] * len(X.shape)
    slic[axis] = slice(0, orig_size)
    slic = tuple(slic)

    tmp_X[slic] = X

    # Finally, we resample along the relevant axis
    resampled_X = signal.resample(tmp_X, tmp_target_size, axis=axis)

    # And extract just the parts we want
    slic = [slice(None)] * len(X.shape)
    slic[axis] = slice(0, target_size)
    slic = tuple(slic)

    return resampled_X[slic]


__all__.append('fast_resample')


def epoch_data(X, segment_len=None, trials=None):
    """Epoch a continuous data array. Takes a 2d [channels x samples] array and
    returns a [channels x segment_len x ntrials] array.

    Data can EITHER be epoched by specifying a segment_len value or a trials
    array. If a segment_len is passed then the samples array is split into
    none-overlapping segments of the specified length. Any samples not fitting
    into the final epoch are dropped. If a trials array (of shape [ntrials x 2]
    each row containing a start_ind and a stop_ind) then X is split into the
    trails it specifies.

    Parameters
    ----------
    X : 2d data array
        Data to be epoched
    segment_len : int > 0
        Length of continuous data segments to split dataset into
    trials : 2d array
        Trial start and stop indices contained in an [ntrials x 2] array

    Returns
    -------
    3d array
        Epoched dataset

    """

    if (X.ndim == 3) and (X.shape[0] > 0):
        raise ValueError('Data is already epoched')

    if (segment_len is not None) and (trials is not None):
        raise ValueError("Please specify either 'segment_len' or 'trials'. Can only apply one or the other")

    if segment_len is not None:
        nsegs = X.shape[1] // segment_len
        # Doing the reshape with FORTRAN ordering to get the desired behaviour.
        # Force the array back to be memory-contiguous afterwards. (Might be a better way to do this)
        Xout = X[:, :nsegs * segment_len].reshape(X.shape[0], segment_len, nsegs, order='F')
        return np.ascontiguousarray(Xout)

    if trials is not None:
        if np.any(trials < 0):
            raise ValueError("Negative trial index found, 'trials' should be strictly positive")
        if np.any(trials > X.shape[1]):
            outs = trials[trials > X.shape[1]]
            raise ValueError("Trial indices {0} are out of bounds for axis 1 of X (size={1})".format(outs, X.shape[1]))

        trial_len = np.abs(np.diff(trials[0, :])[0])
        Xout = np.zeros((X.shape[0],  trial_len, trials.shape[0]))
        for ii in range(trials.shape[0]):
            Xout[:, :, ii] = X[:, trials[ii, 0]:trials[ii, 1]]
        return Xout


__all__.append('epoch_data')


def get_valid_samples(data, delay_vect, mode='valid', backwards=False):
    """
    Helper function for excluding or replacing data samples which are not
    preceded by a full delay vect of samples for prediction.

    Parameters
    ----------
    data : ndarray
        Array of data to trim or change, of size [nchannels x nsamples x ntrials]
    delay_vect : ndarray
        Vector of lags included in model
    mode : {'valid','full_nan','full'}
        Options for excluding or replacing residuals which do not have a full
        model prediction ie the third sample of an order 5 model. 'valid'
        removes samples without a full model prediction, 'full_nan' returns
        resids of the same size as the data with nans replacing excluded
        samples and 'full' returns resids keeping non-full model samples in
        place. (Default is 'valid')
    backwards : Boolean
        Flag indicating whether to edit the first or last samples

    Returns
    -------
    ndarray
        data with non-valid samples removed or replaced with nans

    """

    if mode == 'full':
        # just pass through
        return data

    # Don't work in place
    ret = data.copy()

    if mode == 'valid':
        if backwards:
            ret = ret[:, :-len(delay_vect), :]
        else:
            ret = ret[:, len(delay_vect):, :]

    elif mode == 'full_nan':
        if backwards:
            ret[:, -len(delay_vect):, :] = np.nan
        else:
            ret[:, :len(delay_vect), :] = np.nan

    else:
        raise ValueError("Residual return mode is not recognised, please use \
                          'valid', 'full_nan' or 'full'")

    return ret


__all__.append('get_valid_samples')


def gesd(x, alpha=0.05, p_out=.1, outlier_side=0):
    """Detect outliers using Generalized ESD test

     Parameters
     ----------
     x : vector
        Data set containing outliers
     alpha : scalar
        Significance level to detect at (default = 0.05)
     p_out : int
        Maximum number of outliers to detect (default = 10% of data set)
     outlier_side : {-1,0,1}
        Specify sidedness of the test
           - outlier_side = -1 -> outliers are all smaller
           - outlier_side = 0  -> outliers could be small/negative or large/positive (default)
           - outlier_side = 1  -> outliers are all larger

    Returns
    -------
    idx : boolean vector
        Boolean array with TRUE wherever a sample is an outlier
    x2 : vector
        Input array with outliers removed

    References
    ----------
    B. Rosner (1983). Percentage Points for a Generalized ESD Many-Outlier Procedure. Technometrics 25(2), pp. 165-172.
    http://www.jstor.org/stable/1268549?seq=1

    """

    if outlier_side == 0:
        alpha = alpha/2

    if not isinstance(x, np.ndarray):
        x = np.asarray(x)

    n_out = int(np.ceil(len(x)*p_out))

    if np.any(np.isnan(x)):
        # Need to find outliers only in finite x
        y = np.where(np.isnan(x))[0]
        idx1, x2 = gesd(x[np.isfinite(x)], alpha, n_out, outlier_side)

        # idx1 has the indexes of y which were marked as outliers
        # the value of y contains the corresponding indexes of x that are outliers
        idx = np.zeros_like(x).astype(bool)
        idx[y[idx1]] = True

    n = len(x)
    temp = x.copy()
    R = np.zeros((n_out,))
    rm_idx = np.zeros((n_out,), dtype=int)
    lam = np.zeros((n_out,))

    for j in range(0, int(n_out)):
        i = j+1
        if outlier_side == -1:
            rm_idx[j] = np.nanargmin(temp)
            sample = np.nanmin(temp)
            R[j] = np.nanmean(temp) - sample
        elif outlier_side == 0:
            rm_idx[j] = int(np.nanargmax(abs(temp-np.nanmean(temp))))
            R[j] = np.nanmax(abs(temp-np.nanmean(temp)))
        elif outlier_side == 1:
            rm_idx[j] = np.nanargmax(temp)
            sample = np.nanmax(temp)
            R[j] = sample - np.nanmean(temp)

        R[j] = R[j] / np.nanstd(temp)
        temp[int(rm_idx[j])] = np.nan

        p = 1-alpha/(n-i+1)
        t = stats.t.ppf(p, n-i-1)
        lam[j] = ((n-i) * t) / (np.sqrt((n-i-1+t**2)*(n-i+1)))

    # Create a boolean array of outliers
    idx = np.zeros((n,)).astype(bool)
    idx[rm_idx[np.where(R > lam)[0]]] = True

    x2 = x[~idx]

    return idx, x2


def _find_outliers_in_dims(X, axis=-1, metric_func=np.std, gesd_args=None):
    """Find outliers across specified dimensions of an array"""

    if gesd_args is None:
        gesd_args = {}

    if axis == -1:
        axis = np.arange(X.ndim)[axis]

    squashed_axes = tuple(np.setdiff1d(np.arange(X.ndim), axis))
    metric = metric_func(X, axis=squashed_axes)

    rm_ind, _ = gesd(metric, **gesd_args)

    return rm_ind


def _find_outliers_in_segments(X, axis=-1, segment_len=100,
                               metric_func=np.std, gesd_args=None):
    """Create dummy-segments in a dimension of an array and find outliers in it"""

    if gesd_args is None:
        gesd_args = {}

    if axis == -1:
        axis = np.arange(X.ndim)[axis]

    # Prepare to slice data array
    slc = []
    for ii in range(X.ndim):
        if ii == axis:
            slc.append(slice(0, segment_len))
        else:
            slc.append(slice(None))

    # Preallocate some variables
    starts = np.arange(0, X.shape[axis], segment_len)
    metric = np.zeros((len(starts), ))
    bad_inds = np.zeros(X.shape[axis])*np.nan

    # Main loop
    for ii in range(len(starts)):
        if ii == len(starts)-1:
            stop = None
        else:
            stop = starts[ii]+segment_len

        # Update slice on dim of interest
        slc[axis] = slice(starts[ii], stop)
        # Compute metric for current chunk
        metric[ii] = metric_func(X[tuple(slc)])
        # Store which chunk we've used
        bad_inds[slc[axis]] = ii

    # Get bad segments
    rm_ind, _ = gesd(metric, **gesd_args)
    # Convert to int indices
    rm_ind = np.where(rm_ind)[0]
    # Convert to bool in original space of defined axis
    bads = np.isin(bad_inds, rm_ind)
    return bads


def detect_artefacts(X, axis=None, reject_mode='dim', metric_func=np.std,
                     segment_len=100, gesd_args=None, ret_mode='bad_inds'):
    """Detect bad observations or segments in a dataset

    Parameters
    ----------
    X : ndarray
        Array to find artefacts in.
    axis : int
        Index of the axis to detect artefacts in
    reject_mode : {'dim' | 'segments'}
        Flag indicating whether to detect outliers across a dimension (dim;
        default) or whether to split a dim into segments and detect outliers in
        the them (segments)
    metric_func : function
        Function defining metric to detect outliers on. Defaults to np.std but
        can be any function taking an array and returning a single number.
    segement_len : int > 0
        Integer window length of dummy epochs for bad_segment detection
    gesd_args : dict
        Dictionary of arguments to pass to gesd
    ret_mode : {'good_inds','bad_inds','zero_bads','nan_bads'}
        Flag indicating whether to return the indices for good observations,
        indices for bad observations (default), the input data with outliers
        removed (zero_bads) or the input data with outliers replaced with nans
        (nan_bads)

    Returns
    -------
    ndarray
        If ret_mode is 'bad_inds' or 'good_inds', this returns a boolean vector
        of length X.shape[axis] indicating good or bad samples. If ret_mode if
        'zero_bads' or 'nan_bads' this returns an array copy of the input data
        X with bad samples set to zero or np.nan respectively.

    """

    if reject_mode not in ['dim', 'segments']:
        raise ValueError("reject_mode: '{0}' not recognised".format(reject_mode))

    if ret_mode not in ['bad_inds', 'good_inds', 'zero_bads', 'nan_bads']:
        raise ValueError("ret_mode: '{0}' not recognised")

    if axis is None or axis > X.ndim:
        raise ValueError('bad axis')

    if reject_mode == 'dim':
        bad_inds = _find_outliers_in_dims(X, axis=axis, metric_func=metric_func, gesd_args=gesd_args)

    elif reject_mode == 'segments':
        bad_inds = _find_outliers_in_segments(X, axis=axis,
                                              segment_len=segment_len,
                                              metric_func=metric_func,
                                              gesd_args=gesd_args)

    if ret_mode == 'bad_inds':
        return bad_inds
    elif ret_mode == 'good_inds':
        return bad_inds == False  # noqa: E712
    elif ret_mode in ['zero_bads', 'nan_bads']:
        out = X.copy()

        slc = []
        for ii in range(X.ndim):
            if ii == axis:
                slc.append(bad_inds)
            else:
                slc.append(slice(None))
        slc = tuple(slc)

        if ret_mode == 'zero_bads':
            out[slc] = 0
            return out
        elif ret_mode == 'nan_bads':
            out[slc] = np.nan
            return out


class PCA(AbstractAnam):
    """
    Class for handling PCA-based reduction before fitting a model
    """

    hdf5_outputs = ['npcs', 'data_mean', '_U', '_s', '_VT',
                    'explained_variance', 'explained_variance_ratio',
                    'components', 'loadings', 'scores']

    def __init__(self, data=None, npcs=None):
        AbstractAnam.__init__(self)

        # Need to cope with no-argument initialisation for anamnesis
        if data is not None:
            self.data_mean = data.mean(axis=0)
            self._pca_svd(data, npcs)

    def _pca_svd(self, data, npcs=10):
        """
        Compute a Principal Components Analysis on a given dataset using the SVD
        method.

        Parameters
        ----------
        X : ndarray
            Input data of shape [nsamples x nfeatures]. The second dimension is
            reduced by the PCA.

        Returns
        -------
        scores : ndarray [nsamples x npcs]
            The dimensionality-reduced data. This contains the value of each
            observation in the new PCA-space.

        components : ndarray [npcs x nfeatures]
            The eigenvectors describing how each feature (node or connection) loads
            onto the latent PCA dimensions.

        loadings : ndarray [npcs x nfeatures]
            The components scaled by their contribution to the variance in the
            original data

        explained_variance_ratio : ndarray [npcs]
            The proportion of variance explained by each PC

        """

        self.npcs = npcs

        # Demean observations
        self.data_mean = data.mean(axis=0)[None, :]

        # compute
        self._U, self._s, self._VT = np.linalg.svd(data - self.data_mean, full_matrices=False)

        # Variance explained metrics
        var = self._s ** 2 / (data.shape[0]-1)
        self.explained_variance = var[:npcs]
        self.explained_variance_ratio = var[:npcs] / var.sum()

        # The weights for each original variable in each principal component
        self.components = self._VT[:npcs, :]  # Eigenvectors
        self.loadings = self.components * self._s[:npcs, None]  # Scaled by variance contributed to data

        # The new co-ordinates of each observation in PCA-space
        self.scores = self._s[:npcs] * self._U[:, :npcs]

        # Check that component self.scores are properly decorrelated
        try:
            C = np.corrcoef(self.scores.T)
            assert(np.sum(np.abs(C - np.diag(np.diag(C)))) < 1e-10)
        except AssertionError:
            print('Observations are not properly de-correlated by PCA. Data demeaning might have gone wrong.')
            raise

    def project_score(self, scores):
        """
        Compute a projection of a set of scores back to original data space
        """
        return self.data_mean + np.dot(scores, self.components)


__all__.append('PCA')
register_class(PCA)
