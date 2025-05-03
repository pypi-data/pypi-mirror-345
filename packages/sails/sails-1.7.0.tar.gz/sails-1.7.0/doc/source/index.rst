.. sails documentation master file, created by
   sphinx-quickstart on Tue Jun 27 22:33:00 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/sails_montage.png


SAILS is a python package for modelling frequency domain power and connectivity
in time-series and networks. It provides implementations of a range of
autoregressive model fitting, validation and selection routines to describe the
linear dependencies in time-series. The spectral content of the fitted models
can be explored with within and between channel frequency metrics.


Features
========

SAILS currently provides:

 * Multivariate autoregressive (MVAR) model fits using OLS or Vieira-Morf
 * A range of MVAR model diagnostics (Stablility-index, R-square, Durbin-Watson, Percent-Consistency)
 * Model order selection via AIC or BIC
 * Decomposition of models into oscillatory modes
 * Estimation of power spectra using Fourier or Modal transforms
 * Wide range of connectivity metrics

    - Transfer Function, Spectral Matrix
    - Coherency, Magnitude Squared Coherence, Phase Coherence
    - Directed Transfer Function and variants
    - Partial Directed Coherence
    - Isolated Effective Coherence

Quick Start
===========

SAILS can be installed from `PyPI <https://pypi.org/project/sails/>`_ using pip::

    pip install sails

and used to model and describe frequency content in networks of time-series::

    import sails
    import numpy as np

    # Create a simulated signal
    sample_rate = 100
    siggen = sails.Baccala2001_fig2()
    X = siggen.generate_signal(sample_rate=sample_rate,num_samples=1000)

    # Fit an autoregressive model with order 3
    model = sails.OLSLinearModel.fit_model(X,np.arange(4))

    # Compute power spectra and connectivity
    freq_vect = np.linspace(0,sample_rate/2)
    metrics = sails.FourierMvarMetrics.initialise(model,sample_rate,freq_vect)


Tutorials
=========

Please see our tutorials and example gallery for help getting started with datawoi
analysis in SAILS.

.. toctree::
   :maxdepth: 2

   tutorials
   gallery
   api
   references
   cite
