Repository structure
====================

Antelop involves a few distinct components that undergo separate development, need separate installations on the various host machines, but are all interconnected when Antelop is deployed. The bulk of the project consists of the python package and graphical user interface, which are installed together as a single pip package. Therefore, the repository as a whole is structured as a python package, with a `pyproject.toml` in the root directory describing the project, and the bulk of the source code under `src/antelop`. However, there are a few other components that are distinct from the python package, and therefore require their own directory in the root of the repository.

The structure is as follows:

* **docs** - this folder contains all the documentation, built automatically and hosted at https://antelop.readthedocs.io/en/latest/setup.html.
* **install_scripts** - this folder should be seen by admins wanting to install Antelop's cluster pipelines and databases. It contains installation scripts, containers, and a README to help users get started with setting up Antelop as easily as possible.
* **src/antelop** - this folder contains all the code for the graphical user interface and the python pacakge.
* **workflows** - this folder contains the Nextflow scripts which need to be installed on the computational server/HPC. This folder is for development purposes - it gets copied to the cluster during installation.

Since the bulk of the project is the gui and python interface, we will discuss the structure of `src/antelop` in more detail.

Graphical user interface
------------------------

The graphical user interface code is held inside the `src/antelop` of the repository. It contains all the code needed to run the gui or the python interface.

The gui is written as a streamlit app, which is a user-friendly python web development framework. The local installation deployment method just runs the streamlit app in your terminal, which starts a streamlit srever and opens your browser much like a jupyter notebook. The shared machine deployment option essentially just bundles the web app with a minimal version of the chromium browser inside a singularity container, and runs chromium in 'app' mode, which gives it a desktop-like feel.

Within the antelop directory, we find many subdirectories. The antelop directory is itself a package, and most subdirectories are subpackages that can be imported through the syntax::

    import antelop.gui.search

However, note that we use the main `__init__.py` so that users can import commonly used functions and classes from the package root.

Analysis directory
^^^^^^^^^^^^^^^^^^
This contains antelop's analysis standard library. It also includes `hello_world.py`, which is used in antelop tutorials to demonstrate how to write analysis functions. The rest of the scripts are organised by common function. They are all commented well with proper docstrings so should be self-explanatory. For further information see :ref:`analysis`.

Configs directory
^^^^^^^^^^^^^^^^^

The `configs` directory just holds the root streamlit configuration file that gets copied to the user's home during installation.

Connection directory
^^^^^^^^^^^^^^^^^^^^

This directory holds `connect.py`, which establishes a database connection. This is not always straightforward - inside streamlit, we want to use a cached connection. When multithreading, we want to establish a distinct connection for each process. `import_schemas.py` just imports all the tables once a connection has been established.

Note `load_connection` as a directory only exists to rename this directory on importation.

Gui directory
^^^^^^^^^^^^^
This directory holds all the different streamlit pages that are shown in the app. The structure of this directory follows the layout of the app, as detailed in :ref:`gui`. In particular, subdirectories correspond to pages grouped together in the app.

Streamlit overview
""""""""""""""""""

It's worth noting briefly at this point streamlit's data flow, which is unusual for a web development framework. Any time the user interacts with anything on the page, the entire script is rerun from top to buttom. Internal caching mechanisms allow streamlit to save the state of many widgets, and its very important to cache many objects such as database connections, so they're not recomputed each time the user interacts with the page. It can take a little while to get used to this (for example, nested buttons just don't work as you'd hope). This is a big change from typical web frameworks, where the backend usually involves an API which waits for requests from the frontend.

It's also worth noting that due to this model, the application is frozen to the user while long running computations occur. This is again why caching is so important, as it makes the page much more snappy. Additionally, we want to run some long running computations in the application, such as uploading a large trial recording to the database, which can take around 5 minutes. If this ran in the main streamlit process the user would have to wait for it to finish before they can do anything else. We therefore have a separate process pool to which these jobs are submitted, with a configurable maximum number of workers. In particular, we use this process pool for uploading, downloading, and modifying (restores and temporary deletes) data in the database. Often this is unnecessary - uploading a small single row is very quick, but we generalise this specifically for the cases where it's not quick.

Resources directory
^^^^^^^^^^^^^^^^^^^

The `resources` directory contains images and jsons used inside the web interface.

Schemas
^^^^^^^

The schemas directory describes the structure of our MySQL schemas in DataJoint syntax. This is necessary to be imported in other scripts to interact with the database. In particular, our database is split into distinct but connected schemas, which correspond to different data types. At present these include `metadata`, `ephys`, and `behaviour`.

Scripts directory
^^^^^^^^^^^^^^^^^

Of particular importance is the `scripts` directory. This holds scripts that are not imported as packages but run as standalone applications. Some of these are just utilities used by the singularity containers. Others are run as standalone command line applications, as specified in `pyproject.toml`. For an installed python package to have a command line tool installed with it, the tool needs to be a python function in a script, which are all kept in this folder.

`make_config.py` is used by the command line tool `antelop-config` to interactively create the user's configuration file.

`antelop-python.py` is used to create the `antelop-python` interactive interface. This function loads the configuration, prompts the user for their username and password, establishes a database connection, imports all the tables and analysis functions into the global namespace, and starts an IPython shell.

`run_gui.py` creates the command line tool `antelop`, which starts the streamlit app. Typically streamlit apps are run with `streamlit run app.py`, but we obviously don't want users to have to specify the app install location, so we just wrap it here using runpy to externally run the command.

`app.py` is the main streamlit app. It imports the other modules in the package. It also creates the login page, which checks the user's credentials against the database and establishes a connection if correct. After that, it sets up the sidebar, and displays the other pages depending on what's been selected, and on the user's permissions.

Utils directory
^^^^^^^^^^^^^^^

The utils directory contains utility functions that are reused across the web interface. We split this into several scripts which we discuss here, as it's important to discuss the logical structure of how we organise utility functions.

- **analysis_base.py** contains the base class for antelop analysis functions, the decorator for antelop analysis functions, and other utilities.
- **antelop_utils.py** contains utilities used for analysis, including the script that checks all folders to import the analysis functions, and a function that split recordings into trials based on a masking function.
- **antelop_utils.py** contains assorted utilities for antelop that are more specific than those in **datajoint** or **streamlit** utils, which are written to be more general. This includes, for example, functions that interact with our specific schema or file types, rather than being general tools for use with any schema.
- **datajoint_utils.py** contains functions that add to DataJoint's functionality, including functions that parse the schema structure to return the parent or earliest ancestor of a given table attribute, and functions that perform queries in a manner suitable for displaying results in the web interface (for example, not downloading external store data to the working directory).
- **external_utils.py** is used for triggering anything that runs outside the main container, such as a nextflow pipeline, or a separate GUI app like phy.
- **multithreading_utils.py** uses the library concurrent.futures to establish a single process pool in which to run long-running functions, such as inserting a large trial recording. It's important that the reference to this process pool is maintained as the user interacts with the app, so it is kept in the streamlit session state, along with different session states which hold the future objects necessary for checking the status of jobs in the process pool.
- **os_utils.py** contains utilities that are OS specific, such as those that interact with config files, which are stored in different locations depending on the OS.
- **streamlit_utils.py** contains custom streamlit widgets that we reuse across pages. These often take DataJoint tables as input, so are not general streamlit widgets but are useful for the Antelop project. They include interactive interfaces to select different table entries, and interactive interface to select spike sorter parameters.
- **visualisation_utils.py** contains the built in plotting functions used inside antelop.
