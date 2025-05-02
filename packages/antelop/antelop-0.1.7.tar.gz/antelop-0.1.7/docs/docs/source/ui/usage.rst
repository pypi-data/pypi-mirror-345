Overview
--------

Once you have opened the application, you first need to login. Your database administrator should have sent you your credentials.

You can navigate through Antelop's different pages in the sidebar on the left.

The first page allows you to search through any data in the database. The next set of pages are all involved in getting data into out various different SQL schemas, through uploading raw data and performing computations. With data in the database, you can then use our custom visualisation tools and analysis packages in the following pages. Finally, the admin page is for database administration and is not available for general users.

Schema design
^^^^^^^^^^^^^

We split our database into distinct schemas, which interconnect to form the full Antelop database.

First of all, there is the metadata schema. This contains just metadata about your experiments, animals and recording sessions, such as animal genetics or session datetimes. This is the schema you need to interact with first when adding data to the database.

Next, we have the electrophysiology schema. If your experiment involves extracellular electrophysiology recordings, this is the schema in which you can insert electrophysiology metadata, such as probe designs, and also upload raw recordings from your acquisition system. It also allows you to insert spikesorting parameters, schedule spikesorting jobs on the cluster, and manually curate your results.

The behaviour schema is for experiments with behavioural data. This schema allows you to insert data about your behaviour rig and paradigm, as well as upload raw data from your rig such as event ttls. It also allows you to upload video streams, train tracking models in deeplabcut, and populate the database with kinematics information from your models and videos.

Users should familiarise themselves with the structure of these schemas below (although the gui is designed to make them intuitive to navigate).

.. tabs::
   .. tab:: Metadata schema
      .. image:: ../images/session.png
         :alt: Antelop metadata schema

   .. tab:: Electrophysiology schema
      .. image:: ../images/ephys.png
         :alt: Antelop electrophysiology schema

   .. tab:: Behaviour schema
      .. image:: ../images/behaviour.png
         :alt: Antelop behaviour schema

If you are unfamiliar with how relational databases work, the next section may be worth reading.

Relational database overview
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In general, a relational database consists of a set of distinct tables, which have rows and columns. The columns define the attributes of the table, while the rows represent different data entries in that table. One or more attributes together define the **primary key** for that entry - this has to be a set of attributes that uniquely defines that entry in the table. In addition, attributes can be a **foreign key**, which is the primary key of an entry in a different table. In this way, that entry references an entry in a different table. Other attributes contain specific information about that entry in the table.

The diagrams above depicts the structure of our database. A table which is below another table, connected by a solid line, references the table above it in its composite primary key. We can think of entries in such a table as belonging to the entry in the table above it - for example, an animal belongs to an experiment. In addition, the dashed lines refer to foreign keys which are not primary keys of the table. Such a table refers to but does not belong to the table it references. For example, an animal has a probe inserted into it for electrophysiology, but we do not think of the animal as belonging to its probe.

A DataJoint pipeline consists of a few different table types. The green tables are **manual** tables, which require manual user input to populate them. In our pipeline, the first manual tables define the experiments, the animals used in these experiments, the geometries of the probes inserted into these animals, and the trials done per animal. These tables successively inherit from each other, which means that an experiment belongs to an experimenter, an animal belongs to an experiment, etc. Users need to manually fill out these tables in order - so if you have a trial for a new animal, you have to first add that animal to the animal table, then add the trial for that animal.

The grey tables are **lookup** tables, which have data that is predefined by the database administrator, and do not require user interaction, such as the set of experimenters belonging to a lab.

Further downstream in the pipeline, we encounter **computed** tables in red, which do not require any manual input, but are automatically populated by computation. Computed tables are fully reproducable - they can be deleted and have their entries reinstated by rerunning the computation that populated them. In our case, these computations take the form of predefined nextflow pipelines.

Additionally, we have **imported** tables in blue. These tables track data outside the pipeline, but otherwise, are the same as computed tables. We use them for a very specific purpose, which is tracking the results of manual curation. Manual curation data is large and fairly unstructured. We feel it is not critical to store this data in the antelop pipeline explicitly. Instead, we use external storage space on the cluster, and track these external files. In the event of the loss of this external data, the curated spiking data will still be in the database, but the exact manual curation steps will not be reproducable.
