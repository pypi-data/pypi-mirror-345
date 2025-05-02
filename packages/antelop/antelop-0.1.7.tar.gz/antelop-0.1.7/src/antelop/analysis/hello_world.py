import numpy as np
from antelop import antelop_analysis
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


@antelop_analysis
class Greeting:
    """
    This is Antelop's hello world function.
    """

    name = "greeting"
    query = "Experimenter"
    returns = {"greeting": str}
    args = {"excited": bool}

    def run(key, excited=True):
        full_name = (Experimenter & key).fetch1("full_name")
        if excited:
            return f"Hello, {full_name}!"
        else:
            return f"Hello, {full_name}."


@antelop_analysis
class CountExperiments:
    """
    This is a slightly more complex example showing how we can aggregate over another table and rename variables within the function.
    It's worth noting that when you aggregate, the argument passed to the function will always be a list.
    """

    name = "count_experiments"
    query = "Experimenter"
    data = "Experiment"
    returns = {"count": int}

    def run(key):
        length = len(Experiment & key)
        return length


@antelop_analysis
class GreetingWithCount:
    """
    This example shows how we can build on top of other functions and use multiple attributes, both within the same table and from different tables.
    To do so, we need to define the other functions we want to run in the `inherits` attribute, and pass them as inputs to the function.
    These inner functions can then be run with any restriction - although the typical use case is to use a primary key.
    """

    name = "greeting_with_count"
    query = "Experimenter"
    returns = {"response": str}
    calls = ["greeting", "count_experiments"]

    def run(key):
        greet = greeting(key)["greeting"]
        num_experiments = count_experiments(key)["count"]
        institution = (Experimenter & key).fetch1("institution")
        response = (
            f"{greet} You have run {num_experiments} experiments at {institution}."
        )
        return response


@antelop_analysis
class FirstExperimentName:
    """
    This example shows how we can use a restriction to filter the data within the function.

    Restrictions can of course be passed when running the function, but are useful at this level
    to define when the function doesn't apply to certain attributes, or more commonly, to define
    different subsets of aggregated attributes as different inputs to the function.

    Note, you should always handle the case where the function input is an empty list.
    """

    name = "first_experiment_name"
    query = "Experimenter"
    returns = {"response": str}

    def run(key):
        experiment_name = (Experiment & key).fetch("experiment_name", limit=1)
        if len(experiment_name) == 0:
            return "You have not run any experiments."
        elif len(experiment_name) == 1:
            return f"The first experiment you ran was called {experiment_name[0]}."
        else:
            raise ValueError("This error should never get raised.")


@antelop_analysis
class ExampleFigure:
    """
    Example of a function that returns a matplotlib figure.
    """

    name = "example_figure"
    query = "Experimenter"
    returns = {"figure": plt.Figure}
    args = {"size": ['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large']}

    def run(key, size='medium'):
        full_name = (Experimenter & key).fetch1("full_name")
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f"Hello\n{full_name}!", size=size, ha="center")
        ax.axis("off")
        return fig


@antelop_analysis
class Sta:
    """
    The spike-triggered average for an analog event.

    This example shows how for some functions, it makes sense to define the function as running on the join of two tables.
    """

    name = "sta"
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
