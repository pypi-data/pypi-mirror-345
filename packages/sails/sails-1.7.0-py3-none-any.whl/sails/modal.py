#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import scipy
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

from .anam import AbstractAnam, register_class
from sails.support import ensure_leading_negative
from sails.modelfit import coloured_noise_fit

__all__ = []


def adjust_phase(x):
    """Method for normalising eigenvector matrices to meet the conditions in
    eqn 21 of [Neumaier2001]_.

    Parameters
    ----------
    x : ndarray
        Vector of complex numbers to adjust the phase of

    Returns
    -------
    type
        Vector of numbers with adjusted phase

    """

    ox = np.zeros_like(x)

    # Rows of x
    for j in range(x.shape[0]):
        a = np.atleast_2d(np.real(x[j, :])).T
        b = np.atleast_2d(np.imag(x[j, :])).T
        tmp = np.dot(b.T, b) - np.dot(a.T, a)
        phi = .5 * np.arctan(2 * np.sum(a*b / tmp))
        bnorm = np.linalg.norm(np.sin(phi) * a + np.cos(phi) * b)
        anorm = np.linalg.norm(np.cos(phi) * a + np.sin(phi) * b)

        if bnorm > anorm:
            if phi < 0:
                phi = phi - (np.pi/2.)
            else:
                phi = phi + (np.pi/2.)

        ox[j, :] = x[j, :] * np.exp((0+1j) * phi)

    return ox


__all__.append('adjust_phase')


class MvarModalDecomposition(AbstractAnam):
    """Object which calculates the modal decomposition of a fitted model
    derived from the AbstractLinearModel class. This is typically created using
    the :meth:`initialise` classmethod which computes the decomposition and returns a
    populated object instance.
    """

    # This is only used when used within Anamnesis
    hdf5_outputs = ['nsignals', 'order', 'companion', 'evals', 'evecsr',
                    'evecsl', 'pole_pairs', 'modeinds', 'period',
                    'dampening_time', 'peak_frequency', 'dampening_time_hz', 'nmodes',
                    'delay_vect']

    def __init__(self):
        AbstractAnam.__init__(self)

    @classmethod
    def initialise(cls, model, sample_rate=None, normalise=False):
        """Compute the modal pole-residue decomposition of the A matrix from a
        fitted MVAR model.

        Currently only implemented for a single realisation (A.ndim == 3)

        Parameters
        ----------
        model : LinearModel
            Fitted model object.  Must be derived from AbstractLinearModel.
        sample_rate : float
            sample rate of system in Hz (Default value = None)
        normalise : bool
            Whether to adjust the phase of the eigenvectors (Default value = False)

        Returns
        -------
        type
            Modal decomposition object

        """

        # Create object
        ret = cls()

        A = model.parameters
        nsignals = ret.nsignals = A.shape[0]
        ret.order = A.shape[2] - 1
        nmodes = nsignals * ret.order

        if A.ndim == 4:
            pass
        else:
            # Add dummy epoch
            A = A[..., None]

        A = ensure_leading_negative(A)

        if model.resid_cov.ndim == 2:
            # Add a dummy epoch
            model.resid_cov = model.resid_cov[..., None]

        nrealisations = A.shape[3]

        # preallocate arrays
        ret.evals = np.zeros((nmodes, nrealisations), dtype=complex)
        ret.evecsr = np.zeros((nmodes, nmodes, nrealisations), dtype=complex)
        ret.evecsl = np.zeros((nmodes, nmodes, nrealisations), dtype=complex)

        ret.modeinds = np.zeros((nmodes, nrealisations), dtype=int)
        ret.pole_pairs = np.zeros_like(ret.evals, dtype=int) * np.nan

        for ii in range(nrealisations):

            # Generate companion form
            from .modelfit import A_to_companion
            ret.companion = A_to_companion(A[:, :, 1:, ii])

            # Roots are now the eigenvalues of the companion matrix
            ret.evals[:, ii], ret.evecsl[:, :, ii], ret.evecsr[:, :, ii] = \
                scipy.linalg.eig(ret.companion, left=True, right=True)

            # Apply normalisation from http://climate-dynamics.org/wp-content/uploads/2015/08/arfit.pdf
            if normalise:
                ret.evecsr[:, :, ii] = adjust_phase(ret.evecsr[:, :, ii].T).T

            # take left eigenvecs from right, might preserve scaling better
            ret.evecsl[:, :, ii] = np.linalg.inv(ret.evecsr[:, :, ii].conj().T)

            ret.modeinds[:, ii] = np.argsort(np.abs(ret.evals[:, ii]))[::-1]

            # Loop through poles with an imaginary part and find pairings, poles
            # with a zero imaginary part are left indexed as nan
            ppidx = 0
            for idx in range(len(ret.pole_pairs)):
                if ret.evals[idx].imag > 0:
                    # Find the conjugate pair
                    cidx = (abs(ret.evals[idx] - ret.evals.conj())).argmin()
                    ret.pole_pairs[idx] = ppidx
                    ret.pole_pairs[cidx] = ppidx
                    ppidx += 1

        # Compute the period and dampening time per mode
        # We ignore /0 warnings as they are expected for real modes
        old_warning = np.geterr()['divide']
        np.seterr(divide='ignore')
        ret.period = 2*np.pi / np.abs(np.angle(ret.evals))
        ret.dampening_time = -1.0 / np.log(np.abs(ret.evals))
        np.seterr(divide=old_warning)

        if sample_rate is not None:
            ret.peak_frequency = sample_rate / ret.period
            ret.dampening_time_hz = sample_rate / ret.dampening_time
        else:
            ret.peak_frequency = None
            ret.dampening_time_hz = None

        ret.nmodes = nmodes
        ret.delay_vect = model.delay_vect

        return ret

    @property
    def period_hz(self):
        """This is an old and deprecated way of accessing peak_frequency"""
        return self.peak_frequency

    def compute_residues(self):
        """Compute the residue matrix from the eigenvectors associated with each
        pole.

        Returns
        -------
        ndarray
            Array containing residue matrices for each pole.

        """

        # Compute the residue matrices and frequency responses per mode
        residue = np.zeros((self.nsignals, self.nsignals, self.nmodes), dtype=complex)

        for imode in range(len(self.evals)):
            # Compute residue matrix from left and right eigenvectors
            l = np.atleast_2d(self.evecsl[:self.nsignals, imode]).conj()
            r = np.atleast_2d(self.evecsr[:self.nsignals, imode]).T
            residue[:, :, imode] = l.dot(r).T

        return residue

    def compute_modal_parameters(self):
        """Compute the order 1 or 2 autoregressive coefficients associated with
        each pole or conjugate pair.

         .. warning::

            This function is a work in progress and has not been fully validated.

        Returns
        -------
        ndarray
            Array containing the time-domain AR parameters for each mode

        """

        # Compute the residue matrices and frequency responses per mode
        residue = self.compute_residues()

        A = np.zeros((self.nsignals, self.nsignals, 3, self.pole_pairs.max()+1))

        # Loop through nodes and connections
        for ii in np.arange(self.nsignals):
            for jj in np.arange(self.nsignals):
                # For each pole pair
                for kk in np.arange(self.pole_pairs.max()+1):
                    inds = self.pole_pairs[:, 0] == kk
                    b, a = signal.invresz(residue[ii, jj, inds].squeeze(),
                                          self.evals[inds, 0], [0])

                    # I'm scaling the ar coefficients by the leading numerator coeff.
                    # This scaling doesn't affect the roots (ie peak frequency) but
                    # will show up in the relative measures.
                    A[ii, jj, :len(a), kk] = a * b[0]

        return A

    def modal_freqz(self):
        """Compute filter characteristics for each pole"""

        # Compute the frequency response for the whole system
        w, h = signal.freqz(1, self.evals)
        mag_response = np.abs(h)
        phase_response = np.unwrap(np.angle(h))

        return w, mag_response, phase_response

    def excitation(self, resid_cov):
        """Compute the mode excitation as defined in [Neumaier2001]_.
        This is a metric to  quantify the dynamical importance of each mode in
        the decomposition.

        .. warning::

            This function is a work in progress and has not been fully validated.

        Parameters
        ----------
        resid_cov : ndarray
            Residual covariance matrix for modelled system

        Returns
        -------
        ndarray
            Vector containing modal excitation values

        """

        # Compute the excitation per mode
        inv_evecsr = np.linalg.inv(self.evecsr)

        decoupled_cov = inv_evecsr[:, :self.nsignals].dot(resid_cov[:, :, 0])
        decoupled_cov = decoupled_cov.dot(inv_evecsr[:, :self.nsignals].conj().T)

        abs_lambda_sq = np.power(np.abs(self.evals), 2)

        excitation = (np.diag(decoupled_cov) / (1 - abs_lambda_sq)).real
        excitation = excitation / np.sum(excitation)

        return excitation

    def transfer_function(self, sample_rate, freq_vect, modes=None,
                          sum_modes=True):
        """Compute the transfer function in pole-residue form, splitting the
        system into modes with separate transfer functions. The full system
        transfer function is then a linear sum of each modal transfer function.

        When sum_modes is False, this function returns the transfer function
        for each individual pole (ie will return a transfer function for each
        pole in a conjugate pair). Please use per_mode_transfer_function to
        compute the transfer function for individual modes (ie one transfer
        function for each real pole or complex-conjugate pair)

        Parameters
        ----------
        sample_rate : float
            sample rate of system in Hz
        freq_vect : ndarray
            Vector of frequencies at which to evaluate function
        modes : list of ints
            List of mode indices to evaluate over (optional) (Default value = None)
        sum_modes : bool
            Boolean indicating whether to sum modes or return all (Default value = True)

        Returns
        -------
        ndarray
            Array containing the transfer function for each individual pole

        """

        if (sample_rate is None and freq_vect is not None) or \
           (sample_rate is not None and freq_vect is None):
            raise ValueError('Please define both sample_rate and '
                             'freq_vect (or neither to return '
                             'normalised frequency 0->pi)')

        if freq_vect is None and sample_rate is None:
            # Use normalised frequency
            freq_vect_rads = np.linspace(0, np.pi, 512)
        else:
            # convert user defined frequecies to radians
            freq_vect_rads = (freq_vect / (sample_rate / 2.)) * np.pi

        # Allow us to pick out which modes we want
        if modes is None:
            modes = list(range(len(self.evals)))

        if sum_modes is False:
            nmodes = len(modes)
        else:
            nmodes = 1

        # Compute transfer function per mode
        residue = self.compute_residues()
        H = np.zeros((residue.shape[0],
                      residue.shape[0],
                      len(freq_vect_rads),
                      nmodes), dtype=complex)

        # Compute point on unit circle for each frequency
        z = np.cos(freq_vect_rads) + 1j*np.sin(freq_vect_rads)

        idx = 0

        for imode in modes:

            for ifreq in range(len(freq_vect_rads)):

                # Compute transfer function for this frequency and this mode
                num = residue[:, :, imode] * z[ifreq]
                dom = z[ifreq] - self.evals[imode]

                if sum_modes:
                    H[:, :, ifreq, 0] += num / dom
                else:
                    H[:, :, ifreq, idx] = num / dom

            idx += 1

        return H

    def per_mode_transfer_function(self, sample_rate, freq_vect):
        """Extracts the transfer function for each mode by summing the transfer
        function across pole-pairs where necessary

        The transfer function is computed for each pole using
        :meth:`transfer_function` before summing individual
        modes (real valued poles or complex-conjugate pairs).

        Parameters
        ----------
        sample_rate :
            sample rate of system in Hz
        freq_vect :
            Vector of frequencies at which to evaluate function

        Returns
        -------
        ndarray
            Array containing the transfer function for each individual mode

        """

        H = self.transfer_function(sample_rate, freq_vect, sum_modes=False)

        mi = self.mode_indices

        ret = np.zeros((len(freq_vect), len(mi)), dtype=complex)

        for idx, i in enumerate(mi):
            ret[:, idx] = np.sum(H[..., i], axis=3).squeeze()

        return ret

    def modal_transfer_function(self, sample_rate, modes=None):
        """Compute a transfer function matrix based on the excitation period for
        each mode

        Parameters
        ----------
        sample_rate : float
            sample rate of system in Hz
        modes : list of int
            List of mode indices to evaluate over (optional) (Default value = None)

        Returns
        -------
        ndarray
            Transfer function computed for each mode

        """

        # Allow us to pick out which modes we want
        if modes is None:
            modes = list(range(len(self.evals)))

        # Compute transfer function per mode
        H = np.zeros((self.residue.shape[0],
                      self.residue.shape[0],
                      len(modes)), dtype=complex)

        idx = 0

        for imode in modes:
            fv_rad = (self.peak_frequency[imode] / (sample_rate / 2.)) * np.pi

            # Compute point on unit circle for the relevant frequency
            z = np.cos(fv_rad) + 1j*np.sin(fv_rad)

            # Compute transfer function for this frequency and this mode
            num = self.residue[:, :, imode] * z
            dom = z - self.evals[imode]
            H[:, :, idx] = num / dom

            idx += 1

        return H

    def get_mode_inds(self, fmin=0, fmax=None,
                      mag_thresh=0, resid_thresh=0,
                      index_mode='inclusive'):
        """Helper function to identify mode indices based on given criteria.

        Parameters
        ----------
        fmin : float
             Minimum frequency of modes to include (Default value = 0)
        fmax : float
             Maximum frequency of modes to include (Default value = None)
        mag_thresh : float ( 0 > mag_thresh > 1 )
            Minimum pole magnitude to include (Default value = 0)
        resid_thresh : float
            Minimum value  of mode residue norm to include (Default value = 0)
        index_mode : {'inclusive','exclusive'}
            Flag indicating whether mode selection limits should be inclusive
            or exclusive (Default value = 'inclusive')

        Returns
        -------
        ndarray
            Array of integers indexing the included poles

        """

        if fmax is None:
            fmax = self.freq_vect_hz[-1]/2

        if index_mode == 'inclusive':

            inds = (self.peak_frequency >= fmin) * (self.peak_frequency <= fmax)

            if mag_thresh is not None:
                inds = inds * (np.abs(self.evals) >= mag_thresh)

            if resid_thresh is not None:
                inds = inds * (np.abs(self.residue_norm[:, None]) >= resid_thresh)

        elif index_mode == 'exclusive':

            inds = (self.peak_frequency > fmin) * (self.peak_frequency < fmax)

            if mag_thresh is not None:
                inds = inds * (np.abs(self.evals) > mag_thresh)

            if resid_thresh is not None:
                inds = inds * (np.abs(self.residue_norm[:, None]) > resid_thresh)

        else:
            raise ValueError("index_mode {0} not recognised, please use"
                             "'inclusive' or 'exclusive'".format(index_mode))

        return np.where(inds)[0]

    # TODO: Validate this function
    def modal_timecourse(self, data):
        """Compute the modal time-course from a dataset and a fitted model. This
        is the transformation of a set of [nsignals x time] data observations
        into modal coordinates of shape [nmodes x time].

        .. warning::

            This function is a work in progress and has not been fully validated.

        Parameters
        ----------
        data : ndarray
            Input data to convert into modal co-ordinates

        Returns
        -------
        ndarray
            Data transformed into modal time-series

        """

        # Preallocate modal time-course array
        r = np.zeros((self.nmodes, data.shape[1], data.shape[2]))

        for idx in range(self.order, data.shape[1]):

            # Get modal time-course for this sample
            for iep in range(data.shape[2]):

                # Generate delay embedded data for this sample
                deldat = np.zeros((self.nsignals*(self.order-1),))
                for idelay in range(1, len(self.delay_vect)):
                    deldat[(idelay-1)*self.nsignals:idelay*self.nsignals] = \
                        data[:, idx-idelay, iep]
                    r[:, idx, iep] = self.companion.dot(deldat)

        return r

    @property
    def residue_norm(self):
        """The matrix-norm of the residue matrix of each mode"""
        nmodes = len(self.modeinds)
        residue = self.compute_residues()
        return np.linalg.norm(residue.reshape(-1, nmodes), axis=0)

    @property
    def mode_indices(self):
        """Returns a list of tuples of mode indices where each tuple contains the
        indices of either a pole-pair or an unpaired pole

        Returns
        -------
        List
            list of tuples containing indices into the modes

        """
        modes = []
        handled_nodes = np.zeros_like(self.pole_pairs)
        for k in range(self.pole_pairs.shape[0]):
            # Deal with nodes we've already handled as conjugate pairs
            if handled_nodes[k] == 1:
                continue

            # Is this a real mode
            if np.isnan(self.pole_pairs[k]):
                # Single, real mode
                modes.append((k,))
                handled_nodes[k] = 1
            else:
                # Need to find pair index
                pidx = self.pole_pairs[k]

                indices = np.where(self.pole_pairs == pidx)[0]
                modes.append(tuple(indices))
                for idx in indices:
                    handled_nodes[idx] = 1

        return modes

    def pole_plot(self, ax=None, normscale=50, plottype='unitcircle'):
        """Plot the poles of the current system.

        Parameters
        ----------
        ax : matplotlib axes handle
            Optional axis on which to plot (Default value = None)
        normscale : float
            Scaling factor for points on plot (Default value = 50)
        plottype : {'unitcircle','eigenspectrum'}
            Flag indicating whether to plot results on a unit-circle or an
            eigenspectrum (Default value = 'unitcircle')

        Returns
        -------
        matplotlib axes handle
            Reference to axes on which plot was drawn

        """
        if ax is None:
            plt.figure()
            ax = plt.subplot(111)

        norm_factors = self.residue_norm / self.residue_norm.max()

        if plottype == 'unitcircle':

            x = np.cos(np.linspace(0, 2*np.pi, 128))
            y = np.sin(np.linspace(0, 2*np.pi, 128))
            plt.grid(True)

            ax.plot(x, y, 'k')

            ax.plot(.75*x, .75*y, 'k--', linewidth=.2)
            ax.plot(.5*x, .5*y, 'k--', linewidth=.2)
            ax.plot(.25*x, .25*y, 'k--', linewidth=.2)

            ax.plot(1.15*x[8:25], 1.15*y[8:25], 'k')
            ax.arrow(1.15*x[23], 1.15*y[23], x[24]-x[23], y[24]-y[23],
                     head_width=.05, color='k')

            handled_nodes = np.zeros_like(self.pole_pairs)

            for k in range(self.pole_pairs.shape[0]):
                # Deal with nodes we've already handled as conjugate pairs
                if handled_nodes[k] == 1:
                    continue

                # Need to find pair index
                pidx = self.pole_pairs[k]

                # Deal with real pole case
                if np.isnan(pidx):
                    indices = [k]
                else:
                    indices = np.where(self.pole_pairs == pidx)[0]

                # Stash the real and imaginary parts
                r = []
                i = []
                ms = None

                for idx in indices:
                    handled_nodes[idx] = 1

                    r.append(self.evals[idx].real)
                    i.append(self.evals[idx].imag)

                    # The scaling should be the same for the conjugate pair
                    if ms is None:
                        ms = norm_factors[idx]*normscale

                # Plot them all together to maintain the same colour
                # for each pair
                plt.plot(r, i, '+', ms=ms, markeredgewidth=2)

            ax.set_xlabel('Real')
            ax.set_ylabel('Imaginary')

            ax.set_ylim(-1.2, 1.2)
            ax.set_xlim(-1.2, 1.2)

            ax.annotate('Frequency', xy=(.56, 1.02))

            ax.set_aspect('equal')

        elif plottype == 'eigenspectrum':

            mags = np.abs(self.evals)
            mags = mags / (1-mags)

            if self.peak_frequency is None:
                x_vect = self.period
                xlabel = 'Period (samples)'
            else:
                x_vect = self.peak_frequency
                xlabel = 'Frequency (Hz)'

            yt = np.linspace(0, 1., 11)
            yt_scaled = yt / (1-yt)

            ax.scatter(x_vect, mags, c='k', marker='o', s=norm_factors*normscale)
            ax.set_yticks(yt_scaled[:-2])
            ax.set_yticklabels(yt[:-2])
            ax.grid(True)
            ax.set_xlabel(xlabel)
            ax.set_ylabel('Pole Magnitude')

        return ax


__all__.append('MvarModalDecomposition')
register_class(MvarModalDecomposition)


def find_noise_poles(modes, model, X, sample_rate, metric='diff', include_real_poles=True):
    """Helper function for identifying noise poles using a coloured noise fit
    for reference.

    .. warning::

        This is a work in progress and has not been fully validated.

    Parameters
    ----------
    modes : sails MvarModalDecomposition
        Object containing modal decomposition of system
    model : sails LinearModel
        Object containing fitted autoregressive model
    X : ndarray
        Data on to compute the threshold for
    sample_rate : float
        The sampling frequency of the system
    metric : {'diff','diff_noisenorm','diff_datanorm','diff_sumnorm'}
        Method for comparing coloured noise poles to unconstrained poles
        (Default value = 'diff')
    include_real_poles : bool
        Flag indicating whether to include real valued poles (Default value = True)

    Returns
    -------
    tuple
        tuple containing:
        indices to included modes
        indices to excluded noise modes
        metric value for each mode

    """

    coloured_noise, f_alphas = coloured_noise_fit(X, model.order)
    coloured_modes = MvarModalDecomposition.initialise(coloured_noise, sample_rate=sample_rate)

    from scipy import interpolate
    hz, I = np.unique(coloured_modes.peak_frequency[:, 0], return_index=True)
    pchip = interpolate.pchip(coloured_modes.peak_frequency[I, 0],
                              np.abs(coloured_modes.evals[I, 0]))

    I = np.argsort(modes.peak_frequency[:, 0])
    interp_poles = pchip(modes.peak_frequency[:, 0])
    orig_poles = np.abs(modes.evals[:, 0])

    if metric == 'diff':
        vals = (orig_poles-interp_poles)
    elif metric == 'diff_noisenorm':
        vals = (orig_poles-interp_poles) / interp_poles
    elif metric == 'diff_datanorm':
        vals = (orig_poles-interp_poles) / orig_poles
    elif metric == 'diff_sumnorm':
        vals = (orig_poles-interp_poles) / (orig_poles+interp_poles)

    thresh = 0
    if include_real_poles:
        good_modes = np.where(vals > thresh)[0]
    else:
        good_modes = np.where((vals > thresh) & (np.abs(modes.evals[:, 0].imag) > 1e-10))[0]
    bad_modes = np.setdiff1d(np.arange(modes.nmodes), good_modes)

    return good_modes, bad_modes, vals


def get_noise_thresh_gamma(modes, fmin, fmax):
    """Helper function for identifying noise modes by fitting a gamma
    distribution the pole distributions within frequency bins.

    .. warning::

        This is a work in progress and has not been fully validated.

    Parameters
    ----------
    modes : sails MvarModalDecomposition
        Object containing computed modal decomposition
    fmin : float
        Minimum frequency to include in thresholding
    fmax : float
        Maximum frequency to include in thresholding

    Returns
    -------
    tuple
        tuple containing
        centre frequency of bins
        computed threshold for each bin
        interpolated threshold for each pole

    """

    from scipy.stats import gamma

    x = np.linspace(0, 1, 1024)
    freq_centres = np.linspace(fmin, fmax, 64)
    thresh = np.zeros_like(freq_centres)

    for ii in range(len(freq_centres)):
        inds = modes.get_mode_inds(fmin=freq_centres[ii]-2,
                                   fmax=freq_centres[ii]+2)
        m = np.abs(modes.evals[inds])
        mle_tuple = gamma.fit(1-m, 1)
        rv1 = gamma.pdf(x=x, a=mle_tuple[0], loc=mle_tuple[1], scale=mle_tuple[2])
        thresh[ii] = 1-x[np.argmax(rv1)]

    from scipy import interpolate
    f = interpolate.interp1d(freq_centres, thresh, bounds_error=False)

    return freq_centres, thresh, f(modes.peak_frequency)


def cluster_modes(X, n_clusters, pca_dims):
    """Helper function for computing k-means clustering on modes.

    .. warning::

        This is a work in progress and has not been fully validated.

    Parameters
    ----------
    X : ndarray
        Data to cluster, typically modal eigenvectors
    n_clusters : int
        Number of clusters to compute
    pca_dims : int
        Number of PCA components to reduce data to

    Returns
    -------
    ndarray
        Categorical cluster labels
    ndarray
        Inertia for each point

    """

    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans

    pc = PCA(n_components=pca_dims, whiten=True, copy=True).fit(X)
    km = KMeans(n_clusters=n_clusters)
    clusters = km.fit_predict(pc.components_.T)

    return clusters, km.inertia_


def get_cluster_average(clusters, vals):
    """Helper function for computing an average across defined clusters

    .. warning::

        This is a work in progress and has not been fully validated.

    Parameters
    ----------
    clusters : ndarray
        Categorical cluster labels
    vals : ndarray
        Value to average within clusters

    Returns
    -------
    ndarray
        Average values within clusters

    """

    out = np.zeros((vals.shape[:-1], clusters.max()+1))
    for c in range(clusters.max()+1):
        out[..., c] = vals[..., clusters == c].mean(axis=-1)

    return out


def find_pole_pairs(pole_inds, mode_indices):
    """Find pole pairs within a subset of the poles. Useful for recombining
    poles into pairs after model-reduction or thresholding.

    """

    # Make sure that we track the modes as pairs of poles where necessary
    thresh_modes = []
    thresh_modes_extracted = []
    seen_inds = []
    idx = 0
    for pole in pole_inds:
        if pole in seen_inds:
            continue
        foundmode = None
        for mode in mode_indices:
            if pole in mode:
                foundmode = mode
                break
        if foundmode is None:
            raise Exception("Could not find pole")
        for pole in foundmode:
            seen_inds.append(pole)
            thresh_modes_extracted.append(idx)
            idx += 1

        thresh_modes.append(foundmode)

    return thresh_modes
