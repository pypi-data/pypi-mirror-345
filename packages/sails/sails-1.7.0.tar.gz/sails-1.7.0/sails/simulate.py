#!/usr/bin/python

import numpy as np
from scipy import signal

__all__ = []

# ABSTRACT CLASSES


class AbstractSigGen():
    """Abstract base class for signal generation"""

    def __init__(self, extraargs=None):
        if extraargs is not None:
            self.parse_arguments(extraargs)

    def get_num_sources(self):
        """Helper function for returning number of sources in simulation.

        This is typically overloaded when defining a signal generator class.

        Returns
        -------
        type : int
            Number of sources in simulated signal. If not override, returns 1

        """
        return 1

    def parse_arguments(self, extraargs):
        """Helper function for processing extra-arguments passed to a
        signal-generator.

        Currently only looks for snr_dB for noise levels but can be overloaded
        by a specific class to processes more arguments.

        Parameters
        ----------
        extraargs : dict
            keyword arguments passed to signal generator.

        """
        if not hasattr(self, 'snr_dB'):
            try:
                self.snr_dB = float(extraargs.get('snr_dB', 0.))
            except (TypeError, KeyError):
                raise TypeError(" SNR is not defined (use snr_dB argument)")

    def generate_signal(self, meg_reader):  # pragma: no cover
        """Generate a custom signal for embedding in a dataset

        Parameters
        ----------
        meg_reader :
            MEG data for which to generate signal

        Returns
        -------
        type
            numpy array of shape (samples).  Note that samples must
            be equal to the value of meg_reader.num_samples

        """

        raise NotImplementedError("This is an abstract base class")


__all__.append('AbstractSigGen')


class AbstractLagSigGen(AbstractSigGen):
    """Generic class for making lagged signals"""

    def get_num_sources(self):
        """ """
        print("Warning! get_num_sources is not implemented")
        return None

    def parse_arguments(self, extraargs):
        """Helper function for processing extra-arguments passed to a
        signal-generator.

        Currently only looks for snr_dB for noise levels but can be overloaded
        by a specific class to processes more arguments.

        Parameters
        ----------
        extraargs : dict
            keyword arguments passed to signal generator.

        """

        # Make sure we call the parents parse args as well to get generic
        # parameters such as snr_dB
        super(AbstractMVARSigGen, self).parse_arguments(extraargs)

    def generate_basesignal(self, nsamples):
        """Function defining the starting signal which will be lagged throughout
        the network

        This is an abstracted function and should be overloaded when creating a
        new class.

        Parameters
        ----------
        nsamples : int
            The number of samples to generate

        """
        raise NotImplementedError("This is an abstract base class, "
                                  "generate_basesignal is not defined")

    def generate_noise(self, nsamples):
        """Function defining the additive noise added at each lag

        Parameters
        ----------
        nsamples : int
            The number of samples to generate

        Returns
        -------
        ndarray
            A vector of white noise

        """
        return np.random.randn(nsamples)

    def get_lags(self):
        """Method returning the lagging of the signal through the system. Should

        Returns
        -------
        type
            dimension refers to the source node and the second dimension the target
            node. Each non-zero value indicates that the signal in the first
            dimension will be added into the signal in the second dimension at the
            specified weight.

        """
        raise NotImplementedError("This is an abstract base class, "
                                  "generate_parameters is not defined")

    def generate_signal(self, sample_rate=None, num_samples=None,
                        noise_dB=None):
        """Method for generating a set of time courses based on either the
        structure of a meg_reader object or passed parameters and the
        self.generate_parameters method defined in this class

        Returns a timeseries of dimension [samples x signals]

        Parameters
        ----------
        sample_rate : float
             The sample rate to generate the signal at (Default value = None)
        num_samples :
             The number of samples to generate (Default value = None)
        noise_dB : float
             Noise level of the additive noise (Default value = None)

        Returns
        -------
        ndarray
            A simulated time-series [nchannels x nsamples x nrealisations]

        """

        # Create signal to be lagged
        basesignal = self.generate_basesignal(num_samples)

        # Get the lag matrix
        lags = self.get_lags()

        order = lags.shape[2]

        X = np.zeros((self.get_num_sources(), num_samples))
        X[0, :] = basesignal

        # Main Loop
        for p in range(order):
            for ii in range(self.get_num_sources()):
                for jj in range(self.get_num_sources()):
                    if lags[ii, jj, p] > 0.:
                        X[jj, p+1:] += lags[ii, jj, p] * X[ii, :-p-1] + \
                                       self.generate_noise(num_samples-1-p)

        for ii in range(self.get_num_sources()):
            X[ii, :] = (X[ii, :] - X[ii, :].mean()) / X[ii, :].std()

        return X[..., None]


__all__.append('AbstractLagSigGen')


class AbstractMVARSigGen(AbstractSigGen):
    """Generic class for making MVAR signals"""

    def get_num_sources(self):
        """ """
        print("Warning! get_num_sources is not implemented")
        return None

    def parse_arguments(self, extraargs):
        """Helper function for processing extra-arguments passed to a
        signal-generator.

        Currently only looks for snr_dB for noise levels but can be overloaded
        by a specific class to processes more arguments.

        Parameters
        ----------
        extraargs : dict
            keyword arguments passed to signal generator.

        """

        # Make sure we call the parents parse args as well to get generic
        # parameters such as snr_dB
        super(AbstractMVARSigGen, self).parse_arguments(extraargs)

    def generate_parameters(self):
        """Method to generate the parameters of the MVAR system. Should return a
        [nsignals x nsignals x nlags] parameter matrix in which the first
        dimension refers to the source node and the second dimension the target
        node

        This is an abstract method and should be overloaded when creating a
        specific class.

        """
        raise NotImplementedError("This is an abstract base class, "
                                  "generate_parameters is not defined")

    def check_stability(self):
        """Checks the stability of the parameter matrix by the magnitude of the
        largest eigenvalue of the first lag in the parameter matrix (see
        [Lutkephol2006]_ chapter 1)

        Returns
        -------
        float
            The stability index of the simulated signal

        Notes
        -----
        The stability index of a simulation should be strictly less than 1. If
        this exceeds 1 then the simulated signal is likely to tend to infinity
        or zero.

        """

        from sails.stats import stability_index

        return stability_index(self.generate_parameters())

    def generate_signal(self, sample_rate=None, num_samples=None,
                        noise_dB=None, num_realisations=1):
        """Method for generating a set of time courses based on either the
        structure of a meg_reader object or passed parameters and the
        self.generate_parameters method defined in this class

        Returns a timeseries of dimension [nchannels x nsamples x nrealisations]

        Parameters
        ----------
        sample_rate : float
             The sample rate of the simulated data (Default value = None)
        num_samples : int
             The number of samples to generate (Default value = None)
        noise_dB : float
             The level of additive noise to add to the simulationo (Default value = None)
        num_realisations : int
             Number of realisations to generate (Default value = 1)

        Returns
        -------
        ndarray
            The simulated dataset of size [nchannels x nsamples x nrealisations]

        """
        num_sources = self.get_num_sources()

        # Generate the parameters
        params = self.generate_parameters()

        order = params.shape[2]

        # Preallocate output
        X = np.zeros((num_sources, num_samples, num_realisations))

        for ep in range(num_realisations):

            # Create driving noise signal
            X[:, :, ep] = np.random.randn(num_sources, num_samples)

            # Main Loop
            for t in range(order, num_samples):
                for p in range(1, order):
                    X[:, t, ep] -= params[:, :, p].dot(X[:, t-p, ep])

        return X

    def generate_model(self):
        """Returns a LinearModel containing containing the true model parameters."""

        # We can use the AbstractLinearModel for this as we
        # don't need the fit_model routine
        from sails import AbstractLinearModel

        ret = AbstractLinearModel()
        ret.parameters = self.generate_parameters()
        ret.resid_cov = np.ones((self.get_num_sources(),
                                 self.get_num_sources(), 1))
        ret.delay_vect = np.arange(ret.order + 1)

        return ret


__all__.append('AbstractMVARSigGen')


#################################
# Literature MVAR Data Generators

class Baccala2001_fig1(AbstractMVARSigGen):
    """This class implements [Baccala2001]_ figure 1."""

    def get_num_sources(self):
        """Return the number of sources in the simulation"""

        return 3

    def generate_parameters(self):
        """Create the autoregressive parameters for [Baccala2001]_ figure 1."""

        order = 1

        X = np.zeros((self.get_num_sources(), self.get_num_sources(), order))

        X[0, :, 0] = [.5, .3, .4]
        X[1, :, 0] = [-.5, .3, .1]
        X[2, :, 0] = [0, -.3, -.2]

        X = np.concatenate((np.eye(self.get_num_sources())[..., None], -X),
                           axis=-1)

        return X


__all__.append('Baccala2001_fig1')


class Baccala2001_fig2(AbstractMVARSigGen):
    """This class implements [Baccala2001]_ figure 2."""

    def get_num_sources(self):
        """Return the number of sources in the simulation"""

        return 5

    def generate_parameters(self):
        """Create the autoregressive parameters for [Baccala2001]_ figure 2."""

        order = 3

        X = np.zeros((self.get_num_sources(), self.get_num_sources(), order))

        X[0, :, 0] = [0.95*np.sqrt(2), 0, 0, 0, 0]
        X[1, :, 0] = [0, 0, 0, 0, 0]
        X[2, :, 0] = [0, 0, 0, 0, 0]
        X[3, :, 0] = [0, 0, 0, .25*np.sqrt(2), .25*np.sqrt(2)]
        X[4, :, 0] = [0, 0, 0, .25*np.sqrt(2), .25*np.sqrt(2)]

        X[0, :, 1] = [-0.9025, 0, 0, 0, 0]
        X[1, :, 1] = [.5, 0, 0, 0, 0]
        X[2, :, 1] = [0, 0, 0, 0, 0]
        X[3, :, 1] = [-.5, 0, 0, 0, 0]
        X[4, :, 1] = [0, 0, 0, 0, 0]

        X[0, :, 2] = [0, 0, 0, 0, 0]
        X[1, :, 2] = [0, 0, 0, 0, 0]
        X[2, :, 2] = [-.4, 0, 0, 0, 0]
        X[3, :, 2] = [0, 0, 0, 0, 0]
        X[4, :, 2] = [0, 0, 0, 0, 0]

        X = np.concatenate((np.eye(self.get_num_sources())[..., None], -X),
                           axis=-1)

        return X


__all__.append('Baccala2001_fig2')


class Baccala2001_fig3(AbstractMVARSigGen):
    """This class implements [Baccala2001]_ figure 3."""

    def get_num_sources(self):
        """Return the number of sources in the simulation"""
        return 5

    def generate_parameters(self):
        """Create the autoregressive parameters for [Baccala2001]_ figure 3."""

        order = 2

        X = np.zeros((self.get_num_sources(), self.get_num_sources(), order))

        X[0, :, 0] = [0.95*np.sqrt(2), 0, 0, 0, 0]
        X[1, :, 0] = [-.5, 0, 0, 0, 0]
        X[2, :, 0] = [0, 0, 0, 0, 0]
        X[3, :, 0] = [0, 0, -.5, .25*np.sqrt(2), .25*np.sqrt(2)]
        X[4, :, 0] = [0, 0, 0, -.25*np.sqrt(2), .25*np.sqrt(2)]

        X[0, :, 1] = [-0.9025, 0, 0, 0, 0]
        X[1, :, 1] = [0, 0, 0, 0, 0]
        X[2, :, 1] = [0, .4, 0, 0, 0]
        X[3, :, 1] = [0, 0, 0, 0, 0]
        X[4, :, 1] = [0, 0, 0, 0, 0]

        X = np.concatenate((np.eye(self.get_num_sources())[..., None], -X),
                           axis=-1)

        return X


__all__.append('Baccala2001_fig3')


class Baccala2001_fig4(AbstractMVARSigGen):
    """This class implements [Baccala2001]_ figure 4."""

    def get_num_sources(self):
        """Return the number of sources in the simulation"""
        return 5

    def generate_parameters(self):
        """Create the autoregressive parameters for [Baccala2001]_ figure 4."""

        order = 2

        X = np.zeros((self.get_num_sources(), self.get_num_sources(), order))

        X[0, :, 0] = [0.95*np.sqrt(2), 0, 0, 0, 0]
        X[1, :, 0] = [-.5, 0, 0, 0, 0]
        X[2, :, 0] = [0, 0, 0, 0, 0]
        X[3, :, 0] = [0, 0, -.5, .25*np.sqrt(2), .25*np.sqrt(2)]
        X[4, :, 0] = [0, 0, 0, -.25*np.sqrt(2), .25*np.sqrt(2)]

        X[0, :, 1] = [-0.9025, 0, 0, 0, .5]
        X[1, :, 1] = [0, 0, 0, 0, 0]
        X[2, :, 1] = [0, .4, 0, 0, 0]
        X[3, :, 1] = [0, 0, 0, 0, 0]
        X[4, :, 1] = [0, 0, 0, 0, 0]

        X = np.concatenate((np.eye(self.get_num_sources())[..., None], -X),
                           axis=-1)

        return X


__all__.append('Baccala2001_fig4')


class Baccala2001_fig5(AbstractMVARSigGen):
    """This class implements [Baccala2001]_ figure 5."""

    def get_num_sources(self):
        """Return the number of sources in the simulation"""
        return 5

    def generate_parameters(self):
        """Create the autoregressive parameters for [Baccala2001]_ figure 5."""

        order = 4

        X = np.zeros((self.get_num_sources(), self.get_num_sources(), order))

        # (n - 1)
        X[0, :, 0] = [0.95*np.sqrt(2), 0, 0, 0, 0]
        X[1, :, 0] = [-.5, 0, 0, 0, 0]
        X[2, :, 0] = [0, 0, 0, 0, 0]
        X[3, :, 0] = [0, 0, -.5, .25*np.sqrt(2), .25*np.sqrt(2)]
        X[4, :, 0] = [0, 0, 0, -.25*np.sqrt(2), .25*np.sqrt(2)]

        # (n - 2)
        X[0, :, 1] = [-0.9025, 0, 0, 0, 0]
        X[1, :, 1] = [0, 0, 0, 0, 0]
        X[2, :, 1] = [0, -.4, 0, 0, 0]
        X[3, :, 1] = [0, 0, 0, 0, 0]
        X[4, :, 1] = [0, 0, 0, 0, 0]

        # Nothing at lag (n - 3) [:, :, 2]

        # (n - 4)
        X[0, :, 3] = [0, 0, 0, 0, 0]
        X[1, :, 3] = [0, 0, 0, 0, 0]
        X[2, :, 3] = [.1, 0, 0, 0, 0]
        X[3, :, 3] = [0, 0, 0, 0, 0]
        X[4, :, 3] = [0, 0, 0, 0, 0]

        X = np.concatenate((np.eye(self.get_num_sources())[..., None], -X),
                           axis=-1)

        return X


__all__.append('Baccala2001_fig5')


class Fasoula2013_eqn26(AbstractMVARSigGen):
    """This class implements [Fasoula2013]_ equation 26."""

    def get_num_sources(self):
        """Return the number of sources in the simulation"""
        return 10

    def generate_parameters(self):
        """Create the autoregressive parameters for [Fasoula2013]_ eqn 26."""

        order = 4

        X = np.zeros((self.get_num_sources(), self.get_num_sources(), order))

        X[0, :, 0] = [0.95*np.sqrt(2), 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[1, :, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[2, :, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[3, :, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[4, :, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[5, :, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[6, :, 0] = [0.4, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[7, :, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[8, :, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[9, :, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        X[0, :, 1] = [-0.9025, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[1, :, 1] = [.5, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[2, :, 1] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[3, :, 1] = [-.5, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[4, :, 1] = [0, 0, 0, 0, 0, 0, 0, -.4, 0, 0]
        X[5, :, 1] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[6, :, 1] = [0, 0, 0, 0, 0, 0, -.4, 0, 0, 0]
        X[7, :, 1] = [0, 0, 0, 0, 0, 0, -.9, 0, 0, 0]
        X[8, :, 1] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[9, :, 1] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        X[0, :, 2] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[1, :, 2] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[2, :, 2] = [0, .9, 0, 0, 0, 0, 0, 0, 0, 0]
        X[3, :, 2] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[4, :, 2] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[5, :, 2] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[6, :, 2] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[7, :, 2] = [0, 0, 0, 0, 0, 0, 0, .4, .3, 0]
        X[8, :, 2] = [0, 0, 0, 0, 0, 0, 0, -.3, .4, 0]
        X[9, :, 2] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        X[0, :, 3] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[1, :, 3] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[2, :, 3] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[3, :, 3] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[4, :, 3] = [0, 0, 0, .8, 0, 0, 0, 0, 0, 0]
        X[5, :, 3] = [0, 0, 0, -.8, 0, 0, 0, 0, 0, 0]
        X[6, :, 3] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[7, :, 3] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[8, :, 3] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        X[9, :, 3] = [0, 0, 0, 0, 0, 0, 0.75, 0, 0, 0]

        return X


__all__.append('Fasoula2013_eqn26')


class Schelter2006_fig1(AbstractMVARSigGen):
    """This class implements [Schelter2006]_ figure 1."""

    def get_num_sources(self):
        """Return the number of sources in the simulation"""
        return 5

    def generate_parameters(self):
        """Create the autoregressive parameters for [Schelter2006]_ fig 1."""

        order = 4

        X = np.zeros((self.get_num_sources(), self.get_num_sources(), order))

        X[0, :, 0] = [0.6, 0, 0, 0, 0]
        X[1, :, 0] = [0, .5, 0, 0.6, 0]
        X[2, :, 0] = [0, 0, 0.8, 0, 0]
        X[3, :, 0] = [0, 0, 0, .5, 0]
        X[4, :, 0] = [0, 0, -.2, 0, .7]

        X[0, :, 1] = [0, 0.65, 0, 0, 0]
        X[1, :, 1] = [0, -.3, 0, 0, 0]
        X[2, :, 1] = [0, 0, -.7, 0, 0]
        X[3, :, 1] = [0, 0, .9, 0, .4]
        X[4, :, 1] = [0, 0, 0, 0, -.5]

        X[0, :, 2] = [0, 0, 0, 0, 0]
        X[1, :, 2] = [0, 0, 0, 0, 0]
        X[2, :, 2] = [0, 0, 0, 0, -.1]
        X[3, :, 2] = [0, 0, 0, 0, 0]
        X[4, :, 2] = [0, 0, 0, 0, 0]

        X[0, :, 3] = [0, 0, 0, 0, 0]
        X[1, :, 3] = [0, 0, -.3, 0, 0]
        X[2, :, 3] = [0, 0, 0, 0, 0]
        X[3, :, 3] = [0, 0, 0, 0, 0]
        X[4, :, 3] = [0, 0, 0, 0, 0]

        X = np.concatenate((np.eye(self.get_num_sources())[..., None],  -X),
                           axis=-1)

        return X


__all__.append('Schelter2006_fig1')


class PascualMarqui2014_fig3(AbstractMVARSigGen):
    """This class implements [Pascual-Marqui2014]_ figure 3."""

    def get_num_sources(self):
        """Return the number of sources in the simulation"""
        return 5

    def generate_parameters(self):
        """Create the autoregressive parameters for [Pascual-Marqui2014]_ fig 3."""

        order = 2

        X = np.zeros((self.get_num_sources(), self.get_num_sources(), order))

        X[0, 0, 0] = 1.5
        X[1, 0, 0] = -.2
        X[0, 1, 0] = -.25

        X[1, 1, 0] = 1.8
        X[2, 1, 0] = .9
        X[3, 1, 0] = .9
        X[4, 1, 0] = .9

        X[2, 2, 0] = 1.65
        X[3, 3, 0] = 1.65
        X[4, 4, 0] = 1.65

        X[0, 0, 1] = -.95
        X[1, 1, 1] = -.96
        X[2, 2, 1] = -.95
        X[3, 3, 1] = -.95
        X[4, 4, 1] = -.95

        X[2, 1, 1] = -.8
        X[3, 1, 1] = -.8
        X[4, 1, 1] = -.8

        X = np.concatenate((np.eye(self.get_num_sources())[..., None], -X),
                           axis=-1)

        return X


__all__.append('PascualMarqui2014_fig3')


################################
# Literature Lag Data Generators

class Korzeniewska2003Lag(AbstractLagSigGen):
    """Generate realisations of the time-lagged network defined in
        [Korzeniewska2003]_ figure 1.

    """

    def get_num_sources(self):
        """Return the number of sources in the simulation"""

        return 8

    def generate_basesignal(self, nsamples):
        """Generate oscillatory signal to be propagated through the network.
        This creates a single resonance at one-half of the Nyquist
        frequency via direct pole placement.

        Note: the original base-signal in the paper is a realisation from
        an AR model. I couldn't find the parameters for this mode, so use
        pole placement here. The spectral profile will be different to the
        paper, but the connectivity patterns are the same.

        Parameters
        ----------
        nsamples : int
            The number of samples to generate

        Returns
        -------
        ndarray
            Vector containing generated base signal.

        """

        roots = np.array((1j*.8, -1j*.8))
        b = np.poly(roots)

        return signal.filtfilt(1, b, self.generate_noise(nsamples))

    def get_lags(self):
        """Return the lagged influences between time-series in the simulated
        defined in [Korzeniewska2003]_ figure 1."""

        L = np.zeros((8, 8, 3))

        # Lag 1
        L[0, 3, 0] = 1
        L[0, 7, 0] = 1

        # Lag 2
        L[3, 1, 1] = 1
        L[7, 4, 1] = 1
        L[7, 2, 1] = 1

        # Lag 3
        L[2, 5, 2] = 1
        L[2, 6, 2] = 1

        return L


__all__.append('Korzeniewska2003Lag')


#######################
# Paper Data Generators

class SailsTutorialExample(AbstractSigGen):
    """ """

    def get_num_sources(self):
        """Return the number of sources in the simulation"""

        return 10

    def generate_basesignal(self, f, r, sample_rate, num_samples):
        """Generate a simple signal by pole placement

        Parameters
        ----------
        f : float
            The peak frequency of the resonance to simulate
        r : float ( 0 < r < 1 )
            The pole magnitude of the resonance to simulate
        sample_rate : float
            The sample rate to generate data at
        num_samples : int
            The number of data samples to generate

        Returns
        -------
        ndarray
            A vector containing a simulated resonance

        Notes
        -----
        The parameter r controls both the sharpness and magnitude of the
        generated resonance. Values close to 1 will generate exponentially
        sharper and larger peaks.

        """

        if f > 0:
            wr = (2 * np.pi * f) / sample_rate
            a1 = np.array([1, -2*r*np.cos(wr), (r**2)])
        else:
            a1 = np.poly(.75)

        return signal.filtfilt(1, a1, np.random.randn(1, num_samples)).T

    def generate_signal(self, f1, f2, sample_rate, num_samples,
                        noise_dB=None, num_realisations=1,
                        magnitude_noise=.02):
        """Method for generating a set of time courses based on either the
        structure of a meg_reader object or passed parameters and the
        self.generate_parameters method defined in this class

        Returns a timeseries of dimension [samples x signals x realisations]

        Parameters
        ----------
        f1 : float
            The frequency of the first signal
        f2 : float
            The frequency of the second  signal
        sample_rate : float
            The sample rate of the simulated signal
        num_samples : int
            The number of samples to simulate
        num_realisations : int
            The number of realisations to simulate (Default value = 1)
        magnitude_noise : float
            The variance of additive white noise (Default value = .02)

        Returns
        -------
        ndarray
            The simulated signal of size [nchannels x num_samples x num_realisations]

        """

        X = np.random.randn(self.get_num_sources(), num_samples, num_realisations)

        weight1, weight2 = self.get_connection_weights()
        v = np.random.randn()*magnitude_noise
        sig1 = self.generate_basesignal(f1, .8+v, sample_rate, num_samples)
        sig2 = self.generate_basesignal(f2, .61, sample_rate, num_samples)

        sig1 = (sig1 - sig1.mean(axis=0)) / sig1.std(axis=0)
        sig2 = (sig2 - sig2.mean(axis=0)) / sig2.std(axis=0)

        for ii in range(len(weight1)):
            X[ii, :, :] = X[ii, :, :] + weight1[ii] * np.tile(sig1, num_realisations)

        for ii in range(len(weight2)):
            X[ii, :, :] = X[ii, :, :] + weight2[ii] * np.tile(sig2, num_realisations)

        return X + np.random.randn(*X.shape)

    def get_connection_weights(self, form='vector'):
        """Define the connectivity within the simulated system.

        Parameters
        ----------
        form : {'vector' || 'matrix'}
             Which form of to return the connections  is (Default value = 'vector')

        Returns
        -------
        weight1
            vector or matrix defining connectivity for resonance 1

        weight2
            vector or matrix defining connectivity for resonance 2

        """

        weight1 = np.array([1, 1, 1, 0, 0, 0, 1, 1, 1, 0])
        weight2 = np.array([0, 0, 0, .5, .7, .9, 1, .9, .7, .5])

        if form == 'vector':
            return weight1, weight2
        elif form == 'matrix':
            return weight1[:, None].dot(weight1[None, :]), \
                   weight2[:, None].dot(weight2[None, :])


__all__.append('SailsTutorialExample')


def single_pole_oscillator(freq, sample_rate, seconds, mixing=None, r=.95, noise_std=None, random_seed=None):
    """
    Create a simulated oscillation using an autoregressive filter. A simple
    filter is defined by direct pole placement and applied to white noise to
    generate a random signal with a defined oscillatory peak frequency that
    exhibits random variability frequency, amplitude and waveform.

    Parameters
    ----------
    freq : float
        Peak frequency of signal in Hz
    sample_rate : float
        Sampling rate of the data to be simulated
    seconds : float
        Seconds of data to generate
    mixing :  1d array_like
        Weighting of signal across channels (optional - default is single channel with weight of 1)
    r : scalar
        Magnitude of pole to be created  0 >= r > 1, larger values give bigger
        oscillations with sharper spectral peaks
    noise_std : scalar
        optional scaling of white noise to be added to  simulated data
    random_seed : int
        optional setting to fix random_seed for reproducibility

    Returns
    -------
    ndarray
        data array [nchannels x nsamples]

    """

    if random_seed is not None:
        np.random.seed(random_seed)

    if mixing is None:
        mixing = np.ones((1, ))
    mixing = np.array(mixing)

    if mixing.ndim != 1:
        raise ValueError('Please input a 1d (vector) set of mixing weights')

    if freq > 0:
        freq_rads = (2 * np.pi * freq) / sample_rate
        a1 = np.array([1, -2*r*np.cos(freq_rads), (r**2)])
    else:
        a1 = np.poly(r)

    num_samples = int(sample_rate * seconds)

    x = signal.filtfilt(1, a1, np.random.randn(num_samples, ), axis=0)

    y = np.zeros((len(mixing), x.shape[0]))
    for ii in range(len(mixing)):
        y[ii, :] = mixing[ii] * x

    if noise_std is not None:
        noise = np.std(y) * noise_std * np.random.randn(num_samples, )
        y = y + noise

    if random_seed is not None:
        np.random.seed()  # restore defaults

    return y
