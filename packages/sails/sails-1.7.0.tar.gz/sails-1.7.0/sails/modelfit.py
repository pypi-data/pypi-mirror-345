#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import warnings

import numpy as np

from .anam import AbstractAnam, register_class
from .stats import find_cov_multitrial
from .diags import ModelDiagnostics
from .utils import get_valid_samples

__all__ = []


def A_to_companion(A):
    """Transforms a [nsignals x nsignals x order] MVAR parameter array into the
    [nsignals*order x nsignals*order] companion form. This assumes there is no
    leading identity matrix in the A form.

    Parameters
    ----------
    A : ndarray
        MVAR parameter array of size [nsignals, nsignals, order]

    Returns
    -------
    ndarray
        MVAR parameter matrix in companion form

    """

    nsignals = A.shape[0]
    order = A.shape[2]
    companion = np.eye(nsignals*(order), k=nsignals, dtype=A.dtype).T
    companion[:nsignals, :] = A.reshape((nsignals, nsignals*order), order='F')

    return companion


def get_residuals(data, parameters, delay_vect, backwards=False, mode='valid'):
    """This is a helper function for computing the residuals of a dataset after
    the MVAR predictions have been removed.

    Parameters
    ----------
    data : ndarray
        Data to compute the residuals from, of size [nchannels x nsampes x nrealisations]
    parameters : ndarray
        MVAR parameter matrix, of size [nchannels x nchannels x model order]
    delay_vect : ndarray
        Vector of lag indices corresponding to the third dimension of the parameter matrix
    backwards : bool
        Flag indicating whether the forwards or backwards parameters havebeeen
        passed (Default value = False)
    mode : {'valid','full_nan','full'}
        Options for excluding or replacing residuals which do not have a full
        model prediction ie the third sample of an order 5 model. 'valid'
        removes samples without a full model prediction, 'full_nan' returns
        resids of the same size as the data with nans replacing excluded
        samples and 'full' returns resids keeping non-full model samples in
        place.

    Returns
    -------
    ndarray
        Residual data, of size [nchannels x nsamples x nrealisations]

    """
    # TODO: double check that we are including all the order
    resid = np.zeros_like(data, dtype=data.dtype)

    # for each epoch...
    for ntrial in range(data.shape[2]):
        if backwards:
            pred = np.zeros_like(data[:, :, 0], dtype=data.dtype)

            for m in range(1, len(delay_vect)):
                tmp = parameters[:, :, m].dot(data[:, :, ntrial])
                pred[:, :-delay_vect[m]] += tmp[:, delay_vect[m]:]

            resid[:, :, ntrial] = data[:, :, ntrial] - pred[...]

        else:
            pred = np.zeros_like(data[:, :, 0], dtype=data.dtype)

            for m in range(1, len(delay_vect)):
                tmp = parameters[:, :, m].dot(data[:, :, ntrial])
                pred[:, delay_vect[m]:] += tmp[:, :-delay_vect[m]]

            resid[:, :, ntrial] = data[:, :, ntrial] - pred[...]

    resid = get_valid_samples(resid, delay_vect, mode=mode)

    return resid


__all__.append('get_residuals')


class AbstractLinearModel(AbstractAnam):
    """This is a base class defining data storage and generic methods for
    LinearModel classes. New LinearModels should inherit from
    AbstractLinearModel and overload the fit_model method"""

    # This is only used within Anamnesis
    hdf5_outputs = ['data_cov', 'resid_cov', 'parameters',
                    'maxorder', 'delay_vect']

    def __init__(self):
        AbstractAnam.__init__(self)

    @property
    def nsignals(self):
        """Number of signals in fitted model"""
        return self.parameters.shape[0]

    @property
    def order(self):
        """Order of fitted model"""
        return self.parameters.shape[2] - 1

    @property
    def companion(self):
        """Parameter matrix in companion form"""
        return A_to_companion(self.parameters[:, :, 1:])

    def compute_diagnostics(self, data, compute_pc=False):
        """Compute several diagnostic metrics from a fitted MVAR model and a
        dataset.

        Parameters
        ----------
        data : ndarrat
            The data to compute the model diagnostics with, typically the same
            data used during model fit.
        compute_pc : bool
             Flag indicating whether the compute the percent consistency, this
             is typically the the longest computation of all the metrics here
             (Default value = False)

        Returns
        -------
        sails.ModelDiagnostics
            object containing LL, AIC, BIC, stability
            ratio, durbin-watson, R squared and percent consistency
            measures

        """

        from .diags import ModelDiagnostics

        return ModelDiagnostics.compute(self, data, compute_pc=compute_pc)

    def get_residuals(self, data, mode='valid'):
        """Returns the prediction error from a fitted model. This is a wrapper
        function for get_residuals()

        Parameters
        ----------
        data : ndarray
            Data to compute the residuals of, of size [nchannels x nsamples x nrealisations]

        Returns
        -------
        ndarray
            Residual data

        """

        if self.parameters.ndim == 3:
            resid = get_residuals(data,
                                  self.parameters,
                                  self.delay_vect,
                                  backwards=False,
                                  mode=mode)
        elif self.parameters.ndim == 4:
            # We have different parameters for each epoch
            resid = get_residuals(np.atleast_3d(data[..., 0]),
                                  self.parameters[..., 0],
                                  self.delay_vect,
                                  backwards=False,
                                  mode=mode)
            for e in range(1, self.parameters.shape[3]):
                tmp = get_residuals(np.atleast_3d(data[..., e]),
                                    self.parameters[..., e],
                                    self.delay_vect,
                                    backwards=False,
                                    mode=mode)
                resid = np.concatenate((resid, tmp), axis=2)

        return resid

    def simulate_data(self, num_samples=1000, num_realisations=1, use_cov=True):
        num_sources = self.nsignals
        # Preallocate output
        Y = np.zeros((num_sources, num_samples, num_realisations))

        for ep in range(num_realisations):

            # Create driving noise signal
            Y[:, :, ep] = np.random.randn(num_sources, num_samples)

            if use_cov:
                C = np.linalg.cholesky(self.resid_cov)
                Y[:, :, ep] = Y[:, :, ep].T.dot(C).T

            # Main Loop
            for t in range(self.order, num_samples):
                for p in range(1, self.order):
                    Y[:, t, ep] -= -self.parameters[:, :, p].dot(Y[:, t-p, ep])

        return Y


__all__.append('AbstractLinearModel')
register_class(AbstractLinearModel)


class VieiraMorfLinearModel(AbstractLinearModel):
    """A class implementing the Vieira-Morf linear model fit"""

    # This is only used within Anamnesis
    hdf5_outputs = AbstractLinearModel.hdf5_outputs + ['bwd_parameters']

    def __init__(self):
        AbstractLinearModel.__init__(self)

    def get_residuals(self, data, forward_parameters=True, mode='valid'):
        """Returns the prediction error from a fitted model. This is a wrapper
        function for get_residuals()

        Parameters
        ----------
        data : ndarray
            Data to compute the residuals from, of size [nchannels x nsamples x nrealisations]
        forward_parameters : bool
            If True, use forward parameters, otherwise
            use backward parameters (Default value = True)

        Returns
        -------
        ndarray
            Residual data

        """

        if not forward_parameters:
            if self.bwd_parameters.ndim == 3:
                resid = get_residuals(data,
                                      self.bwd_parameters,
                                      self.delay_vect,
                                      backwards=True,
                                      mode=mode)
            elif self.bwd_parameters.ndim == 4:
                # We have different parameters for each epoch
                resid = get_residuals(data[..., 0],
                                      self.bwd_parameters[..., 0],
                                      self.delay_vect,
                                      backwards=True,
                                      mode=mode)
                for e in range(1, self.bwd_parameters.shape[3]):
                    tmp = get_residuals(data[..., e],
                                        self.bwd_parameters[..., e],
                                        self.delay_vect,
                                        backwards=True,
                                        mode=mode)
                    resid = np.concatenate((resid, tmp), axis=2)
        else:
            resid = AbstractLinearModel.get_residuals(self, data, mode=mode)

        return resid

    @classmethod
    def fit_model(cls, data, delay_vect):
        """Estimates the multichannel autoregressive spectral estimators
        using a Vieira-Morf algorithm. Equations are referenced to
        [Marple1987]_, appendix 15.B.

        This is the multitrial versions of the algorithm, using the AMVAR
        method outlined in [Ding2000]_.

        Parameters
        ----------
        data : numpy.ndarray
            array of shape [nsignals, nsamples, ntrials]
        delay_vect : numpy.ndarray
            Vector containing evenly spaced delays to be
            assessed in the model.  Delays are represented in
            samples.  Must start with zero.

        Returns
        -------
        sails.VieiraMorfLinearModel
            A populated object containing the fitted forward and
            backwards coefficients and several other useful variables and
            methods.

        """

        # Create object
        ret = cls()

        # Shorter reference
        X = data

        # Set-up initial parameters
        delay_vect = delay_vect.astype(int)
        nsignals = X.shape[0]
        ntrials = X.shape[2]
        maxorder = delay_vect.shape[0]-1

        # Begin model fitting
        #  Relevant parameters:
        #  A      - Forward linear prediction coefficients matrix
        #  B      - Backward linear prediction coefficients matrix
        #  PF     - Forward linear prediction error covariance
        #  PB     - Backward linear prediction error covariance
        #  PFH    - Estimate of forward linear prediction error covariance
        #  PBH    - Estimate of backward linear prediction error covariance
        #  PFBH   - Estimate of linear prediction error covariance
        #  RHO    - Estimate of the partial correlation matrix
        #  EF     - Forward linear prediction error
        #  EB     - Backward linear prediction error

        # Initialisation

        # Eq 15.91
        # Initialise prediction error as the data
        EF = X.copy().astype(X.dtype)
        EB = X.copy().astype(X.dtype)

        # Eq 15.90
        # Initialise error covariance as the data covariance
        PF = find_cov_multitrial(X, X)
        PB = find_cov_multitrial(X, X)

        # Set order zero coefficients to identity
        A = np.ndarray((nsignals, nsignals, maxorder+1), dtype=X.dtype)
        A[:, :, 0] = np.eye(nsignals)

        # TODO: double check that this is correct behaviour
        B = np.ndarray((nsignals, nsignals, maxorder+1), dtype=X.dtype)
        B[:, :, 0] = np.zeros(nsignals)

        # Main Loop

        M = 0
        while M < maxorder:

            # Create clean arrays for the estimates of the error covariance
            PFH = np.zeros((nsignals, nsignals))
            PBH = np.zeros((nsignals, nsignals))
            PFBH = np.zeros((nsignals, nsignals))

            # Eq 15.89 - get estimates of forward and backwards covariance
            PFH = find_cov_multitrial(EF[:, delay_vect[M+1]:, :],
                                      EF[:, delay_vect[M+1]:, :])
            PBH = find_cov_multitrial(EB[:, delay_vect[M]:-delay_vect[1], :],
                                      EB[:, delay_vect[M]:-delay_vect[1], :])
            PFBH = find_cov_multitrial(EF[:, delay_vect[M+1]:, :],
                                       EB[:, delay_vect[M]:-delay_vect[1], :])

            # Eq 15.88 - compute estimated normalised partial correlation
            # matrix
            tmp = np.linalg.inv(np.linalg.cholesky(PFH)).dot(PFBH)
            chol = np.linalg.cholesky(PBH)
            RHO = tmp.dot(np.array(np.asmatrix(np.linalg.inv(chol)).H))

            M += 1

            # Eq 15.82 & 15.83 - Update forward and backward reflection
            # coefficients
            tmp = np.linalg.cholesky(PF).dot(RHO)
            A[:, :, M] = - tmp.dot(np.linalg.inv(np.linalg.cholesky(PB)))

            tmp = np.linalg.cholesky(PB).dot(np.array(np.asmatrix(RHO).H))
            B[:, :, M] = - tmp.dot(np.linalg.inv(np.linalg.cholesky(PF)))

            # Eq 15.75 & 15.76 - Update forward and backward error covariances
            tmp = np.eye(nsignals) - (A[:, :, M].dot(B[:, :, M]))
            PF = tmp.dot(PF)

            tmp = np.eye(nsignals) - (B[:, :, M].dot(A[:, :, M]))
            PB = tmp.dot(PB)

            # might not need this if statement, subsequent xrange will handle
            # it, # though this is clearer
            if M > 1:
                A_t = A.copy()
                B_t = B.copy()

                # We are working from the equations - the FORTRAN is wrong!

                # Eq 15.71 & 15.72 - Update forward and backward predictor
                # coefficients
                for k in range(1, M):
                    mk = M-k

                    # TODO  - double check backwards coeffs against Ding2000
                    # simulations
                    A[:, :, k] = A_t[:, :, k] + A[:, :, M].dot(B_t[:, :, mk])
                    B[:, :, k] = B_t[:, :, k] + B[:, :, M].dot(A_t[:, :, mk])

            # Eq 15.84 & 15.85 - Update the residuals
            for t in range(ntrials):
                tmp = EF[:, :, t].copy()
                tmp2 = EB[:, :, t].copy()

                update_A = A[:, :, M].dot(tmp2[:, :-delay_vect[1]])
                EF[:, delay_vect[1]:, t] = tmp[:, delay_vect[1]:] + update_A

                update_B = B[:, :, M].dot(tmp[:, delay_vect[1]:])
                EB[:, delay_vect[1]:, t] = tmp2[:, :-delay_vect[1]] + update_B

        # Sanity check for single channel case
        if nsignals == 1 and np.allclose(PF, PB) is False:
            ret.status = -1
            warnings.warn("Warning: problem with model fit. PF != PB. "
                          "See single channel identity in Marple "
                          "top of p405")

        # Correct for sign flip in VM estimatation
        ret.parameters = -A
        ret.bwd_parameters = -B

        # Populate return object
        ret._data = X
        ret.maxorder = maxorder
        ret.delay_vect = delay_vect
        ret.data_cov = find_cov_multitrial(X, X)
        resids = ret.get_residuals(X)
        ret.resid_cov = find_cov_multitrial(resids, resids)

        return ret


__all__.append('VieiraMorfLinearModel')
register_class(VieiraMorfLinearModel)


class OLSLinearModel(AbstractLinearModel):
    """A class implementing ordinary least squares linear model fit"""

    @classmethod
    def fit_model(cls, data, delay_vect, estimator=None):
        """This is a class method which fits a linear model and returns a
        populated :class:`OLSLinearModel` instance containing the fitted model.

        Parameters
        ----------
        data : ndarray
            The data to be used to compute the model fit
        delay_vect : ndarray
            A vector of lag indices defining the lags to fit
        estimator : None or sklearn class
            If None, fit using standard OLS normal equations.
            If set to an appropriate sklearn class, use that estimator.


        Returns
        -------
        sails.OLSLinearModel
            A populated object containing the fitted coefficients and several
            other useful variables and methods.

        """

        # Create object
        ret = cls()

        # Set-up initial parameters
        nsignals = data.shape[0]
        nsamples = data.shape[1]
        maxorder = delay_vect.shape[0]-1
        maxlag = delay_vect[-1].astype(int)

        # Preallocate design matrix
        X = np.zeros((nsamples-maxlag, nsignals*maxorder))
        # Preallocate observation matrix
        Y = np.zeros((nsamples-maxlag, nsignals))

        # Create design matrix
        for idx in range(nsamples-maxlag):
            X[idx, :] = data[:, -delay_vect[1::].astype(int)+idx].reshape(-1)
            Y[idx, :] = data[:, idx, 0]

        # B is shaped [maxorder*nsignals, nsignals]
        #
        # [ A[1, 1, 1] A[1, 1, 2] ... A[1, 1, p] A[1, 2, 1] A[1, 2, 2] ... A[1, 2, p] ]
        # [ A[2, 1, 1] A[2, 1, 2] ... A[2, 1, p] A[2, 2, 1] A[2, 2, 2] ... A[2, 2, p] ]

        if estimator is None:
            # Use normal equations
            B = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(Y)
        else:
            # Fit the passed in estimator with our data
            estimator.fit(X, Y)

            # The coefficients are transposed in the sklearn implementation
            B = estimator.coef_.T

        # Reshape output
        parameters = np.zeros((nsignals, nsignals, maxorder+1))
        parameters[..., 0] = -np.eye(nsignals)
        for idx in range(nsignals):
            parameters[:, idx, 1:] = B[idx*maxorder:(idx+1)*maxorder].T

        resids = get_residuals(data, -parameters, delay_vect)
        ret.data_cov = find_cov_multitrial(data, data)
        ret.resid_cov = find_cov_multitrial(resids, resids)
        ret.parameters = parameters
        ret.maxorder = maxorder
        ret.delay_vect = delay_vect

        return ret


__all__.append('OLSLinearModel')
register_class(OLSLinearModel)


def sliding_window_fit(model_class, data, delay_vect,
                       win_len_samp, win_step_samp,
                       compute_diagnostics=True):
    """A helper function for fitting many MVAR models within sliding windows
    across a dataset.

    Parameters
    ----------
    model_class : LinearModel
        The SAILS linear model typee to fit
    data : ndarray
        Data to fit the model on, of size [nchannels x nsamples x nrealisations]
    delay_vect : ndarray
        A vector of lags specifying which lags to fit
    win_len_samp : int
        The window length in samples
    win_step_samp : int
        The step size between windows in samples
    compute_diagnostics : boolean
        Flag indicating whether to compute model diagnostics at each window
        (Default value = True)

    Returns
    -------
    LinearModel
        An instance of linear model passed into the function containing MVAR
        parameters for all windows. The parameters are stored in
        model.parameters which is of size:
        [nchannels x nchannels x model order x nwindows]

    """

    # Compute start and end samples of our windows
    start_pts = list(range(0,
                           data.shape[1] - max(delay_vect) - win_len_samp,
                           win_step_samp))
    end_pts = [x + win_len_samp for x in start_pts]

    # Preallocate model outputs
    params = np.zeros((data.shape[0], data.shape[0],
                       len(delay_vect), len(start_pts)))
    resid_cov = np.zeros((data.shape[0], data.shape[0],
                          len(start_pts)))

    # Preallocate diagnostic outputs
    if compute_diagnostics:
        diag = []

    # Main model loop
    x = np.zeros((win_len_samp, len(start_pts)))
    for ii in range(len(start_pts)):
        x = data[:, start_pts[ii]:end_pts[ii], :]

        # Fit model
        m = model_class.fit_model(x, delay_vect)
        params[:, :, :, ii] = m.parameters
        resid_cov[:, :, ii] = m.resid_cov

        # Compute diagnostics
        if compute_diagnostics:
            diag.append(m.compute_diagnostics(x))

    # Create output class
    M = model_class()
    M.parameters = params
    M.resid_cov = resid_cov
    M.delay_vect = delay_vect
    M.win_len_samp = win_len_samp
    M.win_step_samp = win_step_samp
    M.time_vect = (np.array(start_pts) + np.array(end_pts)) / 2

    if compute_diagnostics:
        D = ModelDiagnostics.combine_diag_list(diag)

    if compute_diagnostics:
        return M, D
    else:
        return M


__all__.append('sliding_window_fit')


def pca_reduced_fit(X, delay_vect, ndim, linear_model=VieiraMorfLinearModel):
    """
    Helper for computing an MVAR on dimensionality reduced data (using PCA).

    Returns a
    model fitted to reduced data, the reduced model projected back to original
    data dimensions and the pca object used for reduction

    Parameters
    ----------
    X : ndarray
        The data to compute the reduced model fit on
    delay_vect : ndarray
        A vector of lags specifying which lags to fit
    ndim : int
        Number of components to reduce data to.
    linear_model : class
        Subclass of AbstractLinearModel to use for fit.
        Defaults to VieiraMorfLinearModel.
        (Default value = True)

    Returns
    -------
    red_model : AbstractLinearModel
        An instance of the linear model passed into the function containing MVAR
        parameters for all windows for the reduced model.

    proj_model : AbstractLinearModel
        An instance of the linear model passed into the function containing MVAR
        parameters for all windows for the projected model.

    pc : sails.utils.PCA
        PCA class with information about the PCA projection included
    """

    # PCA requires [samples x channels] whereas data is [channels x samples]
    from .utils import PCA

    pc = PCA(X.T, ndim)
    Xred = pc.scores.T
    Xred = Xred[:, :, None]

    # Fit MVAR to dim-reduced data
    red_model = linear_model.fit_model(Xred, delay_vect)

    # Project back to data dimensions
    Afull = np.zeros((X.shape[0], X.shape[0], len(delay_vect)))

    # Don't project identity at start
    Afull[:, :, 0] = -np.eye(X.shape[0])

    for ii in range(1, len(delay_vect)):
        Afull[:, :, ii] = np.dot(pc.components.T, red_model.parameters[:, :, ii]).dot(pc.components)

    resid_cov_full = np.dot(pc.components.T, red_model.resid_cov[:, :]).dot(pc.components)[:, :, None]

    # Store projected model
    proj_model = linear_model()
    proj_model.parameters = Afull
    proj_model.resid_cov = resid_cov_full
    proj_model.delay_vect = delay_vect

    return red_model, proj_model, pc


__all__.append('pca_reduced_fit')


def coloured_noise_fit(X, model_order):
    """A helper function to fit an autoregressive model whose parameters are
    constrained to be coloured noise as definede by [Kasdin1995]_.

    Parameters
    ----------
    X : ndarray
        The data to compute the model fit on
    model_order : int
        The maximum lag to be computed

    Returns
    -------
    LinearModel
        A SAILS linear model instance containing the fitted model
    float
        The power of the final model fit.

    """

    from .tutorial_utils import generate_pink_roots, model_from_roots

    # Initialise returned model
    M = AbstractLinearModel()
    M.parameters = np.zeros((X.shape[0], X.shape[0], model_order, X.shape[2]))
    M.resid_cov = np.eye(X.shape[0])  # Assumed for now
    M.delay_vect = np.arange(model_order)

    # Range of 1/f^alpha values to explore
    powers = np.linspace(.05, 1.95, 200)

    fit_inds = np.zeros((X.shape[0],), dtype=int)
    for ichan in range(X.shape[0]):
        ss = np.zeros(powers.shape)
        for ii in range(len(powers)):

            rts = generate_pink_roots(powers[ii], order=model_order)
            m = model_from_roots(rts)

            resid = get_residuals(X[None, ichan, :, :], m.parameters, np.arange(model_order))
            ss[ii] = np.power(resid, 2).sum()

        fit_inds[ichan] = np.argmin(ss).astype(int)
        rts = generate_pink_roots(powers[fit_inds[ichan]], order=model_order)
        M.parameters[ichan, ichan, :, 0] = -np.poly(rts)

    fit_powers = powers[fit_inds]

    return M, fit_powers


__all__.append('coloured_noise_fit')
