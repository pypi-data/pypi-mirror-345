#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colorbar as cb
from mpl_toolkits.axes_grid1 import Grid
from matplotlib import patches

__all__ = []


def root_plot(rts, ax=None, figargs=dict(), plotargs=dict()):
    """Plot a set of roots (complex numbers).

    Parameters
    ----------
    rts : ndarray_like
        Roots to plot
    ax : matplotlib axes handle
        Optional Axes on which to place plot. (Default value = None)
    figargs : dict
        extra arguments to pass to plt.figure (Default value = dict())
    plotargs : dict
        extra arguments to pass to plt.plot (Default value = dict())

    Returns
    -------
    Axes
        Axes object on which plot was drawn

    """

    if 'figsize' not in figargs:
        figargs['figsize'] = (6, 6)

    if ax is None:
        plt.figure(*figargs)
        ax = plt.subplot(111)

    # Unit Circle
    y = np.sin(np.linspace(0, 2*np.pi, 128))
    x = np.cos(np.linspace(0, 2*np.pi, 128))
    ax.plot(x, y, 'k')
    # Inner circles
    ax.plot(.75*x, .75*y, 'k--', linewidth=.2)
    ax.plot(.5*x, .5*y, 'k--', linewidth=.2)
    ax.plot(.25*x, .25*y, 'k--', linewidth=.2)
    ax.grid(True)

    # Arrow annotation
    ax.plot(1.15*x[8:25], 1.15*y[8:25], 'k')
    ax.arrow(1.15*x[23], 1.15*y[23], x[24]-x[23], y[24]-y[23],
             head_width=.05, color='k')

    # Add poles
    ax.plot(rts.real, rts.imag, 'k+', **plotargs)

    # Labels
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlim(-1.2, 1.2)
    ax.set_xlabel('Real')
    ax.set_ylabel('Imaginary')
    ax.annotate('Frequency', xy=(.56, 1.02))
    ax.set_aspect('equal')

    return ax


__all__.append('root_plot')


def plot_diagonal(freq_vect, metric, F=None, title=None, ax=None):
    """Plot the diagonal spectra from a connectivity array. This is generally
    used to summarised the within-channel spectra within a network.

    Parameters
    ----------
    freq_vect : ndarray
        Vector of frequency values indexing the x-axis
    metric : ndarray
        Matrix of connectivity values of size [nchannels x nchannels x nfrequencies]
    F : matplotlib figure handle
        Handle for matplotlib figure to plot in (Default value = None)
    title : str
        String to use as figure title(Default value = None)
    ax : matplotlib axes handle
        Handle for matplotlib axes to plot in (Default value = None)

    """

    if F is None:
        F = plt.figure(figsize=(6, 6))

    if ax is None:
        ax = F.subplots(1)

    for ii in range(metric.shape[0]):
        ax.plot(freq_vect, metric[ii, ii, :, 0])

    if title is not None:
        ax.set_title(title)

    ax.set_xlabel('Frequency')
    ax.grid(True)


def plot_metric_summary(freq_vect, metric, ind=0, F=None, title=None):
    """Plot the within-channel spectra and connectivity matrix for a given
    connectivity metric.

    Parameters
    ----------
    freq_vect : ndarray
        Vector of frequency values indexing the x-axis
    metric : ndarray
        Matrix of connectivity values of size [nchannels x nchannels x nfrequencies]
    ind : int
        Index into frequency dimension to plot connectivity matrix (Default value = 0)
    F : matplotlib figure handle
        Handle for matplotlib figure to plot in (Default value = None)
    title : str
        String to use as figure title(Default value = None)

    """

    F = plt.figure(figsize=(12, 6))
    ax = F.subplots(1, 2)

    plot_diagonal(freq_vect, metric, F=F, ax=ax[0])
    ylimits = ax[0].get_ylim()
    ax[0].vlines(freq_vect[ind], ylimits[0], ylimits[1])

    s = metric[:, :, ind, 0] - np.diag(np.diag(metric[:, :, ind, 0]))
    im = ax[1].imshow(np.abs(s))
    F.colorbar(im)


def plot_vector(metric, x_vect, y_vect=None, x_label=None, y_label=None,
                title=None, labels=None, line_labels=None, F=None,
                cmap=plt.cm.jet, triangle=None, diag=False,
                thresh=None, two_tail_thresh=False, font_size=10,
                use_latex=False):
    """Function for plotting frequency domain connectivity at a single time-point.

    Parameters
    ----------
    metric : ndarray
        matrix containing connectivity values [nsignals x signals x frequencies
        x participants] in which the first dimension refers to source nodes and
        the second dimension refers to target nodes
    x_vect : ndarray
        vector of frequencies to label the x axis
    y_vect : ndarrat
        vector containing the values for the y-axis
    x_label : string [optional]
        label for the x axis (Default value = None)
    y_label : string [optional]
        label for the y axis (Default value = None)
    title : string [optional]
        title for the figure (Default value = None)
    labels : list
        list of node labels for columns and vectors (Default value = None)
    line_labels : list
        list of labels for each separate line (participant
        dimension in metric) (Default value = None)
    F : figurehandle [optional]
        handle of existing figure to plot within (Default value = None)
    triangle : string [optional]
        string to indicate whether only the 'upper' or 'lower'
        triangle of the matrix should be plotted (Default value = None)
    diag : bool [optional]
        flag to indicate whether the diagonal elements should
        be plotted (Default value = False)
    thresh : ndarray [optional]
        matrix containing thresholds to be plotted alongside
        connectivity values [nsignals x nsignals x frequencies] (Default value = None)
    two_tailed_thresh : bool [optional]
        flag to indicate whether both signs (+/-) of the
        threshold should be plotted
    font_size : int [optional]
        override the default font size
    use_latex : bool
        Flag to indicate whether to render text in latex (Default value = False)

    Returns
    -------
    matplotlib figure handle
        Figure handle containing the plot

    """

    # Set up plotting parameters
    matplotlib.rcParams.update({'font.size': font_size})
    if use_latex:
        matplotlib.rcParams['text.latex.preamble'].append(r'\usepackage{amsmath}')
        plt.rc('font', **{'family': 'sans-serif',
                          'sans-serif': ['Helvetica']})
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

    if metric.ndim > 3 and metric.shape[3] > 1:
        # We want to plot each line separately
        ppt = metric.shape[3]
    elif metric.ndim > 3 and metric.shape[3] == 1:
        ppt = 1
    elif metric.ndim == 3:
        ppt = 1
        metric = metric[..., None]

    # Sanity check axis labels
    x_vect = x_vect.squeeze()
    if y_vect is not None:
        y_vect = y_vect.squeeze()
    nbSignals = metric.shape[0]

    # If we don't have any labels, make some up
    if labels is None:
        labels = [chr(65 + (x % 26)) for x in range(nbSignals)]

    if line_labels is None:
        line_labels = [chr(97 + (x % 26)) for x in range(ppt)]

    # Make figure if we don't have one
    if F is None:
        F = plt.figure(figsize=(8.3, 5.8))
        plt.axis('off')

    # Get label indices
    x_label_idx = []
    y_label_idx = []
    for g in range(nbSignals * nbSignals):
        i = int(g / nbSignals)
        j = int(g % nbSignals)

        if triangle == 'upper':
            if i == 0:
                x_label_idx.append(g)
            if i == j-1:
                y_label_idx.append(g)

        elif triangle == 'lower':
            if j == 0:
                x_label_idx.append(g)
            if i == j+1:
                y_label_idx.append(g)
        else:
            if i == 0:
                x_label_idx.append(g)
            if j == 0:
                y_label_idx.append(g)

    # Write labels to plot
    ax_pad = 0.25

    # Make grid with appropriate amount of subplots
    grid = Grid(F, 111,
                nrows_ncols=(nbSignals, nbSignals),
                axes_pad=ax_pad,
                share_all=True)

    # Plot up the matrix
    for g in range(nbSignals*nbSignals):
        i = int(g / nbSignals)
        j = int(g % nbSignals)

        if triangle == 'lower' and i < j:
            grid[g].set_visible(False)
            continue
        elif triangle == 'upper' and i > j:
            grid[g].set_visible(False)
            continue

        if diag is False and i == j:
            grid[g].set_visible(False)
            [grid[g].axis[k].set_visible(False) for k in grid[g].axis.keys()]

        if thresh is not None:
            grid[g].plot(x_vect, thresh[i, j, :], 'k--')
            if two_tail_thresh:
                grid[g].plot(x_vect, -thresh[i, j, :], 'k--')

        if ppt > 1 or thresh is not None:
            for p in range(ppt):
                grid[g].plot(x_vect, metric[i, j, :, p],
                             label=line_labels[p])
                grid[g].set_xlim(x_vect[0], x_vect[-1])

        else:
            grid[g].fill_between(x_vect, metric[i, j, :, 0],
                                 0, facecolor='black',
                                 alpha=.9)

        if y_vect is not None:
            grid[g].set_ylim(y_vect[0], y_vect[-1])

        grid[g].grid()

    if line_labels is not None and ppt > 1:
        grid[nbSignals-1].legend(bbox_to_anchor=(1.05, 1), loc=2)

    ymin, ymax = grid[g].get_ylim()

    grid.axes_llc.set_xlim(x_vect[0], x_vect[-1])

    if triangle == 'lower':
        x_x_pos = x_vect[2]
        x_y_pos = ymax*1.2
        y_x_pos = -x_vect[-2]
        y_y_pos = 1.2
        # Plot the labels
        for g in x_label_idx:
            i = int(g / nbSignals)
            j = int(g % nbSignals)

            grid[g].text(y_x_pos, y_y_pos, r'$\mathbf{%s}$' % (labels[i]))

        for g in y_label_idx:
            i = int(g / nbSignals)
            j = int(g % nbSignals)

            grid[g].text(x_x_pos, x_y_pos,
                         r'$\mathbf{%s \rightarrow}$' % (labels[i-1]))
    elif triangle == 'upper':
        x_x_pos = x_vect[:-2].mean()
        x_y_pos = ymax*1.2
        y_x_pos = -x_vect[-2]
        y_y_pos = .5
        # Plot the labels
        for g in x_label_idx:
            i = int(g / nbSignals)
            j = int(g % nbSignals)

            grid[g].text(x_x_pos, x_y_pos,
                         r'$\mathbf{%s \rightarrow}$' % (labels[j]))

        for g in y_label_idx:
            i = int(g / nbSignals)
            j = int(g % nbSignals)

            grid[g].text(y_x_pos, y_y_pos,
                         r'$\mathbf{%s}$' % (labels[i]))
    else:
        x_x_pos = x_vect[2]
        x_y_pos = ymax*1.2
        y_x_pos = -x_vect[:-2].mean() * 1.7
        y_y_pos = ymax * .5
        # Plot the labels
        for g in x_label_idx:
            i = int(g / nbSignals)
            j = int(g % nbSignals)

            grid[g].text(x_x_pos, x_y_pos,
                         r'$\mathbf{%s \rightarrow}$' % (labels[j]))

        for g in y_label_idx:
            i = int(g / nbSignals)
            j = int(g % nbSignals)

            grid[g].text(y_x_pos, y_y_pos,
                         r'$\mathbf{%s}$' % (labels[i]))

    for g in range(nbSignals * nbSignals):
        [k.set_visible(True) for k in grid[g].texts]

    if x_label is not None:
        grid[nbSignals*(nbSignals-1)].set_xlabel(x_label)
    if y_label is not None:
        grid[nbSignals*(nbSignals-1)].set_ylabel(y_label)

    if title is not None:
        plt.suptitle(title)

    return F


def plot_matrix(metric, x_vect, y_vect, x_label=None, y_label=None,
                z_vect=None, title=None, labels=None, F=None, vlines=None,
                cmap=plt.cm.jet, font_size=8, use_latex=False, diag=True):

    """Function for plotting frequency domain connectivity over many time points

    Parameters
    ----------
    metric : ndarray
        matrix containing connectivity values [nsignals x signals x frequencies
        x participants] in which the first dimension refers to source nodes and
        the second dimension refers to target nodes
    x_vect : 1d array
        vector of frequencies to label the x axis
    y_vect : 1d array [optional]
        vector containing the values for the y-axis
    z_vect : 1d array [optional]
        vector containing values for the colour scale (Default value = None)
    x_label : string [optional]
        label for the x axis (Default value = None)
    y_label : string [optional]
        label for the y axis (Default value = None)
    title : string [optional]
        title for the figure (Default value = None)
    labels : list
        list of node labels for columns and vectors (Default value = None)
    F : figurehandle [optional]
        handle of existing figure to plot within (Default value = None)
    vlines : list
        List of x-axis values to plot a dashed vertical line (Default value = None)
    cmap : matplotlib colormap [optional]
        matplotlib.cm.<colormapname> to use for
        colourscale (redundant for plot vector??) (Default value = plt.cm.jet)
    font_size : int [optional]
        override the default font size
    use_latex : bool
        Flag indicating whether to render text in latex (Default value = False)
    diag : bool
        Flag indicating whether to plot the diagonal subplots (Default value = True)

    Returns
    -------
    matplotlib figure handle
        Figure handle containing the plot

    """
    # Set up plotting parameters
    matplotlib.rcParams.update({'font.size': font_size})
    if use_latex:
        matplotlib.rcParams['text.latex.preamble'].append(r'\usepackage{amsmath}')
        plt.rc('font', **{'family': 'sans-serif',
                          'sans-serif': ['Helvetica']})
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

    # Sanity check axis labels
    x_vect = x_vect.squeeze()
    y_vect = y_vect.squeeze()
    nbSignals = metric.shape[0]

    # Set up colour scale
    if z_vect is None:

        if diag is True:
            mx = np.abs(metric).max()
        else:
            upper_tri = np.tril(np.abs(metric).max(axis=(2, 3)), k=-1).max()
            lower_tri = np.triu(np.abs(metric).max(axis=(2, 3)), k=1).max()
            mx = np.max([upper_tri, lower_tri])

        if metric.min() < 0:
            cbounds = np.linspace(-mx, mx)
        else:
            cbounds = np.linspace(0, mx)
    else:
        cbounds = z_vect

    # Make figure if we don't have one
    if F is None:
        F = plt.figure(figsize=(8.3, 5.8))
    plt.axis('off')

    # Write labels to plot
    step = 1. / nbSignals

    # Horizontal
    for i in range(len(labels)):
        plt.text((step*i)+.05, 1.01,
                 r'$\mathbf{%s \rightarrow}$' % (labels[i]),
                 fontsize=font_size,
                 rotation='horizontal')

    # Vertical
    for i in range(len(labels), 0, -1):
        plt.text(-.08, (step*i)-step/10 - .06,
                 r'$\mathbf{%s}$' % (labels[-i]),
                 fontsize=font_size,
                 verticalalignment='center',
                 rotation='vertical')

    # Make grid with appropriate amount of subplots
    grid = Grid(F, 111,
                nrows_ncols=(nbSignals, nbSignals),
                axes_pad=0.1,
                share_all=True)

    # Plot up the matrix
    for g in range(nbSignals*nbSignals):
        i = int(g / nbSignals)
        j = int(g % nbSignals)

        if i != j or diag is True:
            grid[g].contourf(x_vect, y_vect, metric[i, j, :, :],
                             np.linspace(cbounds[0], cbounds[-1], 10),
                             cmap=cmap)
            if vlines is not None:
                grid[g].vlines(vlines, y_vect[0], y_vect[-1], linestyles='dashed')
        else:
            grid[g].set_visible(False)

        if j == 0:
            grid[g].set_ylabel(y_label)
        if i == nbSignals-1:
            grid[g].set_xlabel(x_label)

    # Set labels
    grid.axes_llc.set_ylim(y_vect[0], y_vect[-1])

    # Set colourbar
    ax = F.add_axes([.92, .12, .02, .7], visible=True)
    cb.ColorbarBase(ax, boundaries=cbounds, cmap=cmap)

    if title is not None:
        plt.suptitle(title, fontsize=16)

    return F


def plot_netmat(data, colors=None, cnames=None, xtick_pos=None, ytick_pos=None,
                labels=None, ax=None, hregions='top', vregions='right', showgrid=True,
                **kwargs):
    """Function for plotting connectivity matrices

    Any additional keyword arguments will be passed into pcolormesh

    Parameters
    ----------
    data : ndarray
        2D numpy array of netmat data to plot of size [nrois x nrois]
    colors : dict
        dictionary mapping colour names to matplotlib-usable colours. If not
        provided, name from cnames will be used. (Default value = None)
    cnames : list
         list of len(nrois).  List of colour names for each region (Default value = None)
    labels : list
         List of region labels for the X and Y axes (Default value = None)
    ax : matplotlib axis handle
         Matplotlib axes to plot in (Default value = None)

    Additional Parameters
    ---------------------

    xtick_pos : ndarray
         Positions of X ROI division lines in netmat (Default value = None)
    ytick_pos : ndarray
         Positions of Y ROI division lines in netmat (Default value = None)
    hbar_offset : int
        Offset of ROI bar in Y co-ordinates (default: 2)
    vbar_offset : int
        Offset of ROI bar in X co-ordinates (default: 2)
    bar_gap : float
        Gap to put between ROI bars (default: 0.1)
    bar_thickness : float
        Thickness of the ROI bar (default: 2.5)
    label_fontsize : float
        Font size to use for region labels (default: 5)
    hregions : {'top','bottom','off'}
         Location to place horizontal coloured bars indicating regions of ROIs.
         (Default value = 'top')
    vregions : {'left','right','off'}
         Location to place vertical coloured bars indicating regions of ROIs.
         (Default value = 'right')
    showgrid : bool
         Flag to indicate whether to show grid-lines (Default value = True)
    **kwargs :
        Additional arguments are passed to pcolormesh

    Returns
    -------
    matplotlib axes handle
        axes handle containing the plot

    """

    num_rois = data.shape[0]

    hbar_offset = kwargs.pop('hbar_offset', 2)
    vbar_offset = kwargs.pop('vbar_offset', 2)
    bar_gap = kwargs.pop('bar_gap', 0.1)
    bar_thickness = kwargs.pop('bar_thickness', 2.5)
    label_fontsize = kwargs.pop('label_fontsize', 5)

    # Parse the h and vregions parameters
    if hregions not in ['top', 'bottom', 'off', True, False]:
        raise Exception("hregions must be one of top, bottom, off")

    if hregions is True:
        hregions = 'top'
    if hregions is False:
        hregions = 'off'

    if vregions not in ['left', 'right', 'off', True, False]:
        raise Exception("vregions must be one of left, right, off")

    if vregions is True:
        vregions = 'top'
    if vregions is False:
        vregions = 'off'

    # Ensure that we have a set of axes
    if ax is None:
        plt.figure()
        ax = plt.subplot(1, 1, 1)

    # See comment below regarding pcolormesh vs imshow
    ax.pcolormesh(data, **kwargs)
    plt.axis('scaled')

    if cnames is not None:
        start = None

        for k in range(num_rois):
            thiscname = cnames[k]

            if start is None:
                start = k
                curcname = thiscname

            if k != (num_rois - 1):
                nextcname = cnames[k+1]

            if (k == (num_rois - 1)) or (nextcname != curcname):
                # Need to draw and reset start point
                if colors is not None:
                    color = colors[curcname]
                else:
                    color = curcname

                width = bar_thickness

                if vregions == 'right':
                    ll_x = num_rois + vbar_offset
                else:
                    ll_x = -vbar_offset

                if start == 0:
                    ll_y = start
                    height = k - start + 1 - bar_gap
                elif k == (num_rois - 1):
                    ll_y = start + bar_gap
                    height = k - start + 1
                else:
                    ll_y = start + bar_gap
                    height = k - start + 1 - bar_gap - bar_gap

                if vregions != 'off':
                    rect = patches.Rectangle((ll_x, ll_y), width, height,
                                             linewidth=0, facecolor=color,
                                             clip_on=False)
                    ax.add_patch(rect)

                height = bar_thickness

                if hregions == 'top':
                    ll_y = num_rois + hbar_offset
                else:
                    ll_y = -hbar_offset

                if start == 0:
                    ll_x = start
                    width = k - start + 1 - bar_gap
                elif k == (num_rois - 1):
                    ll_x = start + bar_gap
                    width = k - start + 1
                else:
                    ll_x = start + bar_gap
                    width = k - start + 1 - bar_gap - bar_gap

                if hregions != 'off':
                    rect = patches.Rectangle((ll_x, ll_y), width, height,
                                             linewidth=0, facecolor=color,
                                             clip_on=False)
                    ax.add_patch(rect)

                start = None

    if xtick_pos is None:
        ax.set_xticks([])
    else:
        ax.set_xticks(xtick_pos)

    if ytick_pos is None:
        ax.set_yticks([])
    else:
        ax.set_yticks(ytick_pos)

    # Remove the major labels either way
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    if labels is not None:
        ax.set_xticks([x + 0.5 for x in range(num_rois)], minor=True)
        ax.set_yticks([x + 0.5 for x in range(num_rois)], minor=True)
        ax.set_xticklabels(labels, minor=True, fontsize=label_fontsize, rotation=-90)
        ax.set_yticklabels(labels, minor=True, fontsize=label_fontsize)

    plt.xlim(0, num_rois)
    plt.ylim(0, num_rois)

    if showgrid:
        plt.grid(True, color='w', lw=1)

    return ax


__all__.append('plot_netmat')
