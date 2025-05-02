import datajoint as dj


def schema(conn, classes):
    schema = dj.Schema(schema_name="antelop_ephys", connection=conn)

    # import the metadata schema
    metadata = dj.create_virtual_module("metadata", "antelop_metadata")

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

    tables = {
        "ProbeGeometry": ProbeGeometry,
        "SortingParams": SortingParams,
        "ProbeInsertion": ProbeInsertion,
        "Recording": Recording,
        "SpikeSorting": SpikeSorting,
        "Probe": Probe,
        "Channel": Channel,
        "LFP": LFP,
        "Unit": Unit,
        "SpikeTrain": SpikeTrain,
        "Waveform": Waveform,
    }

    return tables, schema
