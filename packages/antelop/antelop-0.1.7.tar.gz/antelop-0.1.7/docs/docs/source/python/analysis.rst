.. _analysis:

Writing analysis functions
==========================

Antelop provides a comprehensive standard library of analysis functions, discussed in :ref:`stdlib`. However, you will of course want to write your own analysis functions. We therefore provide a structured way of doing this, and recommend that you write your own functions within this framework.

Framework motivations
---------------------

You may ask why don't you just write your functions yourself. In :ref:`script` we detail how to interact with your database programmatically using a python script. You could, of course, just fetch the appropriate data in a script, and do your analysis from there. There are a few drawbacks to this approach, however:

* This typically requires you to hardcode database keys into your script
* It therefore doesn't encourage code reuse across different projects or users
* It doesn't explicitly detail the data it depends on
* It doesn't explicitly check that the data you need doesn't change across different runs of the script
* There's no integration with the gui

We therefore provide a framework for writing analysis functions that addresses these limitations. In particular, in our framework, you:

* Write functions based on an arbitrary key so they can run on the entire database
* Explicitly detail the database tables your function depends on
* We provide a mechanism to explicitly store and rerun analysis functions, checking the data dependencies haven't changed, to aid reproducibility
* User-defined functions are automatically integrated into the gui, with the correct argument selection tools and display widgets

Writing custom functions
------------------------

Analysis functions in antelop are written as classes decorated by the `antelop_analysis` decorator. The class name can be anything, but must be unique and should be somewhat descriptive of the function's behaviour. These classes must define the following attributes:

* `name`: (str) The name of the function, as it will be accessed in the gui and python interface.
* `query`: (str or list[str]) The name of the table that the function will query to give you the primary key. Note this does not mean the function will only query this table, but it will run in parallel on all keys in this table, or a subset of these keys. The query attribute could also be a list, which we discuss later.
* `data`: (str or list[str]) The name of the tables the function will fetch data from. This has to be specified to enforce our data immutability checks.
* `args`: (dict[str, type]) (Optional) A dictionay of additional argument names, along with their python data types.
* `returns`: (dict[str, type]) A dictionary of the names of return values as keys, to the datatypes of the return values as values. Note the name is a string used for display purposes - it doesn't need to match the variable name in the function, but does need to be ordered to match the return values. Supported datatypes include python builtin types, `numpy.ndarray`, and `matplotlib.figure.Figure`, which will get displayed correctly in the gui. Other data types can of course be returned but the gui won't know how to display them.
* `hidden`: (bool) (Optional) This attribute can be set to `True` if you want to hide the function from the gui. This is useful for helper functions that are only built to be called from other functions, but not run standalone.
* `calls`: (list[str]) (Optional) This defines a list of other antelop functions that this function depends on. This is useful for building up complex analysis functions from simpler ones, which helps with code reuse and modularity. Functions can be specified in the `folder.function` syntax, or, if the function is in the same script, just the `function` syntax.
* `key`: (dict) (Optional) This parameter can be useful if your script is only designed to be run on, say, a single experiment. It should represent the key for the data the function applies to, which will be automatically applied in the gui.

The function itself is then written in the `run` method of the class. This method takes the argument `key`, which is calculated when you run the function. Additionally, it should take in its optional arguments, preferably with well defined default arguments.

The first thing you will typically do is use the key to fetch your data for the function. Note all your predefined data tables are available directly in the function namespace, as are other analysis functions under their usual `script.function()` notation.

Example functions
-----------------
All of the following functions are examples written to demonstrate the flexibility possible within this framework. They are all available under the `hello_world` script in the standard library.

Greeting
""""""""
This first function simply greets all users. It is a minimal example of how to write a function. The results were shown above::

    from antelop import antelop_analysis

    @antelop_analysis
    class Greeting:
        """
        This is Antelop's hello world function.
        """
    
        name = 'greeting'
        query = 'Experimenter'
        returns = {'greeting':str}
        args = {'excited':bool}
    
        def run(key,excited=True):
            full_name = (Experimenter & key).fetch1('full_name')
            if excited:
                return f'Hello, {full_name}!'
            else:
                return f'Hello, {full_name}.'

Count experiments
"""""""""""""""""
This second example counts a user's experiments. It demonstrates how your function can query one table for the keys it depends upon, while fetching data from a different table. For the following functions I show the results of running it with the restriction to the user `rbedford` to keep things simple::

    @antelop_analysis
    class CountExperiments:
        """
        This is a slightly more complex example showing how we can aggregate over another table and rename variables within the function.
        It's worth noting that when you aggregate, the argument passed to the function will always be a list.
        """
    
        name = 'count_experiments'
        query = 'Experimenter'
        data = 'Experiment'
        returns = {'count':int}
    
        def run(key):
            length = len(Experiment & key)
            return length

+-------------+------------------------------+
| experimenter| count                        |
+=============+==============================+
| rbedford    | 5                            |
+-------------+------------------------------+

Greeting with count
"""""""""""""""""""
The following example shows how you can recursively call a function from within another function. This is really useful for code reusability::

    @antelop_analysis
    class GreetingWithCount:
        """
        This example shows how we can build on top of other functions and use multiple attributes, both within the same table and from different tables.
        To do so, we need to define the other functions we want to run in the `inherits` attribute, and pass them as inputs to the function.
        These inner functions can then be run with any restriction - although the typical use case is to use a primary key.
        """
    
        name = 'greeting_with_count'
        query = 'Experimenter'
        returns = {'response':str}
        calls = ['greeting', 'count_experiments']
    
        def run(key):
            greet = greeting(key)['greeting']
            num_experiments = count_experiments(key)['count']
            institution = (Experimenter & key).fetch1('institution')
            response = f'{greet} You have run {num_experiments} experiments at {institution}.'
            return response

+-------------+-------------------------------------------------------------+
| experimenter| response                                                    |
+=============+=============================================================+
| rbedford    | Hello, Rory Bedford! You have run 5 experiments at MRC LMB. |
+-------------+-------------------------------------------------------------+

Spike-triggered average
"""""""""""""""""""""""
For the following example, the natural domain over which to define our function is actually a join of two tables. This is because a spike-triggered average is defined to run on both a behavioural variable and a spiketrain::

    @antelop_analysis
    class Sta:
        """
        The spike-triggered average for an analog event.
    
        This example shows how for some functions, it makes sense to define the function as running on the join of two tables.
        """
    
        name = 'sta'
        query = ['SpikeTrain', 'AnalogEvents']
        returns = {
            'Spike-triggered average': np.ndarray,
            'Timestamps (s)': np.ndarray
        }
        args = {
            'window_size': float,
            'sample_rate': float
        }
    
        def run(key, window_size=1, sample_rate=1000):
    
            spiketrain = (SpikeTrain & key).fetch1('spiketrain')
            data, timestamps = (AnalogEvents.proj('data','timestamps') & key).fetch1('data', 'timestamps')
    
            # interpolate the event data
            event_func = interp1d(timestamps, data, fill_value=0, bounds_error=False)
    
            # create window timestamps
            step = 1 / sample_rate
            start_time = - (window_size // step) * step
            window_timestamps = np.arange(start_time, 0, step)
    
            # create matrix of window times for each spike - shape (n_spikes, window_samples)
            sta_times = spiketrain[:, None] + window_timestamps
    
            # get the event values in each window
            sta_values = event_func(sta_times)
    
            # average over all spikes
            sta = np.mean(sta_values, axis=0)
    
            return sta, window_timestamps


+------------------------+------------------+--------------+------------+-------------------+-----------+----------+-------------------+-------------+-------------------------+------------------+
| experimenter           | experiment_id    | session_id   | animal_id  | sortingparams_id  | probe_id  | unit_id  | behaviour_rig_id  | feature_id  | Spike-triggered average | Timestamps (s)   |
+========================+==================+==============+============+===================+===========+==========+===================+=============+=========================+==================+
| rbedford               | 1                | 1            | 1          | 1                 | 1         | 1        | 1                 | 1           | np.ndarray              | np.ndarray       |
+------------------------+------------------+--------------+------------+-------------------+-----------+----------+-------------------+-------------+-------------------------+------------------+
