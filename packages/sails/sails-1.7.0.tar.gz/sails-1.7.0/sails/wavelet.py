#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np
from scipy import signal


def morlet(x, freqs, sample_rate, win_len=4, ncycles=5, ret_basis=False, ret_mode='power', normalise='wikipedia'):
    """Compute a morlet wavelet time-frequency transform on a univariate dataset.

    Parameters
    ----------
    x : vector array_like
        Time-series to compute wavelet transform from.
    freqs : array_like
        Array of frequency values in Hz
    sample_rate : scalar
        Sampling frequency of data in Hz
    win_len : scalar
        Length of wavelet window
    ncycles : int
        Width of wavelets in number of cycles
    ret_basis : bool
        Boolean flag indicating whether to return the basis set alongside the transform.
    ret_mode : {'power', 'amplitude', 'complex'}
        Flag indicating whether which form of the wavelet transform to return.
    normalise : {None, 'simple', 'tallon', 'wikipedia', 'mne'}
        Flag indicating which normalisation factor to apply to the wavelet
        basis. See `sails.wavelet.get_morlet_basis` for details.
        Default = 'wikipedia'.

    Returns
    -------
    2D array
        Array containing morlet wavelet transformed data [nfreqs x nsamples]

    """
    orig_dim = x.ndim
    if orig_dim == 1:
        x = x[np.newaxis, :]

    if 0 in freqs:
        raise ValueError("0 cannot be in freqs.")

    cwt = np.zeros((x.shape[0], len(freqs), x.shape[1]), dtype=complex)

    # Get morlet basis
    mlt = get_morlet_basis(freqs, ncycles, win_len, sample_rate, normalise)

    for jj in range(x.shape[0]):
        for ii in range(len(freqs)):
            a = signal.convolve(x[jj, :], mlt[ii].real, mode='same', method='fft')
            b = signal.convolve(x[jj, :], mlt[ii].imag, mode='same', method='fft')
            cwt[jj, ii, :] = a+1j*b

    if ret_mode == 'power':
        cwt = np.power(np.abs(cwt), 2)
    elif ret_mode == 'amplitude':
        cwt = np.abs(cwt)
    elif ret_mode != 'complex':
        raise ValueError("'ret_mode not recognised, please use one of {'power','amplitude','complex'}")

    if orig_dim == 1:
        cwt = cwt[0, ...]

    if ret_basis:
        return cwt, mlt
    else:
        return cwt


def cross_morlet(x, freqs, sample_rate, win_len=4, ncycles=5, ret_mode='power', normalise='wikipedia'):
    """Compute a morlet cross wavelet time-frequency transform on a multivariate dataset.

    Parameters
    ----------
    x : vector array_like
        Time-series to compute cross wavelet transform from.
    freqs : array_like
        Array of frequency values in Hz.
    sample_rate : scalar
        Sampling frequency of data in Hz.
    win_len : scalar
        Length of wavelet window.
    ncycles : int
        Width of wavelets in number of cycles.
    ret_mode : {'power', 'amplitude', 'complex'}
        Flag indicating whether which form of the wavelet transform to return.
    normalise : {None, 'simple', 'tallon', 'wikipedia', 'mne'}
        Flag indicating which normalisation factor to apply to the wavelet
        basis. See `sails.wavelet.get_morlet_basis` for details.
        Default = 'wikipedia'.

    Returns
    -------
    4D array
        Array containing morlet cross wavelet transformed data [nfreqs x nsamples x nchannels x nchannels].

    """
    if ret_mode not in ['power', 'amplitude', 'complex']:
        raise ValueError("'ret_mode not recognised, please use one of {'power','amplitude','complex'}")

    # Run standard wavelet decomposition return complex values
    wt = morlet(x, freqs, sample_rate, win_len=win_len, ncycles=ncycles, ret_mode='complex', normalise=normalise)

    # Preallocate output array [nchannels x nchannels x nfreqs x ntimes]
    S = np.empty((wt.shape[0], wt.shape[0], wt.shape[1], wt.shape[2]), dtype=complex)

    # Main loop
    for ii in range(wt.shape[1]):
        for jj in range(wt.shape[2]):
            S[:, :, ii, jj] = np.dot(wt[:, ii, jj, np.newaxis], wt[np.newaxis, :, ii, jj].conj())

    if ret_mode == 'power':
        S = np.power(np.abs(S), 2)
    elif ret_mode == 'amplitude':
        S = np.abs(S)
    elif ret_mode != 'complex':
        raise ValueError("'ret_mode not recognised, please use one of {'power', 'amplitude', 'complex'}")

    return S


def get_morlet_basis(freq, ncycles, win_len, sample_rate, normalise='wikipedia'):
    """Compute a morlet wavelet basis set based on specified parameters.

    Parameters
    ----------
    freq : array_like
        Array of frequency values in Hz
    ncycles : int
        Width of wavelets in number of cycles
    win_len : scalar
        Length of wavelet window
    sample_rate : scalar
        Sampling frequency of data in Hz
    normalise : {None, 'simple', 'tallon', 'wikipedia', 'mne'}
        Flag indicating which normalisation factor to apply to the wavelet
        basis (default is 'wikipedia') - can be one of:

        * None - no normalisation is applied

        * 'simple' - wavelet is normalised by its own sum

        * 'tallon' - normalisation from Tallon-Baudry et al 1997

        * 'wikipedia' normalisation from https://en.wikipedia.org/wiki/Morlet_wavelet

        * 'mne' - normalisation used in MNE-Python

    Returns
    -------
    list of vector arrays
        Complex valued arrays containing morlet wavelets

    References
    ----------
    .. [1] Tallon-Baudry, C., Bertrand, O., Delpuech, C., & Pernier, J. (1997).
       Oscillatory γ-Band (30–70 Hz) Activity Induced by a Visual Search Task in
       Humans. In The Journal of Neuroscience (Vol. 17, Issue 2, pp. 722–734).
       Society for Neuroscience.
       https://doi.org/10.1523/jneurosci.17-02-00722.1997

    """
    m = []
    for ii in range(len(freq)):
        # Sigma controls the width of the gaussians applied to each wavelet. This
        # is adaptive for each frequency to match ncycles
        sigma = ncycles / (2*np.pi*freq[ii])

        # Compute time vector for this wavelet
        t = np.arange(-win_len*sigma, win_len*sigma, 1/sample_rate)

        # Compute oscillatory component
        wave = np.exp(2*np.pi*1j*t*freq[ii])

        # Compute gaussian-window component
        gauss = np.exp((-(t/2)**2) / (2*sigma**2))

        # Make wavelet
        mlt = wave * gauss

        if normalise == 'simple':
            # Set simple normalisation (output amplitude should match
            # oscillation amplitude)
            mlt = 2 * mlt / np.abs(mlt).sum()
        elif normalise == 'tallon':
            # Set normalisation factor from Tallon-Baudry 1997
            A = (sigma*np.sqrt(np.pi))**(-1/2)
            mlt = A * mlt
        elif normalise == 'wikipedia':
            # Set normlisation from wikipedia: https://en.wikipedia.org/wiki/Morlet_wavelet
            A = (1 + np.exp(-sigma**2) - 2 * np.exp(-3/4 * sigma**2)) ** -0.5
            A = np.pi**(-.25) * A
            mlt = A * mlt
        elif normalise == 'mne':
            # Set normalisation step from MNE-python
            # https://github.com/mne-tools/mne-python/blob/master/mne/time_frequency/tfr.py#L98
            mlt = mlt / (np.sqrt(0.5) * np.linalg.norm(mlt.ravel()))

        m.append(mlt)

    return m
