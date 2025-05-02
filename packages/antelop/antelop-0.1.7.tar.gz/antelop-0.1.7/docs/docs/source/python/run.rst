Reproducability framework
=========================

Antelop provides a custom framework for running analysis functions on the database. These functions can include any outputs you would want to save for eventual conclusion in a paper, such as plots, tables, or other data. This framework provides a few features that can help your workflow significantly: namely, tight integration with the GUI, automatic saving of your results, and integration with your lab's GitHub so you can share scripts easily.

However, the primary feature that makes this framework important is its focus on reproducibility. In neuroscience, it is incredibly difficult to reproduce results from a paper, and keep precise track of what analysis you ran and on what data. For instance, after preprocessing, you may run a script on 100 units you recorded in an electrophysiolgoy experiment, and store this somewhere on your machine. You may then later change some spikesorting parameters and preprocess things again, or modify your script slightly, or forget what arguments you used for your analysis routine, or lose track of your data, or leave the lab, etc. It quickly becomes nearly impossible to reproduce how that exact figure or table was created.

Our framework builds upon the benefits of having a centralised and structured lab database, and version control in GitHub. We end up with a framework that can exactly rerun any analysis you have done, on the same data, with the same parameters, and the same code. This is a powerful tool for ensuring the reproducibility of your work, and for sharing your work with the community. Our framework ends up producing a small metadata file that records everything necessary to reproduce what was run, and any future user just needs to drag and drop this into the GUI or load it in python and can rerun your exact analysis. We aim to make this level of rigour in your reproducability efforts easy and standardized.

Reproducibility
---------------

In particular, the important things to consider in order to make an analysis routine exactly reproducible are:

* Data consistency: the data you are analysing should be fixed in time, and not change between runs.
* Function consistency: the code of the analysis function should also be exactly fixed.
* Parameter consistency: the parameters passed to the function should be recorded exactly.
* Dependency consistency: the exact environment in which you are running your analysis should be recorded.

Now, some of these challenges are already addressed by widely used tools in the community. For example, for the final point of dependency consistency, tools such as virtual environments (eg conda), or containers (eg singularity), should be used to reproduce the environment in which the function was run, and are widely distributed with the code repository accompanying a publication. Data availability is addressed by a number of tools as described in `DataJoint's documentation <https://datajoint.com/docs/core/datajoint-python/0.14/publish-data/>`_. For example, you can provide access to your MySQL database to the community, or export your data to a format such as NWB for sharing, or containerise your database in Docker with a SQL dump so users can run their own instance of your database. We provide additional functionality on top of these methods, designed to be used alongside them, that rigourously checks the consistency of the data when sharing for a publication.

Reproducibility file
^^^^^^^^^^^^^^^^^^^^

We provide a method to run your analysis function that saves the results to disk, alongside an additional metadata file, that enables exact reproducibility of the function call, as per our criteria discussed above.

This file is json-based, and includes the following information:

* `location`: the location of the function
* `folder`: the folder of the function
* `name`: the name of the function that was run
* `restriction`: the restriction that the fucntion was run on
* `arguments`: the arguments passed to the function
* `data_hash`: a hash of all data in the database the function could make use of
* `code_hash`: a hash of the code of the function to check it hasn't changed

Of particular importance is the data hash. Recall that each function in antelop specifies the database tables it will run on, the key it will use to fetch data, and other functions it can call. Our algorithm uses the MD5 hashing algorithm on all rows in the tables matching the function call's key that are available to the function. The hash runs on all table attributes, including blobs. The function can't run on any data outside these rows, so checking their hash is sufficient to ensure the data hasn't changed. One complication is that other functions called by the parent function can depend on different tables to the parent; our algorithm therefore traverses the graph of function calls to collect all tables the parent function depends on, including those from arbitrarily deep other function calls.

A quick note on hashing results: we do not want to enforce that your analysis routines are necessarily deterministic, so we do not check a hash of your results. If you want to add this and your function is definitely deterministic, it would be very straightforaward to compute a hash of the pickle file of the results.

