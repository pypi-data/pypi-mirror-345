# SPDX-FileCopyrightText: Copyright 2021, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the license found in the LICENSE.txt file in the root
# directory of this source tree.


# =======
# Imports
# =======

import numpy
import scipy
from .electrocardiogram import electrocardiogram
from .._utilities.plot_utilities import plt, matplotlib, get_theme, \
        show_or_save_plot


# =================
# Covariance Matrix
# =================

def covariance_matrix(
        size=2**9,
        sample=2,
        cor=False,
        ecg_start=0.0,
        ecg_end=30.0,
        ecg_wrap=True,
        plot=False,
        verbose=False):
    """
    Create covariance matrix based on the autocorrelation of electrocardiogram
    signal.

    Parameters
    ----------

    size : int, default=2**9
        Size of the matrix.

    sample : int, default=2
        Sampling pace of the autocorrelation function.

    cor : bool, default=False
        If `True`, instead of the covariance matrix, the correlation matrix is
        returned.

    ecg_start : float, default=0.0
        Start time of the electrocardiogram signal in seconds.

    ecg_end : float, default=30.0
        End time of the electrocardiogram signal in seconds.

    ecg_wrap : bool, default=True
        If `True`, the electrocardiogram signal is assumed to be wrapped.

    plot : bool or str, default=False
        If `True`, the covariance matrix is plotted. If ``plot`` is a string,
        the plot is not shown, rather saved with a filename as the given
        string. If the filename does not contain file extension, the plot is
        saved in both ``svg`` and ``pdf`` formats. If the filename does not
        have directory path, the plot is saved in the current directory.

    verbose : bool, default=False
        if `True`, the saved plot filename is printed.

    Returns
    -------

        matrix : numpy.ndarray
            The covariance (or correlation, if `cor` is `True`) matrix.

    See Also
    --------

    detkit.electrocardiogram
    detkit.design_matrix

    Notes
    -----

    **Autocorrelation Function:**

    The covariance matrix is computed based on the autocorrelation of and ECG
    signal. It is assumed that the ECG signal is wide-sense stationary
    stochastic process, so its autocovariance function can be defined by

    .. math::

        \\kappa(\\Delta t) = \\mathbb{E}[
            (f(t+\\Delta t) - \\bar{f})(f(t) - \\bar{f})],

    where :math:`f` is the ECG signal, :math:`\\Delta t` is the lag-time of the
    autocorrelation function, :math:`\\mathbb{E}` is the expectation operator,
    and :math:`\\bar{f}` is the mean of the :math:`f`. The autocorrelation
    function is defined by

    .. math::

        \\tau(\\Delta t) = \\sigma^{-2} \\kappa(\\Delta t),

    where :math:`\\sigma^2 = \\kappa(0)` is the variance of the ECG signal.

    **Covariance Matrix:**

    The covariance matrix :math:`\\boldsymbol{\\Sigma}` is defined by its
    :math:`i,j` components as

    .. math::

        \\Sigma_{ij} = \\kappa(\\vert i - j \\vert f_s \\nu)

    where :math:`f_s = 360` Hz is the sampling frequency of the ECG signal and
    :math:`\\nu` is the sampling of the autocorrelation function that is
    specified by ``sample`` argument.

    The total time span of the correlation matrix is

    .. math::

        \\Delta t = n \\frac{\\nu}{f_s},

    where :math:`n` is the size of the matrix.

    For instance, for the matrix size ``2**9`` and sampling ``2``, the
    matrix spans 2.84 seconds.

    **Correlation versus Covariance:**

    If `cor` is `True`, the correlation matrix is instead computed and plotted.
    The covariance matrix :math:`\\boldsymbol{\\Sigma}` is a scalar multiple of
    the correlation matrix :math:`\\mathbf{K}` by

    .. math::

        \\mathbf{K} = \\sigma^{-2} \\boldsymbol{\\Sigma}.

    Examples
    --------

    .. code-block:: python

        >>> from detit.datasets import covariance_matrix
        >>> A = covariance_matrix(size=2**9, cor=True, plot=True)

    .. image:: ../_static/images/plots/covariance.png
        :align: center
        :class: custom-dark

    """

    # Load electrocardiogram signal
    tie, signal = electrocardiogram(start=ecg_start, end=ecg_end,
                                    bw_window=0.5, freq_cut=45, plot=False)

    # Signal
    signal = signal - numpy.mean(signal)
    n = signal.size

    # Compute auto-covariance function
    if ecg_wrap:
        # Assume ECG signal is wrapped
        acf = scipy.ndimage.convolve1d(signal, signal[::-1], mode='wrap') / n
        add, half = 0, 2
    else:
        # No wrapping
        acf = scipy.signal.fftconvolve(signal, signal[::-1], mode='full') / n
        add, half = 1, 1

    # Lag time
    fs = 360  # in Hz
    lag_time = numpy.arange(-n//half+add, n//half) / fs

    # Select half of the ACF function
    lag_time = lag_time[n//half+add:]
    acf = acf[n//half+add:]

    # Sample ACF and lag time
    lag_time = lag_time[:size*sample:sample]
    acf = acf[:size*sample:sample]

    # Toeplitz matrix to form covariance matrix from autocorrelation function
    matrix = scipy.linalg.toeplitz(acf, acf)

    # Change covariance to correlation
    var = numpy.var(signal)
    if cor:
        # Convert covariance to correlation
        matrix = matrix / var

        # Convert auto-covariance to auto-correlation
        acf = acf / var

    # Plot
    if plot is not False:
        _plot(signal, var, lag_time, acf, matrix, cor, size, sample,
              filename=plot, verbose=verbose)

    return matrix


# ====
# Plot
# ====

@matplotlib.rc_context(get_theme(font_scale=1))
def _plot(
        signal,
        var,
        lag_time,
        acf,
        matrix,
        cor,
        size,
        sample,
        filename=None,
        verbose=False):
    """
    Plots the ECG signal.
    """

    # Sample time from the lag time of the autocorrelation

    # Eigenvalues of the autocorrelation function
    eig = scipy.linalg.eigh(matrix, eigvals_only=True)[::-1]

    # fig, ax = plt.subplots(ncols=2, figsize=(7.4, 3.6))
    fig, ax = plt.subplots(ncols=3, figsize=(9.8, 3), layout='constrained')

    # Settings
    title_fontsize = 11
    label_fontsize = 10
    tick_fontsize = 10

    # Limit of the colormap plot
    if cor:
        limit = 1
    else:
        limit = numpy.around(var, decimals=2)

    # Plot autocorrelation function
    ax[0].plot(lag_time, acf, color='black')
    ax[0].set_xlim([lag_time[0], lag_time[-1]])
    ax[0].set_ylim(top=limit)
    ax[0].set_xlabel(r'$\Delta t$ (sec)', fontsize=label_fontsize)
    ax[0].set_ylabel(r'$\tau(\Delta t)$', fontsize=label_fontsize)
    if cor:
        title = '(b) Autocorrelation'
    else:
        title = '(b) Autocovariance'
    ax[0].set_title(title, fontsize=title_fontsize)
    ax[0].axhline(0, color='grey', linewidth=0.5)
    ax[0].tick_params(axis='both', labelsize=tick_fontsize)
    ax[0].set_yticks([0, 0.5*limit, limit])

    # Plot correlation matrix
    cmap = plt.cm.seismic
    mat = ax[1].matshow(matrix, cmap=cmap,
                        extent=[0, lag_time[-1], lag_time[-1], 0],
                        aspect=1, vmin=-limit, vmax=limit)
    cb = fig.colorbar(mat, ax=ax[1], ticks=numpy.array([-limit, 0, limit]),
                      orientation='vertical', pad=0.03, aspect=20)
    cb.solids.set_rasterized(True)
    cb.ax.tick_params(labelsize=tick_fontsize)
    ax[1].xaxis.set_label_position('top')
    ax[1].set_xlabel(r'$\Delta t$ (sec)', fontsize=label_fontsize)
    ax[1].set_ylabel(r'$\Delta t$ (sec)', fontsize=label_fontsize)
    ax[1].tick_params(axis='x', which='both', bottom=False, top=True,
                      labelbottom=False)
    if cor:
        title = '(c) Correlation Matrix'
    else:
        title = '(c) Covariance Matrix'
    ax[1].set_title(title, y=-0.13, fontsize=title_fontsize)
    ax[1].tick_params(axis='both', labelsize=tick_fontsize)

    # Plot eigenvalues of correlation matrix
    ax[2].loglog(numpy.arange(1, 1+eig.size), eig, color='black')
    ax[2].set_xlim([1, eig.size+1])
    ax[2].set_xlabel(r'$i$', fontsize=label_fontsize)
    ax[2].set_ylabel(r'$\lambda_i$', fontsize=label_fontsize)
    if cor:
        title = '(d) Eigenvalues of Correlation'
    else:
        title = '(d) Eigenvalues of Covariance'
    ax[2].set_title(title, fontsize=title_fontsize)

    # Find x limit of the plot in base 2
    base_2 = int(numpy.log2(size) + 0.5)
    x_range = 2**numpy.arange(0, base_2+1)
    ax[2].set_xticks(x_range)
    ax[2].set_xticklabels([r'$2^{%d}$' % y for y in numpy.arange(0, base_2+1)])
    ax[2].yaxis.set_major_locator(matplotlib.ticker.LogLocator(numticks=4))
    ax[2].tick_params(axis='x', which='minor', length=0)
    ax[2].tick_params(axis='y', which='minor', length=0)
    ax[2].tick_params(axis='both', labelsize=tick_fontsize)
    ax[2].set_xlim([1, size+1])
    ax[2].yaxis.tick_right()
    ax[2].yaxis.set_label_position('right')
    ax[2].grid(which='major')

    # Save plot
    show_or_save_plot(plt, filename=filename, default_filename='covariance',
                      transparent_background=True, bbox_extra_artists=None,
                      verbose=verbose)
