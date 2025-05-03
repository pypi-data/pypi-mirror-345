from scipy._lib import doccer
from numpydoc.docscrape import NumpyDocString
import inspect
import itertools


def format_docstring(func, docdict):
    """

    This function makes use of the doccer utils from scipy
    https://github.com/scipy/scipy/blob/main/scipy/_lib/doccer.py

    Parameters
    ----------
    func : function
        Handle to function with docstring to update
    docdict : dict
        Dictionary of strings to map into function docstring

    Returns
    -------
    func
        function with docstring updated in-place

    """
    func.__doc__ = doccer.docformat(func.__doc__, doccer.unindent_dict(docdict))
    return func


def validate_docstring(func, raise_error=False):
    """Check that the args/kwargs in a functions docstring match it's signature.

    Parameters
    ----------
    func : function
        Handle to function to be checked
    raise_error : bool, optional
        Flag indicating whether to raise a full error or just a warning,
        by default 'False' which just raises a warning

    Returns
    -------
    tests : list of bool
        list of which args match, list length matches the longer of the args
        in the docstring, or the args in the signature

    Raises
    ------
    RuntimeError
        Raised if args do not match and `raise_error` is True
    RuntimeWarning
        Raised if args do not match and `raise_error` is Fase

    """
    nds = NumpyDocString(func.__doc__)
    sig = inspect.signature(func)

    tests = []
    names = []

    for idoc, isig in itertools.zip_longest(nds['Parameters'], sig.parameters):
        idoc = 'MISSING' if idoc is None else idoc.name
        isig = 'MISSING' if isig is None else isig
        names.append((idoc, isig))
        boolcheck = (idoc == 'MISSING') or (isig == 'MISSING') or (idoc != isig)
        tests.append(boolcheck is False)  # True if all matching

    if False in tests:
        print(func)
        print('{} : {} : {}'.format('Dstring', 'Sig', 'Match'))
        for name, test in zip(names, tests):
            print('{} : {} : {}'.format(name[0],  name[1], test))

    if False in tests and raise_error:
        raise RuntimeError('{} : args in docstring do not match function signature'.format(func))
    elif False in tests:
        raise RuntimeWarning('{} : args in docstring do not match function signature'.format(func))

    return tests


# ---------------------------------------------------------------------------------
# DocStrings for STFT Module


docdict = {}

docdict['axis'] = """
    axis : int
        Axis of input array along which the computation is performed. (Default value = -1)"""

docdict['fs'] = """
    fs : float
        Sampling rate of the data"""

docdict['freq_range'] = """
    fmin : {float, None}
        Smallest frequency in desired range (left hand boundary)
    fmax : {float, None}
        Largest frequency in desired range (right hand boundary)"""

docdict['spec_mode'] = """
    mode : {'psd', 'magnitude', 'angle', 'phase', 'complex'}
        Which type of spectrum to return (Default value = 'psd')"""

docdict['nfft'] = """
    nfft : int
        Length of the FFT to use (Default value = 256)"""

docdict['fft_side'] = """
    side : {'onesided', 'twosided'}
        Whether to return a one-sided or two-sided spectrum (Default value = 'onesided')"""

docdict['return_onesided'] = """
    return_onesided : bool, optional
        If `True`, return a one-sided spectrum for real data. If
        `False` return a two-sided spectrum. Defaults to `True`, but for
        complex data, a two-sided spectrum is always returned."""

docdict['fft_scale'] = """
    scale : float
        Scaling factor to be applied to FFT result. Typically defined by
        `_set_scaling` via the config options (Default value = 1.)"""

docdict['fft_scaling'] = """
    scaling : { 'density', 'spectrum' }
        Selects between computing the power spectral density ('density')
        where `Pxx` has units of V**2/Hz and computing the power
        spectrum ('spectrum') where `Pxx` has units of V**2, if `x`
        is measured in V and `fs` is measured in Hz. Defaults to
        'density'"""

docdict['fft_core'] = docdict['nfft'] + docdict['axis'] + docdict['fft_side'] + \
                      docdict['spec_mode'] + docdict['fft_scale'] + docdict['fs'] + docdict['freq_range']

docdict['fft_user'] = docdict['nfft'] + docdict['axis'] + docdict['return_onesided'] + \
                      docdict['spec_mode'] + docdict['fft_scaling'] + docdict['fs'] + docdict['freq_range']

docdict['average'] = """
    average : { 'mean', 'median', 'median_bias' }, optional
        Method to use when averaging across sliding window segments in a periodograms.
        Defaults to 'mean'."""

docdict['irasa'] = """
    method : {'original', 'modified'}
        whether to compute the original implementation of IRASA or the modified update
        (default is 'original')
    resample_factors : {None, array_like}
        array of resampling factors to average across or None, in which a set
        of factors are automatically computed (default is None).
    aperiodic_average : {'mean', 'median', 'median_bias', 'min'}
        method for averaging across irregularly resampled spectra to estimate
        the aperiodic component (default is 'median')."""

docdict['nperseg'] = """
    nperseg : int
        Length of each segment. Defaults to None, but if window is str or
        tuple, is set to 256, and if window is array_like, is set to the
        length of the window."""

docdict['noverlap'] = """
    noverlap : int
        Number of samples that successive sliding windows should overlap."""

docdict['nstep'] = """
    nstep : int, optional
        Number of points to step forward between segments. If `None`,
        ``noverlap = nperseg // 2``. Defaults to `None`."""

docdict['window_type'] = """
    window_type : str or tuple or array_like, optional
        Desired window to use. If `window` is a string or tuple, it is
        passed to `scipy.signal.windows.get_window` to generate the
        window values, which are DFT-even by default. See `scipy.signal.windows`
        for a list of windows and required parameters.
        If `window` is array_like it will be used directly as the window and its
        length must be nperseg. Defaults to a Hann window."""

docdict['window'] = """
    window : array_like,
        Vector containing window function to apply."""

docdict['detrend_func'] = """
    detrend_func : function or None
        Specifies how to detrend each segment. If it is a function,
        it takes a segment and returns a detrended segment.
        If `detrend` is None, no detrending is done. Defaults to None."""

docdict['detrend'] = """
    detrend : str or function or `False`, optional
        Specifies how to detrend each segment. If `detrend` is a
        string, it is passed as the `type` argument to the `detrend`
        function. If it is a function, it takes a segment and returns a
        detrended segment. If `detrend` is `False`, no detrending is
        done. Defaults to 'constant'."""

docdict['padded'] = """
    padded : bool, optional
        Specifies whether the input signal is zero-padded at the end to
        make the signal fit exactly into an integer number of window
        segments, so that all of the signal is included in the output.
        Defaults to `False`. Padding occurs after boundary extension, if
        `boundary` is not `None`, and `padded` is `True`."""

docdict['stft_window'] = docdict['nperseg'] + docdict['nstep'] + docdict['window'] + \
                         docdict['detrend_func'] + docdict['padded']

docdict['stft_window_user'] = docdict['nperseg'] + docdict['noverlap'] + \
                              docdict['window_type'] + docdict['detrend']

docdict['verbose'] = """
    verbose : {None, 'DEBUG', 'INFO', 'WARNING', 'CRITICAL'}
        String indicating the level of detail to be printed to the screen during computation."""

docdict['output_axis'] = """
    output_axis : { 'auto', 'time_first'}
        Flag indicating where to roll the time and frequencies dimensions to in
        output array. 'auto' will return the transformed dimensions back the
        position of the transformed input, 'glm' will roll the time windows to (Default value = 'auto')"""

docdict['pxx_complex'] = """
    pxx : ndarray
        Array containing a complex valued Fourier transform result."""

docdict['multitaper_core'] = """
    num_tapers : {int, 'auto'}
        The number of tapers to use if set to an integer value, if set to
        `'auto'` then the number of tapers is automatically computed from
        `freq_resolution` and `time_half_bandwidth` (Default value = 'auto')
    freq_resolution : int
        Required frequency resolution of the tapers used if `num_tapers` is set
        to `auto` (Default value = 1)
    time_half_bandwidth : int
        Required time bandwidth value of the tapers used if `num_tapers` is set
        to `auto` (Default value = 5)
    apply_tapers : {'broadcast', 'loop}
        Flag indicating whether to compute each taper in one-shot by broadcasting
        or to iterate through each in a loop. Broadcasting is probably faster but
        more memory intensive. (Default value = 'broadcast')"""

docdict['glmperiodogram'] = """
    reg_categorical : dict or None
        Dictionary of covariate time series to be added as binary regessors. (Default value = None)
    reg_ztrans : dict or None
        Dictionary of covariate time series to be added as z-standardised regessors. (Default value = None)
    reg_unitmax : dict or None
        Dictionary of confound time series to be added as positive-valued unitmax regessors. (Default value = None)
    contrasts : dict or None
        Dictionary of contrasts to be computed in the model.
        (Default value = None, will add a simple contrast for each regressor)
    fit_intercept : bool
        Specifies whether a constant valued 'intercept' regressor is included in the model. (Default value = True)"""


stft_funcs = ['apply_sliding_window',
              'compute_fft',
              'compute_stft',
              'compute_multitaper_stft',
              'compute_spectral_matrix_fft',
              '_proc_roll_input',
              '_proc_unroll_output',
              '_proc_spectrum_mode',
              '_proc_spectrum_scaling',
              '_proc_trim_freq_range',
              '_set_freqvalues',
              '_set_onesided',
              '_set_nfft',
              '_set_noverlap',
              '_set_scaling',
              '_set_heinzel_scaling',
              '_set_detrend',
              '_set_mode',
              '_set_frange',
              'periodogram',
              'multitaper',
              'glm_periodogram',
              'glm_multitaper',
              'irasa',
              'glm_irasa']
