Schemas
=======

Here we detail the DataJoint schemas used within Antelop.

Metadata
--------

.. code-block:: python

    @schema
    class Experimenter(classes["lookup"]):
        definition = """
        # Researchers using this database
        experimenter : varchar(40) # Experimenter username
        ---
        full_name : varchar(40) # Full name
        group : varchar(40) # Research group/lab
        institution : varchar(40) # Research institution
        admin : enum('False', 'True') # Admin privileges
        """

    @schema
    class Experiment(classes["manual"]):
        definition = """
        # A cohesive collection of animals and recordings operating under the same paradigm
        -> Experimenter
        experiment_id : smallint # Unique experiment ID (auto_increment)
        ---
        experiment_name : varchar(40) # Short experiment description
        experiment_notes : varchar(1000) # Optional experiment annotations
        experiment_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Animal(classes["manual"]):
        definition = """
        # Animal with genetic information and other metadata
        -> Experiment
        animal_id : int # Unique mouse ID (auto_increment)
        ---
        age = NULL : varchar(20) # Age of the animal in ISO 8601 duration format
        age_reference = NULL : enum('birth', 'gestational') # Reference point for the age
        genotype = NULL : varchar(100) # Mouse genotype
        sex = 'U' : enum('M', 'F', 'U', 'O') # Sex of the animal
        species : varchar(40) # Species of the animal
        weight = NULL : varchar(40) # Weight of the animal including units
        animal_name : varchar(40) # Unique animal name
        animal_notes : varchar(1000) # Optional mouse annotations
        animal_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Session(classes["manual"]):
        definition = """
        # Represents a single recording session
        -> Experiment
        session_id : int # Unique session ID (auto_increment)
        ---
        session_name : varchar(40) # Short session description
        session_timestamp : timestamp # Date and time of start of session (YYYY-MM-DD HH:MM:SS)
        session_duration = NULL : int # Duration of the session in seconds
        session_notes : varchar(1000) # Optional session annotations
        session_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

Electrophysiology
-----------------

.. code-block:: python

    @schema
    class ProbeGeometry(classes["manual"]):
        definition = """
        # Probeinterface ProbeGroup files used across animals
        -> metadata.Experimenter
        probegeometry_id : smallint # Unique probe ID (auto_increment)
        ---
        probe : json # ProbeInterface format
        probegeometry_name : varchar(40) # Short probe description
        probegeometry_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class SortingParams(classes["manual"]):
        definition = """
        # Parameters to be passed to the spike sorting pipeline
        -> metadata.Animal
        sortingparams_id : smallint # Unique params ID (auto_increment)
        ---
        sortingparams_name : varchar(40) # Short sortingparams description
        manually_sorted = 'False' : enum('False', 'True') # Data externally spike sorted
        params : json # Spikesorting parameters
        sortingparams_notes: varchar(1000) # Optional sorting parameters description
        sortingparams_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class ProbeInsertion(classes["manual"]):
        definition = """
        # Probe insertion for this animal
        -> metadata.Animal
        ---
        -> ProbeGeometry
        yaw : decimal(3, 0) # Probe extrinsic rotation relative to dv axis (deg)
        pitch : decimal(3, 0) # Probe extrinsic rotation relative to ap axis (deg)
        roll : decimal(3, 0) # Probe extrinsic rotation relative to ml axis (deg)
        ap_coord : decimal(5, 0) # Probe anterior-posterior coordinate relative to bregma (um)
        ml_coord : decimal(5, 0) # Probe medial-lateral coordinate relative to bregma (um)
        dv_coord : decimal(5, 0) # Probe dorsal-ventral coordinate relative to bregma (um)
        probeinsertion_notes : varchar(1000) # Optional probe insertion description
        probeinsertion_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Recording(classes["manual"]):
        definition = """
        # Recording for this animal
        -> ProbeInsertion
        -> metadata.Session
        ---
        recording : attach@raw_ephys # Recording folder
        ephys_acquisition: varchar(40) # Equipment type
        device_channel_mapping = NULL : json # Mapping of device channels to probe channels
        probe_dv_increment : decimal(4, 0) # Probe dorsal-ventral coordinate increment relative to previous session (um)
        recording_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class SpikeSorting(classes["imported"]):
        definition = """
        # Parent table for all curated and populated ephys data
        -> Recording
        -> SortingParams
        ---
        phy : varchar(200) # Tracks phy folders for manual curation
        manually_curated : enum('False','True') # Has the data been manually curated
        spikesorting_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        spikesorting_in_compute : enum('False','True') # Implements row locking
        """

    @schema
    class Probe(classes["computed"]):
        definition = """
        # Usually a tetrode but can be any valid probe (such as a neuropixel probe)
        -> SpikeSorting
        probe_id : int # Given by probegeometry file
        ---
        probe_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Channel(classes["computed"]):
        definition = """
        # Corresponds to a single electrode on the probe
        -> Probe
        channel_id : int # Given by probegeometry file
        ---
        ap_coord : decimal(5, 0) # Probe anterior-posterior coordinate relative to bregma (mm)
        ml_coord : decimal(5, 0) # Probe medial-lateral coordinate relative to bregma (mm)
        dv_coord : decimal(5, 0) # Probe dorsal-ventral coordinate relative to bregma (mm)
        channel_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class LFP(classes["computed"]):
        definition = """
        # Local field potential
        -> Channel
        ---
        lfp : longblob # LFP array for session, low-pass filtered, in uV
        lfp_sample_rate : int # Set to be 2.5 times the sample rate
        lfp_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Unit(classes["computed"]):
        definition = """
        # Unit found by spikesorting
        -> Probe
        unit_id : int # Unique ID for this unit
        ---
        ap_coord : decimal(5, 0) # Probe anterior-posterior coordinate relative to bregma (mm)
        ml_coord : decimal(5, 0) # Probe medial-lateral coordinate relative to bregma (mm)
        dv_coord : decimal(5, 0) # Probe dorsal-ventral coordinate relative to bregma (mm)
        unit_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class SpikeTrain(classes["computed"]):
        definition = """
        # Timestamps for when the unit fires
        -> Unit
        ---
        spiketrain: mediumblob # Numpy array of spike times in seconds
        spiketrain_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Waveform(classes["computed"]):
        definition = """
        # Waveform for each time the unit fires
        -> Unit
        -> Channel
        ---
        waveform : longblob # Numpy array shape n*m, where n is number of spikes, m is number of samples, in uV
        waveform_sample_rate : int # Original sample rate from acquisition system
        ms_before : float # Milliseconds before peak extracted
        ms_after : float # Milliseconds after peak extracted
        waveform_deleted = 'False' : enum('False', 'True') # Implements a temporary delete function
        """

Behaviour
---------

.. code-block:: python

    @schema
    class BehaviourRig(classes["manual"]):
        definition = """
        # Custom json mapping for the behaviour rig
        -> metadata.Experimenter
        behaviourrig_id: smallint # Unique identifier for the behaviour rig (auto_increment)
        ---
        behaviourrig_name: varchar(40) # Name of the behaviour rig
        rig_json: json # Custom json for the behaviour rig
        behaviourrig_deleted = 'False': enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class MaskFunction(classes["manual"]):
        definition = """
        # Custom analysis function holding the masking functions for a rig
        -> BehaviourRig
        mask_id: smallint # Unique identifier for the mask function in the rig (auto_increment)
        ---
        maskfunction_name: varchar(40) # Name of the mask function
        mask_function: json # Serialised version of the mask function
        maskfunction_description: varchar(500) # Description of the mask function
        maskfunction_deleted = 'False': enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class LabelledFrames(classes["manual"]):
        definition = """
        # Holds the user labelled frames for deeplabcut training
        -> BehaviourRig
        -> metadata.Experiment
        dlcmodel_id: smallint # Unique identifier for the DLC model in the rig (auto_increment)
        ---
        dlcparams: json # Parameters for the DLC model
        labelled_frames: attach@labelled_frames # External data for the labelled frames
        labelledframes_in_compute: enum('False', 'True') # Are the labelled frames in a computation
        labelledframes_deleted = 'False': enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class DLCModel(classes["computed"]):
        definition = """
        # The trained DLC model for a particular rig
        -> BehaviourRig
        -> metadata.Experiment
        dlcmodel_id: smallint # Unique identifier for the DLC model in the rig (auto_increment)
        ---
        dlcmodel: attach@dlcmodel # External data for the DLC model
        evaluation_metrics: json # Evaluation metrics for the DLC model
        evaluated_frames: attach@evaluated_frames # Labelled images for validation
        dlcmodel_deleted = 'False': enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Feature(classes["manual"]):
        definition = """
        # Features for objects in the behaviour rig
        -> BehaviourRig
        feature_id: int # Unique identifier for a feature in the rig (auto_increment)
        ---
        feature_name: varchar(40) # Name of the feature
        source_type: enum('acquisition', 'stimulus', 'processing', 'deeplabcut') # Type of source for the feature
        data_type: enum('analog', 'digital', 'interval', 'kinematics') # Type of data for the feature
        feature_description: varchar(500) # Description of the feature
        feature_data=null: attach@feature_behaviour # External data for the feature
        feature_deleted = 'False': enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class World(classes["manual"]):
        definition = """
        # Represents the world for a particular session
        -> metadata.Session
        ---
        -> BehaviourRig
        dlc_training = 'False': enum('False', 'True') # Was the DLC model trained on this data
        world_deleted = 'False': enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Video(classes["imported"]):
        definition = """
        # Represents the video for a particular session
        -> World
        -> BehaviourRig
        video_id: smallint # Unique identifier for the video in the session (auto_increment)
        ---
        video: attach@behaviour_video # External data for the video
        timestamps = NULL: longblob # numpy array of event timestamps
        video_deleted = 'False': enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Self(classes["manual"]):
        definition = """
        # Represents the self for a particular session
        -> World
        -> metadata.Animal
        ---
        self_deleted = 'False': enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class Object(classes["imported"]):
        definition = """
        # Represents the environment objects for a particular session
        -> World
        -> Feature
        ---
        object_name: varchar(40) # Name of the object
        object_type: enum('World', 'Self') # Type of object
        -> [nullable] Self
        object_deleted = 'False': enum('False', 'True') # Implements a temporary delete function
        """

    @schema
    class AnalogEvents(classes["imported"]):
        definition = """
        # Represents the analog events for a particular session
        -> Object
        ---
        data: longblob # numpy array of event values
        -> [nullable] Self
        timestamps: longblob # numpy array of event timestamps
        x_coordinate: float # X coordinate of the feature in the rig
        y_coordinate: float # Y coordinate of the feature in the rig
        z_coordinate: float # Z coordinate of the feature in the rig
        unit: varchar(40) # units of the array
        analogevents_name: varchar(40) # Name of the analog event
        analogevents_deleted = 'False': enum('False', 'True')
        """

    @schema
    class DigitalEvents(classes["imported"]):
        definition = """
        # Represents the digital events for a particular session
        -> Object
        ---
        data: longblob # numpy array of event values
        -> [nullable] Self
        timestamps: longblob # numpy array of event timestamps
        unit: varchar(40) # units of the array
        x_coordinate: float # X coordinate of the feature in the rig
        y_coordinate: float # Y coordinate of the feature in the rig
        z_coordinate: float # Z coordinate of the feature in the rig
        digitalevents_name: varchar(40) # Name of the digital event
        digitalevents_deleted = 'False': enum('False', 'True')
        """

    @schema
    class IntervalEvents(classes["imported"]):
        definition = """
        # Represents the interval events for a particular session
        -> Object
        ---
        data: longblob # numpy array of event values
        -> [nullable] Self
        timestamps: longblob # numpy array of event timestamps
        x_coordinate: float # X coordinate of the feature in the rig
        y_coordinate: float # Y coordinate of the feature in the rig
        z_coordinate: float # Z coordinate of the feature in the rig
        intervalevents_name: varchar(40) # Name of the interval event
        intervalevents_deleted = 'False': enum('False', 'True')
        """

    @schema
    class Mask(classes["imported"]):
        definition = """
        # Splits the recording session into individual trials
        -> World
        -> MaskFunction
        ---
        data: longblob # numpy array of event values
        timestamps: longblob # numpy array of event timestamps
        mask_name: varchar(40) # Name of the mask
        mask_deleted = 'False': enum('False', 'True')
        """

    @schema
    class Kinematics(classes["computed"]):
        definition = """
        # Animal kinematics from DeepLabCut
        -> Object
        -> Video
        ---
        data: longblob # numpy array of kinematic values
        -> [nullable] DLCModel
        -> [nullable] Self
        timestamps: longblob # numpy array of kinematic timestamps
        kinematics_name: varchar(40) # Name of the kinematics
        kinematics_deleted = 'False': enum('False', 'True')
        """
