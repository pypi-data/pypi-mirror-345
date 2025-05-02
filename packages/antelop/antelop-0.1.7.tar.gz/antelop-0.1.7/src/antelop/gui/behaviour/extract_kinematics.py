import streamlit as st
from antelop.utils.streamlit_utils import dropdown_query_table
from antelop.utils.external_utils import schedule_inference_dlc, inference_dlc_progress


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Behaviour")
        st.subheader("Extract kinematics from videos")

        st.divider()

        query = (tables["World"] & {"world_deleted": "False"}) & (
            tables["DLCModel"] & {"dlcmodel_deleted": "False"}
        ) - tables["Kinematics"]

        # Select the feature to add
        tablename, key = dropdown_query_table(
            tables, {"World": query}, username, headless=True
        )

        if key is None:
            st.warning(
                "You don't have any unprocessed videos or don't yet have a trained deeplabcut model."
            )

        else:
            st.divider()
            st.subheader("Check your data")

            query = (
                (
                    tables["World"]
                    & {"world_deleted": "False"}
                    & (tables["DLCModel"] & {"dlcmodel_deleted": "False"})
                    - tables["Kinematics"]
                    & key
                )
                .aggr(
                    (
                        tables["World"] * tables["DLCModel"] - tables["Kinematics"]
                        & {
                            "world_deleted": "False",
                            "dlcmodel_deleted": "False",
                            "kinematics_deleted": "False",
                        }
                    ).proj(),
                    number_models="count(*)",
                )
                .proj("number_models")
            )

            if len(query) == 0:
                st.warning("There is nothing to be processed.")
                return

            df = query.fetch(format="frame")
            st.dataframe(df, use_container_width=True)
            total = df["number_models"].sum()
            st.write(f"Total number of inference jobs to run: {total}")

            st.divider()

            # schedule computation section
            st.subheader("Schedule computation")

            # ask for user password for scheduling the job
            password = st.text_input(
                "Please enter your cluster password", type="password"
            )

            st.text("")
            if st.button("Schedule deeplabcut inference"):
                if key["experimenter"] != username:
                    st.error("You can only train models on your own data")

                else:
                    try:
                        num_videos = total

                        # send job
                        schedule_inference_dlc(key, num_videos, password)

                        # success message
                        st.success("Job sent to cluster!")
                        st.info("You will receive an email once your job is completed")

                    except Exception as e:
                        st.error("Error submitting job to cluster")
                        print(e)

            # if there are any downlaods this session
            if "inference_dlc_jobs" in st.session_state:
                # button which shows spikesort statuses
                if st.button("Check model inference progress"):
                    inference_dlc_progress()
