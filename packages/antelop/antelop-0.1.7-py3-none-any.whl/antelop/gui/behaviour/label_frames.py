import streamlit as st
from antelop.utils.streamlit_utils import dropdown_query_table, edit_params, create_dlc_folder, check_dlc_folder, upload_dlc
from antelop.utils.multithreading_utils import dlc_thread_pool, dlcup_thread_pool
from antelop.connection.transaction import transaction_context
from antelop.utils.antelop_utils import (
    extract_frames,
)
import streamlit_antd_components as sac
import pandas as pd
import json
import yaml


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Behaviour")
        st.subheader("Label frames for DeepLabCut training.")

        if len(tables["World"] & {"experimenter": username}) == 0:
            st.text("")
            st.warning("No data found.")
            return

        st.divider()

        st.subheader("Select Experiment")

        _, key = dropdown_query_table(
            tables, {"Experiment": tables["Experiment"]}, username, headless=True
        )
        rigs = (tables["BehaviourRig"] & key).fetch()
        rigdict = {i["behaviourrig_name"]: i["behaviourrig_id"] for i in rigs}
        key["behaviourrig_id"] = rigdict[
            st.selectbox("Select behaviourrig_name", rigdict.keys())
        ]
        dlcmodel_id = (
            max(list((tables["LabelledFrames"] & key).fetch("dlcmodel_id")), default=0)
            + 1
        )
        st.selectbox("Select dlcmodel_id", [dlcmodel_id])
        key["dlcmodel_id"] = dlcmodel_id
        st.info(
            "You can only label frames for a new model here. If you want to update a previous training set, you need to delete it and create a new training dataset."
        )

        if "experiment_id" in key:
            # fetch rig to check it has body parts
            rigjson = (tables["BehaviourRig"] & key).fetch1("rig_json")
            bodypart = False
            for feature in rigjson["features"]:
                if (
                    "source_type" in feature["source"]
                    and feature["source"]["source_type"] == "deeplabcut"
                ):
                    bodypart = True

            if not bodypart:
                st.error(
                    "This rig does not have any body parts to label. Please add body parts to the rig before proceeding."
                )
            else:
                # add dlc folder to session state if it exists
                if "dlc_folder" not in st.session_state:
                    st.session_state.dlc_folder = {}
                status, conf = check_dlc_folder(key, tables)
                name = f"{key['experimenter']}_{key['behaviourrig_id']}_{key['experiment_id']}_{key['dlcmodel_id']}"
                if status:
                    st.session_state.dlc_folder[name] = conf

                st.divider()

                sac.buttons(
                    [
                        sac.ButtonsItem(label="Select Training Videos"),
                        sac.ButtonsItem(label="Download Videos"),
                        sac.ButtonsItem(label="Enter Parameters"),
                        sac.ButtonsItem(label="Extract Frames"),
                        sac.ButtonsItem(label="Label Frames"),
                    ],
                    key="mode",
                    gap="md",
                    use_container_width=True,
                )

                if st.session_state.mode == "Select Training Videos":
                    videos = pd.DataFrame(
                        (tables["World"] * tables["Session"].proj("session_name") & key)
                        .proj("session_id", "session_name", "dlc_training")
                        .fetch()
                    )
                    videos["dlc_training"] = videos["dlc_training"].map(
                        {"True": True, "False": False}
                    )

                    st.text("")
                    st.info(
                        "Here you can update which sessions belong in the training set for your deeplabcut model."
                    )
                    st.warning(
                        """Note, these videos will need to get downloaded to your local machine for you to annotate them, so selecting too many will make this download very slow."""
                    )
                    st.text("")

                    edited_videos = st.data_editor(
                        videos,
                        column_config={"dlc_training": st.column_config.CheckboxColumn()},
                        disabled=["session_id", "session_name"],
                        column_order=["session_id", "session_name", "dlc_training"],
                        hide_index=True,
                        use_container_width=True,
                    )

                    st.text("")

                    if st.button("Save"):
                        merge = pd.merge(edited_videos, videos, how="left", indicator=True)
                        merge = merge[merge["_merge"] == "left_only"]
                        merge["dlc_training"] = merge["dlc_training"].map(
                            {True: "True", False: "False"}
                        )
                        del merge["session_name"]
                        del merge["_merge"]

                        with transaction_context(tables["World"].connection):
                            for i, row in merge.iterrows():
                                tables["World"].update1(row.to_dict())

                if st.session_state.mode == "Download Videos":
                    if name in st.session_state.dlc_folder.keys():
                        st.text("")
                        st.info("Training videos already downloaded.")

                    else:
                        st.text("")
                        st.info(
                            "Training videos can take a while to download, so this will occur in a separate thread."
                        )
                        st.text("")

                        if st.button("Download training videos"):
                            dlc_pool = dlc_thread_pool()
                            future = dlc_pool.submit(create_dlc_folder, key, st.session_state.username, st.session_state.password)
                            st.session_state.download_dlc_futures.append((future, name))
                            st.success("Download in progress.")

                        # add a button which shows download statuses
                        # uses all downloads in current session stored in session state
                        if "download_dlc_futures" in st.session_state:
                            if st.button("Check download progress"):
                                st.write("Download statuses:")

                                # initialise data
                                display_futures = []

                                # display job progress
                                for (
                                    future,
                                    query_name,
                                ) in st.session_state.download_dlc_futures:
                                    # compute statuses
                                    if future.done():
                                        if future.exception():
                                            status = "download error"
                                            print(future.exception())
                                        else:
                                            status = "download success"
                                    else:
                                        status = "download in progress"

                                    display_futures.append((query_name, status))

                                # make dataframe to display
                                df = pd.DataFrame(
                                    display_futures, columns=["Query", "Status"]
                                )

                                # show dataframe
                                st.dataframe(df, hide_index=True)

                if st.session_state.mode == "Enter Parameters":
                    if name not in st.session_state.dlc_folder.keys():
                        st.error(
                            """You need to download the training videos to your machine first."""
                        )

                    else:
                        st.text("")
                        st.info("Please edit the parameters for your DeepLabCut model.")
                        st.text("")
                        new_params = edit_params(key, tables)

                        st.text("")
                        if st.button("Save parameters"):
                            conf = st.session_state.dlc_folder[name]
                            with open(conf, "w") as f:
                                yaml.dump(new_params["config"], f)
                            comp = conf.parent / "compute.json"
                            with open(comp, "w") as f:
                                json.dump(new_params["compute"], f)
                            st.success("Parameters saved!")

                if st.session_state.mode == "Extract Frames":
                    if name not in st.session_state.dlc_folder.keys():
                        st.error("Please enter parameters first.")
                        return
                    else:
                        algo = st.selectbox(
                            "Select mode for frame extraction", ["uniform", "kmeans"]
                        )
                        st.text("")
                        if st.button("Extract frames"):
                            dlc_pool = dlc_thread_pool()
                            conf = st.session_state.dlc_folder[name]
                            future = dlc_pool.submit(extract_frames, *(conf, algo))
                            st.session_state.extract_frames_futures.append((future, name))
                            st.success("Extraction in progress.")

                if st.session_state.mode == "Label Frames":
                    if name not in st.session_state.dlc_folder.keys():
                        st.error("Please enter parameters first.")

                    elif not any(
                        (
                            st.session_state.dlc_folder[name].parent / "labeled-data"
                        ).iterdir()
                    ):
                        st.error("Please extract frames first.")

                    else:
                        conf = st.session_state.dlc_folder[name]
                        videos = conf.parent / "labeled-data"
                        vid_dict = {i.stem: i for i in videos.iterdir() if i.is_dir()}
                        selected_vid = vid_dict[
                            st.selectbox("Select video to label", list(vid_dict.keys()))
                        ]

                        st.text("")
                        st.info(
                            """Please use the button below to open a separate GUI to label your training frames. Make sure to save your results when you're done."""
                        )
                        st.text("")
                        if st.button("Label frames"):
                            command = f"""import deeplabcut; deeplabcut.label_frames(['{str(conf)}','{str(selected_vid)}'])"""
                            st.text("")
                            st.write(
                                "Please open an IPython console inside your antelop conda environment and copy and paste in the following command:"
                            )
                            st.code(command)
                            st.warning(
                                "This is a temporary measure while we figure out a bug in DeepLabCut"
                            )

                        st.text("")
                        st.info(
                            "Once you are happy with your labelled frames, use the button below to upload them to the database. You are required to do this before you can train your model on the cluster."
                        )
                        st.text("")
                        if st.button("Upload results"):
                            dlcup_pool = dlcup_thread_pool()
                            future = dlcup_pool.submit(
                                upload_dlc,
                                key,
                                username=st.session_state.username,
                                password=st.session_state.password,
                            )
                            st.session_state.upload_dlc_futures.append((future, name))
                            st.success("Upload in progress.")

                        if "upload_dlc_futures" in st.session_state:
                            if st.button("Check upload progress"):
                                st.write("Upload statuses:")

                                # initialise data
                                display_futures = []

                                # display job progress
                                for (
                                    future,
                                    query_name,
                                ) in st.session_state.upload_dlc_futures:
                                    # compute statuses
                                    if future.done():
                                        if future.exception():
                                            status = "upload error"
                                            print(future.exception())
                                        else:
                                            status = "upload success"
                                    else:
                                        status = "upload in progress"

                                    display_futures.append((query_name, status))

                                # make dataframe to display
                                df = pd.DataFrame(
                                    display_futures, columns=["Query", "Status"]
                                )

                                # show dataframe
                                st.dataframe(df, hide_index=True)
