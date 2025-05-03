#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import os
from os.path import abspath, expanduser, isdir, isfile, join, split

import numpy as np

__all__ = []


def generate_pink_roots(power, order=24):
    """Generates the poles of a system with a pink spectrum according to eqn
    116 in [Kasdin1995]_

    Parameters
    ----------
    power : float
        Power of pole must be between -2 and 2.
    order :
        Order of system to generate (Default value = 24)

    Returns
    -------
    ndarray
        Roots of the system (length of order)

    """
    a = np.zeros((order,))
    a[0] = 1
    for k in range(1, order):
        a[k] = (k - 1 - (power/2.)) * (a[k-1] / k)

    return np.roots(a)


__all__.append('generate_pink_roots')


def model_from_roots(roots):
    """Sets up a univariate model based on the roots of a polynomial

    Parameters
    ----------
    roots : ndarray
        Vector of polynomial roots.

    Returns
    -------
    AbstractLinearModel
        Model fit class containing the parameters defined by the input roots

    """

    # We can use the AbstractLinearModel for this as we
    # don't need the fit_model routine
    from sails import AbstractLinearModel

    ret = AbstractLinearModel()
    ret.parameters = -np.poly(roots)[None, None, :]
    ret.resid_cov = np.ones((1, 1, 1))
    ret.delay_vect = np.arange(ret.order + 1)

    return ret


__all__.append('model_from_roots')


def find_support_path():
    """Returns the path to the support files directory"""
    d, f = split(__file__)

    return join(abspath(d), 'support')


__all__.append('find_support_path')


def find_example_path():
    """Returns the path to the tutorial example data directory (if available)"""

    example_path = os.getenv('SAILS_EXAMPLE_DATA', None)

    if example_path is None:
        # Try the user's home directory
        example_path = join(expanduser("~"), "sails-example-data")

    # A sentinel file which we ensure is in the git repo for the example data
    sentinel = join(example_path, 'SAILS_EXAMPLE_DATA')

    # Check for directory and sentinel file
    if not isdir(example_path) or not isfile(sentinel):
        error = """
Error: Could not find the sails example data (looked in
{})

If you wish to use the example data, download it from git
using:

    git clone https://github.com/sails-dev/sails-example-data

If the git repository is in your home directory, this function
will then find the path.  If you wish to store the data in another
location, set the SAILS_EXAMPLE_DATA environment variable to
the location of the git checkout
""".format(example_path)

        raise Exception(error)

    return example_path


__all__.append('find_example_path')


def set_sail():
    """ """
    import os
    import time
    rows, columns = os.popen('stty size', 'r').read().split()
    cols = int(columns)

    ship = ['    __|__ __|__ ',
            '    )    ))    )\\',
            '    )    ))    )\\\\',
            '    )____))____) \\\\',
            '\\---__|______|____\\\\----',
            '~~;\\_____________/']

    air = ''
    air = [air + ' '*cols for ii in range(6)]
    air = '\n'.join(air) + '\n'

    sea = ''
    sea = [sea + '~'*cols for ii in range(3)]
    sea = '\n'.join(sea)

    msg = list(air+sea)

    for step in range(5, cols-25):
        msg = list(air+sea)
        for ii in range(len(ship)):
            start = step + (cols+1)*(ii+1)
            stop = start + len(ship[ii])
            msg[start:stop] = ship[ii]

        print('\033[2J\033[<3>A')
        print(''.join(msg))
        time.sleep(1.0/15)

    start = cols//2 + cols*(2) - 2
    stop = start+5
    msg[start:stop] = 'SAILS'
    print('\033[2J\033[<3>A')
    print(''.join(msg))
    time.sleep(2)


__all__.append('set_sail')
