import streamlit as st
from antelop.utils.streamlit_utils import dropdown_query_table
from antelop.utils.external_utils import schedule_spikesorting, spikesorting_progress
import numpy as np


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Electrophysiology")
        st.subheader("Schedule Spikesorting")

        st.divider()

        st.subheader("Select the data you want to sort")

        # get user to interactively select session
        _, session_dict = dropdown_query_table(
            tables=tables,
            subtables={
                "Recording": tables["Recording"]
                & (
                    tables["Recording"]
                    * (tables["SortingParams"] & tables["ProbeInsertion"])
                    - tables["SpikeSorting"]
                ).proj()
            },
            username=username,
            headless=True,
        )

        if session_dict == None:
            st.error(
                """You can't perform any spikesorting yet as you haven't inserted any recordings into the database, or all current recordings have already been spikesorted."""
            )
            st.warning("Please go to the insert tab and add some data.")

        else:
            st.divider()

            # check parameters section
            st.subheader("Check your parameters")

            # query database to show parameter sets for these experiments
            query = (
                (
                    tables["Recording"]
                    & (
                        tables["Recording"]
                        * (tables["SortingParams"] & {"manually_sorted": "False"} & tables["ProbeInsertion"])
                        - tables["SpikeSorting"]
                        & session_dict
                    ).proj()
                )
                .aggr(
                    (
                        tables["SortingParams"] * tables["Recording"]
                        - tables["SpikeSorting"]
                    ).proj(),
                    number_params="count(*)",
                )
                .proj("number_params")
            )
            st.text("")

            if st.button("Check"):
                # can only spikesort your own data
                if session_dict["experimenter"] != username:
                    st.text("")

                    st.error("You can only perform computations on your own data")

                # need at least one parameter set
                elif len(query) == 0:
                    st.text("")

                    st.warning("There is nothing to be spikesorted.")
                    st.info(
                        """This could be because you haven't yet inserted spikesorting parameters or probeinsertions for these animals, or all available recordings and parameter sets have already been computed."""
                    )

                else:
                    df = query.fetch()

                    st.write("Sessions to be spikesorted:")

                    st.dataframe(df)

                    numjobs = df["number_params"].sum()

                    st.write(f"Total number of spikesorting jobs to run: {numjobs}")

            st.divider()

            # schedule computation section
            st.subheader("Schedule computation")

            # ask for user password for scheduling the job
            password = st.text_input(
                "Please enter your cluster password", type="password"
            )

            st.text("")

            # Spikesort
            if st.button("Spikesort"):
                # can only spikesort your own data
                if session_dict["experimenter"] != username:
                    st.error("You can only perform computations on your own data")

                # need at least one parameter set
                elif len(query) == 0:
                    st.error("There is no data to spikesort.")

                else:
                    numjobs = query.fetch()["number_params"].sum()

                    # correction since datajoint returns np.int64 which isn't serialisable
                    session_dict = {
                        key: (int(val) if isinstance(val, np.integer) else val)
                        for key, val in session_dict.items()
                    }

                    try:
                        # send job
                        schedule_spikesorting(session_dict, username, password, numjobs)

                        # success message
                        st.text("")
                        st.success("Spikesorting job sent to cluster!")
                        st.info("You will receive an email once your job is completed")

                    except Exception as e:
                        print(e)
                        st.error("Error submitting job to cluster")

            st.text("")

        # if there are any downlaods this session
        if "spikesort_jobs" in st.session_state:
            # button which shows spikesort statuses
            if st.button("Check spikesorting progress"):
                spikesorting_progress()
