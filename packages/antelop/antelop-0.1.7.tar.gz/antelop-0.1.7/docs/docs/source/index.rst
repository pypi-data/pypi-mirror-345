Welcome to Antelop's documentation!
====================================

.. figure:: images/antelop-transparent.png
    :alt: Antelop logo

.. raw:: html

   <div class="mission-container">
       <p><p>
       <p><strong>Antelop</strong> is a data storage, preprocessing, visualisation and analysis platform for systems neuroscience.</p>
       <p>Our mission statement is to lower the entry barrier for labs to adopt modern, high-throughput data engineering practices, to facilitate better reproducibility and collaboration within the field.</p>
   </div>


Why should I use Antelop?
--------------------------

Modern systems neuroscience labs have to deal with increasingly large amounts of data, along with increasingly complex computational processing of this data. Many labs leave data management up to the individual researchers, who typically design their own file hierarchies, and their own scripts to parse these files and process them. This leads to poor reproducibility, difficulties with collaboration and sharing of data, and can be time consuming for the individual researchers. Many labs therefore seek a solution to centralise their data storage and processing, in a way that can easily be used by all the lab's researchers.

A number of tools exist to address these challenges, such as relational databases such as MySQL for storing structured data, object stores such as Amazon S3 for unstructured data, and scientific workflow systems such as Nextflow for creating complex computational pipelines. However, constructing a working data platform using these and other tools is time consuming and challenging. Neuroscientists should be able to spend their time doing neuroscience, not data engineering.

However, the requirements of different systems neuroscience labs are often fairly uniform. For example, if a lab performs electrophysiology experiments, they typically want to store the raw experimental output from their acquisition system, and extract both LFPs and spike trains from this raw data, before applying a number of analysis routines on this extracted data, most likely involving behavioural data from the recording session. We believe that a platform that allows these steps to be done, with the flexibility to incorporate a range of different experimental setups and computational infrastructures, with highly customizable processing parameters, and an extendible set of analysis tools, could be an immense benefit to a number of neuroscience labs.

Antelop Features
----------------

* A **MySQL and S3 database**, facilitating:

   + An uniform yet flexible way to structure experimental data
   + A centralised location for data storage and collaboration
   + A fast and rich query language to search your data

* A set of **HPC- or cloud-based preprocessing pipelines**, supporting:

   + Uniform and reproducible preprocessing of several experimental datatypes
   + Efficient workload distribution and parallelisation
   + Diverse preprocessing parameters 

* A **graphical user interface**, which provides a simple and intuitive means for users to:

   + Manage their experimental data and metadata
   + Import and export data to common formats such as NWB
   + Schedule data processing jobs on the HPC/cloud
   + Visualise many datatypes
   + Run and inspect analysis pipelines from our comprehensive standard library
   + GitHub integration for your lab's custom analysis scripts

* A **python package**, which extends the graphical interface through:

   + Interaction with the database through SQL queries
   + Programmatic flexibility for when you have more custom processing requirements
   + An object-oriented paradigm for extending the analysis suite

Supported data types
--------------------

* **Extracellular electrophysiology**

   + Supports a wide range of probes, such as tetrodes, neuropixels, or custom probe designs
   + Supports a wide range of the most popular modern spike sorters
   + Is integrated with phy for manual curation
   + Allows for localisation of units through the probe insertion coordinates
   + Provides a set of standard analysis functions and visualisations for the unit spike trains and LFPs

* **Behavioural data**

   + Supports a range of behavioural data types, such as videos, hardware ttls, or tracking data
   + The geometry of your behavioural rig and all hardware acquisitions are specified via a custom json file
   + Data is then automatically parsed and stored in the database in stuctured arrays
   + We also incorporate the training and inference of DeepLabCut models for tracking

* **Analysis suite**

   + Provides a broad set of standard analysis functions for electrophysiology and behavioural data, such as spike-triggered averages
   + Also provides a set of visualisations for these analyses, such as raster plots and tuning curves
   + Writing custom analysis functions is straightforward, and we provide a particular object-oriented paradigm for your own functions that performs database queries for you under the hood

In the near future, we plan to incorporate the following additional features:

* **Calcium imaging**


.. dropdown:: Screenshots

    .. tab-set::

        .. tab-item:: Search

            .. figure:: images/antelop.png
                :alt: Antelop screenshot
                :scale: 35%

        .. tab-item:: Spiketrain

            .. figure:: images/vis.png
                :alt: Antelop screenshot
                :scale: 35%

        .. tab-item:: Unit Waveforms

            .. figure:: images/unit.png
                :alt: Antelop screenshot
                :scale: 35%

        .. tab-item:: Analysis

            .. figure:: images/analysis.png
                :alt: Antelop screenshot
                :scale: 35%

        .. tab-item:: Python

            .. figure:: images/antelop-python.png
                :alt: Antelop screenshot
                :scale: 35%


.. dropdown:: Credits

    Antelop is built upon a number of existing projects, without which, its development would not be possible. Most notably:

    * `Streamlit <https://streamlit.io/>`_ (for the user interface)
    * `Neo <https://neo.readthedocs.io/>`_ (for reading a wide range of electrophysiology acquisition inputs)
    * `Spikeinterface <https://spikeinterface.readthedocs.io/>`_ (for the containerised spike sorters and electrophysiology processing)
    * `DeepLabCut <https://www.mackenziemathislab.org/deeplabcut>`_ (for animal tracking)
    * `DataJoint <https://datajoint.com/>`_ (for the SQL queries)
    * `Nextflow <https://www.nextflow.io/>`_ (for constructing computational pipelines)


.. toctree::
   :hidden:
   :caption: Graphical User Interface
   :maxdepth: 2

   ui/installation
   ui/usage
   ui/search
   ui/meta
   ui/ephys
   ui/behaviour
   ui/vis
   ui/analysis
   ui/admin

.. toctree::
   :hidden:
   :caption: Python Interface
   :maxdepth: 2

   python/config
   python/interactive
   python/script
   python/run
   python/stlib
   python/analysis

.. toctree::
   :hidden:
   :caption: Administration
   :maxdepth: 3
   
   installation/index.rst
   developer/index.rst
   api/index.rst


.. note::

   This project is under active development
