import streamlit as st
import pandas as pd
from antelop.utils.streamlit_utils import dropdown_query_table
from antelop.utils.datajoint_utils import (
    form_query,
    query_without_external,
    query_to_str,
    release_computation,
    names_to_ids,
)
from antelop.utils.multithreading_utils import release_thread_pool


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    tables = tables["Experimenter"]._admin().tables

    with col2:
        st.title("Database Administration")
        st.subheader("Release entry stuck in computation")

        st.divider()

        # just check spikesorting table
        subtables = {key: val for key, val in tables.items() if key == "SpikeSorting"}

        # get input restriction
        tablename, restriction = dropdown_query_table(
            tables, subtables, username=None, in_compute="True", headless=True
        )

        if not tablename:
            st.warning("There are no entries currently in computation.")

        else:
            # form datajoint querystring
            restriction_with_ids = names_to_ids([restriction], tables)
            querystring = f"{tablename} & {str(restriction_with_ids[0])}"
            print(querystring)

            # form query
            query = form_query(querystring, tables)

            st.text("")

            if st.button("Search"):
                st.text("")

                if querystring:
                    st.markdown("##### Data in computation:")

                    # query results to display
                    df, number = query_without_external(query)

                    # show table
                    if number == 0:
                        st.warning("No entries to show!")
                    else:
                        st.dataframe(df, hide_index=True)
                        st.text("Number of items: {}".format(number))
                else:
                    st.error("You must enter a query first!")

            st.text("")

            # warning message
            st.info(
                """
            Note that the behaviour of this function depends on whether your data is stuck in computation during spikesorting, or while uploading the results of your manual curation.\n
            In the former case, this amounts to a true delete, as there is no data that needs to be saved, while in the latter case, it simply sets the 'in_compute' attribute to False, so that the job can be rerun."""
            )
            st.text("")
            st.warning(
                """
            Before releasing an entry from computation, please check the logs to see why the computation failed, and make the appropriate modifications, to avoid wasting computational resources.\n
            Please also try to ensure you don't release data that is actually currently in computation, as opposed to having failed computation, as this will cause your job to fail, wasting resources.\n
            Common causes of jobs failing are corrupted data, misentered parameters, or the job timing out."""
            )

            st.text("")

            status = (
                st.text_input(
                    label="Please enter your password to confirm computation release:",
                    type="password",
                )
                == st.session_state.password
            )

            st.text("")

            # release from computation
            if st.button("Release computation"):
                st.text("")

                if querystring:
                    st.text("")

                    # delete only if password correct
                    if status:
                        # check how many entries to release
                        num_release = len(query)

                        # if number releases over 1000, run in separate thread
                        if num_release > 1000:
                            # retrieve thread pool
                            rel_thread_pool = release_thread_pool()

                            # make name for query
                            query_name = query_to_str(form_query(querystring, tables))

                            # submit job to thread pool
                            future = rel_thread_pool.submit(
                                release_computation,
                                tablename,
                                restriction,
                                username=st.session_state.username,
                                password=st.session_state.password,
                            )

                            # append future to session state
                            st.session_state.release_futures.append(
                                (future, query_name)
                            )

                            st.success("Release computation in progress!")

                        # otherwise run in main thread
                        else:
                            # release data
                            release_computation(
                                tablename,
                                restriction,
                                conn=tables["Experimenter"].connection,
                            )

                            st.success("Data released from computation!")

                    # incorrect password
                    else:
                        st.error("Password incorrect.")

                else:
                    st.error("You must enter a query first!")

            st.text("")

            # add a button which shows download statuses
            # uses all downlaods in current session stored in session state
            # if there are any downloads this session
            if "release_futures" in st.session_state:
                if st.button("Check release computation progress"):
                    st.write("Release computation statuses:")

                    # initialise data
                    display_futures = []

                    # display job progress
                    for future, query_name in st.session_state.release_futures:
                        # compute statuses
                        if future.done():
                            if future.exception():
                                print(future.exception())
                                status = "release computation error"
                            else:
                                status = "release computation success"
                        else:
                            status = "release computation in progress"

                        display_futures.append((query_name, status))

                    # make dataframe to display
                    df = pd.DataFrame(display_futures, columns=["Query", "Status"])

                    # show dataframe
                    st.dataframe(df, hide_index=True)

                # if there are no downloads in this session
                else:
                    st.write("No downloads underway.")
