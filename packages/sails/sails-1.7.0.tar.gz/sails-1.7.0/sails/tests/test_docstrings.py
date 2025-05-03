#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

"""Test STFT Module."""

import unittest


class TestSTFTDocstrings(unittest.TestCase):
    """Compare simple periodogram outputs against scipy."""

    def test_stft_docstrings(self):
        from .._docstring_utils import validate_docstring, stft_funcs
        from .. import stft

        for func in stft_funcs:
            validate_docstring(getattr(stft, func), raise_error=True)
