import streamlit as st
from antelop.utils.streamlit_utils import (
    dropdown_query_table,
    server_directory_browser,
)
from antelop.utils.datajoint_utils import upload
from antelop.utils.multithreading_utils import feature_thread_pool
import pandas as pd


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Behaviour")
        st.subheader("Add features for the behaviour rig")

        st.divider()

        # Select the feature to add
        tablename, key = dropdown_query_table(
            tables, {"Feature": tables["Feature"]}, username, headless=True
        )

        # if no features in database raise warning
        if tablename == None:
            st.warning(
                "You need to add a behaviour rig to the database before adding features"
            )

        else:
            # Query if there's already a feature attached
            query = tables["Feature"] & key & {"feature_data": None}

            if len(query) == 0:
                st.text("")
                st.warning(
                    "This feature already has data attached. Uploading data again will overwrite the existing data, so make sure you want to update the feature."
                )

            # Get user to select the feature data
            if "feature_id" in key and key["experimenter"] == username:
                st.divider()

                # get feature data
                feature_data = server_directory_browser("Select feature data", None)

                # add to key
                key["feature_data"] = feature_data

                if feature_data:
                    st.divider()

                    # make insert button
                    if st.button("Insert"):
                        # retrieve thread pool
                        up_thread_pool = feature_thread_pool()

                        # submit job to thread pool
                        future = up_thread_pool.submit(
                            upload,
                            tablename,
                            key,
                            "update",
                            username=st.session_state.username,
                            password=st.session_state.password,
                        )

                        # append future to session state
                        st.session_state.feature_futures.append(
                            (future, tablename, key)
                        )
                        st.text("")
                        st.success("Upload in progress!")

            elif key["experimenter"] != username:
                st.error("You can only insert your own data!")

            # print warning
            st.text("")
            st.info(
                "Note that uploading large features can take a while. This will occur in a separate thread so you can still use Antelop while the upload is occurring, and can use the button below to check your upload status."
            )

            st.text("")

            if "feature_futures" in st.session_state:
                if st.button("Check insert progress"):
                    # if there are any downloads this session
                    if "feature_futures" in st.session_state:
                        st.write("Upload statuses:")

                        # initialise data
                        display_futures = []

                        # compute job statuses
                        for (
                            future,
                            tablename,
                            insert_dict,
                        ) in st.session_state.feature_futures:
                            # compute statuses
                            if future.done():
                                if future.exception():
                                    status = "upload error"
                                else:
                                    status = "upload success"
                            else:
                                status = "upload in progress"

                            # primary keys for display
                            keys = {
                                key: val
                                for key, val in insert_dict.items()
                                if key in tables[tablename].primary_key
                            }
                            display = "-".join([str(i) for i in keys.values()])

                            display_futures.append((tablename, display, status))

                        # make dataframe to display
                        df = pd.DataFrame(
                            display_futures, columns=["Table", "Primary Key", "Status"]
                        )

                        # show dataframe
                        st.dataframe(df, hide_index=True)

                    # if there are no downloads in this session
                    else:
                        st.write("No uploads underway.")
