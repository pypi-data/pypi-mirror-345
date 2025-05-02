Access/installation
===================

Local installation
^^^^^^^^^^^^^^^^^^
The local installation instructions are identical as for the web app, listed in :ref:`installation`. The difference is that it requires fewer dependencies, so can be installed more quickly. If you have already installed the web app, this should be working already. If not, read ahead

Antelop requires python3.9. We **strongly** recommend using a virtual environment for your installation. Many users will use conda to manage virtual environments. To setup your environment and install antelop::

    conda create -n antelop python=3.9
    conda activate antelop
    pip install antelop

This will enable both the interactive IPython interface and the script interface.

Configuration
"""""""""""""

The configuration is also identical as for the web app. However, the only configs necessary are the MySQL and S3 hosts, and the analysis scripts directory. If you're not going to use the gui, the rest can all be left blank. We detail here only the configurations necessary for the python interface. The full configuration is detailed in :ref:`configuration`. This minimal configuration works for both the interactive IPython interface and the script interface.

In order, the steps are:

- MySQL host: The host address of your lab's MySQL database.
- S3 host: The host address of your lab's S3 store.
- Analysis scripts:
  - Custom analysis scripts are written and kept in folders on your local machine.
  - You must specify the absolute paths to these folders here.
- Github:
  - If you want to automatically have access to your lab's Antelop analysis scripts, you can configure Antelop to automatically pull from your lab's Github repository.
  - Simply give your repository an optional name, such as 'trilab-scripts', and enter the URL of the GitHub repository. Note that the name should be a unique and usable python variable, so avoid spaces and special characters. Your scripts will be available under this name.  

If you want to manually edit your configuration file, it is stored in ~/.config/antelop/config.toml on Unix, and in %APPDATA%/antelop/config.toml on Windows.

Cluster installation
^^^^^^^^^^^^^^^^^^^^
The cluster installation is provided as a singularity container. This should have been set up and configured by your database administrator. The container can be run as an executable, or can be used in a bash script to run python scripts on your cluster.

    /path/to/antelop-python.sif

If you are going to use the container frequently, we strongly recommend setting up an alias in your .bashrc file. This will allow you to run the container with a simple command, such as `antelop-python`.

    alias antelop-python="/path/to/antelop-python.sif"