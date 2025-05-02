import datajoint as dj


def schema(conn, classes):
    schema = dj.Schema(
        schema_name="antelop_behaviour", connection=conn, create_tables=True
    )

    # import the metadata schema
    metadata = dj.create_virtual_module("metadata", "antelop_metadata")

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

    tables = {
        "BehaviourRig": BehaviourRig,
        "MaskFunction": MaskFunction,
        "LabelledFrames": LabelledFrames,
        "DLCModel": DLCModel,
        "Feature": Feature,
        "World": World,
        "Video": Video,
        "Self": Self,
        "Object": Object,
        "AnalogEvents": AnalogEvents,
        "DigitalEvents": DigitalEvents,
        "IntervalEvents": IntervalEvents,
        "Mask": Mask,
        "Kinematics": Kinematics,
    }

    return tables, schema
