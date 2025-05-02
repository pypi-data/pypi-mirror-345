import streamlit as st
from datajoint.user_tables import TableMeta
from antelop.utils.datajoint_utils import (
    query_without_external,
    download_data,
    safe_delete,
    form_query,
    show_deletes,
    query_to_str,
    delete_status,
    ids_to_names,
    names_to_ids,
)
from antelop.utils.streamlit_utils import (
    dropdown_query_table,
    server_directory_browser,
    children_buttons,
    go_back,
)
from antelop.utils.multithreading_utils import delete_thread_pool, download_thread_pool
import pandas as pd
import streamlit_antd_components as sac


def show(username, tables):

    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Search Database")
        st.subheader("Search across all schemas")

        st.divider()

        def top_chg():
            if hasattr(st.session_state, "search_fct"):
                del st.session_state.search_fct

        sac.buttons(
            [
                sac.ButtonsItem(label="Sequential Filter", icon="sort-down"),
                sac.ButtonsItem(label="Manual Query", icon="pen"),
            ],
            key="search_mode",
            gap="md",
            use_container_width=True,
            on_change=top_chg,
        )

        st.text("")

        if st.session_state["search_mode"] == "Sequential Filter":

            def reset_tablename():
                if hasattr(st.session_state, "tablename"):
                    del st.session_state.tablename

            if not hasattr(st.session_state, "schema"):
                if hasattr(st.session_state, "tablename"):
                    del st.session_state.tablename

            # get schema
            if hasattr(st.session_state, "go_back"):
                if st.session_state.go_back:
                    st.session_state.schema = st.session_state.tmp_schema
                    st.session_state.go_back = False
            sac.buttons(
                [
                    sac.ButtonsItem(label="Metadata", icon="table"),
                    sac.ButtonsItem(label="Electrophysiology", icon="lightning"),
                    sac.ButtonsItem(label="Behaviour", icon="joystick"),
                ],
                key="schema",
                use_container_width=True,
                on_change=reset_tablename,
            )

            # make table mapping
            table_mapping = {
                "Metadata": ["Experimenter", "Experiment", "Animal", "Session"],
                "Electrophysiology": [
                    "ProbeGeometry",
                    "ProbeInsertion",
                    "SortingParams",
                    "Recording",
                    "SpikeSorting",
                    "Probe",
                    "Channel",
                    "LFP",
                    "Unit",
                    "SpikeTrain",
                    "Waveform",
                ],
                "Behaviour": [
                    "BehaviourRig",
                    "LabelledFrames",
                    "DLCModel",
                    "MaskFunction",
                    "Feature",
                    "World",
                    "Video",
                    "Self",
                    "Object",
                    "DigitalEvents",
                    "AnalogEvents",
                    "IntervalEvents",
                    "Kinematics",
                    "Mask",
                ],
            }

            # get input restriction
            subtables = {
                key: val
                for key, val in tables.items()
                if key in table_mapping[st.session_state["schema"]]
            }
            tablename, restriction = dropdown_query_table(
                tables, subtables, username, search_page=True
            )

            if tablename == None:
                st.text("")
                st.error("No tables to search in this schema")
                st.stop()

            else:
                # form datajoint querystring
                querystring = f"{tablename} & {str(restriction)}"

                # form query
                query = form_query(querystring, tables)

        elif st.session_state["search_mode"] == "Manual Query":
            # get manual query
            querystring = st.text_input("Enter your manual query")

            # form query
            if querystring:
                query = form_query(querystring, tables)

        st.text("")

        if st.session_state.search_mode == "Sequential Filter":
            index = ["Data", "Navigation"].index(
                st.session_state.get("search_fct", "Data")
            )
            sac.buttons(
                [
                    sac.ButtonsItem(label="Data"),
                    sac.ButtonsItem(label="Navigation"),
                ],
                key="search_fct",
                use_container_width=True,
                index=index,
            )
        elif st.session_state.search_mode == "Manual Query":
            sac.buttons(
                [
                    sac.ButtonsItem(label="Data"),
                ],
                key="search_fct",
                use_container_width=True,
            )

        st.text("")

        if querystring:
            if st.session_state["search_fct"] == "Data":
                # query results to display
                df, number = query_without_external(
                    query, st.session_state["search_mode"]
                )
                del_col = [False] * len(df)
                df.insert(0, "delete", del_col)

                # show table
                if number == 0:
                    st.warning("No entries to show!")
                else:
                    disabled = df.columns.to_list()
                    disabled.remove("delete")
                    config = {"delete": st.column_config.CheckboxColumn("delete")}
                    delete_df = st.data_editor(
                        df,
                        column_config=config,
                        hide_index=True,
                        use_container_width=True,
                        disabled=disabled,
                    )
                    st.text("Number of items: {}".format(number))

            elif st.session_state["search_fct"] == "Navigation":
                children_buttons(query, tables)
                # query results to display
                delete_df, number = query_without_external(
                    query, st.session_state["search_mode"]
                )
                del_col = [False] * len(delete_df)
                delete_df.insert(0, "delete", del_col)
                if st.button("Back"):
                    go_back()

        st.divider()

        # download and delete section
        sac.buttons(
            [
                sac.ButtonsItem(label="Download", icon="cloud-download"),
                sac.ButtonsItem(label="Delete", icon="trash"),
            ],
            key="mode2",
            gap="md",
            use_container_width=True,
        )

        # download section
        if st.session_state["mode2"] == "Download":
            st.header("Download results")

            # leave blank if no query yet
            if not querystring:
                st.warning("No query entered yet")

                return

            # get user to input download path
            download_path = server_directory_browser("Select download location:")
            filename = st.text_input("Enter filename") + ".npy"
            download_path = download_path / filename

            st.text("")

            # download data
            if st.button("Download"):
                # retrieve thread pool
                down_thread_pool = download_thread_pool()

                # make name for query
                query = (
                    query & True
                )  # protection seems to help download more complex queries
                query_name = query_to_str(query)

                # if recording or video, download in separate thread
                if query.table_name in ["recording", "_video"]:
                    # submit job to thread pool
                    future = down_thread_pool.submit(
                        download_data,
                        querystring,
                        download_path,
                        st.session_state["search_mode"],
                        username=st.session_state.username,
                        password=st.session_state.password,
                    )

                    # append future to session state
                    st.session_state.download_futures.append((future, query_name))

                    st.success("Download in progress.")

                else:
                    # download in main thread
                    download_data(
                        querystring,
                        download_path,
                        st.session_state["search_mode"],
                        conn=tables["Experimenter"].connection,
                    )

                    st.success("Download complete.")

            st.text("")

            # notice
            st.info(
                "Note that downloading large session recordings can take a while. This will occur in a separate thread so you can still use Antelop while the download is occurring, and can use the button below to check your download status."
            )
            st.warning(
                "If you try to download the same data to the same location again before the first download is finished you will potentially corrupt your downloaded data."
            )

            st.text("")

            # add a button which shows download statuses
            # uses all downloads in current session stored in session state
            if "download_futures" in st.session_state:
                if st.button("Check download progress"):
                    # if there are any downlaods this session
                    if "download_futures" in st.session_state:
                        st.write("Download statuses:")

                        # initialise data
                        display_futures = []

                        # display job progress
                        for future, query_name in st.session_state.download_futures:
                            # compute statuses
                            if future.done():
                                if future.exception():
                                    status = "download error"
                                else:
                                    status = "download success"
                            else:
                                status = "download in progress"

                            display_futures.append((query_name, status))

                        # make dataframe to display
                        df = pd.DataFrame(display_futures, columns=["Query", "Status"])

                        # show dataframe
                        st.dataframe(df, hide_index=True)

                    # if there are no downloads in this session
                    else:
                        st.write("No downloads underway.")

        # delete section - only for sequential filter
        if st.session_state["mode2"] == "Delete":
            st.header("Delete data")

            # leave blank if no query yet
            if not querystring:
                st.warning("No query entered yet")

            else:
                query = form_query(querystring, tables)

                # print a warning if manual query and add additional restriction to query
                if st.session_state["search_mode"] == "Manual Query":
                    st.warning(
                        "Note for manual queries, we automatically add the additional restriction that you can only delete your own data. This will be reflected when you check deletes, so the number of entries here will potentially differ from your full search."
                    )

                    query = query & {"experimenter": username}

                # for sequential filters, check experimenter is the user
                admin = (tables["Experimenter"] & {"experimenter": username}).fetch1("admin")
                if admin == "False" and st.session_state["search_mode"] == "Sequential Filter" and (
                    "experimenter" not in restriction.keys()
                    or not restriction["experimenter"] == username
                ):
                    st.error("""You don't have permission to delete this data""")

                # don't want to delete from experimenter table
                elif isinstance(query, tables["Experimenter"].__class__):
                    st.error("You can't delete from the experimenter table")

                # some manual queries, such as joins, are too complex to delete
                # simple queries are our user defined tables or TableMeta type
                elif not isinstance(
                    query, tuple([t.__class__ for t in tables.values()] + [TableMeta])
                ):
                    st.error("This manual query is too complex to delete from")
                    st.warning(
                        "Typically, you can only delete restricted entries from a single table"
                    )

                else:
                    # check delete mode
                    full_names = {
                        val.full_table_name: key for key, val in tables.items()
                    }
                    tablename = full_names[query.full_table_name]
                    delete_mode = delete_status(tablename, tables, query)

                    if delete_mode == "none":
                        st.error("This table cannot be deleted from")

                    else:
                        st.text("")

                        st.info(
                            "Note that deletes cascade to avoid orphaned database entries. Please use the button below to check which tables will get deleted from."
                        )

                        st.text("")

                        cols = query.proj().heading.names
                        cols = ids_to_names(cols)
                        to_delete = delete_df[delete_df["delete"] == True][
                            cols
                        ].to_dict(orient="records")

                        if delete_mode == "custom-behave":
                            # change query to world and query
                            querystring = "World & " + querystring.split("&")[1]
                            query = form_query(querystring, tables)
                            delete_mode = "perm"

                        if delete_mode == "perm":
                            st.error(
                                "This delete will be permanent and cannot be undone."
                            )
                            st.text("")

                        to_delete_ids = names_to_ids(to_delete, tables)
                        delete_query = query & to_delete_ids
                        for key, val in tables.items():
                            if query.table_name == val.table_name:
                                delete_table_name = key
                                break
                        delete_querystring = f"{delete_table_name} & {str(to_delete_ids)}"


                        if st.button("Check deletes"):
                            # show cascaded deletes
                            descendant_dict = show_deletes(tables, delete_query)
                            st.write("Entries that will get deleted:")
                            st.dataframe(
                                pd.DataFrame(data=descendant_dict).set_index("Table")
                            )

                        status = (
                            st.text_input(
                                label="Please enter your password to confirm computation release:",
                                type="password",
                            )
                            == st.session_state.password
                        )

                        st.text("")

                        # delete button
                        if st.button("Delete"):
                            # delete only if password correct
                            if status:
                                if delete_mode == "temp":
                                    # get cascaded deletes
                                    descendant_dict = show_deletes(tables, delete_query)

                                    # count total number of entries to delete
                                    total_deletes = sum(
                                        descendant_dict["Number entries to be deleted"]
                                    )

                                    # use main thread if less than 1000 entries
                                    if total_deletes < 1000:
                                        # delete data
                                        safe_delete(
                                            delete_querystring,
                                            conn=tables["Experimenter"].connection,
                                        )

                                        st.text("")

                                        st.success("Delete complete.")

                                    # otherwise use thread pool
                                    else:
                                        # retrieve thread pool
                                        del_thread_pool = delete_thread_pool()

                                        # submit job to thread pool
                                        future_delete = del_thread_pool.submit(
                                            safe_delete,
                                            delete_querystring,
                                            username=st.session_state.username,
                                            password=st.session_state.password,
                                        )

                                        # form query name
                                        query_name = query_to_str(delete_query)

                                        # append future to session state
                                        st.session_state.delete_futures.append(
                                            (future_delete, query_name)
                                        )

                                        st.success("Deletion in progress.")

                                elif delete_mode == "perm":
                                    # delete data
                                    delete_query.delete(safemode=False, force=True)

                                    st.success("Data deleted.")

                            # incorrect password
                            else:
                                st.error("Password incorrect.")

                    st.text("")

                    # notice
                    st.info(
                        "Note that temporary deletes can take a while if there are a very large number of rows to update. This will occur in a separate thread so you can still use Antelop while the delete is occurring, and can use the button below to check your delete status."
                    )

                    st.text("")

                    # add a button which shows download statuses
                    # uses all downlaods in current session stored in session state
                    if "delete_futures" in st.session_state:
                        if st.button("Check delete progress"):
                            # if there are any downlaods this session
                            if (
                                "delete_futures" in st.session_state
                                and len(st.session_state.delete_futures) > 0
                            ):
                                st.write("Delete progress:")

                                # initialise data
                                display_futures = []

                                # display job progress
                                for (
                                    future,
                                    queryname,
                                ) in st.session_state.delete_futures:
                                    # compute statuses
                                    if future.done():
                                        if future.exception():
                                            status = "delete error"
                                        else:
                                            status = "delete success"
                                    else:
                                        status = "delete in progress"

                                    display_futures.append((queryname, status))

                                # make dataframe to display
                                df = pd.DataFrame(
                                    display_futures, columns=["Query", "Status"]
                                )

                                # show dataframe
                                st.dataframe(df, hide_index=True)

                            # if there are no downloads in this session
                            else:
                                st.write("No deletes underway.")
