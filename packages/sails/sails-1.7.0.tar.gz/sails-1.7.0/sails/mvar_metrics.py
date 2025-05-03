#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np

from .anam import AbstractAnam, register_class
from sails.support import ensure_leading_positive, ensure_leading_negative
from sails import plotting

__all__ = []


class AbstractMVARMetrics(AbstractAnam):
    """This is a base class for computing various connectivity metrics from
    fitted autoregressive models"""

    hdf5_outputs = []

    def __init__(self):
        AbstractAnam.__init__(self)

    @property
    def S(self):
        """Spectral Matrix of shape [nsignals, nsignals, order, epochs]"""
        return spectral_matrix(self.H, self.resid_cov)

    @property
    def PSD(self):
        """Power Spectral Density matrix"""
        return np.abs(psd_matrix(self.S, self.sample_rate))

    @property
    def inv_S(self):
        """Inverse Power Spectrl Density matrix"""
        return inv_spectral_matrix(self.H, self.resid_cov)

    @property
    def coherency(self):
        """Complex-valued coherency"""
        return coherency(self.S)

    @property
    def magnitude_squared_coherence(self):
        """Magnitude squared coherence"""
        return magnitude_squared_coherence(self.S)

    @property
    def imaginary_coherence(self):
        """Imaginary part of complex coherency"""
        return imaginary_coherence(self.S)

    @property
    def phase_coherence(self):
        """Phase angle of complex coherency"""
        return phase_coherence(self.S)

    @property
    def partial_coherence(self):
        """Partialled magnitude-squared coherence"""
        return partial_coherence(self.inv_S)

    @property
    def ff_directed_transfer_function(self):
        """Full-frequency directed transfer function"""
        return ff_directed_transfer_function(self.H)

    @property
    def d_directed_transfer_function(self):
        """Direct directed transfer function"""
        return d_directed_transfer_function(self.H, self.inv_S)

    @property
    def directed_transfer_function(self):
        """Directed transfer function"""
        return directed_transfer_function(self.H)

    @property
    def partial_directed_coherence(self):
        """Partial directed coherence"""
        return partial_directed_coherence(self.Af)

    @property
    def isolated_effective_coherence(self):
        """Isolated effective coherence"""
        return isolated_effective_coherence(self.Af, self.resid_cov)

    @property
    def geweke_granger_causality(self):
        """Geweke granger causality"""
        return geweke_granger_causality(self.S, self.H, self.resid_cov)

    def plot_diags(self, metric='S', inds=None, F=None, ax=None):
        """Helper function for plotting the diagonal part of a connectivty
        metric. Calls sails.plotting.plot_diagonal.

        Parameters
        ----------
        metric : str
            Name of the connectivity metric to plot (Default value = 'S')
        F : matplotlib figure handle
            Handle for matplotlib figure to plot in (Default value = None)
        ax : matplotlib axes handle
            Handle for matplotlib axes to plot in (Default value = None)

        """

        met = getattr(self, metric)
        plotting.plot_diagonal(self.freq_vect, met, title=metric, F=F, ax=ax)

    def plot_summary(self, metric='S', ind=1):
        """Helper function for plotting a summary of a connectivty metric.
        Calls sails.plotting.plot_summary.

        Parameters
        ----------
        metric : str
            Name of the connectivity metric to plot (Default value = 'S')
        ind : int
           Index into frequency dimension to plot connectivity matrix (Default value = 1)


        """

        met = getattr(self, metric)
        plotting.plot_metric_summary(self.freq_vect, met, ind=ind)

    def get_spectral_generalisation(self, metric='S'):
        """Compute the spectral generalisation matrix for a given metric.
        Returns the spatial similarity of different frequencies.

        Parameters
        ----------
        metric : str
            Name of the connectivity metric to plot (Default value = 'S')

        Returns
        -------
        ndarray
            Matrix of spectral generalisation [nfrequencies x nfrequencies]

        """

        met = np.abs(getattr(self, metric)[:, :, :, 0])
        met = met.reshape((met.shape[0]**2, met.shape[2]))

        return met.T.dot(met)

    def get_node_weight(self, metric='S'):
        """Compute the node weight for a given connectivity metric.

        Parameters
        ----------
        metric : str
            Name of the connectivity metric to plot (Default value = 'S')

        Returns
        -------
        ndarray
            Node-weight matrix of size [nchannels x nchannels]


        """

        met = np.abs(getattr(self, metric)[:, :, :, 0])
        for ii in range(met.shape[2]):
            met[:, :, ii] = met[:, :, ii] - np.diag(np.diag(met[:, :, ii]))

        nconnections = met.shape[0]+met.shape[1]-1

        return met[:, 0, :] + met[0, :, :] / nconnections


__all__.append('AbstractMVARMetrics')
register_class(AbstractMVARMetrics)


class ModalMvarMetrics(AbstractMVARMetrics):
    """This class for computing various connectivity metrics based on a Modal
    decomposition of a fitted MVAR model

    This is typically called using the :meth:`initialise` or
    :meth:`initialise_from_modes` classmethods to compute the decomposition and
    return a class instance containing them.

    """

    def __init__(self):
        AbstractMVARMetrics.__init__(self)

    # This is only used when used within Anamnesis
    hdf5_outputs = ['resid_cov', 'freq_vect', 'sample_rate', 'H', 'modes']

    @classmethod
    def initialise(cls, model, sample_rate, freq_vect, sum_modes=True):
        """Compute some basic values from the pole-residue decomposition of the
        A matrix. This is a class method which creates and returns a
        :class:`ModalMvarMetrics` instance containing the decomposition
        parameters with methods computing various connectivity metrics.

        This class computes the transfer function H using modal parameters.

        Currently only implemented for a single realisation (A.ndim == 3)

        Parameters
        ----------
        model : sails LinearModel
            SAILS class instance containing a fitted linear model.
        sample_rate : float
            Sample rate of the dataset
        freq_vect : ndarray
            Vector of specifying which frequencies to compute connectivity at.
        sum_modes : bool
            Flag indicating whether to sum across modes (Default value = True)

        Returns
        -------
        sails.ModalMvarMetrics instance

        """

        # Create object
        ret = cls()
        A = model.parameters
        resid_cov = model.resid_cov

        if A.ndim == 4:
            NotImplementedError('Modal Metrics only implemented for single '
                                'realisations of A')
        else:
            # Add dummy epoch
            A = A[..., None]

        A = ensure_leading_negative(A)

        if resid_cov.ndim == 2:
            resid_cov = resid_cov[..., None]  # Add a dummy epoch
        if resid_cov.shape[2] != A.shape[0]*A.shape[2]:
            # Repeat resid cov per epoch/mode (probably only valid for
            # modes...)
            resid_cov = np.repeat(resid_cov, A.shape[0]*A.shape[2], axis=-1)

        ret.resid_cov = resid_cov
        ret.freq_vect = freq_vect
        ret.sample_rate = sample_rate

        # Compute transfer function
        from .modal import MvarModalDecomposition
        ret.modes = MvarModalDecomposition.initialise(model,
                                                      sample_rate=sample_rate,
                                                      normalise=False)
        ret.H = ret.modes.transfer_function(sample_rate, freq_vect, sum_modes=sum_modes)

        return ret

    @classmethod
    def initialise_from_modes(cls, model, modes, sample_rate, freq_vect, mode_inds=None, sum_modes=True):
        """Compute some basic values from the pole-residue decomposition of the
        A matrix. This is a class method which creates and returns a
        :class:`sails.ModalMvarMetrics` instance containing the decomposition
        parameters with methods computing various connectivity metrics.

        This class computes the transfer function H using modal parameters. A
        sub-set of modes can be used to compute a reduced H.

        Currently only implemented for a single realisation (A.ndim == 3)

        Parameters
        ----------
        model : sails LinearModel
            SAILS class instance containing a fitted linear model.
        modes : sails MvarModalDecomposition
            SAILS class instance containing a fitted modal decomposition
        sample_rate : float
            The sample rate of the fitted data
        freq_vect : ndarray
            Vector of specifying which frequencies to compute connectivity at.
        mode_inds : ndarray
            Which modes to use when constructing H (Default value = None)
        sum_modes :Boolean
            Flag indicating whether to sum across modes when constructing H
            (Default value = True)

        Returns
        -------
        sails.ModalMvarMetrics instance

        """
        # Create object
        ret = cls()
        ret.modes = modes
        ret.freq_vect = freq_vect
        ret.sample_rate = float(sample_rate)

        A = model.parameters
        resid_cov = model.resid_cov

        if A.ndim == 4:
            NotImplementedError('Modal Metrics only implemented for single '
                                'realisations of A')
        else:
            # Add dummy epoch
            A = A[..., None]

        A = ensure_leading_positive(A)

        if resid_cov.ndim == 2:
            resid_cov = resid_cov[..., None]  # Add a dummy epoch
        if resid_cov.shape[2] != A.shape[0]*A.shape[2]:
            # Repeat resid cov per epoch/mode (probably only valid for
            # modes...)
            resid_cov = np.repeat(resid_cov, A.shape[0]*A.shape[2], axis=-1)
        ret.resid_cov = resid_cov

        if mode_inds is None:
            mode_inds = np.arange(modes.nmodes)

        # Compute transfer function
        ret.H = ret.modes.transfer_function(sample_rate, freq_vect,
                                            modes=mode_inds,
                                            sum_modes=sum_modes)

        return ret


__all__.append('ModalMvarMetrics')
register_class(ModalMvarMetrics)


class FourierMvarMetrics(AbstractMVARMetrics):
    """This class for computing various connectivity metrics based on the
    Fourier transform of the MVAR co-efficients.

    This is typically called using the :meth:`initialise` classmethod to compute
    the frequency transform and return a class instance with methods for
    computing different connectivity estimators

    """

    # This is only used when used within anamnesis
    hdf5_outputs = ['resid_cov', 'freq_vect', 'sample_rate', 'H', '_A', 'Af']

    def __init__(self):
        AbstractMVARMetrics.__init__(self)

    @classmethod
    def initialise(cls, model, sample_rate, freq_vect, nmodes=None):
        """Compute some basic values from the Fourier transform of the A
        matrix. This is a class method which creates and returns a
        :class:`FourierMvarMetrics` instance with methods computing
        various connectivity metrics.

        This class computes the transfer function H the Fourier transform.

        Parameters
        ----------
        model : sails LinearModel
            SAILS class instance containing a fitted linear model.
        sample_rate : float
            Sample rate of the dataset
        freq_vect : ndarray
            Vector of specifying which frequencies to compute connectivity at.

        Returns
        -------
        sails.FourierMvarMetrics instance

        """

        # Create object
        ret = cls()
        A = model.parameters
        resid_cov = model.resid_cov

        if A.ndim == 3:
            A = A[..., None]  # Add a dummy epoch

        ret._A = A

        A = ensure_leading_positive(A)

        if resid_cov.ndim == 2:
            resid_cov = resid_cov[..., None]  # Add a dummy epoch

        if resid_cov.shape[2] != A.shape[3]:
            # Repeat resid cov per epoch/mode (probably only valid for
            # modes...)
            resid_cov = np.repeat(resid_cov, A.shape[3], axis=-1)

        ret.resid_cov = resid_cov
        ret.freq_vect = freq_vect
        ret.sample_rate = float(sample_rate)

        # Get frequency transform of A
        ret.Af = ar_spectrum(A, resid_cov, sample_rate, freq_vect)

        # Get transfer function
        ret.H = transfer_function(ret.Af)

        return ret


__all__.append('FourierMvarMetrics')
register_class(FourierMvarMetrics)


def modal_transfer_function(evals, evecl, evecr, nchannels,
                            sample_rate=None, freq_vect=None):
    """Compute the transfer function in pole-residue form, splitting the system
    into modes with separate transfer functions. The full system transfer
    function is then a linear sum of each modal transfer function.

    Parameters
    ----------
    evals : ndarray
        Complex valued eigenvalues from an eigenvalue decomposition of an MVAR
        parameter matrix.
    evecl : ndarray
        Complex valued left-eigenvectorsfrom an eigenvalue decomposition of an
        MVAR parameter matrix.
    evecr : ndarry
        Complex valued right-eigenvectorsfrom an eigenvalue decomposition of an
        MVAR parameter matrix.
    nchannels : int
        Number of channels in the decomposed system
    sample_rate : float
        The sampling  rate of the decomposed system (Default value = None)
    freq_vect : ndarray
        Vector of frequencies at which to evaluate the transfer function (Default value = None)

    Returns
    -------
    ndarray
        Modal transfer-function (H) of size [nchannels x nchannels x nfrequencies x nmodes]

    """

    if (sample_rate is None and freq_vect is not None) or \
       (sample_rate is not None and freq_vect is None):
        raise ValueError('Please define both sample_rate and freq_vect '
                         '(or neither to return normalised frequency 0->pi)')

    if freq_vect is None and sample_rate is None:
        # Use normalised frequency
        freq_vect_rads = np.linspace(0, np.pi, 512)
    else:
        # convert user defined frequecies to radians
        freq_vect_rads = (freq_vect / (sample_rate / 2.)) * np.pi

    # Compute transfer function per mode
    H = np.zeros((nchannels, nchannels,
                 len(freq_vect_rads), len(evals)), dtype=complex)

    # Compute point on unit circle for each frequency
    z = np.cos(freq_vect_rads) + 1j*np.sin(freq_vect_rads)

    for imode in range(len(evals)):

        # Compute residue matrix from left and right eigenvectors
        l = np.atleast_2d(evecl[:nchannels, imode]).T
        r = np.atleast_2d(evecr[:nchannels, imode]).conj()
        residue = l.dot(r)

        for ifreq in range(len(freq_vect_rads)):

            # Compute transfer function for this frequency and this mode
            num = residue * z[ifreq]
            dom = z[ifreq] - evals[imode]
            H[:, :, ifreq, imode] = num / dom

    return H


__all__.append('modal_transfer_function')


# Spectrum estimators


def sdf_spectrum(A, sigma, sample_rate, freq_vect):
    """Estimate of the Spectral Density as found on wikipedia and [Quirk1983]_.

    This assumes that the spectral representation of A is invertable

    Parameters
    ----------
    A : ndarray
        Matrix of autoregressive parameters, of size [nchannels x nchannels x model order]
    sigma : ndarray
        Residual covariance matrix of the modelled system
    sample_rate : float
        The samplingfrequency of the modelled system
    freq_vect : ndarray
        Vector of frequencies at which to evaluate the spectrum

    Returns
    -------
    ndarray
        Frequenecy transform of input A, of size [nchannels x nchannels x nfrequencies]


    """
    # model order
    order = A.shape[2] - 1
    nsignals = A.shape[0]
    T = 1./sample_rate
    spectrum = np.zeros((nsignals, nsignals, len(freq_vect)), dtype=complex)
    eye = np.eye(nsignals)

    for node1 in range(nsignals):
        for node2 in range(nsignals):
            for idx, f in zip(range(len(freq_vect)), freq_vect):

                est = eye[node1, node2]

                for k in range(1, order+1):
                    est = A[node1, node2, k] * np.exp(0-1j*2*np.pi*k*f*T)

                num = sigma[node1, node2] * T
                dom = np.abs(est)**2
                spectrum[node1, node2, idx] = num / dom

    return spectrum


__all__.append('sdf_spectrum')


def psd_spectrum(A, sigma, sample_rate, freq_vect):
    """Estimate the PSD representation of a set of MVAR coefficients as stated in
    [Penny2009]_ section 7.4.4.

    This assumes that the spectral representation of A is invertable

    WARNING: does not behave as expected for some data, use with caution.
    ar_spectrum is recommended.

    Parameters
    ----------
    A : ndarray
        Matrix of autoregressive parameters, of size [nchannels x nchannels x model order]
    sigma : ndarray
        Residual covariance matrix of the modelled system
    sample_rate : float
        The samplingfrequency of the modelled system
    freq_vect : ndarray
        Vector of frequencies at which to evaluate the spectrum

    Returns
    -------
    ndarray
        Frequenecy transform of input A, of size [nchannels x nchannels x nfrequencies]


    """
    # model order
    order = A.shape[2] - 1
    nsignals = A.shape[0]
    T = 1./sample_rate
    spectrum = np.zeros((nsignals, nsignals, len(freq_vect)), dtype=complex)
    eye = np.eye(nsignals)

    for node1 in range(nsignals):
        for node2 in range(nsignals):
            for idx, f in zip(range(len(freq_vect)), freq_vect):

                # Normalised digital frequency
                f = f / sample_rate

                est = eye[node1, node2]

                for k in range(1, order+1):
                    est += A[node1, node2, k] * np.exp(0-1j*2*np.pi*k*f)

                spectrum[node1, node2, idx] = est

    # Compute the PSD_mvar

    psd = np.zeros_like(spectrum)
    for idx, f in zip(range(len(freq_vect)), freq_vect):
        A_inv = np.linalg.inv(spectrum[..., idx])
        # Hermitian of the inverse
        A_inv_herm = np.array(np.asmatrix(A_inv).H)
        psd[:, :, idx] = T * (A_inv.dot(sigma).dot(A_inv_herm))

    return psd


__all__.append('psd_spectrum')


def ar_spectrum(A, sigma, sample_rate, freq_vect):
    """Estimate the spectral representation of a set of MVAR coefficients as
    suggested by [Baccala2001]_, the equation without a number just
    below equation 13.

    Parameters
    ----------
    A : ndarray
        Matrix of autoregressive parameters, of size [nchannels x nchannels x model order]
    sigma : ndarray
        Residual covariance matrix of the modelled system
    sample_rate : float
        The samplingfrequency of the modelled system
    freq_vect : ndarray
        Vector of frequencies at which to evaluate the spectrum

    Returns
    -------
    ndarray
        Frequenecy transform of input A, of size [nchannels x nchannels x nfrequencies]


    """

    # This routine assumes that our parameter matrix is of the form where
    # we have a leading positive.  Ensure that this is the case.
    A = ensure_leading_positive(A)

    if A.ndim == 3:
        A = A[..., None]

    # model order
    order = A.shape[2] - 1

    nsignals = A.shape[0]
    nepochs = A.shape[3]

    spectrum = np.zeros((nsignals, nsignals,
                         len(freq_vect), nepochs), dtype=complex)

    for idx, f in zip(range(len(freq_vect)), freq_vect):
        # Normalised digital frequency
        f = f / sample_rate

        est = 0+0j

        for k in range(1, order+1):
            est -= A[:, :, k, :] * np.exp(0-1j*2*np.pi*k*f)

        spectrum[:, :, idx, :] = est

    return spectrum


__all__.append('ar_spectrum')


def transfer_function(Af):
    """Function for computing the transfer function of a system from the
    frequency transform of the autoregressive parameters.

    Parameters
    ----------
    Af :
        Frequency domain version of parameters (can be calculated using
        ar_spectrum function) [nchannels x nchannels x nfreqs x nepochs]

    Returns
    -------
    ndarray
        System transfer function, of size [nchannels x nchannels x nfreqs x nepochs]


    Note
    ----

    This function computes this the transfer function :math:`H` as defined by:

    .. math:: H(f) = ( I - Af(f) )^{-1}

    where :math:`Af` is the frequency transformed autoregessive parameter
    matrix and :math:`I` is identity.

    """

    # Remove identity from Af
    Afi = np.repeat(np.eye(Af.shape[0])[:, :, None],
                    Af.shape[2], axis=-1)[..., None] - Af

    nchannels = Af.shape[0]
    nfreqs = Af.shape[2]
    nepochs = Af.shape[-1]

    tf = np.zeros((nchannels, nchannels,
                   nfreqs, nepochs), dtype=complex)

    for e in range(nepochs):
        for f in range(nfreqs):
            tf[:, :, f, e] = np.linalg.inv(Afi[:, :, f, e])

    return tf


__all__.append('transfer_function')


def spectral_matrix(H, noise_cov):
    """Function for computing the spectral matrix, the matrix of spectra and
    cross-spectra.

    Parameters
    ----------
    H : ndarray
        The transfer matrix [nchannels x nchannels x nfreqs x nepochs]
    noise_cov : ndarray
        The noise covariance matrix of the system
        [nchannels x nchannels x nepochs]

    Returns
    -------
    ndarray
        System spectral matrix, of size [nchannels x nchannels x nfreqs x nepochs]

    Note
    ----

    This function computes the system spectral matrix as defined by:

    .. math:: S(f) = H(f)\\Sigma H(f)^H

    where :math:`H` is the  transfer function, :math:`\\Sigma` is the residual
    covariance and :math:`^H` the Hermitian transpose.

    """

    # Make sure that we have the 4th dimension
    if H.ndim < 4:
        H = H[:, :, :, None]

    S = np.zeros_like(H)

    for i in range(H.shape[2]):
        for j in range(H.shape[3]):
            S[:, :, i, j] = H[:, :, i, j].dot(
                noise_cov[:, :, j]).dot(H[:, :, i, j].T.conj())

    return S


__all__.append('spectral_matrix')


def psd_matrix(S, sample_rate):
    """Function for computing the power spectral density matrix with units matched
    to scipy.signal.welch(X, axis=1, scaling='spectrum')

    Parameters
    ----------
    S :
        The spectral matrix [nchannels x nchannels x nfreqs x nepochs]
    sample_rate :
        The sampling rate of the system

    Returns
    -------


    """

    return S / sample_rate


__all__.append('psd_matrix')


def inv_spectral_matrix(H, noise_cov):
    """Function for computing the inverse spectral matrix.

    Parameters
    ----------
    H :
        The transfer matrix [nchannels x nchannels x nfreqs x nepochs]
    noise_cov :
        The noise covariance matrix of the system
        [nchannels x nchannels x nepochs]

    Returns
    -------
    ndarray
        Inverse system spectral matrix, of size [nchannels x nchannels x nfreqs x nepochs]

    Note
    ----

    This function computes the inverse spectral matrix as defined by:

    .. math:: S(f) = ( H(f)\\Sigma H(f)^H )^{-1}

    where :math:`H` is the  transfer function, :math:`\\Sigma` is the residual
    covariance and :math:`^H` the Hermitian transpose.

    """

    inv_S = np.zeros_like(H)

    S = spectral_matrix(H, noise_cov)

    for f in range(S.shape[2]):
        for e in range(S.shape[3]):
            inv_S[:, :, f, e] = np.linalg.pinv(np.abs(S[:, :, f, e]))

    return inv_S


__all__.append('inv_spectral_matrix')


def coherency(S):
    """Method for computing the Coherency. This is the complex form of
    coherence, from which metrics such as magnitude squared coherence can be
    derived

    Parameters
    ----------
    S : ndarray
        The system spectral matrix in 3D or 4D form, of size
        [nchannels x nchannels x nfreqs x nepochs]

    Returns
    -------
    ndarray
        Complex-valued coherency matrix, of size [nchannels x nchannels x nfreqs x nepochs]

    Note
    ----

    This function computes the coherency as defined by:

    .. math:: Coh_{ij}(f) = \\frac{S_{ij}(f)}{ \\sqrt{ | S_{ii}(f)S_{jj}(f) | } }

    where :math:`S` is the system spectral matrix.

    """

    coh = np.zeros_like(S)

    for i in range(S.shape[0]):
        for j in range(S.shape[0]):
            coh[i, j, :, :] = S[i, j, :, :] / \
                (np.sqrt(np.abs(S[i, i, :, :] * S[j, j, :, :])))

    return coh


__all__.append('coherency')


def magnitude_squared_coherence(S):
    """Method for computing the Magnitude Squred Coherence.

    Parameters
    ----------
    S : ndarray
        The system spectral matrix in 3D or 4D form, of size
        [nchannels x nchannels x nfreqs x nepochs]

    Returns
    -------
    ndarray
        Magnitude squared coherence matrix, of size [nchannels x nchannels x nfreqs x nepochs]

    Note
    ----

    This function computes this magnitude squared coherence as defined by:

    .. math:: MSC_{ij}(f) = \\frac{ |S_{ij}(f)|^2 }{ \\sqrt{ | S_{ii}(f)S_{jj}(f) | } }

    where :math:`S` is the system spectral matrix. This is closely related to
    the complex valued-coherency.

    """

    return np.power(np.abs(coherency(S)), 2)


__all__.append('magnitude_squared_coherence')


def imaginary_coherence(S):
    """Method for computing the imaginary coherence

    Parameters
    ----------
    S : ndarray
        The system spectral matrix in 3D or 4D form, of size
        [nchannels x nchannels x nfreqs x nepochs]

    Returns
    -------
    ndarray
        Imaginary coherence matrix, of size [nchannels x nchannels x nfreqs x nepochs]

    Note
    ----

    This function computes the imaginary cohereence as defined by:

    .. math:: iCoh_{ij}(f) = \\Im \\bigg( \\frac{ S_{ij}(f) }{ \\sqrt{ | S_{ii}(f)S_{jj}(f) | } }  \\bigg)

    where :math:`S` is the system spectral matrix. This is closely related to
    the complex valued-coherency.


    """

    return coherency(S).imag


__all__.append('imaginary_coherence')


def phase_coherence(S):
    """Method for computing the phase coherence

    Parameters
    ----------
    S : ndarray
        The system spectral matrix in 3D or 4D form, of size
        [nchannels x nchannels x nfreqs x nepochs]

    Returns
    -------
    ndarray
        Phase coherence matrix, of size [nchannels x nchannels x nfreqs x nepochs]

    Note
    ----

    This function computes the phase-coherence as defined by:

    .. math:: pCoh_{ij}(f) = \\arg \\bigg( \\frac{ S_{ij}(f) }{ \\sqrt{ | S_{ii}(f)S_{jj}(f) | } } \\bigg )

    where :math:`S` is the system spectral matrix. This is closely related to
    the complex valued-coherency.


    """

    return np.angle(coherency(S))


__all__.append('phase_coherence')


def partial_coherence(inv_S):
    """Method for computing the Partial Coherence.

    Parameters
    ----------
    inv_S : ndarray
        The system spectral matrix in 3D or 4D form, of size
        [nchannels x nchannels x nfreqs x nepochs]

    Returns
    -------
    ndarray
        Complex-valued coherency matrix, of size [nchannels x nchannels x nfreqs x nepochs]

    Note
    ----

    This function computes the partial coherence using the inverse spectral
    matrix :math:`P = S^{-1}` where :math:`S` is the system spectral matrix.
    The partial coherence is then computed as:

    .. math:: PCoh_{ij}(f) = \\frac{ |P_{ij}(f)|^2 }{ \\sqrt{ | P_{ii}(f)P_{jj}(f) | } }

    """

    pcoh = np.zeros_like(inv_S)

    for i in range(inv_S.shape[0]):
        for j in range(inv_S.shape[0]):
            pcoh[i, j, :, :] = np.power(np.abs(inv_S[i, j, :, :]), 2) / \
                (inv_S[i, i, :, :] * inv_S[j, j, :, :])

    return pcoh


__all__.append('partial_coherence')


def ff_directed_transfer_function(H):
    """Function for computing the full-frequency directed transfer function as defined in [Korzeniewska2003]_.

    Parameters
    ----------
    H : ndarray
        The system transfer function [nchannels x nchannels x nfreqs x nepochs]

    Returns
    -------
    ndarray
        The full-frequency directed transfer function

    Note
    ----

    This function computes the directed transfer function from the system transfer function :math:`H`.

    .. math:: ffDTF_{ij}(f) = \\frac{ | H_{ij}(f) |^2 }{ \\sqrt{ \\sum_f \\sum_f | \\bar{H}_{ij}(f) |^2 } }

    This is similar to the directed transfer function with the exceptiont hat
    the normalisation in the denominator is summed across frequency.

    """

    dtf = np.zeros_like(H)

    for e in range(H.shape[3]):
        for i in range(H.shape[0]):
            # Make the denominator for this channel over all frequencies
            dtf_denom = np.sum(np.power(np.abs(H[i, :, :, e]), 2))

            # Estimate ffDTF
            for f in range(H.shape[2]):
                for j in range(H.shape[0]):
                    dtf[i, j, f, e] = np.power(
                        np.abs(H[i, j, f, e]), 2) / dtf_denom

    return dtf


__all__.append('ff_directed_transfer_function')


def d_directed_transfer_function(H, inv_S):
    """Function for computing the direct directed transfer function as defined in [Korzeniewska2003]_.

    Parameters
    ----------
    H :
        The transfer matrix [nchannels x nchannels x nfreqs x nepochs]
    s :
        inv_S: The inverse spectral matrix
        [nchannels x nchannels x nfreqs x nepochs]
    inv_S :


    Returns
    -------
    ndarray
        The direct directed transfer function

    Note
    ----

    This function computes the direct directed transfer function by point-wise
    multiplicationo of the partial coherence :math:`P` and the full-frequency
    directed transfer function :math:`dDTF`.

    .. math:: dDTF(F) = P(f) * ffDTF(f)

    This is similar to the directed transfer function with the exceptiont hat
    the normalisation in the denominator is summed across frequency.


    """

    return partial_coherence(inv_S) * ff_directed_transfer_function(H)


__all__.append('d_directed_transfer_function')


def partial_directed_coherence(Af):
    """Function to estimate the partial directed coherence from a set of
    multivariate parameters as defined in [Baccala2001]_.

    Parameters
    ----------
    Af : ndarray
        Frequency domain version of parameters (can be calculated using
        ar_spectrum function), of size
        [nchannels x nchannels x nfrequencies x nrealisations]

    Returns
    -------
    ndarray
        The partial directed coherence of the system.

    Note
    ----

    This function computes the partial coherence using the frequency transform
    of the autoregressive parameters :math:`Af` subtracted from Identity.

    .. math:: \\bar{Af}(f) = I - Af(f)

    The partial directed coherence is then

    .. math:: PDC_{ij}(f) = \\frac{ | \\bar{Af}_{ij}(f)| }{ \\sqrt{ \\sum_i | \\bar{Af}_{ij}(f) |^2 } }

    """

    pdc = np.zeros_like(Af)

    # Remove identity from Af
    Afi = np.repeat(np.eye(Af.shape[0])[:, :, None],
                    Af.shape[2], axis=-1)[..., None] - Af

    for e in range(Afi.shape[3]):
        for j in range(Afi.shape[0]):
            for f in range(Afi.shape[2]):
                pdc_denom = np.sqrt(
                    (np.abs(Afi[:, j, f, e])**2).sum())
                for i in range(Afi.shape[0]):
                    pdc[i, j, f, e] = np.abs(
                        Afi[i, j, f, e]) / pdc_denom

    return pdc


__all__.append('partial_directed_coherence')


def isolated_effective_coherence(Af, noise_cov):
    """Function for estimating the Isolated Effective Coherence as defined in
    [Pascual-Marqui2014]_.

    Parameters
    ----------
    Af : ndarray
        Frequency domain version of parameters (can be calculated
        using ar_spectrum function)
        [nchannels x nchannels x nfreqs x nepochs]
    noise_cov : ndarray
        The noise covariance matrix of the system
        [nchannels x nchannels x nepochs]

    Returns
    -------
    ndarray
        The isolated effective coherence.

    """

    # Remove identity from Af
    Afi = np.repeat(np.eye(Af.shape[0])[:, :, None],
                    Af.shape[2], axis=-1)[..., None] - Af

    nchannels = Afi.shape[0]
    nfreqs = Afi.shape[2]
    nepochs = Afi.shape[3]

    iec = np.zeros((nchannels, nchannels, nfreqs, nepochs), dtype=complex)

    for e in range(nepochs):
        # Get inverse of the residual noise covariance and set off-diagonal
        # elements to zero
        S = noise_cov[..., e]  # S = np.linalg.inv(noise_cov[..., e])
        iso_s = np.linalg.inv(np.diag(np.diag(S)))

        for f in range(nfreqs):
            for i in range(nchannels):
                for j in range(nchannels):

                    iso_params = np.diag(np.diag(Afi[:, :, f, e]))
                    # Set all parameters except the diagonal and connection of
                    # interest to zero
                    iso_params[i, j] = Afi[i, j, f, e]

                    denom_col = iso_s[j, j] * np.abs(iso_params[j, j])**2

                    numerator = iso_s[i, i] * np.abs(iso_params[i, j])**2

                    iec[i, j, f, e] = numerator / (numerator + denom_col)

    return iec.real


__all__.append('isolated_effective_coherence')


def directed_transfer_function(H):
    """Method for computing the Directed Transfer Function as defined in
    [Kaminski1991]_.

    Parameters
    ----------
    H : ndarray
        The transfer matrix [nchannels x nchannels x nfreqs x nepochs]

    Returns
    -------
    ndarray
        The directed transfer function of the system.

    Note
    ----

    This function computes the directed transfer function from the system transfer function :math:`H`.

    .. math:: DTF_{ij}(f) = \\frac{ | H_{ij}(f) |^2 }{ \\sqrt{ \\sum_j | \\bar{H}_{ij}(f) |^2 } }

    """

    dtf = np.zeros_like(H)

    for e in range(H.shape[3]):
        for i in range(H.shape[0]):
            for f in range(H.shape[2]):
                # Make the denominator for this channel
                dtf_denom = np.sum(np.power(np.abs(H[i, :, f, e]), 2))
                for j in range(H.shape[0]):
                    dtf[i, j, f, e] = np.power(
                        np.abs(H[i, j, f, e]), 2) / dtf_denom

    return dtf


__all__.append('directed_transfer_function')


def geweke_granger_causality(S, H, sigma):
    """This function computes the Geweke-Granger causality as defined in
    [Barrett2010]_

    Parameters
    ---------
    S : ndarray
        Spectral matrix [nchannels x nchannels x nfreqs x nepochs]
    H : ndarray
        The transfer matrix [nchannels x nchannels x nfreqs x nepochs]
    sigma : ndarray
        Residual noise covariance matrix

    Returns
    -------
    ndarray
        The Geweke-Granger causality


    """

    nchannels = S.shape[0]
    nfreqs = S.shape[2]
    nepochs = S.shape[3]

    ggc = np.zeros((nchannels, nchannels, nfreqs, nepochs), dtype=complex)

    for e in range(nepochs):

        # Compute conditional sigma matrix
        cond_sigma = np.zeros((nchannels, nchannels))
        inv_sigma = np.linalg.inv(sigma[:, :, e])
        for ii in range(nchannels):
            for jj in range(nchannels):
                cond_sigma[ii, jj] = sigma[jj, jj, e] - \
                                sigma[ii, jj, e]*inv_sigma[ii, ii]*sigma[jj, ii, e]

        for f in range(nfreqs):
            for ii in range(nchannels):
                for jj in range(nchannels):

                    denom = H[ii, jj, f, e] * cond_sigma[ii, jj] * H[ii, jj, f, e].conj()
                    denom = np.abs(S[ii, ii, f, e] - denom)

                    ggc[ii, jj, f, e] = np.log(np.abs(S[ii, ii, f, e]) / denom)

    return ggc


__all__.append('geweke_granger_causality')
