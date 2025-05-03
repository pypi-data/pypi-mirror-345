#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np

from .anam import AbstractAnam, register_class
from .utils import get_valid_samples
from .stats import find_cov_multitrial, durbin_watson, \
    stability_index, stability_ratio, \
    rsquared_from_residuals, percent_consistency

from .modelvalidation import approx_model_selection_criteria

__all__ = []


class DelayDiagnostics(AbstractAnam):
    """Class which computes the mutual information as a function of lag from zero
    lag to the first zero crossing of the autocorrelation function.
    """

    # This is only used within Anamnesis
    hdf5_outputs = ['MI', 'MI_diff', 'delay_vect_samples', 'delay_vect_ms',
                    'time_vect', 'autocorrelation', 'maxdelay', 'first_zero']

    def __init__(self):
        AbstractAnam.__init__(self)

        # TODO: Add docstrings for these
        self.MI = None

        self.MI_diff = None

        self.delay_vect_samples = None

        self.delay_vect_ms = None

        self.time_vect = None

        self.autocorrelation = None

        self.maxdelay = None

        self.first_zero = None

    @classmethod
    def delay_search(cls, data, maxdelay, step, sample_rate,
                     constant_window=True):
        """Compute MI as a function of lag from zero lag to the first zero
        crossing of the autocorrelation function

        Parameters
        ----------
        data : numpy.ndarray
            array of [signals, samples, trials]
        maxdelay : int
            maximum delay to consider
        step : int
            step to increment the delay by
        sample_rate : float
            sample rate of data
        constant_window : bool
            Flag indicating that the same number of
            datapoints should be included at each delay.
            Default is True

        Returns
        -------
        DelayDiagnostics
            Populated object containing diagnostics for each value in delay

        """

        ret = cls()

        # Set up input parameters
        sample_rate = float(sample_rate)
        ret.maxdelay = maxdelay
        ret.time_vect = np.arange(data.shape[1]) * (1 / sample_rate)
        ret.delay_vect_samples = np.arange(1, ret.maxdelay)
        ret.delay_vect_ms = ret.delay_vect_samples * (1/sample_rate)

        # TODO: Check that we're not out of range of number of samples
        nsignals = data.shape[0]
        nsamples = data.shape[1]
        ntrials = data.shape[2]

        # Compute Autocorrelation
        # printv("Computing Autocorrelations")
        ac = np.zeros((nsignals, ntrials, nsamples), dtype=complex)

        for i in range(nsignals):
            for j in range(ntrials):
                ac[i, j, :] = np.correlate(data[i, :, j], data[i, :, j],
                                           'full')[nsamples-1:]

        ret.autocorrelation = ac

        # Find first zero crossing
        avg = ret.autocorrelation.mean(axis=0).mean(axis=0)
        zero_crossings = np.where(np.diff(np.sign(avg)))[0]

        ret.first_zero = zero_crossings[0]

        # printv("First zero crossing at %s samples %s ms" % (ret.first_zero,
        #                                     ret.time_vect[ret.first_zero]*1000))

        # Compute Mutual Information

        # TODO: Convert this to use stats.mutual_information
        nbins = 21
        bins = np.linspace(-8, 8, nbins)

        ret.MI = np.zeros((nsignals,
                           ret.delay_vect_samples.shape[0]),
                          dtype='float64')

        for d in range(ret.delay_vect_samples.shape[0]):

            delay = ret.delay_vect_samples[d]

            idx = nsamples - delay

            # Calculate MI for each signal, for each trial
            for s in range(nsignals):
                for t in range(ntrials):
                    if constant_window:
                        A = data[s, :-ret.maxdelay, t]
                        B = data[s, delay:-ret.maxdelay+delay, t]
                    else:
                        A = data[s, :-(delay), t]
                        B = data[s, delay:, t]

                    Ps = np.histogram(A, bins=bins)[0]
                    Pst = np.histogram(B, bins=bins)[0]
                    Ps_st = np.histogram2d(A, B, bins=bins)[0]

                    Ps = Ps / float(idx)
                    Pst = Pst / float(idx)
                    Ps_st = Ps_st / float(idx)

                    for i in range(nbins-1):
                        for j in range(nbins-1):
                            if Ps_st[i, j] != 0.0:
                                ret.MI[s, d] += Ps_st[i, j] * \
                                    np.log2(Ps_st[i, j] / (Ps[i] * Pst[j]))

        ret.MI = ret.MI / float(ntrials)

        ret.MI_diff = np.diff(ret.MI)

        # self.MI_dim_selection = model.find_elbow(self.MI)

        return ret


__all__.append('DelayDiagnostics')
register_class(DelayDiagnostics)


class ModelDiagnostics(AbstractAnam):
    """
    Class to store and display LinearModel diagnostic information. Several
    diagnostic criteria are computed including:

    R_square (``R_square``)
        the percentage of variance explained in each channel

    Stability Index (``SI``)
        Indicator of the stability of the MVAR parameters (SI<1 indicates a
        stable model)

    Stability Ratio (``SR``)
        A stronger test of stability computed from the ratio of the largest
        eigenvalue of A to all others.

    Durbin-Watson (``DW``)
        A test of autocorrelation in residuals of the model fit.  Values should
        be close to 2 indicating no autocorrelation, values close to 0 indicate
        a positive autocorrelation and 4 and negative autocorrelation.

    Log Likelihood (``LL``)
        The log-likelihood of the model.

    Akaike's Information Criterion (``AIC``)
        An indication of the model 'quality', lower values indicate a more
        accurate, less complex model.

    Bayesian Information Criterion (``BIC``)
        An indication of the model 'quality', lower values indicate a more
        accurate, less complex model.

    Percent Consistency (``PC``)
        Indicates how well a model captures the auto and cross correlation in a
        time-series.  Only computed if ``compute_pc`` is passed to the relevant
        function.
    """

    # This is only used within Anamnesis
    hdf5_outputs = ['R_square', 'SR', 'DW', 'PC', 'AIC', 'BIC', 'LL', 'SI']

    def __init__(self):
        """Constructor for ModelDiagnostics.

        This fills the diagnostic variables with placeholders. The diagnostics
        should be computed using the ModelDiagnostics.compute classmethod.

        """

        AbstractAnam.__init__(self)

        self.R_square = None
        self.SR = None
        self.DW = None
        self.PC = None
        self.AIC = None
        self.BIC = None
        self.LL = None
        self.SI = None

        self.is_list = False

    @classmethod
    def compute(cls, model, data, compute_pc=False):
        """
        Classmethod for computing a set of model diagnostics from a fitted
        model applied to a time-series dataset.

        Parameters
        ----------
        model: sails LinearModel class
            A fitted linear model
        data: ndarray
            A 3d time-series of size [nchannels x nsamples x ntrials]
        compute_pc: bool
            Flag indicating whether to compute the percent consistency, this
            can be time-consuming for large datasets (Default=False).

        Returns
        -------
        sails ModelDiagnostics instance

        """

        ret = cls()

        # Get residuals - adjust valid samples next
        resid = model.get_residuals(data, mode='full')

        # Adjust data and resids for valid samples
        data = get_valid_samples(data, model.delay_vect)
        resid = get_valid_samples(resid, model.delay_vect)

        # Get covariance of the residuals
        ret.resid_cov = find_cov_multitrial(resid, resid)

        # Compute Durbin-Watson test for residual autocorrelation
        ret.DW = durbin_watson(resid, step=np.diff(model.delay_vect)[0])[0]

        # Compute the stability index and ratio
        ret.SI = stability_index(model.parameters)
        ret.SR = stability_ratio(model.parameters)

        # Estimate the R^2 - per signal
        ret.R_square = rsquared_from_residuals(data, resid, per_signal=True)

        # Estimate Percent Consistency - Ding et al 2000.
        if compute_pc:
            # This can cause memory issues with large datasets
            ret.PC = percent_consistency(data, resid)
        else:
            ret.PC = None

        # Compute LL, AIC and BIC
        # LL, AIC, BIC = est_model_selection_criteria(model.parameters, resid)

        # Approximate AIC and BIC
        LL, AIC, BIC = approx_model_selection_criteria(model.parameters, resid)

        ret.LL = LL
        ret.AIC = AIC
        ret.BIC = BIC

        return ret

    @classmethod
    def combine_diag_list(cls, diags):
        """
        Helper function for combining diagnostics from a list of
        ModelDiagnostics instances for easy comparison and visualisation.

        Parameters
        ----------
        diags: list of ModelDiagnostics instances
            The ModelDiagnostics to concatenate

        Returns
        -------
        sails ModelDiagnostics instance

        """

        ret = cls()

        ret.resid_cov = np.concatenate([d.resid_cov[..., None] for d in diags], axis=2)

        ret.DW = np.r_[[d.DW for d in diags]]
        ret.SI = np.r_[[d.SI for d in diags]]
        ret.SR = np.r_[[d.SR for d in diags]]

        if diags[0].PC is not None:
            ret.PC = np.r_[[d.PC for d in diags]]

        ret.R_square = np.c_[[d.R_square for d in diags]]

        ret.LL = np.r_[[d.LL for d in diags]]
        ret.AIC = np.r_[[d.AIC for d in diags]]
        ret.BIC = np.r_[[d.BIC for d in diags]]

        ret.is_list = True

        return ret

    def summary(self, all_models=True):
        """Print the ModelDiagnostics in a pre-formatted table"""

        if self.is_list:
            template = "{0:<10}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}{6:<10}"

            print(template.format('Model', 'SI', 'SR', 'DW', 'AIC', 'BIC', 'R Square'))
            print('_'*70)

            for ii in range(self.SI.shape[0]):
                print(template.format(ii,
                                      np.round(self.SI[ii], 3),
                                      np.round(self.SR[ii], 3),
                                      np.round(self.DW[ii], 3),
                                      np.round(self.AIC[ii], 3),
                                      np.round(self.BIC[ii], 3),
                                      np.round(self.R_square[ii, :].mean(), 3)))
            print('_'*70)
            print(template.format('Total',
                                  np.round(self.SI.mean(), 3),
                                  np.round(self.SR.mean(), 3),
                                  np.round(self.DW.mean(), 3),
                                  np.round(self.AIC.mean(), 3),
                                  np.round(self.BIC.mean(), 3),
                                  np.round(self.R_square.mean(), 3)))
        else:
            template = "{0:<10}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}"

            print(template.format('SI', 'SR', 'DW', 'AIC', 'BIC', 'R Square'))
            print('_'*60)

            print(template.format(np.round(self.SI, 3),
                                  np.round(self.SR, 3),
                                  np.round(self.DW, 3),
                                  np.round(self.AIC, 3),
                                  np.round(self.BIC, 3),
                                  np.round(self.R_square.mean(), 3)))


__all__.append('ModelDiagnostics')
register_class(ModelDiagnostics)
