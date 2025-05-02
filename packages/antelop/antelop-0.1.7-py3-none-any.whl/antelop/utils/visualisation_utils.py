import streamlit as st
import streamlit_antd_components as sac
import numpy as np
from plotly import graph_objects as go
from antelop.connection import import_schemas
import antelop.connection.st_connect as connect
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import probeinterface as pi
from probeinterface.plotting import plot_probe_group
from pathlib import Path
import os


@st.cache_data(ttl=3600, max_entries=3)
def plot_session(session_dict, selected_animals, selected_objects, timerange):
    # unpack objects
    (
        analog_groups,
        digital_groups,
        interval_objects,
        kinematics_objects,
        masks_objects,
    ) = selected_objects

    conn = st.session_state.conn
    tables = st.session_state.tables

    # get spike trains for the selected animals and sorting parameters - requires a slight abuse of union
    query = False
    for i, (animal_id, param_id, selected_units, selected_lfps) in enumerate(
        selected_animals
    ):
        if i == 0:
            query = (
                tables["SpikeTrain"].proj()
                & session_dict
                & {"animal_id": animal_id, "sortingparams_id": param_id}
                & selected_units
            )
        else:
            query = query + (
                tables["SpikeTrain"].proj()
                & session_dict
                & {"animal_id": animal_id, "sortingparams_id": param_id}
                & selected_units
            )

    spiketrains = (
        tables["SpikeTrain"] * tables["Animal"].proj("animal_name") & query
    ).fetch()

    # get lfps for the selected animals and sorting parameters
    query = False
    for i, (animal_id, param_id, selected_units, selected_lfps) in enumerate(
        selected_animals
    ):
        if i == 0:
            query = (
                tables["LFP"].proj()
                & session_dict
                & {"animal_id": animal_id, "sortingparams_id": param_id}
                & selected_lfps
            )
        else:
            query = query + (
                tables["LFP"].proj()
                & session_dict
                & {"animal_id": animal_id, "sortingparams_id": param_id}
                & selected_lfps
            )

    lfps = (tables["LFP"] * tables["Animal"].proj("animal_name") & query).fetch()

    # update spiketrains to only include the selected time range
    for i, unit in enumerate(spiketrains):
        spiketrain = unit["spiketrain"]
        spiketrains[i]["spiketrain"] = spiketrain[
            (spiketrain >= timerange[0]) & (spiketrain <= timerange[1])
        ]

    # update lfps to only include the selected time range
    for i, lfp in enumerate(lfps):
        sample_rate = lfp["lfp_sample_rate"]
        start_sample = int(timerange[0] * sample_rate)
        end_sample = int(timerange[1] * sample_rate)
        lfps[i]["lfp"] = lfp["lfp"][start_sample:end_sample]

    # calculate animals
    animals = np.unique(spiketrains["animal_name"])

    # calculate unit numbers per animal
    unit_numbers = [
        len(spiketrains[spiketrains["animal_name"] == animal]) for animal in animals
    ]

    # make list of subplot heights
    subplot_heights = [30 + i * 6 for i in unit_numbers]
    subplot_heights += [20] * len(lfps)
    subplot_heights += [50] * len(analog_groups)
    subplot_heights += [50] * len(digital_groups)
    if len(interval_objects) > 0:
        subplot_heights.append(8 * len(interval_objects))
    if len(kinematics_objects) > 0:
        subplot_heights.append(8 * len(kinematics_objects))
        subplot_heights.append(8 * len(kinematics_objects))
    if len(masks_objects) > 0:
        subplot_heights.append(8 * len(masks_objects))

    # create figure
    fig = make_subplots(
        rows=len(subplot_heights),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=subplot_heights,
    )

    # loop through animals
    for i, animal in enumerate(animals):
        # calculate probes for each animal
        probes = np.unique(
            spiketrains[spiketrains["animal_name"] == animal]["probe_id"]
        )

        # keep track of y position and unit labels
        y_pos = 1
        y_text = []

        # loop through probes
        for j, probe in enumerate(probes):
            # calculate units for each animal and probe
            units = np.unique(
                spiketrains[
                    (spiketrains["animal_name"] == animal)
                    & (spiketrains["probe_id"] == probe)
                ]["unit_id"]
            )

            # loop through units
            for k, unit in enumerate(units):
                # store y label
                y_text.append(str(probe) + "-" + str(unit))

                # get spike times for each unit
                spiketrain = spiketrains[
                    (spiketrains["animal_name"] == animal)
                    & (spiketrains["probe_id"] == probe)
                    & (spiketrains["unit_id"] == unit)
                ]["spiketrain"][0]
                spiketrain = spiketrain.astype("float32")

                # create y values for each unit
                y = np.ones_like(spiketrain, dtype="uint8") * y_pos

                # add unit to plot
                fig.add_trace(
                    go.Scattergl(
                        x=spiketrain,
                        y=y,
                        mode="markers",
                        marker=dict(symbol="line-ns-open"),
                        name=str(unit),
                        showlegend=False,
                    ),
                    row=i + 1,
                    col=1,
                )

                # update y position
                y_pos += 1

        # update axes
        fig.update_yaxes(
            title_text=f"{animal} spiketrains",
            tickvals=np.arange(1, y_pos),
            ticktext=y_text,
            row=i + 1,
            col=1,
        )

    # current row
    row = len(animals)

    for i, lfp in enumerate(lfps):
        # make timestamps
        timestamps = np.arange(lfp["lfp"].size) / lfp["lfp_sample_rate"] + timerange[0]

        name = f"{lfp['probe_id']}-{lfp['channel_id']}"

        # add lfp to plot
        fig.add_trace(
            go.Scattergl(
                x=timestamps, y=lfp["lfp"], mode="lines", name=name, showlegend=False
            ),
            row=row + 1,
            col=1,
        )
        fig.update_yaxes(title_text=name, row=row + 1, col=1)
        row += 1

    # loop through analog events
    for i, (name, group) in enumerate(analog_groups):
        row += 1

        # pull data
        groupdata = (
            tables["AnalogEvents"] * tables["Object"].proj("object_name")
            & session_dict
            & group
        ).fetch(as_dict=True)

        # filter data to be in timerange
        for j, event in enumerate(groupdata):
            timestamps = event["timestamps"]
            data = event["data"]
            groupdata[j]["timestamps"] = timestamps[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]
            groupdata[j]["data"] = data[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]

        # plot events
        for event in groupdata:
            if event["timestamps"].size > 0:
                fig.add_trace(
                    go.Scattergl(
                        x=event["timestamps"],
                        y=event["data"],
                        mode="lines",
                        name=event["object_name"],
                        showlegend=True,
                    ),
                    row=row,
                    col=1,
                )

        fig.update_yaxes(title_text=f"{name} ({event['unit']})", row=row, col=1)

    # loop through digital events
    for i, (name, group) in enumerate(digital_groups):
        row += 1

        # pull data
        groupdata = (
            tables["DigitalEvents"] * tables["Object"].proj("object_name")
            & session_dict
            & group
        ).fetch(as_dict=True)

        # filter data to be in timerange
        for j, event in enumerate(groupdata):
            timestamps = event["timestamps"]
            data = event["data"]
            groupdata[j]["timestamps"] = timestamps[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]
            groupdata[j]["data"] = data[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]

        # plot events
        for event in groupdata:
            fig.add_trace(
                go.Scattergl(
                    x=event["timestamps"],
                    y=event["data"],
                    mode="markers",
                    name=event["object_name"],
                    showlegend=True,
                ),
                row=row,
                col=1,
            )

        fig.update_yaxes(title_text=f"{name} ({event['unit']})", row=row, col=1)

    # loop through interval events
    if len(interval_objects) > 0:
        row += 1
        y_text = []

        # pull data
        interval_events = (
            tables["IntervalEvents"] * tables["Object"].proj("object_name")
            & session_dict
            & interval_objects
        ).fetch(as_dict=True)

        # filter data to be in timerange
        for j, event in enumerate(interval_events):
            timestamps = event["timestamps"]
            data = event["data"]
            interval_events[j]["timestamps"] = timestamps[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]
            interval_events[j]["data"] = data[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]

        for i, event in enumerate(interval_events):
            y_text.append(event["object_name"])

            # get timestamps and data
            timestamps = event["timestamps"]
            data = event["data"]

            # clean data
            if len(data) > 0:
                if data[0] == -1:
                    data = data[1:]
                    timestamps = timestamps[1:]
            if len(data) > 0:
                if data[-1] == 1:
                    data = data[:-1]
                    timestamps = timestamps[:-1]

            # slightly hacky - convert -1 to 2, then duplicate timestamps
            data = (-data + 3) // 2
            timestamps = np.repeat(timestamps, data)

            # now make y values, where every third value is none
            y = np.ones_like(timestamps) * i
            y[2::3] = None

            fig.add_trace(
                go.Scattergl(
                    x=timestamps,
                    y=y,
                    mode="lines",
                    name=event["object_name"],
                    showlegend=False,
                ),
                row=row,
                col=1,
            )

        fig.update_yaxes(
            title_text="Interval events",
            tickvals=np.arange(len(y_text)),
            ticktext=y_text,
            row=row,
            col=1,
        )

    # loop through kinematics events
    if len(kinematics_objects) > 0:
        row += 1

        # pull data
        kinematics_events = (
            tables["Kinematics"] * tables["Object"].proj("object_name")
            & session_dict
            & kinematics_objects
        ).fetch(as_dict=True)

        # filter data to be in timerange
        for j, event in enumerate(kinematics_events):
            timestamps = event["timestamps"]
            x, y = event["data"][:, 0], event["data"][:, 1]
            kinematics_events[j]["timestamps"] = timestamps[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]
            kinematics_events[j]["x"] = x[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]
            kinematics_events[j]["y"] = y[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]

            # get timestamps and data
            timestamps = event["timestamps"]
            x = event["x"]
            y = event["y"]

            # plot events
            if event["timestamps"].size > 0:
                fig.add_trace(
                    go.Scattergl(
                        x=timestamps,
                        y=x,
                        mode="lines",
                        name=f"""{event["object_name"]} x-axis""",
                        showlegend=True,
                    ),
                    row=row,
                    col=1,
                )
                fig.add_trace(
                    go.Scattergl(
                        x=timestamps,
                        y=y,
                        mode="lines",
                        name=f"""{event["object_name"]} y-axis""",
                        showlegend=True,
                    ),
                    row=row + 1,
                    col=1,
                )

        fig.update_yaxes(title_text="Kinematics x-axis", row=row, col=1)
        fig.update_yaxes(title_text="Kinematics y-axis", row=row + 1, col=1)

        row += 1

    # loop through masks events
    if len(masks_objects) > 0:
        row += 1
        y_text = []

        # pull data
        masks_events = (tables["Mask"] & session_dict & masks_objects).fetch(
            as_dict=True
        )

        # filter data to be in timerange
        for j, event in enumerate(masks_events):
            timestamps = event["timestamps"]
            data = event["data"]
            masks_events[j]["timestamps"] = timestamps[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]
            masks_events[j]["data"] = data[
                (timestamps >= timerange[0]) & (timestamps <= timerange[1])
            ]

        for i, event in enumerate(masks_events):
            y_text.append(event["mask_name"])

            # get timestamps and data
            timestamps = event["timestamps"]
            data = event["data"]

            # clean data
            if len(data) > 0:
                if data[0] == -1:
                    data = data[1:]
                    timestamps = timestamps[1:]
            if len(data) > 0:
                if data[-1] == 1:
                    data = data[:-1]
                    timestamps = timestamps[:-1]

            # slightly hacky - convert -1 to 2, then duplicate timestamps
            data = (-data + 3) // 2
            data = data.astype("int", casting="unsafe")
            timestamps = np.repeat(timestamps, data)

            # now make y values, where every third value is none
            y = np.ones_like(timestamps) * i
            y[2::3] = None

            fig.add_trace(
                go.Scattergl(
                    x=timestamps,
                    y=y,
                    mode="lines",
                    name=event["mask_name"],
                    showlegend=False,
                ),
                row=row,
                col=1,
            )

        fig.update_yaxes(
            title_text="Masks",
            tickvals=np.arange(len(y_text)),
            ticktext=y_text,
            row=row,
            col=1,
        )

    # custom layout config that uses the last subplot in a hacky way
    row = "" if row == 1 else row
    fig["layout"][f"xaxis{row}_rangeslider_visible"] = True
    fig["layout"][f"xaxis{row}_rangeslider_thickness"] = 0.05
    fig["layout"][f"xaxis{row}_title"] = "Time (seconds)"
    fig["layout"][f"xaxis{row}_range"] = timerange

    # global layout config
    fig.update_layout(height=sum(subplot_heights) * 5, width=800)

    return fig


@st.cache_data(ttl=3600, max_entries=3)
def plot_kinematics(kinematics_dict, timerange):

    conn = st.session_state.conn
    tables = st.session_state.tables

    # pull data
    kinematics_events = (
        tables["Kinematics"] * tables["Object"].proj("object_name") & kinematics_dict
    ).fetch(as_dict=True)

    # filter data to be in timerange
    for j, event in enumerate(kinematics_events):
        timestamps = event["timestamps"]
        data = event["data"]
        kinematics_events[j]["timestamps"] = timestamps[
            (timestamps >= timerange[0]) & (timestamps <= timerange[1])
        ]
        kinematics_events[j]["data"] = data[
            (timestamps >= timerange[0]) & (timestamps <= timerange[1])
        ]

    for i, event in enumerate(kinematics_events):
        df = pd.DataFrame(
            {
                "time": kinematics_events[i]["timestamps"],
                "x": kinematics_events[i]["data"][:, 0],
                "y": kinematics_events[i]["data"][:, 1],
            }
        )

        date_to_val = df["time"].map(
            pd.Series(data=np.arange(len(df)), index=df["time"].values).to_dict()
        )
        timerange = df["time"].max() - df["time"].min()
        tickvals = [int(timerange) * k * 2 for k in range(1, 15)]
        dlist = list(date_to_val)
        index_tickvals = [dlist.index(tv) for tv in tickvals]
        ticktext = [format(df["time"][id], ".1f") for id in index_tickvals]

        kin_fig = go.Figure(
            go.Scattergl(
                x=df["x"],
                y=df["y"],
                mode="markers",
                marker_color=date_to_val,
                marker_colorscale="Plasma",
                marker_showscale=True,
                marker_size=8,
                marker_colorbar=dict(
                    tickvals=tickvals, ticktext=ticktext, title_text="Time (s)"
                ),
                customdata=df["time"],
                hovertemplate="%{customdata}<br>x: %{x}<br>y: %{y}",
            )
        )

        kin_fig.update_layout(
            width=800,
            height=700,
            title_text=f"{event['object_name'].capitalize()} kinematics",
            xaxis_title="x (pixels)",
            yaxis_title="y (pixels)",
        )

    return kin_fig


def choose_animals(tables, session_dict):
    # calculate what animals have spikesorted data
    animals = (
        (
            tables["Animal"] * tables["SpikeSorting"] * tables["SortingParams"]
            & session_dict
        )
        .proj("animal_name", "sortingparams_name")
        .fetch()
    )

    # loop through animals, and make dict of animal ids to animal names
    animal_dict = {}
    for animal in animals:
        animal_dict[animal["animal_name"]] = animal["animal_id"]

    # make another dict that keeps track of the sorting parameters for each animal
    params_dict = {}
    for animal_id in animal_dict.values():
        ids = animals[animals["animal_id"] == animal_id]["sortingparams_id"]
        names = animals[animals["animal_id"] == animal_id]["sortingparams_name"]
        params_dict[animal_id] = {name: id for id, name in zip(ids, names)}

    # get user to select the animals they want to visualise
    if len(animal_dict) > 1:
        selected_animals = st.multiselect(
            "Select the animals you want to visualise",
            list(animal_dict.keys()),
            list(animal_dict.keys())[0],
        )
    elif len(animal_dict) == 1:
        selected_animals = list(animal_dict.keys())
    else:
        return []

    st.divider()
    st.markdown("**Neural activity**")

    # loop through selected animals, and choose a unique sorting parameter if there are multiple
    animals_with_sorting = []
    for animal in selected_animals:
        if len(params_dict[animal_dict[animal]]) > 1:
            param_id = params_dict[animal_dict[animal]][
                st.selectbox(
                    f"The animal '{animal}' has been spikesorted multiple times, please select which sorting parameter set you want to visualise",
                    list(params_dict[animal_dict[animal]].keys()),
                )
            ]
        else:
            param_id = list(params_dict[animal_dict[animal]].values())[0]

        # now, for this animal, select the units you want to visualise
        # first query the probes
        probes = (
            tables["Probe"]
            & session_dict
            & {"animal_id": animal_dict[animal], "sortingparams_id": param_id}
        ).fetch(as_dict=True)

        # initialise selected units
        selected_units = []
        selected_lfps = []

        st.text("")
        st.markdown("***Units***")
        st.text(f'Select the units you want to visualise for animal "{animal}"')

        # loop through probes and get user to select units
        for probe in probes:
            # get units for this probe
            units = (
                tables["Unit"]
                & session_dict
                & {
                    "animal_id": animal_dict[animal],
                    "sortingparams_id": param_id,
                    "probe_id": probe["probe_id"],
                }
            ).fetch(as_dict=True)

            # make a dict mapping unit names to unit dicts
            unit_dict = {}
            for unit in units:
                unit_dict[str(unit["unit_id"])] = unit

            # get user to select the units they want to visualise
            selected_units += [
                unit_dict[i]
                for i in sac.checkbox(
                    items=list(unit_dict.keys()),
                    label=f"""Probe {probe["probe_id"]} units""",
                    index=list(range(len(unit_dict))),
                    check_all="Select all",
                )
            ]

        st.markdown("***LFPs***")
        st.text(f'Select the LFPs you want to visualise for animal "{animal}"')

        # loop through probes and get user to select units
        for probe in probes:
            # get units for this probe
            lfps = (
                tables["Channel"].proj()
                & session_dict
                & {
                    "animal_id": animal_dict[animal],
                    "sortingparams_id": param_id,
                    "probe_id": probe["probe_id"],
                }
            ).fetch(as_dict=True)

            # make a dict mapping unit names to unit dicts
            lfp_dict = {}
            for lfp in lfps:
                lfp_dict[str(lfp["channel_id"])] = lfp

            # get user to select the units they want to visualise
            selected_lfps += [
                lfp_dict[i]
                for i in sac.checkbox(
                    items=list(lfp_dict.keys()),
                    label=f"""Probe {probe["probe_id"]} channels""",
                    check_all="Select all",
                )
            ]

        animals_with_sorting.append(
            (animal_dict[animal], param_id, selected_units, selected_lfps)
        )

    return animals_with_sorting


def choose_kinematics(tables, session_dict):
    if len(tables["Kinematics"] & session_dict) == 0:
        return []
    st.divider()

    # get the objects for this session
    kinematics = (tables["Object"] * tables["Kinematics"].proj() & session_dict).fetch(
        as_dict=True
    )

    # for interval events, just select any objects
    st.markdown("***Kinematics object***")
    kinematics_dict = {obj["object_name"]: obj for obj in kinematics}
    selected_object = kinematics_dict[
        st.selectbox("Select kinematics object", list(kinematics_dict.keys()))
    ]

    return selected_object


def choose_objects(tables, session_dict):
    if (
        len(tables["AnalogEvents"] & session_dict) == 0
        and len(tables["DigitalEvents"] & session_dict) == 0
        and len(tables["IntervalEvents"] & session_dict) == 0
        and len(tables["Kinematics"] & session_dict) == 0
        and len(tables["Mask"] & session_dict) == 0
    ):
        return ([], [], [], [], [])
    st.divider()
    st.markdown("**Environment features**")

    # get the objects for this session
    analog = (
        tables["Object"] * tables["AnalogEvents"].proj("unit") & session_dict
    ).fetch(as_dict=True)
    digital = (
        tables["Object"] * tables["DigitalEvents"].proj("unit") & session_dict
    ).fetch(as_dict=True)
    interval = (
        tables["Object"] * tables["IntervalEvents"].proj() & session_dict
    ).fetch(as_dict=True)
    kinematics = (tables["Object"] * tables["Kinematics"].proj() & session_dict).fetch(
        as_dict=True
    )
    masks = (tables["Mask"].proj("mask_name") & session_dict).fetch(as_dict=True)

    # for analog events, we want the user to be able to add a number of groups with a common y axis
    analog_groups = []
    analog_used = []
    st.markdown("***Analog events***")
    i = 1
    keep_going = st.checkbox(f"Add group {i}", key=f"Add group {i}")
    while keep_going:
        # get the user to select objects not already in a group
        analog_dict = {
            obj["object_name"]: obj
            for obj in analog
            if obj["object_name"] not in analog_used
        }
        name = st.text_input("Enter name", list(analog_dict.keys())[0])
        selected_objects = sac.checkbox(
            items=analog_dict.keys(),
            label=f"Select the objects you want to visualise for group {i}",
            check_all="Select all",
        )

        # ask user if they want a new group
        i += 1
        if len(selected_objects) > 0:
            # check all selected objects have the same unit
            if (
                len(
                    set(
                        [analog_dict[obj_name]["unit"] for obj_name in selected_objects]
                    )
                )
                > 1
            ):
                st.error("All objects in a group must have the same unit")
                keep_going = False

            else:
                analog_used += selected_objects
                analog_groups.append(
                    (name, [analog_dict[obj_name] for obj_name in selected_objects])
                )

                if (
                    len(
                        [obj for obj in analog if obj["object_name"] not in analog_used]
                    )
                    > 0
                ):
                    keep_going = st.checkbox(f"Add group {i}", key=f"Add group {i}")

                else:
                    keep_going = False

        else:
            keep_going = False

    # for digital events, we want the user to be able to add a number of groups with a common y axis
    digital_groups = []
    digital_used = []
    st.markdown("***Digital events***")
    i = 1
    keep_going = st.checkbox(f"Add group {i}", key=f"Add digital group {i}")
    while keep_going:
        # get the user to select objects not already in a group
        digital_dict = {
            obj["object_name"]: obj
            for obj in digital
            if obj["object_name"] not in digital_used
        }
        name = st.text_input("Enter name", list(digital_dict.keys())[0])
        selected_objects = sac.checkbox(
            items=digital_dict.keys(),
            label=f"Select the objects you want to visualise for group {i}",
            check_all="Select all",
        )

        # ask user if they want a new group
        i += 1
        if len(selected_objects) > 0:
            # check all selected objects have the same unit
            if (
                len(
                    set(
                        [
                            digital_dict[obj_name]["unit"]
                            for obj_name in selected_objects
                        ]
                    )
                )
                > 1
            ):
                st.error("All objects in a group must have the same unit")
                keep_going = False

            else:
                digital_used += selected_objects
                digital_groups.append(
                    (name, [digital_dict[obj_name] for obj_name in selected_objects])
                )

                if (
                    len(
                        [
                            obj
                            for obj in digital
                            if obj["object_name"] not in digital_used
                        ]
                    )
                    > 0
                ):
                    keep_going = st.checkbox(
                        f"Add group {i}", key=f"Add digital group {i}"
                    )

                else:
                    keep_going = False

        else:
            keep_going = False

    # for interval events, just select any objects
    st.markdown("***Interval events***")
    interval_dict = {obj["object_name"]: obj for obj in interval}
    selected_objects = sac.checkbox(
        items=interval_dict.keys(),
        label="Select the interval events you want to visualise",
        check_all="Select all",
    )

    interval_objects = [interval_dict[obj_name] for obj_name in selected_objects]

    # for interval events, just select any objects
    st.markdown("***Kinematics object***")
    kinematics_dict = {obj["object_name"]: obj for obj in kinematics}
    selected_objects = sac.checkbox(
        items=kinematics_dict.keys(),
        label="Select the kinematics objects you want to visualise",
        check_all="Select all",
    )

    kinematics_objects = [kinematics_dict[obj_name] for obj_name in selected_objects]

    # for mask events, just select any objects
    st.markdown("***Masks***")
    mask_dict = {obj["mask_name"]: obj for obj in masks}
    selected_objects = sac.checkbox(
        items=mask_dict.keys(),
        label="Select the mask events you want to visualise",
        check_all="Select all",
    )

    mask_objects = [mask_dict[obj_name] for obj_name in selected_objects]

    return (
        analog_groups,
        digital_groups,
        interval_objects,
        kinematics_objects,
        mask_objects,
    )


@st.cache_data(ttl=3600, max_entries=3)
def plot_units(spikesorting_dict, selected_units):

    conn = st.session_state.conn
    tables = st.session_state.tables

    # fetch waveform data
    waveforms = (tables["Waveform"] & spikesorting_dict & selected_units).fetch()

    # loop through probes
    probes = np.unique(waveforms["probe_id"])
    figures = {}

    for probe in probes:
        # get unique channels for this probe
        channels = np.unique(waveforms[waveforms["probe_id"] == probe]["channel_id"])
        figures[int(probe)] = {}

        # split channels into groups of 4 (2x2 layout)
        channel_groups = [channels[i:i + 4] for i in range(0, len(channels), 4)]

        for group_idx, group_channels in enumerate(channel_groups):
            # make subplots
            num_rows = (len(group_channels) + 1) // 2  # Max 2 rows
            fig = make_subplots(
                rows=num_rows,
                cols=2,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=[f"Channel {channel}" for channel in group_channels],
            )

            # loop through channels in the group
            for i, channel in enumerate(group_channels):
                # get units for this channel
                units = waveforms[
                    (waveforms["probe_id"] == probe) & (waveforms["channel_id"] == channel)
                ]

                # plot units
                for j, unit in enumerate(units):
                    waveform = np.median(unit["waveform"], axis=0)
                    timestamps = (
                        np.arange(waveform.shape[0]) / (unit["waveform_sample_rate"] / 1000)
                    ) - unit["ms_before"]

                    color = px.colors.qualitative.Plotly[
                        j % len(px.colors.qualitative.Plotly)
                    ]

                    fig.add_trace(
                        go.Scattergl(
                            x=timestamps,
                            y=waveform,
                            mode="lines",
                            name=f"Unit {unit['unit_id']}",
                            legendgroup=f"Unit {unit['unit_id']}",
                            line=dict(color=color),
                            showlegend=True if i == 0 else False,
                        ),
                        row=(i // 2) + 1,
                        col=(i % 2) + 1,
                    )

                fig.update_yaxes(title_text="Voltage (uV)", row=(i // 2) + 1, col=(i % 2) + 1)
                if (i // 2) + 1 == num_rows:
                    fig.update_xaxes(title_text="Time (ms)", row=(i // 2) + 1, col=(i % 2) + 1)

            fig.update_layout(
                title=f"Probe {probe} - Group {group_idx + 1} waveforms",
                showlegend=True,
                width=800,
                height=400 * num_rows,
            )

            figures[int(probe)][f"Group {group_idx + 1}"] = fig

    return figures


@st.cache_data(ttl=3600, max_entries=3)
def plot_isi(spikesorting_dict, selected_units):
    """
    Plot the isi of the selected units
    """

    conn = st.session_state.conn
    tables = st.session_state.tables

    # fetch spiketrains
    spiketrains = (tables["SpikeTrain"] & spikesorting_dict & selected_units).fetch()

    # loop through probes
    probes = np.unique(spiketrains["probe_id"])
    figures = {}

    for probe in probes:
        # get unique channels for this probe
        units = np.unique(spiketrains[spiketrains["probe_id"] == probe]["unit_id"])

        # make subplots
        fig = make_subplots(
            rows=(len(units) + 1) // 2,
            cols=2,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=[f"Unit {unit}" for unit in units],
        )

        # loop through channels
        for i, unit in enumerate(units):
            spiketrain = spiketrains[
                (spiketrains["probe_id"] == probe) & (spiketrains["unit_id"] == unit)
            ]

            # calculate intervals
            isi = np.diff(spiketrain["spiketrain"][0])
            isi = isi[isi > 0]
            isi = isi * 1000
            isi = isi[isi < 10]
            isi = np.append(isi, -1 * isi)

            fig.add_trace(
                go.Histogram(
                    x=isi,
                    name=f"Unit {spiketrain['unit_id']}",
                    legendgroup=f"Unit {spiketrain['unit_id']}",
                    nbinsx=100,
                    histnorm="probability density",
                ),  # in the future this will need to be changed if we have sparse extraction
                row=(i // 2) + 1,
                col=(i % 2) + 1,
            )

            fig.update_yaxes(
                title_text="ISI histogram", row=(i // 2) + 1, col=(i % 2) + 1
            )
            if i // 2 + 1 == len(units) // 2 or len(units) == 1:
                fig.update_xaxes(
                    title_text="Time (ms)",
                    row=(i // 2) + 1,
                    col=(i % 2) + 1,
                    showticklabels=True,
                )
            else:
                fig.update_xaxes(showticklabels=True, row=(i // 2) + 1, col=(i % 2) + 1)
        fig.update_layout(
            title=f"Probe {probe} ISI histograms",
            width=800,
            height=400 * ((len(units) + 1) // 2),
            showlegend=False,
        )
        figures[int(probe)] = fig

    return figures


@st.cache_data(ttl=3600, max_entries=3)
def unit_stats(spikesorting_dict, selected_units):
    """
    Computes some statistics for each unit
    """

    conn = st.session_state.conn
    tables = st.session_state.tables

    # fetch spiketrains
    spiketrains = (tables["SpikeTrain"] & spikesorting_dict & selected_units).fetch()

    # loop through probes
    probes = np.unique(spiketrains["probe_id"])
    figures = {}

    for probe in probes:
        data = []

        T = (tables['Session'] & spikesorting_dict).fetch1('session_duration')

        # get unique channels for this probe
        units = np.unique(spiketrains[spiketrains["probe_id"] == probe]["unit_id"])

        # loop through channels
        for i, unit in enumerate(units):
            spiketrain = spiketrains[
                (spiketrains["probe_id"] == probe) & (spiketrains["unit_id"] == unit)
            ]

            N = len(spiketrain["spiketrain"][0])
            diff = 1000 * np.diff(spiketrain["spiketrain"][0])
            tr = 1.5  # violation threshold in ms
            nv = len(diff[diff < tr])
            C = (nv * T) / (2 * N**2 * tr)  # formula from ultramegasort package

            mean_rate = N / T

            data.append(
                {"Unit": unit, "Mean firing rate (Hz)": mean_rate, "ISI violations": C}
            )

        figures[int(probe)] = pd.DataFrame(data)

    return figures


def plot_probe(probefile):

    # check if probefile in resources
    resources = Path(os.path.abspath(__file__)).parent.parent / "resources"
    for path in resources.rglob(Path(probefile).with_suffix(".png").name):
        if path.is_file():
            return path
    
    # otherwise plot manually
    probe = pi.io.read_probeinterface(probefile)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    plot_probe_group(probe, ax=ax)
    return fig
