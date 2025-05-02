.. _installation:

Access/installation
-------------------

How you access the GUI depends on your infrastructure and how your database administrator setup Antelop. The recommended approach is to install Antelop locally via pip.

Local installation
^^^^^^^^^^^^^^^^^^

Antelop can be installed locally on your machine via pip. This is the recommended approach for most users.

Antelop requires python3.9. We **strongly** recommend using a virtual environment for your installation. Many users will use conda to manage virtual environments. To setup your environment and run antelop::

    conda create -n antelop python=3.9
    conda activate antelop
    pip install antelop[gui]

With antelop installed, you can now run the GUI by typing `antelop` in your terminal, in the activated environment. Just like a Jupyter notebook, this will run a local server and will open the application in your browser.

Optional dependencies
"""""""""""""""""""""
Additional dependencies can be installed to enable extra features in antelop, but these are not required for basic functionality. We provide them as additional dependencies, since these dependencies can be difficult ot install on certain systems.

In particular, if you want to use phy from within antelop, use the phy extra::

    pip install antelop[gui, phy]

And if you want to use deeplabcut's gui tools, run::

    pip install antelop[gui, deeplabcut]

To install all optional dependencies, run::

    pip install antelop[full]

Note the the lightweight version with no additional dependencies just allows you to use antelop's :ref:`python`.

Configuration
"""""""""""""

On first use, you'll need to run `antelop-config` to configure your app, or alternatively, run `antelop` to be directed to a graphical configuration tool. This process includes linking antelop to your lab's database, your compute cluster, and local storage.

In order, the steps are:

- MySQL host: The host address of your lab's MySQL database.
- S3 host: The host address of your lab's S3 store.
- Local storage:

  - You can add many local storage locations which will be searchable within Antelop.
  - Each folder must first be given a name, such as 'Documents', which will be used to identify it in Antelop.
  - It must then be given an absolute path, in either Windows or Unix format.

- Analysis scripts:

  - Custom analysis scripts are written and kept in folders on your local machine.
  - You must specify the absolute paths to these folders here.

- Number of cores: Antelop runs many operations in background processes. You can specify the number of cores to use here. This must be an integer greater than 0.
- Cluster host: The hostname of your compute cluster, as you would use in an SSH command.
- Cluster antelop install path: The path to the antelop installation on your cluster. This will be given to you by your antelop administrator. Must be an absolute Unix path.
- Cluster data directory:

  - Most clusters have a way of mounting your cluster storage onto your local machine. Antelop needs to know the path to this directory on your local machine.
  - This should be an absolute Windows or Unix path.
  - If mounting is not possible, you won't be able to manually curate data in phy and track cluster jobs progress, but all other antelop features will still work.
- Github:
  - If you want to automatically have access to your lab's Antelop analysis scripts, you can configure Antelop to automatically pull from your lab's Github repository.
  - Simply give your repository an optional name, such as 'trilab-scripts', and enter the URL of the GitHub repository. Note that the name should be a unique and usable python variable, so avoid spaces and special characters. Your scripts will be available under this name.  

If you want to manually edit your configuration file, it is stored in ~/.config/antelop/config.toml on Unix, and in %APPDATA%/antelop/config.toml on Windows.


Desktop app on shared machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Antelop can be run on a shared linux machine, such as a cluster head node. However, users need to access Antelop from their own machines. Since Antelop is a graphical application, we recommend using `X2Go <https://wiki.x2go.org/doku.php>`_, which enables you to run graphical applications on a remote machine. You should install the X2Go client on your Windows, Mac or Linux machine.

Inside the X2Go Client, you should start a new session, which you can name 'Antelop'. You then need to enter the host machine on which Antelop is installed, and your username. Under 'Session type', you want to select 'Single application' in the dropdown box. You then need to enter the command that runs Antelop, which should be of the form::

    /path/to/antelop.sh

Where your database administrator will give you the path for your particular installation.

Additionally, you should click on the media tab and uncheck 'Enable sound support'.

Optionally, under the shared folders tab, you can select data on your local machine that you want to use within Antelop. This could be a folder on your machine where you store trial data, for example. To do this, click on the folder icon and navigate to the folder you want to use in Antelop, then click 'Add'. Make sure you select the 'Automount' checkbox. This data will show up under the 'local' folder inside Antelop.

Once you're happy with all your options, click 'Ok'. We then recommend that you make a desktop shortcut to Antelop for easy access. Click on the options button for the Antelop session, and select 'Create session icon on desktop'.

With this initial setup complete, you now just need to click on the Antelop desktop shortcut, and enter your password, and Antelop will boot. There is no further setup required - everything should just work out of the box, including tools such as Phy, scheduling jobs on the cluster, and connecting to your lab's database. Note Antelop can take a while to boot up - sometimes around fifteen seconds.

Persistent webapp
^^^^^^^^^^^^^^^^^

If you are using a persistent web interface hosted on a dedicated lab server, you will simply need to navigate to the URL in your web browser given to you by the database administrator from within your institution's network (or using a proxy or VPN if outside the network).

Note however that the web version of antelop is slightly more limited - you cannot display certain graphical applications such as phy, and may not be able to schedule jobs depending on whether your cluster is directly accessible via SSH.
