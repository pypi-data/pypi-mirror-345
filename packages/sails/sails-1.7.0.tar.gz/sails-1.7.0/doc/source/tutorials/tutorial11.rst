Tutorial 11 - Morlet Wavelet Decomposition
=======================================================

In this tutorial, we will look at describing time-frequency dynamics in a
signal using a Morlet Wavelet decomposition.

For this tutorial, we will use the same MEG example data which we have used in previous
tutorials.

We start by importing our modules and finding and loading the example data.

.. code-block:: python

    import os
    from os.path import join

    import h5py

    import numpy as np
    import matplotlib.pyplot as plt

    import sails

    plt.style.use('ggplot')


SAILS will automatically detect the example data if downloaded into your home
directory. If you've used a different location, you can specify this in an
environment variable named ``SAILS_EXAMPLE_DATA``.

.. code-block:: python

    # Specify environment variable with example data location
    # This is only necessary if you have not checked out the
    # example data into $HOME/sails-example-data
    #os.environ['SAILS_EXAMPLE_DATA'] = '/path/to/sails-example-data'

    # Locate and validate example data directory
    example_path = sails.find_example_path()

    # Load data using h5py
    data_path = os.path.join(sails.find_example_path(), 'meg_occipital_ve.hdf5')
    X = h5py.File(data_path, 'r')['X'][:, 122500:130000, 0]

    sample_rate = 250

    time_vect = np.linspace(0, X.shape[1] // sample_rate, X.shape[1])

The Morlet Wavelet transform first defines a set of wavelet functions to use as
am adaptive basis set. These wavelets are simple burst-like oscillations
created to a pre-defined set of parameters.

.. code-block:: python

    # Wavelet frequencies in Hz
    freqs = [10]
    # Number of cycles within the oscillatory event
    ncycles = 5
    # Length of window in seconds
    win_len = 10

    # Compute wavelets
    mlt = sails.wavelet.get_morlet_basis(freqs, ncycles, win_len, sample_rate, normalise=False)

``mlt`` is now a list of wavelet basis functions. In this case, we have a
single 10Hz basis. This wavelet is a complex-valued array (in the same way that
a Fourier transform returns a complex valued result). To visualise the wavelet,
we can plot the real and imaginary parts of the complex function.

.. code-block:: python

    plt.figure()
    plt.plot(mlt[0].real)
    plt.plot(mlt[0].imag)
    plt.legend(['Real', 'Imag'])

Note that the real and imaginary components are the same apart from a 90 degree
phase shift in the time-series. This shift allow the wavelet transform to
estimate the full amplitude envelope and phase of the underlying signal.

The ``ncycles`` parameter is critical for defining the time-frequency
resolution of the wavelet transform. A small value (typically less than 5) will
lead to high temporal resolution but low frequency resolution whilst a large
value (typically greater than 7) will have a low temporal resolutoin and a high
frequency resolution. We will look into this in more detail later - for now, we
can see that this parameter simply changes the number of cycles of oscillation
present in our basis wavelets.

.. code-block:: python

    # Compute wavelets
    mlt3 = sails.wavelet.get_morlet_basis(freqs, 3, win_len, sample_rate, normalise=False)
    mlt5 = sails.wavelet.get_morlet_basis(freqs, 5, win_len, sample_rate, normalise=False)
    mlt7 = sails.wavelet.get_morlet_basis(freqs, 7, win_len, sample_rate, normalise=False)

    plt.figure()
    for idx, mlt in enumerate([mlt3, mlt5, mlt7]):
        y = mlt[0].real
        t = np.arange((len(y))) - len(y)/2 # zero-centre the wavelet
        plt.plot(t, y + idx*2)
    plt.legend(['3-cycles', '5-cycles', '7-cycles'])

We can see that the frequency of the oscillation in each wavelet is unchanged
whilst the number of cycles is modified by changing ``ncycles``.

We will often compute wavelets for a range of frequencies rather than just one.
Here we pass in an array of frequency values to compute wavelets for.

.. code-block:: python

    freqs = [3, 6, 9, 12, 15]

    # Compute wavelets
    mlt = sails.wavelet.get_morlet_basis(freqs, ncycles, win_len, sample_rate, normalise=False)

    plt.figure()
    for ii in range(len(freqs)):
        y = mlt[ii].real
        t = np.arange((len(y))) - len(y)/2 # zero-centre the wavelet
        plt.plot(t, y + ii*2)
    plt.legend(freqs)

This time, we see that changing frequency keeps a consistent number of cycles
in each wavelet but modifies the oscillatory period.

To compute the wavelet transform itself, each wavelet basis function is
convolved across the dataset. In this instance (as the wavelet function is
symmetric and the input time-series are real values) this convolution is
similar to computing the correlation between the basis function and the
time-series at each point in time.

Let's compute the wavelet transform at 10Hz on our real data.

.. code-block:: python

    freqs = [10]
    cwt = sails.wavelet.morlet(X[0, :], freqs, sample_rate)

    plt.figure()
    plt.subplot(211)
    plt.plot(X.T)
    plt.subplot(212)
    plt.plot(cwt.T)

We can see that the wavelet power tracks the amplitude of the oscillations
visible in the original time-series.

Finally, let's compute a full wavelet transform across a wider range of frequencies

.. code-block:: python

    freqs = np.linspace(1, 20, 38)
    cwt = sails.wavelet.morlet(X[0, :], freqs, sample_rate, normalise='tallon')

    plt.figure()
    plt.subplot(211)
    plt.plot(time_vect, X.T)
    plt.xlim(time_vect[0], time_vect[-1])
    plt.subplot(212)
    plt.pcolormesh(time_vect, freqs, cwt)
