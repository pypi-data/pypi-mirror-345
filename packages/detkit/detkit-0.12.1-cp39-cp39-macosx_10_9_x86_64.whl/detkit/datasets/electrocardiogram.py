# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import numpy
import scipy
import scipy.signal
from .._utilities.plot_utilities import plt, matplotlib, get_theme, \
        show_or_save_plot
from pkgutil import iter_modules

__all__ = ['electrocardiogram']


# ========
# load ecg
# ========

def _load_ecg():
    """
    Load electrocardiogram signal.
    """

    ecg = None
    found = False

    # Search through the sub modules of scipy package
    for submodule in iter_modules(scipy.__path__):

        if submodule.name == 'datasets':
            # In new scipy versions
            from scipy.datasets import electrocardiogram
            found = True
            break
        elif submodule.name == 'misc':
            # In older scipy versions
            from scipy.misc import electrocardiogram
            found = True
            break

    if not found:
        raise RuntimeError('Cannot find electrocardiogram function in scipy ' +
                           'package.')
    else:
        ecg = electrocardiogram()

    return ecg


# =================
# Electrocardiogram
# =================

def electrocardiogram(
        start=0.0,
        end=10.0,
        bw_window=0.5,
        freq_cut=45,
        plot=False,
        plot_bw=False,
        verbose=False):
    """
    Load an electrocardiogram signal as an example for a 1D signal.

    Parameters
    ----------

    start : float, default=0.0
        Start of the signal in seconds.

    end : float, default=10.0
        End of the signal in seconds.

    bw_window : default=1.0
        Length of moving average filter (in seconds) to remove baseline wander
        (bw). If zero, BW is not removed. If set to zero, baseline is not
        removed.

    freq_cut : float, default=45
        Frequencies (in Hz) above this limit will be cut by low-pass filter. If
        `numpy.inf`, no filtering is performed.

    plot : bool or str, default=False
        If `True`, the ECG signal and its autocorrelation function, the
        covariance (or correlation) matrix and its eigenvalues are plotted.
        If ``plot`` is a string, the plot is not shown, rather saved with a
        filename as the given string. If the filename does not contain file
        extension, the plot is saved in both ``svg`` and ``pdf`` formats. If
        the filename does not have directory path, the plot is saved in the
        current directory.

    plot_bw : bool, default=False
        If `True`, plots the baseline wander and the original signal along with
        the filtered signal. This option is effective only if ``plot`` is not
        `False`.

    verbose : bool, default=False
        if `True`, the saved plot filename is printed.

    Returns
    -------

        ecg : numpy.array
            ECG signal.

        time : numpy.array
            Time axis corresponding to the ECG signal.

    See Also
    --------

    detkit.covariance_matrix

    Notes
    -----

    The signal is sampled at 360 Hz.

    Two filters are applied on the original ECG signal:

    * Removing baseline wander (BW) by moving average filter. BW is the trend
      of the signal caused by respiration and movements of the person. Usually,
      BW is on the frequency range of 0.1 HZ to 0.5 Hz. Unfortunately, a
      high-pass filter above 0.5 Hz does not cleanly remove the BW. The best
      approach so far was a moving average filter with the kernel duration of
      about 1 seconds.

    * Removing noise by low-pass filter with critical frequency of 45 Hz.
      This also removes the 60 Hz power-line frequency that interferes with the
      measurement device.

    References
    ----------

    .. [1] Moody GB, Mark RG. The impact of the MIT-BIH Arrhythmia Database.
           IEEE Eng in Med and Biol 20(3):45-50 (May-June 2001).
           (PMID: 11446209); DOI: `10.13026/C2F305
           <https://doi.org/10.13026/C2F305>`__

    .. [2] Goldberger AL, Amaral LAN, Glass L, Hausdorff JM, Ivanov PCh, Mark
           RG, Mietus JE, Moody GB, Peng C-K, Stanley HE. PhysioBank,
           PhysioToolkit, and PhysioNet: Components of a New Research Resource
           for Complex Physiologic Signals. Circulation 101(23):e215-e220;
           DOI: `10.1161/01.CIR.101.23.e215
           <https://doi.org/10.1161/01.CIR.101.23.e215>`__

    Examples
    --------

    .. code-block:: python

        >>> from detkit.datasets import electrocardiogram
        >>> time, ecg = electrocardiogram(plot=True, plot_bw=True)

    .. image:: ../_static/images/plots/electrocardiogram.png
        :align: center
        :class: custom-dark
    """

    # Read dataset
    ecg = _load_ecg()

    # Sampling frequency in Hz for this dataset
    fs = 360

    # Time for ecg array based on sampling frequency
    time = numpy.arange(ecg.size) / fs

    # Remove baseline wander by moving average filter
    if bw_window > 0.0:
        ecg_filtered, ecg_bw = _remove_baseline_wander(ecg, fs, bw_window)
    else:
        ecg_filtered = ecg
        ecg_bw = numpy.zeros_like(ecg)

    # Remove high frequencies from ECG signal
    if not numpy.isinf(freq_cut):
        filter_order = 5
        ecg_filtered = _remove_noise(ecg_filtered, fs, freq_cut, filter_order)

    # Cut time
    start_index = int(start*fs + 0.5)
    end_index = int(end*fs + 0.5)
    time = time[start_index:end_index + 1]
    ecg = ecg[start_index:end_index + 1]
    ecg_bw = ecg_bw[start_index:end_index + 1]
    ecg_filtered = ecg_filtered[start_index:end_index + 1]

    # Plot
    if plot is not False:
        _plot(time, ecg, ecg_bw, ecg_filtered, plot_bw=plot_bw, filename=plot,
              verbose=verbose)

    return time, ecg_filtered


# ======================
# Remove Baseline Wander
# ======================

def _remove_baseline_wander(
        signal,
        fs,
        bw_window=1):
    """
    Using a moving average filter to remove baseline wander of the ECG signal.

    Parameters
    ----------

    signal : numpy.array
        The ECG signal.

    fs : float
        Sampling frequency of the signal

    window : float, default=1.0
        The duration of the moving average window in seconds.

    Returns
    -------

    signal_filtered : numpy.array
        Signal with baseline removed.

    signal_bw : numpy.array
        Baseline wander of the signal
    """

    # Length of window from seconds to index
    kernel_window = int(bw_window*fs)

    # Moving average kernel
    kernel = numpy.ones((kernel_window,)) / kernel_window

    # Baseline wander
    signal_bw = numpy.convolve(signal, kernel, mode='same')

    signal_filtered = signal - signal_bw

    return signal_filtered, signal_bw


# ============
# Remove noise
# ============

def _remove_noise(
        signal,
        fs,
        freq_cut=45,
        filter_order=5):
    """
    Remove high frequency noise from ECG signal.

    This function uses Butter filter to design a low-pass FIR filter.

    Parameters
    ----------

    signal : numpy.array
        ECG signal

    fs : float
        Sampling frequency of the signal.

    freq_cut : float, default=45
        Frequencies (in Hz) above this limit will be cut.

    order : int, default=5
        Order of the filter. Higher number means stronger filter.

    Returns
    -------

    signal_filtered : numpy.array
        Signal with baseline removed.
    """

    # Nyquist frequency is half of sampling frequency
    nyq = 0.5 * fs

    # Ratio of cut frequency
    cut = freq_cut / nyq

    # Design filter
    sos = scipy.signal.butter(filter_order, cut, 'lowpass', output='sos')

    # Apply filter
    signal_filtered = scipy.signal.sosfilt(sos, signal)

    return signal_filtered


# ====
# plot
# ====

@matplotlib.rc_context(get_theme(font_scale=1))
def _plot(
        time,
        ecg,
        ecg_bw,
        ecg_filtered,
        plot_bw=False,
        filename=None,
        verbose=False):
    """
    Plots the ECG signal.

    Parameters
    ----------
    """

    # Settings
    title_fontsize = 11
    label_fontsize = 10
    tick_fontsize = 10

    # Plot baseline wander or not
    if plot_bw:
        fig, (ax_bw, ax_filt) = plt.subplots(nrows=2, figsize=(9.8, 3.4))
    else:
        fig, ax_filt = plt.subplots(nrows=1, figsize=(9.8, 2))

    # Plot baseline wander and the original signal
    if plot_bw:
        ax_bw.plot(time, ecg, color='black', label='Original')
        ax_bw.plot(time, ecg_bw, color='orange', label='Baseline wander')
        ax_bw.set_ylabel("ECG (mV)", fontsize=label_fontsize)
        ax_bw.set_xlim([time[0], time[-1]])
        ax_bw.tick_params(axis='both', labelsize=tick_fontsize)
        lg_bw = ax_bw.legend(fontsize='x-small')
        lg_bw.get_frame().set_alpha(None)
        lg_bw.get_frame().set_facecolor((0, 0, 0, 0.0))

        # Remove bottom axis
        ax_bw.tick_params(axis='x', which='both', bottom=False, top=False,
                          labelbottom=False)

    # Plot filtered signal
    ax_filt.plot(time, ecg_filtered, color='black', label='Filtered')
    ax_filt.set_xlabel(r"$t$ (sec)", fontsize=label_fontsize)
    ax_filt.set_ylabel("ECG (mV)", fontsize=label_fontsize)
    ax_filt.set_xlim([time[0], time[-1]])
    ax_filt.tick_params(axis='both', labelsize=tick_fontsize)

    if plot_bw:
        lg_filt = ax_filt.legend(fontsize='x-small')
        lg_filt.get_frame().set_alpha(None)
        lg_filt.get_frame().set_facecolor((0, 0, 0, 0.0))

    if plot_bw:
        ax_bw.set_title('(a) Electrocardiogram', fontsize=title_fontsize)
    else:
        ax_filt.set_title('(a) Electrocardiogram', fontsize=title_fontsize)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0)

    # Show or save plot
    show_or_save_plot(plt, filename=filename,
                      default_filename='electrocardiogram',
                      transparent_background=True,
                      bbox_extra_artists=None, verbose=verbose)
