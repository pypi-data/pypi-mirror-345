import jsonschema
from pathlib import Path
from antelop.utils.analysis_utils import import_analysis, instantiate_function
from antelop.connection.connect_utils import connect, thread_connect
from antelop.connection.transaction import transaction_context
from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from pynwb.file import Subject
from pynwb.image import ImageSeries
from pynwb.misc import IntervalSeries
from pynwb.behavior import (
    BehavioralTimeSeries,
    BehavioralEpochs,
    Position,
    SpatialSeries,
)
import numpy as np
import tempfile
import yaml
import json
import shutil
import zipfile
import pandas as pd
from functools import partial
import inspect
import traceback
import os
from uuid import uuid4

"""
It's important to mention how our naming conventions work for animals.
Some behavioural events could belong to a specific animal a priori.
Other events, we won't know which animal they belong to until we perform tracking with deeplabcut.
In the first case, the animal will be numbered in the rig specification. For example, a setup with 2 animals will have
features with source_type as a dictionary, with the key 'acquisition' and values 1 or 2.
In the second case, the value of the key 'acquisition' will be -1.
Such objects in the database will initally refer to neither world or self.
After tracking, we will be able to split the arrays, splitting the object table, and referencing the correct self entries.
"""


def validate_behaviour_rig(data):
    """
    Function validates an input behavior rig specification against our custom schema
    :param data: dict
    :return: Bool
    """

    # first, define the schema
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "specification": {"type": "string", "const": "antelop-behaviour"},
            "version": {"type": "string"},
            "reference_point": {"type": "string"},
            "features": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "source": {
                            "type": "object",
                            "properties": {
                                "source_type": {
                                    "type": "string",
                                    "enum": [
                                        "acquisition",
                                        "stimulus",
                                        "processing",
                                        "deeplabcut",
                                    ],
                                },
                                "module": {"type": "string"},
                                "video": {"type": "string"},
                            },
                            "required": ["source_type"],
                        },
                        "ownership": {
                            "type": "object",
                            "properties": {
                                "ownership": {
                                    "type": "string",
                                    "enum": ["world", "self"],
                                },
                                "animal": {"type": "integer"},
                            },
                            "required": ["ownership"],
                        },
                        "data_type": {
                            "type": "string",
                            "enum": ["digital", "analog", "interval", "kinematics"],
                        },
                        "coordinates": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {"type": "number"},
                        },
                        "description": {"type": "string"},
                    },
                    "required": ["name", "source", "data_type", "description"],
                },
            },
            "videos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "format": {"type": "string", "enum": ["avi", "mp4", "mov"]},
                        "reference_point": {"type": "string"},
                    },
                    "required": ["name", "description", "format"],
                },
            },
        },
        "required": ["specification", "version", "reference_point", "features"],
    }

    # now validate the input data
    try:
        jsonschema.validate(data, schema)
    except jsonschema.exceptions.ValidationError:
        return "Json file not valid!"

    # also check the names are all unique
    names = [i["name"] for i in data["features"]]
    if len(names) != len(set(names)):
        return "Feature names not unique!"
    else:
        return True


def validate_mask(data):
    """
    Function validates an input behavior rig specification against our custom schema
    :param data: dict
    :return: Bool
    """

    # first, define the schema
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "function": {"type": "string"},
            },
            "required": ["name", "description", "function"],
        },
    }

    # now validate the input data
    try:
        jsonschema.validate(data, schema)
    except jsonschema.exceptions.ValidationError:
        return "Masks not valid!"
    else:
        return True


def insert_features(primary_key, rig_json):
    """
    Function populates the features table from the json file,
    leaving the feature empty
    """

    # create list to store insert dicts
    feature_list = []

    for i, feature in enumerate(rig_json["features"]):
        # create insert dict
        insert_feature = {}

        # make the feature fit the datajoint table
        insert_feature["experimenter"] = primary_key["experimenter"]
        insert_feature["behaviourrig_id"] = primary_key["behaviourrig_id"]
        insert_feature["feature_id"] = i + 1
        insert_feature["feature_name"] = feature["name"]
        insert_feature["source_type"] = feature["source"]["source_type"]
        insert_feature["data_type"] = feature["data_type"]
        insert_feature["feature_description"] = feature["description"]
        insert_feature["feature_data"] = None

        # append to list
        feature_list.append(insert_feature)

    return feature_list


def upload_rig_json(
    experimenter, rig_name, rigfile, masklist, username=None, password=None, conn=None
):
    """
    Function validates the rig json, converts and uploads it along with corresponding features

    Inputs:
        experimenter (str): experimenter username
        rig_name (str): name of the rig
        rig_json (path): path to the rig json file
        masklist (list of dict): list of mask dictionaries, with keys 'name', 'description', 'function'
    """

    conn_up, tables_up = thread_connect(conn, username, password)

    with open(rigfile, "r") as f:
        read_rig = json.load(f)

    # validate the rig file
    assert validate_behaviour_rig(read_rig)
    assert validate_mask(masklist)

    insert_dict = {
        "experimenter": experimenter,
        "behaviourrig_name": rig_name,
        "rig_json": read_rig,
        "masks": masklist,
    }

    with transaction_context(tables_up["BehaviourRig"].connection):
        tables_up["BehaviourRig"].insert1(insert_dict)
        primary = {
            key: val
            for key, val in insert_dict.items()
            if key not in ["rig_json", "masks"]
        }
        primary_key = (tables_up["BehaviourRig"] & primary).proj().fetch1()

        feature_list = insert_features(primary_key, read_rig)

        tables_up["Feature"].insert(feature_list)


def make_timestamps(length, sample_rate):
    """
    Function makes timestamps for analog events
    """
    return np.linspace(length) / sample_rate


def check_nwb(world, tables, nwbpath):
    """
    Function reads an NWB file and the database features and checks the nwb file is valid
    """

    # pull the features from the database
    rig_json = (tables["BehaviourRig"] & world).fetch1("rig_json")
    features = rig_json["features"]
    videos = rig_json["videos"]

    try:
        # open nwb file
        with NWBHDF5IO(nwbpath, "r") as io:
            read_nwbfile = io.read()

            video_names = {}

            # check the videos
            for i, video in enumerate(videos):
                # get the video path
                video_name = video["name"]
                assert video_name in read_nwbfile.acquisition.keys(), (
                    f"Video {video} not in NWB file"
                )
                video_relative_path = read_nwbfile.acquisition[
                    video_name
                ].external_file[0]
                video_full_path = nwbpath.parent / Path(video_relative_path)
                assert video_full_path.exists(), f"Video {video_name} not in directory"

            # insert the features and objects
            for feature in features:
                # get the data and timestamps
                if feature["source"]["source_type"] == "acquisition":
                    assert hasattr(read_nwbfile.acquisition[feature["name"]], "data")

                elif feature["source"]["source_type"] == "stimulus":
                    assert hasattr(read_nwbfile.stimulus[feature["name"]], "data")

                elif feature["source"]["source_type"] == "processing":
                    assert hasattr(
                        read_nwbfile.processing[feature["source"]["module"]][
                            feature["name"]
                        ],
                        "data",
                    )

    except AssertionError:
        return False

    else:
        return True


def insert_nwb(world, selfs, nwbpath, username=None, password=None):
    """
    Function reads an NWB file and the database features and inserts the data into the database

    Args:
        session (dict): session primary key
        animals (list of dict): animal primary keys
        nwbpath (Path): path to the nwb file

    Returns:
        None
    """

    conn_insert, tables_insert = thread_connect(username=username, password=password)

    # pull the features from the database
    rig_json = (tables_insert["BehaviourRig"] & world).fetch1("rig_json")
    masks = (
        (tables_insert["MaskFunction"] & world)
        .proj("maskfunction_name")
        .fetch(as_dict=True)
    )
    features = rig_json["features"]
    videos = rig_json["videos"]

    with transaction_context(conn_insert):
        # insert world
        tables_insert["World"].insert1(world)
        if "world_deleted" in world.keys():
            del world["world_deleted"]
        if "dlc_training" in world.keys():
            del world["dlc_training"]
        behaviourrig_id = world["behaviourrig_id"]
        selfkey = world.copy()
        del selfkey["behaviourrig_id"]

        # insert selfs
        for self in selfs.values():
            tables_insert["Self"].insert1(
                {**self, "session_id": world["session_id"], "self_deleted": "False"}
            )

        # open nwb file
        with NWBHDF5IO(nwbpath, "r") as io:
            read_nwbfile = io.read()

            video_names = {}

            # insert the videos
            for i, video in enumerate(videos):
                # get the video path
                video_name = video["name"]
                video_relative_path = read_nwbfile.acquisition[
                    video_name
                ].external_file[0]
                if hasattr(read_nwbfile.acquisition[video_name], "timestamps"):
                    timestamps = read_nwbfile.acquisition[video_name].timestamps[:]
                else:
                    timestamps = None
                video_full_path = nwbpath.parent / Path(video_relative_path)
                video_names[video_name] = i + 1

                # insert the video
                tables_insert["Video"].insert1(
                    {
                        **world,
                        "video_id": i + 1,
                        "video": str(video_full_path),
                        "timestamps": timestamps,
                        "video_deleted": "False",
                    },
                    allow_direct_insert=True,
                )

            # insert the features and objects
            for feature in features:
                # calculate feature id from feature name
                query = (
                    tables_insert["Feature"] & world & {"feature_name": feature["name"]}
                )
                feature_id, feature_name = query.fetch1("feature_id", "feature_name")

                # compute if world or self
                if feature["ownership"]["ownership"] == "world":
                    object_type = "World"
                    animal_id = None

                elif feature["ownership"]["ownership"] == "self":
                    object_type = "Self"
                    animal_id = selfs[feature["ownership"]["animal"]]["animal_id"]

                # feature dict to insert
                world["behaviourrig_id"] = behaviourrig_id
                insert_dict = {
                    "feature_id": feature_id,
                    **world,
                    "object_name": feature_name,
                    "object_type": object_type,
                    "animal_id": animal_id,
                    "object_deleted": "False",
                }

                # insert feature dict
                tables_insert["Object"].insert1(insert_dict, allow_direct_insert=True)

                # does the data need units
                if feature["data_type"] in ["digital", "analog"]:
                    need_unit = True
                else:
                    need_unit = False

                # does the data need coordinates
                if feature["data_type"] in ["digital", "analog", "interval"]:
                    coordinates = {
                        "x_coordinate": feature["coordinates"][0],
                        "y_coordinate": feature["coordinates"][1],
                        "z_coordinate": feature["coordinates"][2],
                    }

                # get the data and timestamps
                if feature["source"]["source_type"] == "acquisition":
                    data = read_nwbfile.acquisition[feature["name"]].data[:]
                    if hasattr(read_nwbfile.acquisition[feature["name"]], "timestamps"):
                        timestamps = read_nwbfile.acquisition[
                            feature["name"]
                        ].timestamps[:]
                    else:
                        sample_rate = read_nwbfile.acquisition[feature["name"]].rate
                        timestamps = make_timestamps(len(data), sample_rate)
                    if need_unit:
                        unit = read_nwbfile.acquisition[feature["name"]].unit

                elif feature["source"]["source_type"] == "stimulus":
                    data = read_nwbfile.stimulus[feature["name"]].data[:]
                    if hasattr(read_nwbfile.stimulus[feature["name"]], "timestamps"):
                        timestamps = read_nwbfile.stimulus[feature["name"]].timestamps[
                            :
                        ]
                    else:
                        sample_rate = read_nwbfile.stimulus[feature["name"]].rate
                        timestamps = make_timestamps(len(data), sample_rate)
                    if need_unit:
                        unit = read_nwbfile.stimulus[feature["name"]].unit

                elif feature["source"]["source_type"] == "processing":
                    data = read_nwbfile.processing[feature["source"]["module"]][
                        feature["name"]
                    ].data[:]  # need to check if this is how we access data in modules
                    if hasattr(
                        read_nwbfile.processing[feature["source"]["module"]][
                            feature["name"]
                        ],
                        "timestamps",
                    ):
                        timestamps = read_nwbfile.processing[
                            feature["source"]["module"]
                        ][feature["name"]].timestamps[:]
                    else:
                        sample_rate = read_nwbfile.processing[
                            feature["source"]["module"]
                        ][feature["name"]].rate
                        timestamps = make_timestamps(len(data), sample_rate)
                    if need_unit:
                        unit = read_nwbfile.processing[feature["source"]["module"]][
                            feature["name"]
                        ].unit

                # compute if the event is digital or analog
                if feature["data_type"] == "digital":
                    data_insert = {
                        "feature_id": feature_id,
                        **world,
                        "animal_id": animal_id,
                        "data": data,
                        "timestamps": timestamps,
                        **coordinates,
                        "unit": unit,
                        "digitalevents_name": feature_name,
                        "digitalevents_deleted": "False",
                    }
                    tables_insert["DigitalEvents"].insert1(
                        data_insert, allow_direct_insert=True
                    )

                elif feature["data_type"] == "analog":
                    data_insert = {
                        "feature_id": feature_id,
                        **world,
                        "animal_id": animal_id,
                        "data": data,
                        "timestamps": timestamps,
                        **coordinates,
                        "unit": unit,
                        "analogevents_name": feature_name,
                        "analogevents_deleted": "False",
                    }
                    tables_insert["AnalogEvents"].insert1(
                        data_insert, allow_direct_insert=True
                    )

                elif feature["data_type"] == "interval":
                    data_insert = {
                        "feature_id": feature_id,
                        **world,
                        "animal_id": animal_id,
                        "data": data,
                        "timestamps": timestamps,
                        **coordinates,
                        "intervalevents_name": feature_name,
                        "intervalevents_deleted": "False",
                    }
                    tables_insert["IntervalEvents"].insert1(
                        data_insert, allow_direct_insert=True
                    )

                elif feature["data_type"] == "kinematics":
                    if feature["source"]["source_type"] == "processing":
                        # get the video
                        video_name = feature["source"]["video"]
                        video_id = video_names[video_name]

                        # insert the data
                        data_insert = {
                            "feature_id": feature_id,
                            **world,
                            "video_id": video_id,
                            "animal_id": animal_id,
                            "data": data,
                            "timestamps": timestamps,
                            "kinematics_name": feature_name,
                            "kinematics_deleted": "False",
                        }
                        tables_insert["Kinematics"].insert1(
                            data_insert, allow_direct_insert=True
                        )

            # compute the masks
            for i, mask in enumerate(masks):
                mask_function = instantiate_function(mask, tables_insert)
                name = mask["maskfunction_name"]
                del mask["maskfunction_name"]

                # run the function
                output = mask_function(world)
                data, timestamps = output["data"], output["timestamps"]

                # insert the mask
                tables_insert["Mask"].insert1(
                    {
                        **world,
                        "mask_id": mask["maskfunction_id"],
                        "data": data,
                        "timestamps": timestamps,
                        "mask_name": mask["maskfunction_name"],
                        "mask_deleted": "False",
                    },
                    allow_direct_insert=True,
                )


def recompute_masks(restriction, username=None, password=None):
    conn_insert, tables_insert = thread_connect(username=username, password=password)

    # pull the world from the database
    worlds = (tables_insert["World"] & restriction).proj().fetch(as_dict=True)

    for world in worlds:
        # pull the masks from the database
        masks = (
            (
                tables_insert["MaskFunction"] * tables_insert["World"]
                - tables_insert["Mask"]
                & world
            )
            .proj("maskfunction_name")
            .fetch(as_dict=True)
        )

        # compute the masks
        for mask in masks:
            mask_function = instantiate_function(mask, tables_insert)
            name = mask["maskfunction_name"]
            del mask["maskfunction_name"]

            # run the function
            output = mask_function(world)
            data, timestamps = output["data"], output["timestamps"]

            # insert the mask
            if tables_insert["Mask"] & mask:
                tables_insert["Mask"].update1(
                    {
                        **mask,
                        "data": data,
                        "timestamps": timestamps,
                        "mask_deleted": "False",
                    }
                )
            else:
                tables_insert["Mask"].insert1(
                    {
                        **mask,
                        "data": data,
                        "timestamps": timestamps,
                        "mask_name": name,
                        "mask_deleted": "False",
                    },
                    allow_direct_insert=True,
                )


def check_animals(rig_dict):
    """
    Function reads our custom rig schema and checks how many animals are in the rig
    """
    animals = []
    for feature in rig_dict["features"]:
        if feature["ownership"]["ownership"] == "self":
            animals.append(feature["ownership"]["animal"])

    # return the unique animals in order
    animals = sorted(list(set(animals)))
    animals = [i for i in animals if i != -1]
    return animals


def extract_frames(conf, algo):
    import deeplabcut

    deeplabcut.extract_frames(conf, algo=algo, userfeedback=False)


def select_masks(tables):
    """
    Function displays a streamlit data editor that allows the user to select the masks they want to compute
    """

    # pull available functions
    fcts = import_analysis(tables["Experimenter"].connection, tables)
    fctsls = [
        f"{i}.{j.name}" for i in fcts for j in fcts[i] if hasattr(j, "mask") and j.mask
    ]

    if len(fctsls) == 0:
        st.error("No mask functions available!")
        return

    default = [{"enabled": False, "description": "", "function": fctsls[0]}]
    edited_masks = st.data_editor(
        default,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "enabled": st.column_config.CheckboxColumn(help="Enable mask computation"),
            "function": st.column_config.SelectboxColumn(
                help="Select your function to compute your masks",
                required=True,
                options=fctsls,
            ),
            "description": "description",
        },
    )
    enabled_masks = [i for i in edited_masks if i["enabled"]]
    return enabled_masks


def insert_masks(key, masks, id, tables):
    """
    Function makes dataframe out of masks
    """
    df = pd.DataFrame(masks)
    del df["enabled"]
    df["experimenter"] = key["experimenter"]
    df["behaviourrig_id"] = key["behaviourrig_id"]
    df.rename(
        columns={"name": "mask_name", "description": "maskfunction_description"},
        inplace=True,
    )
    df["mask_id"] = range(id, id + len(df))

    new_serialise = partial(serialise_function, tables=tables)
    df["mask_function"] = df["function"].apply(new_serialise)
    new_name = partial(function_name, tables=tables)
    df["maskfunction_name"] = df["function"].apply(new_name)

    del df["function"]

    return df


def serialise_function(function_name, tables):
    # from a functions folder.name format, return json function code

    fcts = import_analysis(tables["Experimenter"].connection, tables)
    for folder in fcts:
        if function_name.split(".")[0] == folder:
            for fct in fcts[folder]:
                if fct.name == function_name.split(".")[1]:
                    function = fct
                    break
            break
    code = inspect.getsource(function.__class__.__bases__[0])

    return json.dumps(code)


def function_name(function_name, tables):
    # from a functions folder.name format, return class name

    fcts = import_analysis(tables["Experimenter"].connection, tables)
    for folder in fcts:
        if function_name.split(".")[0] == folder:
            for fct in fcts[folder]:
                if fct.name == function_name.split(".")[1]:
                    function = fct
                    break
            break
    name = function.__class__.__bases__[0].__name__
    return name


def display_dlc_images(DLCModel, key):
    """
    Function displays the train and test images for a DLCModel
    """

    # first make temp directory
    name = f"{key['experimenter']}_{key['behaviourrig_id']}_{key['experiment_id']}_{key['dlcmodel_id']}"
    tmpdir = Path(tempfile.gettempdir())
    dlc_dir = tmpdir / "antelop_dlc"
    folder = dlc_dir / name / "evaluation_images"
    folder.mkdir(parents=True, exist_ok=True)

    # download images and unzip
    key = (DLCModel & key).fetch1("evaluated_frames", download_path=folder)
    zip_path = Path(key)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(folder)

    return folder


def delete_masks(key, masks, tables):
    """
    Computes masks to be deleted and permanently deletes them
    """

    to_delete = masks[masks["maskfunction_deleted"]]
    to_delete["experimenter"] = key["experimenter"]
    to_delete["behaviourrig_id"] = key["behaviourrig_id"]
    del to_delete["maskfunction_deleted"]
    del to_delete["mask_function"]
    del to_delete["maskfunction_description"]

    (tables["MaskFunction"] & to_delete).delete_quick()


def export_nwb(session, download_path, username=None, password=None, conn=None):
    """
    Function exports the NWB file for a session
    """
    assert set(session.keys()) == {
        "experimenter",
        "experiment_id",
        "session_id",
    }, "Function takes session primary key only"

    conn_export, tables_export = connect(username, password, conn)

    # pull session info
    session_info = (
        tables_export["Session"]
        * tables_export["Experiment"]
        * tables_export["Experimenter"]
        & session
    ).fetch1()

    # make nwb root
    nwbfile = NWBFile(
        session_description=session_info["session_notes"],
        identifier=str(uuid4()),
        session_id=f"{session_info['experimenter']}_{session_info['experiment_id']}_{session_info['session_id']}",
        session_start_time=session_info["session_timestamp"],
        experimenter=session_info["full_name"],
        lab=session_info["group"],
        institution=session_info["institution"],
        experiment_description=session_info["experiment_notes"],
    )

    # pull all animals - can be from behaviour or ephys
    query = (
        tables_export["Animal"]
        & (tables_export["Self"] * tables_export["Session"] & session)
    ).proj() + (
        tables_export["Animal"]
        & (tables_export["Recording"] * tables_export["Session"] & session)
    ).proj()
    keys = query.fetch(as_dict=True)
    animals = (tables_export["Animal"] & keys).fetch(as_dict=True)

    for i, animal in enumerate(animals):
        subject = Subject(
            subject_id=str(animal["animal_id"]),
            species="Mus Musculus",
            age=animal["age"],
            description=animal["animal_notes"],
            sex=animal["sex"],
            strain=animal["genotype"],
        )
        if len(animal) == 1:
            nwbfile.subject = subject
        else:
            setattr(nwbfile, f"subject_{i}", subject)

    # start context manager and start writing to file
    # context manager simply deletes file if there's an error to avoid partially written nwb
    # we then want to write to nwb in chunks as datasets can be large
    with SafeNWBContext(download_path) as f:
        with NWBHDF5IO(f, "w") as io:
            io.write(nwbfile)

        # ephys data
        recs = (
            (tables_export["Recording"] & session & animals).proj().fetch(as_dict=True)
        )
        for rec in recs:
            pass

            # add probe
            # issue with contact id
            """
            probe = (tables_export['Animal'] * tables_export['ProbeInsertion'] * tables_export['ProbeGeometry'] & rec).fetch1('probe')
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as tmpfile:
                json.dump(probe, tmpfile)
                path = tmpfile.name
            probefile = pi.read_probeinterface(path)
            ndx_probe = ndx_probeinterface.from_probeinterface(probefile.probes[0])
            nwbfile.add_device(ndx_probe)
            """

        # behaviour data
        with NWBHDF5IO(f, "r+") as io:
            nwbfile = io.read()
            behavior_module = nwbfile.create_processing_module(
                name="behavior", description="behavioral data"
            )
            io.write(nwbfile)

        # analog events
        analog_events = (
            (tables_export["AnalogEvents"] & session).proj().fetch(as_dict=True)
        )
        for analog_event in analog_events:
            data = (
                tables_export["AnalogEvents"] * tables_export["Feature"] & analog_event
            ).fetch1()
            timeseries = TimeSeries(
                name=data["analogevents_name"],
                data=data["data"],
                timestamps=data["timestamps"],
                description=data["feature_description"],
                unit=data["unit"],
            )
            with NWBHDF5IO(f, "r+") as io:
                nwbfile = io.read()
                if data["source_type"] == "processing":
                    behaviour_timeseries = BehavioralTimeSeries(
                        time_series=timeseries, name=data["analogevents_name"]
                    )
                    nwbfile.processing["behavior"].add(behaviour_timeseries)
                elif data["source_type"] == "stimulus":
                    nwbfile.add_stimulus(timeseries)
                elif data["source_type"] == "acquisition":
                    nwbfile.add_acquisition(timeseries)
                io.write(nwbfile)

        # digital events
        digital_events = (
            (tables_export["DigitalEvents"] & session).proj().fetch(as_dict=True)
        )
        for digital_event in digital_events:
            data = (
                tables_export["DigitalEvents"] * tables_export["Feature"]
                & digital_event
            ).fetch1()
            timeseries = TimeSeries(
                name=data["digitalevents_name"],
                data=data["data"],
                timestamps=data["timestamps"],
                description=data["feature_description"],
                unit=data["unit"],
            )
            with NWBHDF5IO(f, "r+") as io:
                nwbfile = io.read()
                if data["source_type"] == "processing":
                    behaviour_timeseries = BehavioralTimeSeries(
                        time_series=timeseries, name=data["digitalevents_name"]
                    )
                    nwbfile.processing["behavior"].add(behaviour_timeseries)
                elif data["source_type"] == "stimulus":
                    nwbfile.add_stimulus(timeseries)
                elif data["source_type"] == "acquisition":
                    nwbfile.add_acquisition(timeseries)
                io.write(nwbfile)

        # interval events
        interval_events = (
            (tables_export["IntervalEvents"] & session).proj().fetch(as_dict=True)
        )
        for interval_event in interval_events:
            data = (
                tables_export["IntervalEvents"] * tables_export["Feature"]
                & interval_event
            ).fetch1()
            timeseries = IntervalSeries(
                name=data["intervalevents_name"],
                data=data["data"],
                timestamps=data["timestamps"],
                description=data["feature_description"],
            )
            with NWBHDF5IO(f, "r+") as io:
                nwbfile = io.read()
                if data["source_type"] == "processing":
                    behaviour_timeseries = BehavioralTimeSeries(
                        time_series=timeseries, name=data["intervalevents_name"]
                    )
                    nwbfile.processing["behavior"].add(behaviour_timeseries)
                elif data["source_type"] == "stimulus":
                    nwbfile.add_stimulus(timeseries)
                elif data["source_type"] == "acquisition":
                    nwbfile.add_acquisition(timeseries)
                io.write(nwbfile)

        # interval events
        kinematics = (tables_export["Kinematics"] & session).proj().fetch(as_dict=True)
        with NWBHDF5IO(f, "r+") as io:
            nwbfile = io.read()
            position = Position()
            nwbfile.processing["behavior"].add(position)
            io.write(nwbfile)
        for kinematic in kinematics:
            rig_json = (tables_export["BehaviourRig"] & kinematic).fetch1("rig_json")
            data = (
                tables_export["Kinematics"] * tables_export["Feature"] & kinematic
            ).fetch1()
            timeseries = SpatialSeries(
                name=data["kinematics_name"],
                data=data["data"],
                timestamps=data["timestamps"],
                description=data["feature_description"],
                reference_frame=rig_json["reference_point"],
            )
            with NWBHDF5IO(f, "r+") as io:
                nwbfile = io.read()
                nwbfile.processing["behavior"]["Position"].add_spatial_series(
                    timeseries
                )
                io.write(nwbfile)

        # masks
        mask_epochs = BehavioralEpochs(name="masks")
        masks = (tables_export["Mask"] & session).proj().fetch(as_dict=True)
        for mask in masks:
            data = (
                tables_export["Mask"] * tables_export["MaskFunction"] & mask
            ).fetch1()
            timeseries = IntervalSeries(
                name=data["mask_name"],
                data=data["data"],
                timestamps=data["timestamps"],
                description=data["maskfunction_description"],
            )
            mask_epochs.add_interval_series(timeseries)
        with NWBHDF5IO(f, "r+") as io:
            nwbfile = io.read()
            nwbfile.processing["behavior"].add(mask_epochs)
            io.write(nwbfile)

        # videos
        videos = (tables_export["Video"] & session).proj().fetch(as_dict=True)
        for video in videos:
            rig_json = (tables_export["BehaviourRig"] & video).fetch1("rig_json")
            video_name = rig_json["videos"][video["video_id"] - 1]["name"]
            video_description = rig_json["videos"][video["video_id"] - 1]["description"]
            data = (tables_export["Video"] & video).fetch1(
                download_path=Path(download_path).parent
            )
            behaviour_video = ImageSeries(
                name=video_name,
                external_file=[data["video"]],
                starting_frame=[0],
                format="external",
                timestamps=data["timestamps"],
                unit="s",
                description=video_description,
            )
            with NWBHDF5IO(f, "r+") as io:
                nwbfile = io.read()
                nwbfile.add_acquisition(behaviour_video)
                io.write(nwbfile)


class SafeNWBContext:
    """
    Context manager deletes NWB file if an error occurs
    Designed so that the file should be opened within this context, several times if necessary for memory reasons.
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        return self.file_path

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            print(f"Exception occurred: {exc_value}")
            traceback.print_tb(exc_traceback)

            if os.path.exists(self.file_path):
                os.remove(self.file_path)
                print(f"File {self.file_path} deleted due to error.")
