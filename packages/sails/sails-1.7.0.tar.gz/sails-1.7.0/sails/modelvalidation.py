#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np

from .stats import find_cov_multitrial

__all__ = []


def approx_model_selection_criteria(A, EF, method='ss'):
    """Estimate Akaike's Information Criterion and Bayes Information Criterion
    from a model fit using an approximation of the loglikelihood.

    Two approximations are available:
        'ss': The sum square of the residuals. This approximation is outlined
        in [Burnham2002]_ and [Chatfield2003]_.
        'det': The determinant of the residual covariance matrix.

    The sum squares method is used as default.

    Parameters
    ----------
    A : ndarray
        Array containing the parameters of a fitted model, of shape
        [channels x channels x maxorder]
    EF : ndarray
        Array containing the residuals of the fitted model, of shape
        [channels x samples x trials]
    method : {'ss','det'}
        string indicating which method should be used to approximate
        the loglikelihood ('ss' or 'det') (Default value = 'ss')

    Returns
    -------
    tuple
        tuple of (aLL, AIC, BIC)
        aLL: Approximation of the loglikelihood (determined by the method
        defined above)
        AIC: Estimate of Akaike's Information Criterion
        BIC: Estimate of the Bayesian Information Criterion

    """

    k = A.reshape(-1).shape[0]  # number of parameters
    N = EF.reshape(-1).shape[0]  # number of observations

    if method == 'ss':
        # Chatfield 2004 - The analysis of time series p 256.
        # Burnham and Anderson 2004 - multimodel inference, understanding AIC
        # and BIC in model selection
        SS = np.power(EF, 2).sum()  # sum of squares
        aLL = N*np.log(SS/N)

    elif method == 'det':
        # Method used in the GCCA toolbox
        # TODO: make this work
        # NOT CURRENTLY WORKING!!!!!
        raise Exception("method == 'det' is not currently working")
        cov = find_cov_multitrial(EF, EF)
        aLL = np.log(np.linalg.det(cov))

    else:
        raise Exception("Unknown method")

    aLL = np.float64(aLL.real)

    # Compute AIC and BIC
    aic = np.float64(aLL + 2*k)

    # No-one else seems to approximate the BIC using the methods above, though
    # we are following the same logic as for the AIC so it's probably fine.
    bic = np.float64(aLL + k*np.log(N))

    return aLL, aic, bic


__all__.append('approx_model_selection_criteria')
