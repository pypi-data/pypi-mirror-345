import streamlit as st
from antelop.utils.streamlit_utils import (
    server_directory_browser,
    dropdown_insert_table,
)
from antelop.utils.antelop_utils import insert_nwb, check_animals, check_nwb
from antelop.utils.multithreading_utils import behaviour_thread_pool
import datajoint as dj
import pandas as pd


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Behaviour")
        st.subheader("Import Behaviour Data")

        st.divider()

        st.subheader(
            "Select the session and rig you want to upload behavioural data for"
        )

        tablename, world = dropdown_insert_table(
            tables, {"World": tables["World"]}, username, headless=True
        )

        # if no features in database raise warning
        if tablename == None:
            st.warning(
                """You can't insert any behavioural data because you either don't have the necessary upstream entries or all your sessions already have behavioural data inserted."""
            )

        else:
            st.text("")
            st.info(
                "Select `dlc_training = True` if you want to use this session to train your deeplabcut model."
            )

            # pull behaviour rig
            rig_dict = (tables["BehaviourRig"] & world).fetch1("rig_json")

            # compute the animals in the rig
            animals = check_animals(rig_dict)

            # loop through the animals, getting the user to select which animal it is
            status = True
            animal_keys = {}
            for animal in animals:
                st.divider()
                st.subheader(f"Select animal {animal}")

                # query what animals are in the database
                query = (
                    tables["Animal"]
                    & world
                    & dj.AndList([dj.Not(i) for i in animal_keys.values()])
                )
                animal_select_dict = {
                    i["animal_name"]: i
                    for i in query.proj("animal_name").fetch(as_dict=True)
                }

                # if no animals left, raise warning
                if len(animal_select_dict) == 0:
                    st.warning("No animals left to select")
                    status = False
                    break
                else:
                    # get user to select animal
                    animal_key = animal_select_dict[
                        st.selectbox("Select animal", list(animal_select_dict.keys()))
                    ]
                    del animal_key["animal_name"]
                    animal_keys[animal] = animal_key

            if status:
                # get user to select NWB file
                st.divider()

                st.subheader("Select the NWB file you want to upload")

                nwbpath = server_directory_browser("Select nwb file", "nwb")

                st.divider()

                if st.button("Insert"):
                    # check user only inserting their own data
                    if world["experimenter"] == username:
                        # check nwb file is valid
                        if check_nwb(world, tables, nwbpath):
                            # in separate thread if it has a video, otherwise main thread
                            rig_json = (tables["BehaviourRig"] & world).fetch1(
                                "rig_json"
                            )
                            if ("videos" in rig_json.keys()) and (
                                len(rig_json["videos"]) > 0
                            ):
                                # retrieve thread pool
                                behave_thread_pool = behaviour_thread_pool()

                                # submit job to thread pool
                                query_name = "-".join(
                                    [
                                        key + "-" + str(world[key])
                                        for key in ["experiment_id", "session_id"]
                                    ]
                                )
                                future = behave_thread_pool.submit(
                                    insert_nwb,
                                    world,
                                    animal_keys,
                                    nwbpath,
                                    username=st.session_state.username,
                                    password=st.session_state.password,
                                )
                                st.session_state.behaviour_futures.append(
                                    (future, query_name)
                                )

                                st.text("")
                                st.success("Data insert in progress")

                            else:
                                insert_nwb(world, animal_keys, nwbpath)
                                st.text("")
                                st.success("Data insert success")

                        else:
                            st.text("")
                            st.error("Invalid NWB file")

                    # otherwise print error
                    else:
                        st.text("")
                        st.error("You can only insert your own data!")

            # add a button which shows behaviour statuses
            # uses all behaviours in current session stored in session state
            if ("behaviour_futures" in st.session_state) and (
                len(st.session_state.behaviour_futures) > 0
            ):
                st.text("")

                if st.button("Check upload progress"):
                    st.write("upload statuses:")

                    # initialise data
                    display_futures = []

                    # display job progress
                    for future, query_name in st.session_state.behaviour_futures:
                        # compute statuses
                        if future.done():
                            if future.exception():
                                print(future.exception())
                                status = "upload error"
                            else:
                                status = "upload success"
                        else:
                            status = "upload in progress"

                        display_futures.append((query_name, status))

                    # make dataframe to display
                    df = pd.DataFrame(display_futures, columns=["Query", "Status"])

                    # show dataframe
                    st.dataframe(df, hide_index=True)
