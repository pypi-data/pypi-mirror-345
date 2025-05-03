import numpy as np
from random import sample
from .modelfit import VieiraMorfLinearModel
from .modal import MvarModalDecomposition


def permute_modal_decomp(X_epoch, model_order, sample_rate=1,
                         num_permutations=500, metric='damping_time',
                         modelcls=VieiraMorfLinearModel,
                         metric_lims=None):
    """
    Run non-parametric permutations to identify 'significant' modes from a
    modal decomposition.

    Currently can only permute on damping times but probably want to generalise
    this later.

    """

    nulls = np.zeros((num_permutations,))

    for modelnum in range(num_permutations):
        if modelnum == 0:
            # Our first model is our observed statistic
            X_copy = X_epoch.copy()
            sample_numbers = np.zeros((X_epoch.shape[0], X_epoch.shape[2], 2), np.int)
            sample_numbers[:, :, 0] = np.arange(X_epoch.shape[0])[:, None]
            sample_numbers[:, :, 1] = np.arange(X_epoch.shape[2])[None, :]
        else:
            # Permute the data
            X_copy, sample_numbers = permute_epoch_data(X_epoch)

        # Model fit
        model = VieiraMorfLinearModel.fit_model(X_copy, np.arange(model_order))
        modes = MvarModalDecomposition.initialise(model, sample_rate)

        if metric == 'damping_time':
            if metric_lims is not None:
                cond_lo = modes.peak_frequency < metric_lims[0]
                cond_hi = modes.peak_frequency > metric_lims[1]
                inds = np.logical_or(cond_lo, cond_hi) == False  # noqa: E712
            else:
                inds = np.ones_like(modes.dampening_time).astype(bool)
            nulls[modelnum] = modes.dampening_time[inds].max()

    return nulls


def permute_epoch_data(X_epoch):
    """
    Take a copy of the epoch data, randomise the order of channels and epochs
    and return the randomised copy
    """
    X_copy = np.zeros_like(X_epoch)
    num_chans = X_copy.shape[0]
    num_segments = X_copy.shape[2]
    num_to_permute = num_chans * num_segments

    samples = sample(list(np.arange(num_to_permute)), num_to_permute)
    sample_idx = 0

    sample_numbers = np.zeros((num_chans, num_segments, 2), np.int)

    for chan in range(X_epoch.shape[0]):
        for epoch in range(num_segments):
            orig_chan = int(samples[sample_idx] / num_segments)
            orig_idx = samples[sample_idx] % num_segments
            X_copy[chan, :, epoch] = X_epoch[orig_chan:orig_chan+1, :, orig_idx]
            sample_numbers[chan, epoch, :] = [orig_chan, orig_idx]
            sample_idx += 1

    return X_copy, sample_numbers
