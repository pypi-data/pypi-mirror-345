Analysis
========


Firing_rate
-----------

This module contains the standard library firing rate analysis.

.. class:: exponential_smoothing
   :noindex:

   Smooth the spike train with a exponential kernel.
   
   
   
   **Arguments**:
   
   tau (float): The time parameter of the kernel in seconds.
   
   sample_rate (float): The sample rate of the output firing rate.
   
   truncate (float): The number of time constants to include in the kernel.


   **Query**: SpikeTrain

   **Returns**: {'smoothed_spiketrain': <class 'numpy.ndarray'>, 'timestamps': <class 'numpy.ndarray'>}

   **Calls**: ['firing_rate']

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: firing_rate
   :noindex:

   Smooth the spike train with a kernel.
   
   
   
   **Arguments**:
   
   kernel (np.ndarray[2,n]): The kernel to convolve the spike train with. Should consist of values and timestamps.
   
   sample_rate (float): The sample rate of the spike train.


   **Query**: SpikeTrain

   **Returns**: {'firing_rate': <class 'numpy.ndarray'>}

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: gaussian_smoothing
   :noindex:

   Smooth the spike train with a Gaussian kernel.
   
   
   
   **Arguments**:
   
   sigma (float): The standard deviation of the Gaussian kernel in seconds.
   
   sample_rate (float): The sample rate of the output firing rate
   
   truncate (float): The number of standard deviations to include in the kernel.


   **Query**: SpikeTrain

   **Returns**: {'smoothed_spiketrain': <class 'numpy.ndarray'>, 'timestamps': <class 'numpy.ndarray'>}

   **Calls**: ['firing_rate']

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: plot_firing_rate
   :noindex:

   Smooth the spike train with a Gaussian kernel and plot.
   
   
   
   **Arguments**:
   
   sigma (float): The standard deviation of the Gaussian kernel in seconds.
   
   sample_rate (float): The sample rate of the output firing rate
   
   window_start (float): The start of the window to plot in seconds.
   
   window_end (float): The end of the window to plot in seconds (default is -1 the end of the recording).
   
   width (float): The width parameter of the kernel.
   
   kernel (str): The type of kernel to use ('gaussian', 'rectangular', 'exponential').


   **Query**: SpikeTrain

   **Returns**: {'plot': <class 'matplotlib.figure.Figure'>}

   **Calls**: ['gaussian_smoothing', 'rectangular_smoothing', 'exponential_smoothing']

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: rectangular_smoothing
   :noindex:

   Smooth the spike train with a rectangular kernel.
   
   
   
   **Arguments**:
   
   width (float): The width of the kernel in seconds.
   
   sample_rate (float): The sample rate of the output firing rate.


   **Query**: SpikeTrain

   **Returns**: {'smoothed_spiketrain': <class 'numpy.ndarray'>, 'timestamps': <class 'numpy.ndarray'>}

   **Calls**: ['firing_rate']

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: spike_count_rate
   :noindex:

   Calculate the spike count rate of a neuron.
   
   This is the number of spikes divided by the duration of the recording.


   **Query**: SpikeTrain

   **Returns**: {'firing_rate': <class 'float'>}

   .. dropdown:: See Code

      .. code-block:: python

             def run(key):
                 spiketrain = (SpikeTrain & key).fetch1("spiketrain")
                 spike_count_rate = spiketrain.shape[0] / spiketrain[-1]
         
                 return spike_count_rate



Hello_world
-----------

.. class:: count_experiments
   :noindex:

   This is a slightly more complex example showing how we can aggregate over another table and rename variables within the function.
   
   It's worth noting that when you aggregate, the argument passed to the function will always be a list.


   **Query**: Experimenter

   **Returns**: {'count': <class 'int'>}

   .. dropdown:: See Code

      .. code-block:: python

             def run(key):
                 length = len(Experiment & key)
                 return length


.. class:: example_figure
   :noindex:

   Example of a function that returns a matplotlib figure.


   **Query**: Experimenter

   **Returns**: {'figure': <class 'matplotlib.figure.Figure'>}

   .. dropdown:: See Code

      .. code-block:: python

             def run(key, size='medium'):
                 full_name = (Experimenter & key).fetch1("full_name")
                 fig, ax = plt.subplots()
                 ax.text(0.5, 0.5, f"Hello\n{full_name}!", size=size, ha="center")
                 ax.axis("off")
                 return fig


.. class:: first_experiment_name
   :noindex:

   This example shows how we can use a restriction to filter the data within the function.
   
   
   
   Restrictions can of course be passed when running the function, but are useful at this level
   
   to define when the function doesn't apply to certain attributes, or more commonly, to define
   
   different subsets of aggregated attributes as different inputs to the function.
   
   
   
   Note, you should always handle the case where the function input is an empty list.


   **Query**: Experimenter

   **Returns**: {'response': <class 'str'>}

   .. dropdown:: See Code

      .. code-block:: python

             def run(key):
                 experiment_name = (Experiment & key).fetch("experiment_name", limit=1)
                 if len(experiment_name) == 0:
                     return "You have not run any experiments."
                 elif len(experiment_name) == 1:
                     return f"The first experiment you ran was called {experiment_name[0]}."
                 else:
                     raise ValueError("This error should never get raised.")


.. class:: greeting
   :noindex:

   This is Antelop's hello world function.


   **Query**: Experimenter

   **Returns**: {'greeting': <class 'str'>}

   .. dropdown:: See Code

      .. code-block:: python

             def run(key, excited=True):
                 full_name = (Experimenter & key).fetch1("full_name")
                 if excited:
                     return f"Hello, {full_name}!"
                 else:
                     return f"Hello, {full_name}."


.. class:: greeting_with_count
   :noindex:

   This example shows how we can build on top of other functions and use multiple attributes, both within the same table and from different tables.
   
   To do so, we need to define the other functions we want to run in the `inherits` attribute, and pass them as inputs to the function.
   
   These inner functions can then be run with any restriction - although the typical use case is to use a primary key.


   **Query**: Experimenter

   **Returns**: {'response': <class 'str'>}

   **Calls**: ['greeting', 'count_experiments']

   .. dropdown:: See Code

      .. code-block:: python

             def run(key):
                 greet = greeting(key)["greeting"]
                 num_experiments = count_experiments(key)["count"]
                 institution = (Experimenter & key).fetch1("institution")
                 response = (
                     f"{greet} You have run {num_experiments} experiments at {institution}."
                 )
                 return response


.. class:: sta
   :noindex:

   The spike-triggered average for an analog event.
   
   
   
   This example shows how for some functions, it makes sense to define the function as running on the join of two tables.


   **Query**: ['SpikeTrain', 'AnalogEvents']

   **Returns**: {'Spike-triggered average': <class 'numpy.ndarray'>, 'Timestamps (s)': <class 'numpy.ndarray'>}

   .. dropdown:: See Code

      .. code-block:: python

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



Isi
---

This module contains the standard library isi ratio analysis functions.

.. class:: auto_correlogram
   :noindex:

   Plot the interspike interval histogram of a spike train.
   
   
   
   **Arguments**:
   
   sample_rate (float): The sample rate of the autocorrelogram in Hz.


   **Query**: SpikeTrain

   **Returns**: {'IsiPlot': <class 'matplotlib.figure.Figure'>}

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: isi_plot
   :noindex:

   Plot the interspike interval histogram of a spike train.
   
   
   
   **Arguments**:
   
   bin_size (float): The size of the bins in the histogram in seconds.
   
   window (float): The length of the window to plot in seconds.


   **Query**: SpikeTrain

   **Returns**: {'IsiPlot': <class 'matplotlib.figure.Figure'>}

   .. dropdown:: See Code

      .. code-block:: python

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



Sta
---

This module contains the standard library spike-triggered average analysis functions.

.. class:: analog_sta
   :noindex:

   The spike-triggered average for an analog event.


   **Query**: ['SpikeTrain', 'AnalogEvents']

   **Returns**: {'Spike-triggered average': <class 'numpy.ndarray'>, 'Timestamps (s)': <class 'numpy.ndarray'>}

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: digital_sta
   :noindex:

   The spike-triggered average for a digital event.


   **Query**: ['SpikeTrain', 'DigitalEvents']

   **Returns**: {'Spike-triggered average': <class 'numpy.ndarray'>, 'Timestamps (s)': <class 'numpy.ndarray'>}

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: interval_sta
   :noindex:

   The spike-triggered average for a digital event.


   **Query**: ['SpikeTrain', 'IntervalEvents']

   **Returns**: {'Spike-triggered average': <class 'numpy.ndarray'>, 'Timestamps (s)': <class 'numpy.ndarray'>}

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: plot_analog_sta
   :noindex:

   Plot the spike-triggered average for an analog event.


   **Query**: ['SpikeTrain', 'AnalogEvents']

   **Returns**: {'Spike-triggered average': <class 'matplotlib.figure.Figure'>}

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: plot_digital_sta
   :noindex:

   Plot the spike-triggered average for an analog event.


   **Query**: ['SpikeTrain', 'DigitalEvents']

   **Returns**: {'Spike-triggered average': <class 'matplotlib.figure.Figure'>}

   .. dropdown:: See Code

      .. code-block:: python

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


.. class:: plot_interval_sta
   :noindex:

   Plot the spike-triggered average for an interval event.


   **Query**: ['SpikeTrain', 'IntervalEvents']

   **Returns**: {'Spike-triggered average': <class 'matplotlib.figure.Figure'>}

   .. dropdown:: See Code

      .. code-block:: python

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


