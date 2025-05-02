import streamlit as st
from antelop.utils.streamlit_utils import (
    dropdown_query_table,
    server_directory_browser,
)
from antelop.utils.antelop_utils import export_nwb
from antelop.utils.multithreading_utils import export_thread_pool
import pandas as pd


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Export Data")
        st.subheader("Select session")
        _, session = dropdown_query_table(
            tables, {"Session": tables["Session"]}, username, headless=True
        )

        if session is None:
            st.warning("No data available to export.")
        elif "session_id" in session.keys():
            st.subheader("Select download location")
            download_path = server_directory_browser("Select download location:")
            filename = st.text_input("Enter filename") + ".nwb"

            if st.button("Export"):
                export_pool = export_thread_pool()

                # submit job to thread pool
                future = export_pool.submit(
                    export_nwb,
                    session,
                    download_path / filename,
                    username=st.session_state.username,
                    password=st.session_state.password,
                )

                # append future to session state
                session_name = "_".join([str(i) for i in session.values()])
                st.session_state.export_futures.append((future, session_name))

                st.success("Export in progress.")

        if "export_futures" in st.session_state:
            if st.button("Check export progress"):
                st.write("Export statuses:")

                # initialise data
                display_futures = []

                # display job progress
                for future, query_name in st.session_state.export_futures:
                    # compute statuses
                    if future.done():
                        if future.exception():
                            print(future.exception())
                            status = "export error"
                        else:
                            status = "export success"
                    else:
                        status = "export in progress"

                    display_futures.append((query_name, status))

                # make dataframe to display
                df = pd.DataFrame(display_futures, columns=["Query", "Status"])

                # show dataframe
                st.dataframe(df, hide_index=True)
