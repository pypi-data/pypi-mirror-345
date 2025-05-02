"""
This module contains the standard library isi ratio analysis functions.
"""

import numpy as np
import matplotlib.pyplot as plt
from antelop import antelop_analysis


@antelop_analysis
class IsiPlot:
    """
    Plot the interspike interval histogram of a spike train.

    Arguments:
    bin_size (float): The size of the bins in the histogram in seconds.
    window (float): The length of the window to plot in seconds.
    """

    name = "isi_plot"
    query = "SpikeTrain"
    returns = {"IsiPlot": plt.Figure}

    def run(key, bin_size, window):
        spiketrain = (SpikeTrain & key).fetch1("spiketrain")

        # calculate intervals
        isi = np.diff(spiketrain)

        # plot histogram
        fig, ax = plt.subplots()
        ax.hist(isi, bins=np.arange(0, window, bin_size), density=True)
        ax.set_xlabel("ISI (s)")
        ax.set_ylabel("Probability density")
        ax.set_title("ISI histogram")

        return fig


@antelop_analysis
class AutoCorrelogram:
    """
    Plot the interspike interval histogram of a spike train.

    Arguments:
    sample_rate (float): The sample rate of the autocorrelogram in Hz.
    """

    name = "auto_correlogram"
    query = "SpikeTrain"
    returns = {"IsiPlot": plt.Figure}
    args = {"sample_rate": float}

    def run(key, sample_rate=1000, window=1):
        spiketrain = (SpikeTrain & key).fetch1("spiketrain")

        if spiketrain.size == 0:
            return plt.figure()

        start_time, end_time = 0, spiketrain[-1] - spiketrain[0]

        # calculate intervals between all spikes
        diffs = (spiketrain[:, None] - spiketrain[None, :]).flatten()

        # accumulate into a histogram
        hist, times = np.histogram(
            diffs, bins=np.arange(start_time, end_time, 1 / sample_rate)
        )
        times = (times[:-1] + times[1:]) / 2
        hist = hist[: window * sample_rate]
        times = times[: window * sample_rate]

        # remove mean and normalize
        n = spiketrain.size
        hist = hist.astype(float)
        hist -= n**2 / (end_time * sample_rate)
        hist /= end_time
        hist *= sample_rate

        # plot autocorrelogram
        fig, ax = plt.subplots()
        ax.hist(hist, bins=times)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Auto-correlation (Hz^2)")

        return fig
