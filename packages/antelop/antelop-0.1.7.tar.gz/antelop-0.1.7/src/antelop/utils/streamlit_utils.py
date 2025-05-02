"""
Additional utilities for antelop's web gui, written in streamlit.

Author: Rory Bedford
Date: 07/07/23
"""

from pathlib import Path
import streamlit as st
from datetime import datetime
import shutil
import tempfile
from antelop.utils.datajoint_utils import (
    parent_primaries,
    ancestor_primaries,
    query_without_external,
    searchable_tables,
    check_spare_key,
    insertable_tables,
    delete_restriction,
    get_tablename,
    get_ephys_extensions,
)
from antelop.connection.connect_utils import connect, thread_connect
import yaml
from antelop.utils.os_utils import get_config
from antelop.connection import import_schemas
import pandas as pd
import json
import os
from matplotlib.figure import Figure
import numpy as np
from antelop.utils.antelop_utils import select_masks
import inspect
from pathlib import PosixPath


def display_sorting_parameters(paramdict):
    """
    Function which displays the spikesorting parameters selected
    Inputs: paramdict: dictionary with sorting params
    """
    if "matching" in paramdict.keys():
        data = {
            "Stage": ["LFP", "Preprocessing", "Spikesorting", "Agreement matching"],
            "Parameters (values not shown)": [
                [i for i in paramdict["lfp"].keys()],
                [i for i in paramdict["preprocessing"].keys()],
                [i for i in paramdict["spikesorters"].keys()],
                [i for i in paramdict["matching"].keys()],
            ],
        }
        df = pd.DataFrame(data, index=None)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        data = {
            "Stage": ["LFP", "Preprocessing", "Spikesorting"],
            "Parameters (full parameters not shown)": [
                [i for i in paramdict["lfp"].keys()],
                [i for i in paramdict["preprocessing"].keys()],
                [i for i in paramdict["spikesorters"].keys()],
            ],
        }
        df = pd.DataFrame(data, index=None)
        st.dataframe(df, use_container_width=True, hide_index=True)


def waveform_params_input():
    """
    Function retrieves waveform extraction parameters
    """
    st.markdown(
        """*These parameters determine how much of a single spike's waveform should be extracted aronud the waveform peak.*"""
    )
    ms_before = st.slider("Time before peak (ms)", max_value=3.0, value=1.0, step=0.1)
    ms_after = st.slider("Time after peak (ms)", max_value=3.0, value=2.0, step=0.1)

    return {"ms_before": ms_before, "ms_after": ms_after}


def lfp_params_input():
    """
    Function retrieves LFP extraction parameters
    """
    st.markdown(
        "*These parameters govern the filter applied to the recording to extract LFPs and the sample rate at which LFPs are stored.*"
    )
    min_freq = 0.1
    max_freq = st.slider(
        "Maximum frequency (Hz)", min_value=100, max_value=1000, value=300, step=10
    )
    sample_rate = max_freq * 2.5

    st.write("The following parameters are fixed:")
    data = {
        "Minimum frequency (Hz)": [1],
        "Sample rate (Hz) (2.5 times maximum frequency)": [2.5 * max_freq],
    }
    st.dataframe(data)

    return {"min_freq": 1, "max_freq": max_freq, "sample_rate": 2.5 * max_freq}


def agreement_params_input(numsorters):
    """
    Function to allow interactive input of spikesorting agreement matching parameters.
    Inputs: numsorters: number of spikesorters
    Returns: agreement_params: dict with parameters
    """

    data = {
        "delta_time": [0.4],
        "match_score": [0.5],
        "spiketrain_mode": ["union"],
        "minimum_agreement_count": [numsorters],
    }

    # Custom descriptions for each column
    column_descriptions = {
        "delta_time (ms)": "Number of ms to consider coincident spikes (default 0.4 ms)",
        "match_score": "Minimum agreement score to match units (default 0.5)",
        "spiketrain_mode": "Mode to extract agreement spike trains",
        "minimum_agreement_count": "Minimum number of matches among sorters to include a unit",
    }

    # Create the DataFrame
    df = pd.DataFrame(data)

    # Display the column descriptions
    for col_name, description in column_descriptions.items():
        st.write(f"- **{col_name}**: {description}")

    # Display the DataFrame editor
    newdf = st.data_editor(
        df,
        column_config={
            "spiketrain_mode": st.column_config.SelectboxColumn(
                required=True, options=["union", "restriction"]
            ),
            "minimum_agreement_count": st.column_config.SelectboxColumn(
                required=True, options=list(range(numsorters + 1))
            ),
        },
        hide_index=True,
    )

    agreement_params = newdf.loc[0].to_dict()

    return agreement_params


def preprocessing_params_input():
    """
    Function to allow interactive input of spikesorting preprocessing parameters.
    Inputs: None
    Returns: preprocessing_parameters: dict with parameters
    """
    st.markdown(
        """*These parameters specify the preprocessing applied to the recording before spikesorting.*"""
    )
    st.markdown("###### Bandpass filter:")
    min_freq = st.slider(
        "Minimum frequency (Hz)", min_value=100, max_value=1000, value=300, step=10
    )
    max_freq = st.slider(
        "Maximum frequency (Hz)", min_value=1000, max_value=10000, value=6000, step=50
    )
    bandpass_filter = {"freq_min": min_freq, "freq_max": max_freq}
    preprocessing_parameters = {"bandpass_filter": bandpass_filter}

    return preprocessing_parameters


def interactive_sorter_params_input(default, desc, parent_key=""):
    """
    Function to allow interactive input of spikesorting parameters
    for a number of different spikesorters.
    Inputs: default: default values for each parameter (dict)
            desc: descriptions for each parameter (dict)
            parent_key: used for recursion as some dicts are nested
    Returns: parameters: dict with parameters for this sorter
    """

    parameters = {}
    for key, value in default.items():
        full_key = f"{parent_key}.{key}" if parent_key else key

        # try to retrieve the description for each parameter if possible
        try:
            description = desc.get(full_key, "")
        except KeyError:
            description = None

        text = key.upper() + ": " + description.lower() if description else key

        if isinstance(value, dict):  # if it's a dicitonary we recurse
            edited_value = interactive_sorter_params_input(value, desc, full_key)
        elif isinstance(value, list):
            st.text(text)
            edited_value = st.data_editor(value, key=str(default) + text)
        elif isinstance(value, bool):
            edited_value = st.checkbox(text, value=value, key=str(default) + text)
        elif isinstance(value, int):
            edited_value = st.number_input(text, value=value, key=str(default) + text)
        elif isinstance(value, float):
            edited_value = st.number_input(text, value=value, key=str(default) + text)
        elif value == None:
            edited_value = st.text_input(text, value=value, key=str(default) + text)
            if edited_value == "None":
                edited_value = None
            elif edited_value.isdigit():
                edited_value = int(edited_value)
            elif (
                "." in edited_value
                and edited_value.split(".")[0].isdigit()
                and edited_value.split(".")[1].isdigit()
            ):
                edited_value = float(edited_value)
            else:
                continue
        else:
            edited_value = st.text_input(text, value=value, key=str(default) + text)

        # Save the edited parameter in the dictionary
        parameters[key] = edited_value

    return parameters


def input_sorter_params():
    """
    Higher level function that gets sorter parameters for all spikesorters
    Inputs: None
    Returns: sorter_params: json with parameters
    """

    # load spikesorter information
    resources = Path(os.path.abspath(__file__)).parent.parent / "resources"
    with open(resources / "spikesorter_default_params.json") as f:
        spikesorter_default_params = json.load(f)
    with open(resources / "spikesorter_descriptions.json") as f:
        spikesorter_descriptions = json.load(f)
    sorters = list(spikesorter_default_params.keys())

    sorter_params = dict()

    depth = 0

    while True:
        depth += 1

        if len(sorters) == 0:
            break

        # ask for sorter input
        sorter = st.selectbox(f"Select spikesorter {depth}", ["None"] + sorters)

        if sorter != "None":
            # get parameters for this sorter
            default = spikesorter_default_params[sorter]
            desc = spikesorter_descriptions[sorter]

            # get user input
            with st.expander(f"Input {sorter} parameters"):
                params = interactive_sorter_params_input(default, desc)

            # input parameters into paramdict
            sorter_params[sorter] = params

            # remove sorter from list
            sorters.remove(sorter)

        else:
            break

    return sorter_params

def dropdown_query_table(
    tables,
    subtables,
    username,
    delete_mode="False",
    headless=False,
    in_compute=None,
    restore=False,
    search_page=False,
):
    """
    A custom streamlit widget that allows users to interactively query an existing
    table's primary keys for selection of an entry

    Displays: interactive dropdown selectboxes
    Returns: the primary key selected
    """

    if restore:
        # map datajoint names to antelop names
        full_names = {val.full_table_name: key for key, val in tables.items()}

        # change tables to be queries where entries are deleted but parents aren't
        subtablesnew = dict(subtables)
        for tablename, table in subtables.items():
            query = table
            for parentname in table.parents():
                parent = tables[full_names[parentname]]
                query = query & (parent & delete_restriction(parent)).proj()
            subtablesnew[tablename] = query
        subtables = dict(subtablesnew)

    if not headless:
        # don't show non-empty tables
        available_tables = searchable_tables(subtables, delete_mode)

        if len(available_tables) == 0:
            return None, None
        else:
            if search_page and hasattr(
                st.session_state, "tablename"
            ):  # default in session state
                index = list(available_tables.keys()).index(st.session_state.tablename)
            else:
                index = 0
            # get user to select a table - returns the class object
            tablename = st.selectbox(
                "Select table:", available_tables.keys(), index=index
            )
            table = tables[tablename]
            if search_page:
                st.session_state.tablename = tablename

        # print table definition
        st.text(table.heading)

    else:
        tablename = list(subtables.keys())[0]
        table = list(subtables.values())[0]

        # check if there's any data
        if len(table & delete_restriction(table)) == 0:
            return None, None

    # existing dict is for defaults in GUI
    # default existing_dict to just the username, if they have data, else nothing
    if (
        len(
            table & {"experimenter": username, **delete_restriction(table, delete_mode)}
        )
        > 0
    ):
        existing_dict = {"experimenter": username}
    else:
        existing_dict = {}
    if hasattr(st.session_state, "restriction"):
        existing_dict = {**existing_dict, **st.session_state.restriction}

    # query dict is hard restrictions on what gets shown
    query_dict = delete_restriction(table, delete_mode)

    # if in compute, want to only check spikesorting that are in compute
    if in_compute:
        query_dict["spikesorting_in_compute"] = in_compute
        query_dict["labelledframes_in_compute"] = in_compute

        # tell admin there's no data in compute
        if (
            len(
                table
                & {
                    "spikesorting_in_compute": in_compute,
                    "labelledframes_in_compute": in_compute,
                }
            )
            == 0
        ):
            return None, None

    # calculate all foreign key parents and earliest ancestors
    parent_tables = parent_primaries(table, tables)
    ancestor_tables = ancestor_primaries(table, tables)

    # cycle through primary keys
    for key in table.primary_key:
        # if it's a foreign key
        if key in parent_tables.keys():
            # query only the current table that matches current key
            # but return ancestor attributes
            query = (
                ancestor_tables[key]
                & (table & query_dict & delete_restriction(table, delete_mode)).proj()
            )

            # if the ancestor has a description, show it in the selectbox
            name = get_tablename(ancestor_tables[key])
            if name in ancestor_tables[key].heading.attributes.keys():
                # query available selections
                options = list(query.fetch(key, name, as_dict=True))

                # dictionary to show has both the value and description
                showdict = {i[name]: i[key] for i in options}
                showdict = {"Enter selection...": "Enter selection...", **showdict}

                # if key in existing_dict set default
                if key in existing_dict.keys():
                    index = list(showdict.values()).index(existing_dict[key])
                # if there's only one option, set default to that
                elif len(options) == 1:
                    index = 1
                # otherwise set default to select message
                else:
                    index = 0
                query_dict[key] = showdict[
                    st.selectbox(
                        "Select " + name,
                        showdict.keys(),
                        key=str(table) + str(key),
                        index=index,
                    )
                ]

            # ancestor doesn't have a description
            else:
                # query available selections
                options = ["Enter selection..."] + list(query.fetch(key))

                # if key in existing_dict set default
                if key in existing_dict.keys():
                    index = options.index(existing_dict[key])
                # if there's only one option, set default to that
                elif len(options) == 2:
                    index = 1
                # otherwise set default to select message
                else:
                    index = 0

                # display selectbox of options
                query_dict[key] = st.selectbox(
                    "Select " + key, options, key=str(table) + str(key), index=index
                )

        # not foreign key so query the current table
        else:
            query = table & query_dict

            # if the current table has a description, show it in the selectbox
            name = get_tablename(table)
            if name in table.heading.attributes.keys():
                # query available selections
                options = list(query.fetch(key, name, as_dict=True))

                # dictionary to show has both the value and description
                showdict = {i[name]: i[key] for i in options}
                showdict = {"Enter selection...": "Enter selection...", **showdict}

                # if key in existing_dict set default
                if key in existing_dict.keys():
                    index = list(showdict.values()).index(existing_dict[key])
                # if there's only one option, set default to that
                elif len(options) == 1:
                    index = 1
                # otherwise set default to select message
                else:
                    index = 0

                query_dict[key] = showdict[
                    st.selectbox(
                        "Select " + name,
                        showdict.keys(),
                        key=str(table) + str(key),
                        index=index,
                    )
                ]

            # table doesn't have a description
            else:
                # query available selections
                options = ["Enter selection..."] + list(query.fetch(key))

                # if key in existing_dict set default
                if key in existing_dict.keys():
                    index = options.index(existing_dict[key])
                # if there's only one option, set default to that
                elif len(options) == 2:
                    index = 1
                # otherwise set default to select message
                else:
                    index = 0

                # display selectbox of options
                query_dict[key] = st.selectbox(
                    "Select " + key, options, key=str(table) + str(key), index=index
                )

        # if no selection, break loop and remove placeholder
        if query_dict[key] == "Enter selection...":
            del query_dict[key]
            break

    return tablename, query_dict


def dropdown_insert_table(
    tables, subtables, username, primary_only=False, headless=False
):
    """
    A custom streamlit widget that allows users to interactively insert a new manual entry into the database. It involves querying the table's parents to see possible values.

    Inputs: tables: structure of the database
            existing_dict: entries can be pre-entered (such as experimenter)
    Displays: interactive dropdown selectboxes
    Returns: the dictionary of values to insert
    """

    if not headless:
        # don't show non-empty tables
        available_tables = insertable_tables(tables, subtables, username)

        if len(available_tables) == 0:
            return None, None
        else:
            # get user to select a table - returns the class object
            tablename = st.selectbox("Select table:", available_tables.keys())
            table = tables[tablename]

        # print table definition
        st.text(table.heading)

    else:
        tablename = list(subtables.keys())[0]
        table = list(subtables.values())[0]

        # check if upstream tables populated
        available_tables = insertable_tables(tables, subtables, username)
        if len(available_tables) == 0:
            return None, None

        st.markdown(f"#### {tablename}")

    admin_table = table._admin()

    existing_dict = {"experimenter": username}

    # calculate all foreign key parents and earliest ancestors
    parent_tables = parent_primaries(table, tables)
    ancestor_tables = ancestor_primaries(table, tables)

    spare_key = check_spare_key(table, parent_tables.values())

    # construct join query of all parents of primary keys
    if not spare_key:
        counter = 0
        for parentname, parent in ancestor_tables.items():
            if parentname in table.primary_key:
                if counter == 0:
                    parent_join = (parent & delete_restriction(parent)).proj()
                    counter += 1
                else:
                    parent_join = parent_join * parent.proj()

    # cycle through table keys, checking attribute properties
    if primary_only:
        keys = list(table.primary_key)
    else:
        keys = list(table.heading.attributes.keys())

    insert_dict = {}
    primary_dict = {}

    for key in keys:
        # inserted entries are not deleted
        if key == f"""{table.table_name.replace("_", "")}_deleted""":
            insert_dict[key] = "False"

        # inserted entries are not in a computation
        elif key == f"""{table.table_name.replace("_", "")}_in_compute""":
            insert_dict[key] = 0
        
        # duration is blank
        elif key == "session_duration":
            continue

        # leave if autoincrement
        elif table.heading.attributes[key].autoincrement:
            continue

        # if it's a foreign key, allow to select from existing entries
        elif key in parent_tables.keys():
            # query only the parent table that matches current key
            # but return ancestor attributes
            if spare_key:
                query = (
                    ancestor_tables[key]
                    & parent_tables[key].proj()
                    & primary_dict
                    & {
                        f"""{ancestor_tables[key].table_name.replace("#", "").replace("_", "")}_deleted""": "False"
                    }
                )
            # otherwise, query all possible key combinations remaining
            else:
                query = (
                    ancestor_tables[key]
                    & (parent_join - table)
                    & primary_dict
                    & {
                        f"""{ancestor_tables[key].table_name.replace("#", "").replace("_", "")}_deleted""": "False"
                    }
                )

            # if the ancestor has a description, show it in the selectbox
            name = key.split("_")[0] + "_name"
            if name in ancestor_tables[key].heading.attributes.keys():
                # fetch available options and append descriptions to display
                options = query.fetch(key, name, as_dict=True)
                showdict = {i[name]: i[key] for i in options}

                # if key in existing_dict set default
                if key in existing_dict.keys():
                    if existing_dict[key] not in options:
                        return None, None
                    index = showdict.vals().index(existing_dict[key])
                else:
                    index = 0

                # get user input
                insert_dict[key] = showdict[
                    st.selectbox("Select " + name, showdict.keys(), index=index)
                ]

            # if the ancestor doesn't have a description
            else:
                # query available selections
                options = list(query.fetch(key))

                # if key in existing_dict set default
                if key in existing_dict.keys():
                    if existing_dict[key] not in options:
                        return None, None
                    index = options.index(existing_dict[key])
                else:
                    index = 0

                # get user input
                insert_dict[key] = st.selectbox("Select " + key, options, index=index)

            # if it's a primary key store separately
            if table.heading.attributes[key].in_key:
                primary_dict[key] = insert_dict[key]

        # if it's a primary composite autoincremented key, update automatically
        elif (
            table.heading.attributes[key].in_key
            and table.heading.attributes[key].comment[-16:] == "(auto_increment)"
        ):
            query = admin_table & primary_dict
            next_key = max(query.fetch(key), default=0) + 1
            insert_dict[key] = next_key
            if table.heading.attributes[key].in_key:
                primary_dict[key] = insert_dict[key]

        # if it's an attachment, select the directory
        elif table.heading.attributes[key].is_attachment:
            # get directory path interactively from user

            dirpath = server_directory_browser(message="Select raw data folder")
            insert_dict[key] = dirpath

        # if it's an enum, select from dropdown table
        elif table.heading.attributes[key].type[:4] == "enum":
            options = table.heading.attributes[key].type[6:-2].split("""','""")
            insert_dict[key] = st.selectbox("Select " + key, options)

        # if it's a timestamp, use streamlit widgets
        elif table.heading.attributes[key].type[:9] == "timestamp":
            date = st.date_input("Enter date")
            time = st.time_input("Enter time")
            timestamp = datetime.combine(date, time)
            insert_dict[key] = timestamp

        # if it's ephys_acquisition, select from dropdown of options
        elif key == "ephys_acquisition":
            extensions = list(get_ephys_extensions().keys())
            insert_dict[key] = st.selectbox("Select " + key, extensions)

        elif key in ["yaw", "pitch", "roll"]:
            insert_dict[key] = st.slider("Enter " + key + " (deg)", -180, 180, 0, 1)

        elif key == "ap_coord":
            insert_dict[key] = st.slider("Enter " + key + " (um)", -10000, 10000, 0, 1)

        elif key == "dv_coord":
            insert_dict[key] = st.slider("Enter " + key + " (um)", 0, 8000, 0, 1)

        elif key == "ml_coord":
            insert_dict[key] = st.slider("Enter " + key + " (um)", -6000, 6000, 0, 1)

        elif key == "probe_dv_increment":
            insert_dict[key] = st.slider("Enter " + key + " (um)", 0, 8000, 0, 1)

        # if it's a decimal, select with correct limits
        elif table.heading.attributes[key].type[:7] == "decimal":
            limits = table.heading.attributes[key].type[8:-1].split(",")
            n, f = float(limits[0]), float(limits[1])
            lim = 10 ** (n - f)
            insert_dict[key] = st.slider("Enter " + key, -lim, lim, 0.0, 10 ** (-f))

        # if it's masks, custom widget
        elif key == "masks":
            st.text("Enter masks")
            insert_dict[key] = select_masks(tables)

        # if it's a json, upload file
        elif table.heading.attributes[key].json:
            if table.heading.attributes[key].nullable:
                add_json = st.checkbox(f"Add {key} json?")
            else:
                add_json = True
            if add_json:
                jsonfile = server_directory_browser(message=f"Select {key} json", extension="json")
                if jsonfile:
                    insert_dict[key] = jsonfile

        # if it's a notes box, print a bigger box
        elif key[-5:] == "notes":
            insert_dict[key] = st.text_area("Enter " + key)
            if table.heading.attributes[key].in_key:
                primary_dict[key] = insert_dict[key]

        # otherwise input new value
        else:
            insert_dict[key] = st.text_input("Enter " + key)
            if table.heading.attributes[key].in_key:
                primary_dict[key] = insert_dict[key]

    return tablename, insert_dict


def server_directory_browser(message, extension="directory", custom_path=None):
    """
    A custom Streamlit widget that allows the user to browse directories on the server side.

    Returns: The selected directory path. Returns None if no directory is selected.
    """

    # default root directory should be mounted into the container
    if custom_path:
        current_directory = Path(custom_path)
    else:
        config = get_config()
        basedir = st.selectbox(message, config["folders"].keys(), key=message)
        current_directory = Path(config["folders"][basedir])

    if extension == "directory":
        counter = 0
        while current_directory is not None:
            # Update counter
            counter += 1

            # List the subdirectories in the current directory
            subdirectories = ["Select directory..."]
            subdirectories += [
                subdirectory.name
                for subdirectory in current_directory.iterdir()
                if subdirectory.is_dir() and not subdirectory.name.startswith(".")
            ]

            # Display the selectbox for directory navigation
            if len(subdirectories) > 1:
                selected_subdirectory = st.selectbox(
                    "Select a directory",
                    subdirectories,
                    key=counter,
                    label_visibility="collapsed",
                )
            else:
                contents = []
                for i, file in enumerate(current_directory.iterdir()):
                    if file.is_file() and not file.name.startswith(".") and i < 10:
                        contents.append(file)
                    elif i == 10:
                        contents.append("...")
                        contents.append(
                            f"Total files: {len(list(current_directory.iterdir()))}"
                        )
                        break
                content_str = "Contents:\n" + "\n".join(
                    [
                        str(file.name) if isinstance(file, PosixPath) else file
                        for file in contents
                    ]
                )
                st.text(content_str)
                break

            # Handle directory navigation
            if selected_subdirectory == "Select directory...":
                break
            else:
                current_directory = current_directory / selected_subdirectory

        return current_directory

    elif extension == None:
        counter = 0
        while current_directory is not None:
            # Update counter
            counter += 1

            # List the subdirectories and files in the current directory
            subdirectories = ["Select path..."]
            subdirectories += [
                subdirectory.name
                for subdirectory in current_directory.iterdir()
                if not subdirectory.name.startswith(".")
            ]

            # Display the selectbox for directory navigation
            if len(subdirectories) > 1:
                selected_subdirectory = st.selectbox(
                    "Select a directory",
                    subdirectories,
                    key=f"noex{counter}",
                    label_visibility="collapsed",
                )
            else:
                break

            # Handle directory navigation
            if selected_subdirectory == "Select path...":
                break
            else:
                current_directory = current_directory / selected_subdirectory

            if current_directory.is_file():
                return current_directory

    else:
        counter = 0
        while current_directory is not None:
            # Update counter
            counter += 1

            # List the subdirectories and files in the current directory
            subdirectories = ["Select path..."]
            subdirectories += [
                subdirectory.name
                for subdirectory in current_directory.iterdir()
                if subdirectory.is_dir() and not subdirectory.name.startswith(".")
            ]
            subdirectories += [
                path.name
                for path in current_directory.iterdir()
                if path.suffix == f".{extension}" and not path.name.startswith(".")
            ]

            # Display the selectbox for directory navigation
            if len(subdirectories) > 1:
                selected_subdirectory = st.selectbox(
                    "Select a directory",
                    subdirectories,
                    key=f"ex{counter}",
                    label_visibility="collapsed",
                )
            else:
                st.text("")
                st.warning(f"No {extension}s in this directory!")
                break

            # Handle directory navigation
            if selected_subdirectory == "Select path...":
                break
            else:
                current_directory = current_directory / selected_subdirectory

            if current_directory.suffix == f".{extension}":
                return current_directory


def add_video(video):
    """
    Function to allow interactive input of video parameters
    Inputs: None
    Returns: video_params: dict with parameters
    """

    new_video = {}

    # enter video name
    name = st.text_input(
        "Enter video name",
        value=st.session_state.video_params[video]["name"],
        key="name_video" + str(video),
    )
    new_video["name"] = name

    # enter video format
    index = ["avi", "mp4", "mov"].index(st.session_state.video_params[video]["format"])
    format = st.selectbox(
        "Select video format",
        ["avi", "mp4", "mov"],
        index=index,
        key="format_video" + str(video),
    )
    new_video["format"] = format

    # enter description
    description = st.text_area(
        "Enter description",
        value=st.session_state.video_params[video]["description"],
        key="description_video" + str(video),
    )
    new_video["description"] = description
    new_video["reference_point"] = st.text_input(
        "Enter reference point",
        value=st.session_state.video_params[video]["reference_point"],
        key="reference_point_video" + str(video),
    )

    return new_video


def add_feature(feature, videols):
    """
    Function to allow interactive input of feature parameters
    Inputs: None
    Returns: feature_params: dict with parameters
    """

    new_feature = {}

    # enter feature name
    name = st.text_input(
        "Enter feature name",
        value=st.session_state.feature_params[feature]["name"],
        key="name_feature" + str(feature),
    )
    new_feature["name"] = name

    # enter feature source type
    index = ["stimulus", "acquisition", "processing", "deeplabcut"].index(
        st.session_state.feature_params[feature]["source"]["source_type"]
    )
    source_type = st.selectbox(
        "Select source type",
        ["stimulus", "acquisition", "processing", "deeplabcut"],
        index=index,
        key="source_feature" + str(feature),
    )
    new_feature["source"] = {}
    new_feature["ownership"] = {}
    new_feature["source"]["source_type"] = source_type

    if source_type == "deeplabcut":
        ownership_options = ["self", "world"]
    elif source_type == "stimulus":
        ownership_options = ["world"]
    else:
        ownership_options = ["self", "world"]
    ownership = st.selectbox(
        "Select ownership", ownership_options, key="ownership_processing" + str(feature)
    )
    new_feature["ownership"]["ownership"] = ownership
    if ownership == "self":
        # enter feature animal
        if "animal" in st.session_state.feature_params[feature]["ownership"].keys():
            value = st.session_state.feature_params[feature]["ownership"]["animal"]
        else:
            value = 1
        animal = st.number_input(
            "Enter animal",
            min_value=1,
            value=value,
            key="animal_feature" + str(feature),
        )
        new_feature["source"]["animal"] = animal

    if source_type == "processing":
        # enter processing module
        if "module" in st.session_state.feature_params[feature]["source"].keys():
            value = st.session_state.feature_params[feature]["source"]["module"]
        else:
            value = ""
        module = st.text_input(
            "Enter processing module", value=value, key="module_feature" + str(feature)
        )
        new_feature["source"]["module"] = module

        # enter data type
        index = ["analog", "digital", "interval", "kinematics"].index(
            st.session_state.feature_params[feature]["data_type"]
        )
        data_type = st.selectbox(
            "Select data type",
            ["analog", "digital", "interval", "kinematics"],
            index=index,
            key="data_type_feature" + str(feature),
        )
        new_feature["data_type"] = data_type

        if data_type == "kinematics":
            if "video" in st.session_state.feature_params[feature]["source"].keys():
                video = st.session_state.feature_params[feature]["source"]["video"]
            else:
                video = videols[0]
            options = videols.copy()
            index = options.index(video)
            st.session_state.feature_params[feature]["source"]["video"] = st.selectbox(
                "Select video", options, index=index, key="video_feature" + str(feature)
            )
            new_feature["source"]["video"] = st.session_state.feature_params[feature][
                "source"
            ]["video"]
    elif source_type == "stimulus":
        # enter data type
        index = ["analog", "digital", "interval"].index(
            st.session_state.feature_params[feature]["data_type"]
        )
        data_type = st.selectbox(
            "Select data type",
            ["analog", "digital", "interval"],
            index=index,
            key="data_type_feature" + str(feature),
        )
        new_feature["data_type"] = data_type
    elif source_type == "acquisition":
        # enter data type
        index = ["analog", "digital", "interval"].index(
            st.session_state.feature_params[feature]["data_type"]
        )
        data_type = st.selectbox(
            "Select data type",
            ["analog", "digital", "interval"],
            index=index,
            key="data_type_feature" + str(feature),
        )
        new_feature["data_type"] = data_type
    elif source_type == "deeplabcut":
        new_feature["data_type"] = "kinematics"

    if new_feature["data_type"] == "kinematics":
        pass
    else:
        # enter coordinates
        x = st.number_input(
            "Enter x coordinate",
            min_value=0,
            value=st.session_state.feature_params[feature]["coordinates"][0],
            key="x_feature" + str(feature),
        )
        y = st.number_input(
            "Enter y coordinate",
            min_value=0,
            value=st.session_state.feature_params[feature]["coordinates"][1],
            key="y_feature" + str(feature),
        )
        z = st.number_input(
            "Enter z coordinate",
            min_value=0,
            value=st.session_state.feature_params[feature]["coordinates"][2],
            key="z_feature" + str(feature),
        )
        new_feature["coordinates"] = [x, y, z]

    # enter description
    description = st.text_area(
        "Enter description",
        value=st.session_state.feature_params[feature]["description"],
        key="description_feature" + str(feature),
    )
    new_feature["description"] = description

    return new_feature


def default_feature():
    """
    Function to return default feature parameters
    """

    feature = {
        "name": "",
        "source": {
            "source_type": "stimulus",
        },
        "ownership": {"ownership": "world"},
        "data_type": "analog",
        "coordinates": [0, 0, 0],
        "description": "",
    }

    return feature


def default_video():
    """
    Function to return default video parameters
    """

    video = {"name": "", "description": "", "format": "avi", "reference_point": ""}

    return video


def change_num_features():
    """
    If the user changes the number of features, we need to update the feature_params dict in the session state
    """

    # make session state dict to store feature parameters
    if "feature_params" not in st.session_state:
        feature_dict = {}
        for i in range(1, st.session_state.num_features + 1):
            feature_dict[i] = default_feature()
            st.session_state["feature_params"] = feature_dict

    # if the number of features has increased, add new feature parameters
    for i in range(1, st.session_state.num_features + 1):
        if i not in st.session_state.feature_params.keys():
            st.session_state.feature_params[i] = default_feature()

    # if the number of features has decreased, remove old feature parameters
    new_feature_params = st.session_state.feature_params.copy()
    for i in st.session_state.feature_params.keys():
        if i not in range(1, st.session_state.num_features + 1):
            del new_feature_params[i]

    st.session_state.feature_params = new_feature_params


def change_num_videos():
    """
    If the user changes the number of videos, we need to update the video_params dict in the session state
    """

    # make session state dict to store video parameters
    if "video_params" not in st.session_state:
        video_dict = {}
        for i in range(1, st.session_state.num_videos + 1):
            video_dict[i] = default_video()
            st.session_state["video_params"] = video_dict

    # if the number of videos has increased, add new video parameters
    for i in range(1, st.session_state.num_videos + 1):
        if i not in st.session_state.video_params.keys():
            st.session_state.video_params[i] = default_video()

    # if the number of videos has decreased, remove old video parameters
    new_video_params = st.session_state.video_params.copy()
    for i in st.session_state.video_params.keys():
        if i not in range(1, st.session_state.num_videos + 1):
            del new_video_params[i]

    st.session_state.video_params = new_video_params


def get_rig_videos():
    # request number of videos
    st.session_state["num_videos"] = st.number_input(
        "Enter number of videos", min_value=0
    )
    if st.session_state.num_videos == 0:
        return {}
    change_num_videos()

    # make button with video tabs
    video = st.selectbox("Select video", list(st.session_state.video_params.keys()))

    st.divider()
    st.markdown(f"##### Video {video}")

    # get video parameters
    st.session_state.video_params[video] = add_video(video)

    return st.session_state.video_params


def define_rig_json(videos):
    """
    Function to allow interactive input of behaviour rig parameters
    Inputs: None
    Returns: rig_dict: dict with parameters
    """
    videols = [video["name"] for video in videos]

    # first, need to request the reference point from the user
    reference = st.text_input("Enter the coordinate system reference point (0,0,0)")

    # request number of features
    st.session_state["num_features"] = st.number_input(
        "Enter number of features", min_value=1
    )
    change_num_features()

    # make button with feature tabs
    feature = st.selectbox(
        "Select feature", list(st.session_state.feature_params.keys())
    )

    st.divider()
    st.markdown(f"##### Feature {feature}")

    # get feature parameters
    st.session_state.feature_params[feature] = add_feature(feature, videols)

    # make rig_dict
    rig_dict = {
        "specification": "antelop-behaviour",
        "version": "0.0.1",
        "reference_point": reference,
        "features": list(st.session_state.feature_params.values()),
        "videos": videos,
    }

    return rig_dict


def enter_args(function):
    """
    Function to allow interactive input of analysis function arguments
    Inputs: args: dict with arguments
    Returns: args: dict with user input
    """
    args = {}
    signature = inspect.signature(function.run)
    defaults = {
        param.name: param.default
        for param in signature.parameters.values()
        if param.default is not inspect.Parameter.empty
    }
    for k, v in function.args.items():
        default = None
        if k in defaults.keys():
            default = defaults[k]

        if v == int:
            if not default:
                default = 0
            default = int(default)
            args[k] = st.number_input(f"Enter {k}", key=str(k), value=default)
        elif v == float:
            if not default:
                default = 0.0
            default = float(default)
            args[k] = st.number_input(f"Enter {k}", key=str(k), value=default)
        elif v == bool:
            if not default:
                default = False
            args[k] = st.checkbox(f"Enter {k}", key=str(k), value=default)
        elif isinstance(v, list):
            args[k] = st.selectbox(f"Enter {k}", v)
        else:
            if not default:
                default = ""
            args[k] = st.text_input(f"Enter {k}", key=str(k), value=default)

    return args


def display_analysis(result, returns, primary_key):
    """
    Function to display the results of an analysis function
    """

    if result is None:
        return

    if all([v in [bool, int, float, str, np.ndarray] for v in returns.values()]):
        if isinstance(result, dict):
            st.dataframe([result], use_container_width=True)
        else:
            st.dataframe(result, hide_index=True, use_container_width=True)

    elif Figure in returns.values():
        if isinstance(result, dict):
            result = [result]

        # make dict mapping display key to result
        display_dict = {}
        for data in result:
            key = "-".join([str(data[k]) for k in primary_key])
            display_dict[key] = data

        # interactively get result
        if len(display_dict) == 1:
            current_result = list(display_dict.values())[0]
        else:
            current_result = display_dict[
                st.selectbox("Select result", list(display_dict.keys()))
            ]

        current_result = {
            k: v for k, v in current_result.items() if k in returns.keys()
        }

        if len(returns) > 1:
            attr = st.selectbox("Select data", list(current_result.keys()))
        else:
            attr = list(returns.keys())[0]

        if returns[attr] in [bool, int, float, str]:
            st.write(f"{attr}: {current_result[attr]}")
        elif returns[attr] == Figure:
            st.pyplot(current_result[attr])


def children_buttons(query, tables):
    """
    Function displays buttons to navigate to children table
    """

    children = query.children()
    full_names = {val.full_table_name: key for key, val in tables.items()}

    # query projected table
    df, number = query_without_external(query.proj(), mode='Navigation')
    columns = list(df.columns)

    # add checkboxes for each child
    column_config_dict = {}
    for child in children:
        name = full_names[child]
        num = len(tables[name] & query.proj())
        if num > 0:
            counts = []
            for i, key in enumerate(query.proj()):
                if i < 30:
                    counts.append(len(tables[name] & key))
            df[name] = counts
            columns.append(name)
            df[name + " button"] = False
            column_config_dict[name + " button"] = st.column_config.CheckboxColumn(
                label="Go To", width="small"
            )

    primary_key = list(query.primary_key)

    # display table
    st.session_state.search_data = df
    st.data_editor(
        st.session_state.search_data,
        on_change=reset,
        use_container_width=True,
        disabled=columns,
        hide_index=True,
        column_config=column_config_dict,
        key="search_change",
        args=(primary_key,),
    )


def reset(primary_key):
    # get changed row
    if st.session_state.search_change["edited_rows"]:
        row = list(st.session_state.search_change["edited_rows"].keys())[0]
        column = list(st.session_state.search_change["edited_rows"][row].keys())[
            0
        ].split(" ")[0]
        num = st.session_state.search_data.iloc[row][column]
        if num > 0:
            schema = inverse_table_mapping[column]
            restriction = (
                st.session_state.restriction
                if hasattr(st.session_state, "restriction")
                else {}
            )
            if not hasattr(st.session_state, "prev_data"):
                st.session_state.prev_data = []
            st.session_state.prev_data.append(
                {
                    "schema": st.session_state.schema,
                    "tablename": st.session_state.tablename,
                    "restriction": restriction,
                }
            )
            st.session_state.schema = schema
            st.session_state.tablename = column
            data = st.session_state.search_data.iloc[row]
            restriction = {k: v for k, v in zip(primary_key, data[primary_key])}
            st.session_state.restriction = restriction


def go_back():
    st.session_state.go_back = True
    prev_data = st.session_state.prev_data.pop()
    st.session_state.tablename = prev_data["tablename"]
    st.session_state.restriction = prev_data["restriction"]
    st.session_state.tmp_schema = prev_data[
        "schema"
    ]  # stupid stremalit feature necessitates this
    st.rerun()


inverse_table_mapping = {
    "Experimenter": "Metadata",
    "Experiment": "Metadata",
    "Animal": "Metadata",
    "Session": "Metadata",
    "ProbeGeometry": "Electrophysiology",
    "ProbeInsertion": "Electrophysiology",
    "SortingParams": "Electrophysiology",
    "Recording": "Electrophysiology",
    "SpikeSorting": "Electrophysiology",
    "Probe": "Electrophysiology",
    "Channel": "Electrophysiology",
    "LFP": "Electrophysiology",
    "Unit": "Electrophysiology",
    "SpikeTrain": "Electrophysiology",
    "Waveform": "Electrophysiology",
    "BehaviourRig": "Behaviour",
    "LabelledFrames": "Behaviour",
    "DLCModel": "Behaviour",
    "MaskFunction": "Behaviour",
    "Feature": "Behaviour",
    "World": "Behaviour",
    "Video": "Behaviour",
    "Self": "Behaviour",
    "Object": "Behaviour",
    "DigitalEvents": "Behaviour",
    "AnalogEvents": "Behaviour",
    "IntervalEvents": "Behaviour",
    "Kinematics": "Behaviour",
    "Mask": "Behaviour",
}


def edit_params(key, tables):
    name = f"{key['experimenter']}_{key['behaviourrig_id']}_{key['experiment_id']}_{key['dlcmodel_id']}"
    conf = st.session_state.dlc_folder[name]
    # read the config file
    with open(conf, "r") as f:
        config_dict = yaml.safe_load(f)

    # get user to interactively select options
    st.divider()
    frames = st.slider(
        "Select the range from which you want to extract training frames",
        0.0,
        1.0,
        (0.0, 1.0),
        step=0.01,
    )
    st.text("The frame range is a fraction of the total video length.")
    model = st.selectbox(
        "Select which model to use",
        [
            "resnet_50",
            "resnet_101",
            "resnet_152",
            "mobilenet_v2_1.0",
            "mobilenet_v2_0.75",
            "mobilenet_v2_0.5",
            "mobilenet_v2_0.35",
        ],
    )
    st.text(
        "Resnet_50 should be adequate for most purposes. Please read the DeepLabCut documentation for more information."
    )
    numframes = st.number_input(
        "Enter the number of frames you want to annotate", min_value=10, value=20
    )
    st.text("The more frames you annotate, the better the model will be.")
    training_fraction = st.number_input(
        "Enter the fraction of frames to use for training",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
    )
    st.text(
        "We will use a small portion of your annotated frames to assess the performance of the model."
    )
    p_cutoff = st.number_input(
        "Enter the p-cutoff value", min_value=0.0, max_value=1.0, value=0.6
    )
    st.text(
        "This specifies the threshold of the likelihood and helps distinguish likely body parts from uncertain ones."
    )

    # update the config dict
    config_dict["start"] = frames[0]
    config_dict["stop"] = frames[1]
    config_dict["default_net_type"] = model
    config_dict["numframes2pick"] = numframes
    config_dict["TrainingFraction"] = [training_fraction]
    config_dict["pcutoff"] = p_cutoff

    st.divider()
    augmenter = st.selectbox(
        "Select the augmentation type", ["imgaug", "tensorpack", "scalecrop"]
    )
    st.text(
        "Please read the DeepLabCut documentation for more information on augmentation methods."
    )
    max_snapshots_to_keep = st.number_input(
        "Enter the maximum number of snapshots to keep",
        min_value=1,
        max_value=20,
        value=5,
    )
    st.text("This is the number of snapshots of the model to keep during training.")
    displayiters = st.number_input(
        "Enter the number of iterations between displaying the model",
        min_value=100,
        max_value=10000,
        value=1000,
    )
    st.text(
        "This is the number of iterations between displaying the model performance."
    )
    saveiters = st.number_input(
        "Enter the number of iterations between saving the model",
        min_value=1000,
        max_value=100000,
        value=50000,
    )
    st.text("This is the number of iterations between saving the model.")
    maxiters = st.number_input(
        "Enter the maximum number of iterations",
        min_value=1000,
        max_value=5000000,
        value=1000000,
    )

    train_dict = {
        "augmenter": augmenter,
        "max_snapshots_to_keep": max_snapshots_to_keep,
        "displayiters": displayiters,
        "saveiters": saveiters,
        "maxiters": maxiters,
    }

    params_dict = {"config": config_dict, "compute": train_dict}

    return params_dict


def select_analysis(analysis_functions):
    """
    Function to allow the user to select an analysis function
    Inputs: analysis_functions: dict with analysis functions
    Returns: function: selected function
    """
    counter = 0
    while isinstance(analysis_functions, dict):
        counter += 1
        if counter == 1:
            label_visibility = "visible"
            text = "Select function..."
        else:
            label_visibility = "collapsed"
            text = ""
        display_keys = ["Select function..."]
        for key, val in analysis_functions.items():
            if hasattr(val, "hidden"):
                if not val.hidden:
                    display_keys.append(key)
            else:
                display_keys.append(key)
        function = st.selectbox(
            text, display_keys, key=f"selectbox_{counter}", label_visibility=label_visibility
        )
        if function == "Select function...":
            return None
        else:
            analysis_functions = analysis_functions[function]
    return analysis_functions


def select_probe():
    """
    Function gets user to select probe from resources
    """

    resources = (
        Path(os.path.abspath(__file__)).parent.parent / "resources"
    )
    probedir = resources / "probes"
    selected_probe = server_directory_browser('Select probe', extension='directory', custom_path=probedir)
    if len(list(selected_probe.glob("*.json"))) > 0:
        selected_probe = list(selected_probe.glob("*.json"))[0]
        return selected_probe

def check_dlc_folder(key, tables):
    """
    Function checks if a dlc folder exists and is valid.
    """

    name = f"{key['experimenter']}_{key['behaviourrig_id']}_{key['experiment_id']}_{key['dlcmodel_id']}"
    tmpdir = Path(tempfile.gettempdir())
    dlc_dir = tmpdir / "antelop_dlc"
    folder = dlc_dir / name

    # if there's already a dlc folder
    if folder.exists():
        for i in folder.iterdir():
            if i.name == "videos":
                continue
            else:
                conf = i / "config.yaml"
                if conf.exists():
                    with open(conf, "r") as f:
                        config_dict = yaml.safe_load(f)
                    # need to check if all videos are downloaded and match database
                    if all(
                        [Path(vid).exists() for vid in config_dict["video_sets"].keys()]
                    ):  # UPDATE THIS SO WE ALSO CHECK AGAINST DATABASE
                        return True, conf

    return False, None


def create_dlc_folder(key, username=None, password=None):
    """
    This function creates a dlc folder for a specific experiment.
    If it already exists, it checks the videos, and if they all match, it returns the config path.
    Otherwise, it deletes the DLC folder, downloads the remaining videos, makes the DLC folder and returns the config path.
    """

    conn_dlc, tables_dlc = thread_connect(username=username, password=password)

    name = f"{key['experimenter']}_{key['behaviourrig_id']}_{key['experiment_id']}_{key['dlcmodel_id']}"
    tmpdir = Path(tempfile.gettempdir())
    dlc_dir = tmpdir / "antelop_dlc"
    folder = dlc_dir / name
    folder.mkdir(parents=True, exist_ok=True)
    video_path = folder / "videos"
    video_path.mkdir(parents=True, exist_ok=True)

    # if there's already a dlc folder
    for i in folder.iterdir():
        if i.name == "videos":
            continue
        else:
            conf = i / "config.yaml"
            if conf.exists():
                with open(conf, "r") as f:
                    config_dict = yaml.safe_load(f)
                # need to check if all videos are downloaded and match database
                if all(
                    [Path(vid).exists() for vid in config_dict["video_sets"].keys()]
                ):  # UPDATE THIS SO WE ALSO CHECK AGAINST DATABASE
                    return conf
                else:
                    shutil.rmtree(i)
                    break

    # download the videos
    config = get_config()
    if config["s3"]["host"] == "local":
        key["dlc_training"] = "True"
        videos = (tables_dlc["Video"] * tables_dlc["World"] & key).fetch(
            download_path=video_path
        ) # CAN WE GET THIS TO JUST RETURN FILEPATH
        video_list = list(videos["video"])
    else:
        key["dlc_training"] = "True"
        videos = (tables_dlc["Video"] * tables_dlc["World"] & key).fetch(
            download_path=video_path
        )
        video_list = list(videos["video"])

    import deeplabcut

    conf = deeplabcut.create_new_project(
        name,
        key["experimenter"],
        video_list,
        working_directory=folder,
        copy_videos=False,
    )

    # read the config file
    with open(conf, "r") as f:
        config_dict = yaml.safe_load(f)

    # get the behaviour dict
    behaviour = (tables_dlc["BehaviourRig"] & key).fetch1("rig_json")

    bodyparts = []
    for feature in behaviour["features"]:
        if (
            "source_type" in feature["source"]
            and feature["source"]["source_type"] == "deeplabcut"
        ):
            bodyparts.append(feature["name"])

    # add to config dict
    config_dict["bodyparts"] = bodyparts
    del config_dict["skeleton"]
    with open(conf, "w") as f:
        yaml.dump(config_dict, f)

    return conf


def upload_dlc(key, username=None, password=None):
    """
    Function zips the labelled frames folder and uploads to the database along with the config json
    """

    conn_dlc, tables_dlc = thread_connect(username=username, password=password)

    name = f"{key['experimenter']}_{key['behaviourrig_id']}_{key['experiment_id']}_{key['dlcmodel_id']}"
    conf = st.session_state.dlc_folder[name]
    comp = conf.parent / "compute.json"

    # read the config file
    with open(conf, "r") as f:
        config_dict = yaml.safe_load(f)
    with open(comp, "r") as f:
        compute_dict = json.load(f)
    params_dict = {"config": config_dict, "compute": compute_dict}

    # zip the labelled frames folder
    labelled_frames = conf.parent / "labeled-data"
    target = conf.parent.parent / f"{name}_labelled_frames"
    shutil.make_archive(target, "zip", labelled_frames)
    labeled_zip = target.with_suffix(".zip")

    # upload to database
    key["dlcparams"] = params_dict
    key["labelled_frames"] = str(labeled_zip)
    key["labelledframes_in_compute"] = "False"

    primary_key = {key:val for key, val in key.items() if key in ["experimenter", "behaviourrig_id", "experiment_id", "dlcmodel_id"]}
    print(key)

    if len(tables_dlc["LabelledFrames"]._admin() & primary_key) == 0:
        tables_dlc["LabelledFrames"].insert1(key, allow_direct_insert=True)
    else:
        # if it already exists, delete the old one
        tables_dlc["LabelledFrames"].delete(primary_key, force=True)
        tables_dlc["LabelledFrames"].insert1(key, allow_direct_insert=True, skip_duplicates=True)

