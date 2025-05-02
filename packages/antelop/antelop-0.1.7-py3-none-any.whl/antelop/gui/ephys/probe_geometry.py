import streamlit as st
from antelop.utils.streamlit_utils import (
    dropdown_insert_table,
    server_directory_browser,
    select_probe,
)
from antelop.utils.visualisation_utils import plot_probe
import probeinterface as pi
import json
import streamlit_antd_components as sac
from pathlib import Path
import os


def validate_probe(probefile):
    read_probe = pi.io.read_probeinterface(probefile)
    assert all([probe["ndim"] == 3 for probe in read_probe.to_dict()["probes"]])
    """
    assert all(
        [
            "device_channel_indices" in probe.keys()
            for probe in read_probe.to_dict()["probes"]
        ]
    )
    """


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Electrophysiology")
        st.subheader("Insert Probe Geometry File")

        st.divider()

        # get user to interactively insert table attributes
        tablename, insert_dict = dropdown_insert_table(
            tables,
            {"ProbeGeometry": tables["ProbeGeometry"]},
            username,
            headless=True,
            primary_only=True,
        )

        # get json file
        st.text("")
        option = sac.buttons(
            [
                sac.ButtonsItem(label="Local File", icon="filetype-json"),
                sac.ButtonsItem(label="Standard Library", icon="archive-fill"),
            ],
            use_container_width=True,
        )

        if option == "Local File":
            insert_dict["probe"] = server_directory_browser(
                "Select probe geometry file", "json"
            )
        elif option == "Standard Library":
            probe = select_probe()
            insert_dict["probe"] = str(probe)
        insert_dict["probegeometry_name"] = st.text_input("Enter probe geometry name")

        st.text("")
        col4, col5 = st.columns([0.5, 0.5])

        with col4:
            if st.button("Plot Probe", use_container_width=True):
                try:
                    probefile = insert_dict["probe"]
                    validate_probe(probefile)
                except AssertionError:
                    with col2:
                        st.error(
                            "Probe geometry must be 3D and have channel device indices set."
                        )
                except Exception:
                    with col2:
                        st.error("Probe geometry file not valid!")
                else:
                    st.session_state["plot_probe"] = plot_probe(probefile)

        with col5:
            if st.button("Insert", use_container_width=True):
                # check user only inserting their own data
                if insert_dict["experimenter"] == username:
                    try:
                        # first, validate probe geometry file
                        probefile = insert_dict["probe"]

                        validate_probe(probefile)

                    except AssertionError:
                        with col2:
                            st.error(
                                "Probe geometry must be 3D and have channel device indices set."
                            )

                    except Exception:
                        with col2:
                            st.error("Probe geometry file not valid!")

                    else:
                        # insert into database
                        with open(probefile, "r") as f:
                            insert_dict["probe"] = json.load(f)

                        tables[tablename].insert1(insert_dict)

                        # show success message
                        with col2:
                            st.text("")
                            st.success("Data uploaded to database!")

                # otherwise print error
                else:
                    with col2:
                        st.text("")
                        st.error("You can only insert your own data!")

        if hasattr(st.session_state, "plot_probe"):
            if isinstance(st.session_state["plot_probe"], Path):
                st.image(str(st.session_state["plot_probe"]))
            else:
                st.pyplot(st.session_state["plot_probe"])
