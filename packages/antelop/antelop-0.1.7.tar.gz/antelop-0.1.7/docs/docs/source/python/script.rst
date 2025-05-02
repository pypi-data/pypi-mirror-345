.. _script:

Using antelop in a script
==========================

We also provide a means of connection to your database via a script. This can be very helpful if you want to automatically parse a large amount of pre-existing data and insert it into your database, without having to go through the gui.

Connecting to the database
--------------------------

We do not want to expose database credentials in a script, or write them to disk at all. The safest way to access credentials in a script is via environment variables. It is therefore necessary that you set the `DB_USER` and `DB_PASS` environment variables in the execution environment before running the script. This could be done with `export` in bash, and these can be copied into a slurm environment by adding the following line to your slurm script for HPC use::

#SBATCH --export=DB_USER,DB_PASS

Within your script, you then want to establish a database connection. This can be done as follows::

   from antelop.load_connection import *

This reads all the tables and analysis functions for direct use in the script, just like in :ref:`interactive`.

Custom helper functions
-----------------------

Certain aspects of antelop's database integrity are enforced at the application level. Some parts of our schema design are not completely simple to interact with. For these reasons, we expose several helper functions, which are the recommended way to interact with certain parts of the database. By understanding all of these, it will be fully possible to use antelop in a fully programmatic way, without the gui.

However, it is possible to use the python connector to interact without these helper functions, which could lead to your database being in an inconsistent state. We therefore recommend at least understanding these functions if you are going to insert complex data programmatically.

Split trials
^^^^^^^^^^^^
We designed the masking functions to allow for the splitting of sessions into individual trials. This splitting is a common operation so we provide a function to efficiently do this for you. This function takes as arguments the event data and timestamps you want to split, and the mask data and timestamps, both of which should be a (data, timestamps) tuple. The data can be from any of AnalogEvents, DigitalEvents, IntervalEvents or Kinematics::

   from antelop import split_trials

   mask = (Mask & restriction).fetch1('data','timestamps')
   events = (AnalogEvents & restriction).fetch1('data','timestamps')

   trials = split_trials(events, mask)

This will return a list of (data, timestamps) tuples, each corresponding to a single trial, as defined by the mask.

Upload rig json
^^^^^^^^^^^^^^^
As described in :ref:`behaviour`, antelop uses a custom json-based file format to describe your behaviour rig, all the different elements of your behaviour that will get recorded, and how to parse a NWB file to upload this data into our database structure. It is recommended to use our helper function to upload this file for two reasons. First of all, our function checks that the json file is valid according to our json schema. Downstream function assume this to be the case, so invalid rigs will make downstream processing impossible. Second, our function also automatically populates the `Feature` table, which allows you to further annotate features in the behaviour rig with data such as video attachments.

This function is called `upload_rig_json` takes the following arguments::

    experimenter (str): experimenter username
    rig_name (str): name of the rig
    rig_json (path): path to the rig json file
    masklist (list of dict): list of mask dictionaries, with keys 'name', 'description', 'function'

Note that the rig name, like all other names in the database, should be unique. This is quite important. In our lab, for example, we have four rigs of identical design but with slightly different measurements calibrating camera feeds, so its very important to be able to discriminate their geometries in the database for postprocessing and analysis.

Masking functions are used to split sessions into trials, and are described in :ref:`behaviour-masks`. These are written in antelop's analysis format, so must be present in your analysis folder. The masklist argument is a list of dictionaries, each of which describes a mask, with the following keys:

* name: a unique name for the mask
* description: a description of the mask
* function: the name of the script and function, such as `script.mask1`, where scripts are found in your defined analysis folder. It is very important that these functions are named correctly here otherwise you will have errors inserting your data.

Recompute masks
^^^^^^^^^^^^^^^
As described in :ref:`behaviour-masks`, we store masks in the database, which are used to split sessions into trials. These are computed immediately upon data insertion, to ensure all your behaviour recording sessions have the appropriate data defining trials in them. However, you do need to write your masking functions, which are often fairly customised, and test that they work correctly. The recommended workflow is to insert a small subset of data, such as a single session, and then write your masking functions. Once you are happy that they work, you need to of course recompute the masks in the database for these test sessions, which is what this helper function does.

This function is called `recompute_masks` and takes the following arguments::

    key (dict): session primary key

This will then recompute the masks for this session and will repopulate the database. Note that this doesn't strictly have to be a session key: you can run on more than one session with, say, an experiment key, but for a lot of data this will take a long time, so it's not recommended to do this unless you know what you're doing, and potentially use, say, an HPC to do this.

Insert nwb
^^^^^^^^^^
One data insert that is potentially non-trivial is inserting nwb files. We batch insert all the different data for a single session within the behaviour schema, as they are all interelated and should come from the same nwb file. This is not a simple process. In particular, we took great care in desiging our json schema, that describes your behaviour rig, its geometry and features, and maps the data from our acquisition's nwb output into the correct tables. We therefore expose a function that reads this nwb file, the json file, and the database key, and performs all the necessary inserts.

This function is called `insert_nwb` and takes the following arguments::

    session (dict): session primary key
    animals (list of dict): animal primary keys
    nwbpath (Path): path to the nwb file

Note that the behaviour rig json must already be inserted in the database using the upload_rig_json function (or the gui). Additionally, the NWB file must contain all the data described in the json file, otherwise an error will be raised. It can have additional data not described in the json. Finally, the animal keys must of course match the session key, and the animals must match the json file - ie, if two animals are described as being in the recording inside the behaviour rig file, then two animal keys must be given.


