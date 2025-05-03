#!/usr/bin/python

import numpy as np
from scipy import linalg


def closest_orthogonal(A, verbose=False):
    """Implementation of the closest-orthonormal orthogonalisation method
    defined in [Colclough2015]_

    Parameters
    ----------
    A : ndarray
        Data matrix to orthogonalise, of size [channels, samples]
    verbose : bool
        Flag indicating whether to show detailed output (Default value = False)

    Returns
    -------

    data : numpy.ndarray [channels, samples] of orthogonalised data

    d : numpy.ndarray

    rho : numpy.ndarray

    W : numpy.ndarray

    """

    A = A.T

    U, S, V = linalg.svd(A, full_matrices=False)
    tol = S.max() * max(A.shape) * np.finfo(S.dtype).eps

    # Settings
    max_iter = 300
    it = 0

    # Initialise d to ones, we start with the closest orthonormal matrix
    d = np.ones((A.shape[1],))

    rho = np.zeros((max_iter, 1)) * np.nan

    while it < max_iter:

        # Find orthonormal polar factor
        V, _ = symmetric_orthonormal(A.dot(np.diag(d)).T)

        # Minimise rho w.r.t d
        d = np.diag(np.conj(A).T.dot(V.T))

        # New best estimre
        L = V.T.dot(np.diag(d))

        # Error term
        E = A - L
        rho[it] = np.sum(np.diag(E.T.dot(E)))

        if verbose:
            print('iter: %4d\trho: %g' % (it, rho[it]))

        if it > 1 and np.abs(rho[it] - rho[it-1]) <= tol:
            break

        it += 1

    # Finally calculate the linear operator
    _, W = symmetric_orthonormal(A.dot(np.diag(d)).T)
    W = np.diag(d).dot(W).dot(np.diag(d))

    if it == max_iter:  # pragma: nocover
        # ? Turn this into an exception?
        print("MaxIterationsHit: the results my not be optimal")

    # Tidy up the rho vector
    rho = rho[~np.isnan(rho)]

    return L.T, d, rho, W


def symmetric_orthonormal(A, maintain_mag=False):
    """Implement the [Colclough2015]_ algorithm for multivariate leakage
    correction in MEG.  Also see the OHBA toolbox
    (https://github.com/OHBA-analysis/MEG-ROI-nets) and
    http://empslocal.ex.ac.uk/people/staff/reverson/uploads/Site/procrustes.pdf

    Parameters
    ----------
    A : ndarray
        Data matrix to orthogonalise, of size [channels, samples]
    verbose : bool
        Flag indicating whether to show detailed output (Default value = False)
    maintain_mag : bool
        Flag indicating whether to maintain magnitudes (Default value = False)

    Returns
    -------

    data : numpy.ndarray
          [channels, samples] of orthogonalised data

    W : numpy.ndarray

    """

    Adecom = A.T

    # Do we need to adjust for magnitude?
    if maintain_mag:
        D = np.diag(np.sqrt(np.diag(A.dot(A.T))))
        Adecom = A.T.dot(D)

    # Compute svd
    U, S, V = linalg.svd(Adecom, full_matrices=False)

    # This is equivalent to np.linalg.matrix_rank
    tol = S.max() * max(A.shape) * np.finfo(S.dtype).eps
    rank = sum(S > tol)
    if rank < A.shape[0]:
        raise Exception('Input is not full rank!')

    # Not conj(transpose(V)) in python as V is already transposed
    Lnorm = U.dot(V.conj())
    W = V.T.dot(np.diag(1.0 / S)).dot(V.conj())

    if maintain_mag:
        Lnorm = Lnorm.dot(D)
        W = D.dot(W).dot(D)

    # Ensure that we return in the same order as we were input
    return Lnorm.T, W


def innovations(A, order, mvar_class=None, verbose=False):
    """Implementation of the innovations-orthogonalisation defined in
    [Pascual-Marqui2017]_ . This creates the mixing matrix on the input data
    after variance explained by an MVAR model is removed. The orthogonalisation
    is defined on the residuals but applied to the raw data.

    Parameters
    ----------
    A : ndarray
        Data matrix to orthogonalise, of size [channels, samples]
    order : int
        Model order used during MVAR model fit
    mvar_class : sails LinearModel class
        Model class to do model fitting (Default value = None)
    verbose : bool
        Flag indicating whether to show detailed output (Default value = False)

    Returns
    -------
    ndarray :
        Orthogonalised data matrix, of size [channels, samples]


    """

    if mvar_class is None:
        from .modelfit import VieiraMorfLinearModel
        mvar_class = VieiraMorfLinearModel()

    # Fit AR model to raw data
    delay_vect = np.arange(order)
    m = mvar_class.fit_model(A[:, :, None], delay_vect)

    # Get innovations time-series (aka residuals)
    from sails.modelfit import get_residuals
    innovs = get_residuals(A[:, :, None], m.parameters, delay_vect)

    # Orthogonalise innovations
    orth_innovs, _, _, _ = closest_orthogonal(innovs[:, :, 0])

    # Channels x Channels mixing matrix
    M = np.linalg.pinv(orth_innovs.T).dot(innovs[:, :, 0].T)

    # Apply (un)mixing matrix and return orthogonalised data
    return A.T.dot(M).T
