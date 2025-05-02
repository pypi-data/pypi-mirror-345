"""
This module contains the standard library firing rate analysis.
"""

import numpy as np
from antelop import antelop_analysis
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


@antelop_analysis
class SpikeCountRate:
    """
    Calculate the spike count rate of a neuron.
    This is the number of spikes divided by the duration of the recording.
    """

    name = "spike_count_rate"
    query = "SpikeTrain"
    returns = {"firing_rate": float}

    def run(key):
        spiketrain = (SpikeTrain & key).fetch1("spiketrain")
        spike_count_rate = spiketrain.shape[0] / spiketrain[-1]

        return spike_count_rate


@antelop_analysis
class FiringRate:
    """
    Smooth the spike train with a kernel.

    Arguments:
    kernel (np.ndarray[2,n]): The kernel to convolve the spike train with. Should consist of values and timestamps.
    sample_rate (float): The sample rate of the spike train.
    """

    name = "firing_rate"
    query = "SpikeTrain"
    returns = {"firing_rate": np.ndarray}
    args = {"kernel": np.ndarray, "sample_rate": float}
    hidden = True

    def run(key, kernel, sample_rate):
        # fetch spiketrain
        spiketrain = (SpikeTrain & key).fetch1("spiketrain")

        # interpolate the kernel to the sample rate
        kernel_func = interp1d(
            kernel[1, :], kernel[0, :], fill_value=0, bounds_error=False
        )
        kernel_interpolated = kernel_func(
            np.arange(kernel[1, 0], kernel[1, -1], 1 / sample_rate)
        )

        # timestamps of output
        timestamps = np.arange(0, spiketrain[-1], 1 / sample_rate)

        # bin the spike train
        spiketrain_binned = np.zeros_like(timestamps, dtype=int)
        bin_edges = timestamps - 1 / (2 * sample_rate)
        spiketrain_binned[np.digitize(spiketrain, bin_edges) - 1] = 1

        # convolve the spike train with the kernel
        firing_rate = np.convolve(spiketrain_binned, kernel_interpolated, mode="same")

        # return firing rate and timestamps
        firing_rate = np.vstack((firing_rate, timestamps))

        return firing_rate


@antelop_analysis
class GaussianSmoothing:
    """
    Smooth the spike train with a Gaussian kernel.

    Arguments:
    sigma (float): The standard deviation of the Gaussian kernel in seconds.
    sample_rate (float): The sample rate of the output firing rate
    truncate (float): The number of standard deviations to include in the kernel.
    """

    name = "gaussian_smoothing"
    query = "SpikeTrain"
    returns = {"smoothed_spiketrain": np.ndarray, "timestamps": np.ndarray}
    args = {"sigma": float, "sample_rate": float, "truncate": float}
    calls = ["firing_rate"]

    def run(key, sigma=0.1, sample_rate=100, truncate=3):
        # compute the kernel
        kernel_timestamps = np.arange(
            -truncate * sigma, truncate * sigma, 1 / sample_rate
        )
        kernel_values = np.exp(-(kernel_timestamps**2) / (2 * sigma**2))
        kernel_values *= sample_rate / np.sum(kernel_values)
        kernel = np.vstack((kernel_values, kernel_timestamps))

        # compute the firing rate
        smoothed_spiketrain = firing_rate(key, kernel, sample_rate)

        return (
            smoothed_spiketrain["firing_rate"][0, :],
            smoothed_spiketrain["firing_rate"][1, :],
        )


@antelop_analysis
class RectangularSmoothing:
    """
    Smooth the spike train with a rectangular kernel.

    Arguments:
    width (float): The width of the kernel in seconds.
    sample_rate (float): The sample rate of the output firing rate.
    """

    name = "rectangular_smoothing"
    query = "SpikeTrain"
    returns = {"smoothed_spiketrain": np.ndarray, "timestamps": np.ndarray}
    args = {"width": float, "sample_rate": float}
    calls = ["firing_rate"]

    def run(key, width=0.1, sample_rate=1000):
        # compute the kernel
        kernel_timestamps = np.arange(-width / 2, width / 2, 1 / sample_rate)
        kernel_values = np.ones_like(kernel_timestamps)
        kernel_values *= sample_rate / np.sum(kernel_values)
        kernel = np.vstack((kernel_values, kernel_timestamps))

        # compute the firing rate
        smoothed_spiketrain = firing_rate(key, kernel, sample_rate)

        return (
            smoothed_spiketrain["firing_rate"][0, :],
            smoothed_spiketrain["firing_rate"][1, :],
        )


@antelop_analysis
class ExponentialSmoothing:
    """
    Smooth the spike train with a exponential kernel.

    Arguments:
    tau (float): The time parameter of the kernel in seconds.
    sample_rate (float): The sample rate of the output firing rate.
    truncate (float): The number of time constants to include in the kernel.
    """

    name = "exponential_smoothing"
    query = "SpikeTrain"
    returns = {"smoothed_spiketrain": np.ndarray, "timestamps": np.ndarray}
    args = {"tau": float, "sample_rate": float, "truncate": float}
    calls = ["firing_rate"]

    def run(key, tau=0.1, sample_rate=1000, truncate=5):
        # compute the kernel
        kernel_timestamps = np.arange(0, tau * truncate, 1 / sample_rate)
        kernel_values = np.exp(-kernel_timestamps / tau)
        kernel_values *= sample_rate / np.sum(kernel_values)
        kernel = np.vstack((kernel_values, kernel_timestamps))

        # compute the firing rate
        smoothed_spiketrain = firing_rate(key, kernel, sample_rate)

        return (
            smoothed_spiketrain["firing_rate"][0, :],
            smoothed_spiketrain["firing_rate"][1, :],
        )


@antelop_analysis
class PlotSmoothed:
    """
    Smooth the spike train with a Gaussian kernel and plot.

    Arguments:
    sigma (float): The standard deviation of the Gaussian kernel in seconds.
    sample_rate (float): The sample rate of the output firing rate
    window_start (float): The start of the window to plot in seconds.
    window_end (float): The end of the window to plot in seconds (default is -1 the end of the recording).
    width (float): The width parameter of the kernel.
    kernel (str): The type of kernel to use ('gaussian', 'rectangular', 'exponential').
    """

    name = "plot_firing_rate"
    query = "SpikeTrain"
    returns = {"plot": plt.Figure}
    args = {
        "sample_rate": int,
        "window_start": float,
        "window_end": float,
        "width": float,
        "kernel": ["gaussian", "rectangular", "exponential"],
    }
    calls = ["gaussian_smoothing", "rectangular_smoothing", "exponential_smoothing"]

    def run(
        key,
        window_start=0,
        window_end=-1,
        width=0.1,
        sample_rate=1000,
        kernel="gaussian",
    ):
        # fetch spiketrain
        spiketrain = (SpikeTrain & key).fetch1("spiketrain")

        # compute the smoothed spiketrain
        if kernel == "gaussian":
            result = gaussian_smoothing(key, width, sample_rate)
            smoothed_spiketrain = result["smoothed_spiketrain"]
            timestamps = result["timestamps"]

        elif kernel == "rectangular":
            result = rectangular_smoothing(key, width, sample_rate)
            smoothed_spiketrain = result["smoothed_spiketrain"]
            timestamps = result["timestamps"]

        elif kernel == "exponential":
            result = exponential_smoothing(key, width, sample_rate)
            smoothed_spiketrain = result["smoothed_spiketrain"]
            timestamps = result["timestamps"]

        # crop to within window
        if window_end == -1:
            window_end = timestamps[-1]
        start_idx = np.argmax(timestamps >= window_start)
        end_idx = np.argmax(timestamps >= window_end)
        smoothed_spiketrain = smoothed_spiketrain[start_idx:end_idx]
        timestamps = timestamps[start_idx:end_idx]
        spiketrain = spiketrain[
            (spiketrain >= window_start) & (spiketrain <= window_end)
        ]

        # plot spiketrain and smoothed spiketrain
        fig, ax = plt.subplots()

        ax.plot(timestamps, smoothed_spiketrain, label="Firing rate")
        ax.plot(spiketrain, np.zeros_like(spiketrain), "|", label="Spikes")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Firing rate (Hz)")
        ax.set_title("Firing rate of neuron")

        return fig
