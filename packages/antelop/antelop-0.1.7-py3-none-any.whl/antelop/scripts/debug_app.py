import streamlit as st
from antelop.gui import home, search, session, nopermission, export, config
from antelop.gui.ephys import (
    probe_geometry,
    probe_insertion,
    upload_recording,
    spikesorting_parameters,
    schedule_spikesorting,
    manual_curation,
)
from antelop.gui.admin import restore, permanent_delete, release_computation
from antelop.gui.behaviour import (
    define_rig,
    add_features,
    import_data,
    label_frames,
    train_dlc,
    extract_kinematics,
    recompute_masks,
)
from antelop.gui.visualisation import rasters, waveforms, kinematics
from antelop.gui.analysis import analysis, reproduce
import streamlit_antd_components as sac
from antelop.connection import import_schemas, st_connect
from antelop.utils.os_utils import get_config, validate_config, get_config_path
import pymysql
import os


# @st.experimental_dialog('How can I help you?')
def chatgpt():
    if prompt := st.chat_input("Hey there!"):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write(
            f"I'm currently dumb and can only echo what you say.\n{prompt}"
        )


def main():
    # global configurations
    st.set_page_config(
        page_title="Antelop",
        page_icon=":deer:",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            "Get help": "https://antelop.readthedocs.io",
            "Report a Bug": "mailto:rbedford@mrc-lmb.cam.ac.uk",
        },
    )

    # first check if config file exists
    config_file = get_config()
    if config_file is None:
        config.show(None, None)
        st.stop()

    if not validate_config(config_file):
        config_path = get_config_path()
        os.remove(config_path)
        st.rerun()

    # pages to show in app - different for admins
    pages = {
        "Home": home,
        "Search": search,
        "Export": export,
        "Metadata": session,
        "Insert Probe Geometry": probe_geometry,
        "Make Probe Insertion": probe_insertion,
        "Upload Recording": upload_recording,
        "Insert Spikesorting Parameters": spikesorting_parameters,
        "Schedule Spikesorting": schedule_spikesorting,
        "Manual Curation": manual_curation,
        "Define Behaviour Rig": define_rig,
        "Add Features": add_features,
        "Import Behaviour Data": import_data,
        "Label Frames": label_frames,
        "Train DeepLabCut": train_dlc,
        "Extract Kinematics": extract_kinematics,
        "Compute Masks": recompute_masks,
        "Timeseries": rasters,
        "Unit Waveforms": waveforms,
        "Kinematics": kinematics,
        "Run Analysis": analysis,
        "Reproduce Analysis": reproduce,
        "Restore Entries": restore,
        "Permanent Delete": permanent_delete,
        "Release Computation": release_computation,
        "Config": config,
    }

    # initialise authentication status in session state
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = None

    # check login status
    col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
    if not st.session_state.authentication_status:
        with col2:
            with st.container(border=True):
                st.session_state.username = st.text_input("Enter you username")
                st.session_state.password = st.text_input(
                    "Enter your password", type="password"
                )
                if st.button("Login"):
                    st.session_state.authentication_status = (
                        st_connect.check_credentials()
                    )
                    st.rerun()
            st.warning("Please enter your username and password")

    # if logged in successfully
    if st.session_state.authentication_status:
        try:
            # connect to database
            conn = st_connect.connect()

            # import schema structure
            tables = import_schemas.schema(conn)

            st.session_state.conn = conn
            st.session_state.tables = tables

            admin = (
                tables["Experimenter"] & {"experimenter": st.session_state.username}
            ).fetch1("admin") == "True"
            if not admin:
                pages["Restore Entries"] = nopermission
                pages["Permanent Delete"] = nopermission
                pages["Release Computation"] = nopermission

            # read page selection
            with st.sidebar.container():
                st.subheader("Navigation")
                # menu
                menu = sac.menu(
                    items=[
                        sac.MenuItem("Home", icon="house"),
                        sac.MenuItem("Search", icon="search"),
                        sac.MenuItem("Export", icon="download"),
                        sac.MenuItem(type="divider"),
                        sac.MenuItem("Insert + preprocess", type="group"),
                        sac.MenuItem("Metadata", icon="table"),
                        sac.MenuItem(
                            "Electrophysiology",
                            icon="lightning",
                            children=[
                                sac.MenuItem(
                                    "Insert Probe Geometry", icon="bounding-box"
                                ),
                                sac.MenuItem(
                                    "Make Probe Insertion", icon="arrow-down-right"
                                ),
                                sac.MenuItem("Upload Recording", icon="graph-up"),
                                sac.MenuItem(
                                    "Insert Spikesorting Parameters", icon="sliders"
                                ),
                                sac.MenuItem("Schedule Spikesorting", icon="cpu"),
                                sac.MenuItem("Manual Curation", icon="tools"),
                            ],
                        ),
                        sac.MenuItem(
                            "Behaviour",
                            icon="joystick",
                            children=[
                                sac.MenuItem("Define Behaviour Rig", icon="box"),
                                sac.MenuItem("Add Features", icon="ui-radios-grid"),
                                sac.MenuItem(
                                    "Import Behaviour Data", icon="cloud-upload"
                                ),
                                sac.MenuItem("Compute Masks", icon="repeat"),
                                sac.MenuItem("Label Frames", icon="brush"),
                                sac.MenuItem("Train DeepLabCut", icon="cpu"),
                                sac.MenuItem("Extract Kinematics", icon="camera-reels"),
                            ],
                        ),
                        sac.MenuItem(type="divider"),
                        sac.MenuItem(
                            "Visualisation",
                            icon="eye",
                            children=[
                                sac.MenuItem("Timeseries", icon="calendar3-week"),
                                sac.MenuItem("Unit Waveforms", icon="activity"),
                                sac.MenuItem("Kinematics", icon="compass"),
                            ],
                        ),
                        sac.MenuItem(
                            "Analysis",
                            icon="bezier2",
                            children=[
                                sac.MenuItem("Run Analysis", icon="play"),
                                sac.MenuItem(
                                    "Reproduce Analysis", icon="arrow-counterclockwise"
                                ),
                            ],
                        ),
                        sac.MenuItem(type="divider"),
                        sac.MenuItem(
                            "Admin",
                            icon="person-gear",
                            children=[
                                sac.MenuItem(
                                    "Restore Entries", icon="arrow-counterclockwise"
                                ),
                                sac.MenuItem(
                                    "Permanent Delete", icon="exclamation-triangle"
                                ),
                                sac.MenuItem("Release Computation", icon="unlock"),
                            ],
                        ),
                        sac.MenuItem("Config", icon="gear"),
                        sac.MenuItem(
                            "Documentation",
                            icon="journal-code",
                            href="https://antelop.readthedocs.io",
                        ),
                    ],
                    open_all=False,
                    key="menu",
                )

                # show chatbot
                for i in range(5):
                    st.text("")
                _, col, _ = st.columns([0.1, 0.8, 0.1])
                with col:
                    if st.button("Launch Antelop ChatGPT assistant"):
                        chatgpt()

            # show page
            page = pages[menu]
            page.show(st.session_state.username, tables)

        except pymysql.err.InternalError:
            # print warning message
            st.error("Connection lost")
            st.rerun()

    # incorrect credentials
    elif st.session_state.authentication_status == False:
        with col2:
            st.error("Username/password is incorrect")


if __name__ == "__main__":

    main()