import streamlit as st
from antelop.utils.streamlit_utils import dropdown_query_table
from antelop.utils.datajoint_utils import (
    query_without_external,
    form_query,
    query_to_str,
    show_restores,
    restore,
)
from antelop.utils.multithreading_utils import restore_thread_pool
import pandas as pd


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    tables = tables["Experimenter"]._admin().tables

    with col2:
        st.title("Database Administration")
        st.subheader("Restore data")

        st.divider()

        # don't want to check experimenter table
        subtables = {key: val for key, val in tables.items() if key != "Experimenter"}

        # get input restriction
        tablename, restriction = dropdown_query_table(
            tables, subtables, username=None, delete_mode="True", restore=True
        )

        if not tablename:
            st.warning(
                "There is no temporarily deleted data currently in the database."
            )

        else:
            # form datajoint querystring
            querystring = f"{tablename} & {str(restriction)}"

            # form query
            query = form_query(querystring, tables)

            # make sure only searching deleted data
            query = query & {f"""{query.table_name.replace("_", "")}_deleted""": "True"}

            st.text("")

            if st.button("Search"):
                st.text("")

                if querystring:
                    st.markdown("##### Deleted data:")

                    # query results to display
                    df, number = query_without_external(query)

                    # show table
                    if number == 0:
                        st.warning("No entries to show!")
                    else:
                        st.dataframe(df, hide_index=True, use_container_width=True)
                        st.text("Number of items: {}".format(number))
                else:
                    st.error("You must enter a query first!")

            st.text("")

            st.info(
                """Note that restores cascade to make it a full restore from the original delete. Please use the button below to check which tables will get data restored. If you want to restore only a subset of the data, the recommended workflow is to reverse the original delete, then re-delete the subset of the data you still don't want."""
            )

            st.text("")

            if st.button("Check restores"):
                # show cascaded deletes
                descendant_dict = show_restores(tables, query)
                st.write("Entries that will get restored:")
                st.dataframe(pd.DataFrame(data=descendant_dict).set_index("Table"))

            status = (
                st.text_input(
                    label="Please enter your password to confirm computation release:",
                    type="password",
                )
                == st.session_state.password
            )

            st.text("")

            # download data
            if st.button("Restore"):
                # calculate number of rows to restore
                descendant_dict = show_restores(tables, query)
                num_restores = sum(descendant_dict["Number entries to be restored"])

                # if number restores over 1000, run in separate thread
                if num_restores > 1000:
                    # retrieve thread pool
                    rest_thread_pool = restore_thread_pool()

                    # make name for query
                    query_name = query_to_str(form_query(querystring, tables))

                    # submit job to thread pool
                    future = rest_thread_pool.submit(
                        restore,
                        querystring,
                        username=st.session_state.username,
                        password=st.session_state.password,
                    )

                    # append future to session state
                    st.session_state.restore_futures.append((future, query_name))

                    st.text("")

                    st.success("Restore in progress!")

                # otherwise run in main thread
                else:
                    # restore data
                    print(querystring)
                    restore(querystring, conn=tables["Experimenter"].connection)

                    # show success message
                    st.text("")
                    st.success("Data restored!")

            st.text("")

            # notice
            st.info(
                "Note that restoring data can take a while if there are a large number of rows to update. This will occur in a separate thread so you can still use Antelop while the restore is occurring, and can use the button below to check your download status."
            )

            st.text("")

            # add a button which shows download statuses
            # uses all downlaods in current session stored in session state
            if "restore_futures" in st.session_state:
                if st.button("Check restore progress"):
                    st.write("Restore statuses:")

                    # initialise data
                    display_futures = []

                    # display job progress
                    for future, query_name in st.session_state.restore_futures:
                        # compute statuses
                        if future.done():
                            if future.exception():
                                status = "restore error"
                            else:
                                status = "restore success"
                        else:
                            status = "restore in progress"

                        display_futures.append((query_name, status))

                    # make dataframe to display
                    df = pd.DataFrame(display_futures, columns=["Query", "Status"])

                    # show dataframe
                    st.dataframe(df, hide_index=True)
