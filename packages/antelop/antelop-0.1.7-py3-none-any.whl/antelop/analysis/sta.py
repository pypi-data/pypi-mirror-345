"""
This module contains the standard library spike-triggered average analysis functions.
"""

import numpy as np
from antelop import antelop_analysis
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


@antelop_analysis
class AnalogSta:
    """
    The spike-triggered average for an analog event.
    """

    name = "analog_sta"
    query = ["SpikeTrain", "AnalogEvents"]
    returns = {"Spike-triggered average": np.ndarray, "Timestamps (s)": np.ndarray}
    args = {"window_size": float, "sample_rate": float}

    def run(key, window_size=1, sample_rate=1000):
        spiketrain = (SpikeTrain & key).fetch1("spiketrain")
        data, timestamps = (AnalogEvents.proj("data", "timestamps") & key).fetch1(
            "data", "timestamps"
        )

        # interpolate the event data
        event_func = interp1d(timestamps, data, fill_value=0, bounds_error=False)

        # create window timestamps
        step = 1 / sample_rate
        start_time = -(window_size // step) * step
        window_timestamps = np.arange(start_time, 0, step)

        # create matrix of window times for each spike - shape (n_spikes, window_samples)
        sta_times = spiketrain[:, None] + window_timestamps

        # get the event values in each window
        sta_values = event_func(sta_times)

        # average over all spikes
        sta = np.mean(sta_values, axis=0)

        return sta, window_timestamps


@antelop_analysis
class PlotAnalogSta:
    """
    Plot the spike-triggered average for an analog event.
    """

    name = "plot_analog_sta"
    query = ["SpikeTrain", "AnalogEvents"]
    returns = {"Spike-triggered average": plt.Figure}
    args = {"window_size": float, "sample_rate": float}

    def run(key, window_size=1, sample_rate=1000):
        unit, name = (AnalogEvents.proj("unit", "analogevents_name") & key).fetch1(
            "unit", "analogevents_name"
        )

        result = analog_sta(key, window_size, sample_rate)
        sta, timestamps = result["Spike-triggered average"], result["Timestamps (s)"]

        fig, ax = plt.subplots()

        ax.plot(timestamps, sta)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(f"{name} ({unit})")
        ax.set_title("Spike-triggered average")

        return fig


@antelop_analysis
class DigitalSta:
    """
    The spike-triggered average for a digital event.
    """

    name = "digital_sta"
    query = ["SpikeTrain", "DigitalEvents"]
    returns = {"Spike-triggered average": np.ndarray, "Timestamps (s)": np.ndarray}
    args = {"window_size": float, "sample_rate": float}

    def run(key, window_size=1, sample_rate=1000):
        spiketrain = (SpikeTrain & key).fetch1("spiketrain")
        data, timestamps = (DigitalEvents.proj("data", "timestamps") & key).fetch1(
            "data", "timestamps"
        )

        if spiketrain.size > 0:
            if timestamps.size == 0:
                start_time = spiketrain[0] - window_size
                end_time = spiketrain[-1]
            else:
                start_time = min(timestamps[0], spiketrain[0] - window_size)
                end_time = max(timestamps[-1], spiketrain[-1])

            global_timestamps = np.arange(start_time, end_time, 1 / sample_rate)

            # get the indices of each spike in the global timestamps array
            spiketrain_indices = np.digitize(spiketrain, global_timestamps) - 1

            # make event data match global timestamps, filled with zeros
            event_indices = np.digitize(timestamps, global_timestamps) - 1
            event_data = np.zeros_like(global_timestamps)
            event_data[event_indices] = data

            # create window array - shape (n_spikes, window_samples)
            window_indices = np.arange(-window_size * sample_rate + 1, 0, 1)
            window_array = spiketrain_indices[:, None] + window_indices
            window_timestamps = window_indices / sample_rate

            # get the event values in each window
            sta_values = event_data[window_array]

            # average over all spikes
            sta = np.mean(sta_values, axis=0)

        else:
            sta = np.array([])
            window_timestamps = np.array([])

        return sta, window_timestamps


@antelop_analysis
class PlotDigitalSta:
    """
    Plot the spike-triggered average for an analog event.
    """

    name = "plot_digital_sta"
    query = ["SpikeTrain", "DigitalEvents"]
    returns = {"Spike-triggered average": plt.Figure}
    args = {"window_size": float, "sample_rate": float}

    def run(key, window_size=1, sample_rate=1000):
        unit, name = (DigitalEvents.proj("unit", "digitalevents_name") & key).fetch1(
            "unit", "digitalevents_name"
        )

        result = digital_sta(key, window_size, sample_rate)
        sta, timestamps = result["Spike-triggered average"], result["Timestamps (s)"]

        fig, ax = plt.subplots()

        ax.plot(timestamps, sta)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(f"{name} ({unit})")
        ax.set_title("Spike-triggered average")

        return fig


@antelop_analysis
class IntervalSta:
    """
    The spike-triggered average for a digital event.
    """

    name = "interval_sta"
    query = ["SpikeTrain", "IntervalEvents"]
    returns = {"Spike-triggered average": np.ndarray, "Timestamps (s)": np.ndarray}
    args = {"window_size": float, "sample_rate": float}

    def run(key, window_size=1, sample_rate=1000):
        spiketrain = (SpikeTrain & key).fetch1("spiketrain")
        data, timestamps = (IntervalEvents.proj("data", "timestamps") & key).fetch1(
            "data", "timestamps"
        )

        # delete this, just since some test data corrupted
        if np.any(data == 0):
            return np.array([]), np.array([])

        if timestamps.size == 0:
            window_timestamps = np.arange(-window_size, 0, 1 / sample_rate)
            sta = np.zeros_like(window_timestamps)

        else:
            start_time = min(timestamps[0], spiketrain[0] - window_size)
            end_time = max(timestamps[-1], spiketrain[-1])

            global_timestamps = np.arange(start_time, end_time, 1 / sample_rate)

            # get the indices of each spike in the global timestamps array
            spiketrain_indices = np.digitize(spiketrain, global_timestamps) - 1

            # make event data match global timestamps
            event_indices = np.digitize(global_timestamps, timestamps) - 1
            event_data = data[event_indices]
            event_data[event_data == -1] = 0
            event_data[event_indices == -1] = 0

            # create window array - shape (n_spikes, window_samples)
            window_indices = np.arange(-window_size * sample_rate + 1, 0, 1)
            window_array = spiketrain_indices[:, None] + window_indices
            window_timestamps = window_indices / sample_rate

            # get the event values in each window
            sta_values = event_data[window_array]

            # average over all spikes
            sta = np.mean(sta_values, axis=0)

        return sta, window_timestamps


@antelop_analysis
class PlotIntervalSta:
    """
    Plot the spike-triggered average for an interval event.
    """

    name = "plot_interval_sta"
    query = ["SpikeTrain", "IntervalEvents"]
    returns = {"Spike-triggered average": plt.Figure}
    args = {"window_size": float, "sample_rate": float}

    def run(key, window_size=1, sample_rate=1000):
        name = (IntervalEvents.proj("intervalevents_name") & key).fetch1(
            "intervalevents_name"
        )

        result = interval_sta(key, window_size, sample_rate)
        sta, timestamps = result["Spike-triggered average"], result["Timestamps (s)"]

        fig, ax = plt.subplots()

        ax.plot(timestamps, sta)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(f"{name}")
        ax.set_title("Spike-triggered average")

        return fig
