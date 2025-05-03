#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

from .modal import *  # noqa: F401, F403
from .modelfit import *  # noqa: F401, F403
from .modelvalidation import *  # noqa: F401, F403
from .mvar_metrics import *  # noqa: F401, F403
from .diags import *  # noqa: F401, F403
from .plotting import *  # noqa: F401, F403
from .circular_plots import *  # noqa: F401, F403
from .tutorial_utils import *  # noqa: F401, F403
from .simulate import *  # noqa: F401, F403
from .utils import *  # noqa: F401, F403
from .permute import *  # noqa: F401, F403
from . import stft, wavelet, orthogonalise, stats  # noqa: F401, F403

# Load docstrings
from ._docstring_utils import format_docstring, docdict, stft_funcs
for func in stft_funcs:
    new_func = format_docstring(getattr(stft, func), docdict)
    setattr(stft, func, new_func)
