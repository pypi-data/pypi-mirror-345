import streamlit as st
from antelop.utils.streamlit_utils import dropdown_query_table
from antelop.utils.datajoint_utils import safe_delete, query_to_str, show_deletes
from antelop.utils.external_utils import (
    open_phy,
    schedule_import_phy,
    import_phy_progress,
)
from antelop.utils.multithreading_utils import delete_thread_pool
from antelop.utils.os_utils import get_config
import pandas as pd
import numpy as np
import json


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Electrophysiology")
        st.subheader("Manual Curation")

        st.divider()

        st.subheader("Select the data you want to manually curate")

        # get user to interactively select session
        _, spikesorting_dict = dropdown_query_table(
            tables,
            {"SpikeSorting": tables["SpikeSorting"]},
            username,
            headless=True,
            in_compute="False",
        )

        if spikesorting_dict == None:
            st.error("""You don't have any spikesorted data to manually curate.""")
            st.warning("""Please make sure you have spikesorted some data first.""")

            st.text("")

            # if there are any downlaods this session
            if "import_phy_jobs" in st.session_state:
                # button which shows spikesort statuses
                if st.button("Check upload progress"):
                    import_phy_progress()

        elif (
            "sortingparams_id" in spikesorting_dict.keys()
            and spikesorting_dict["experimenter"] == username
        ):
            st.divider()

            # schedule computation section
            st.subheader("Manual curation")

            config_dict = get_config()
            if config_dict["deployment"]["deployment"] == "apptainer":
                # ask for user password for scheduling the job
                password = st.text_input(
                    "Please enter your cluster password", type="password"
                )

            elif config_dict["deployment"]["deployment"] == "local":
                password = None

            st.text("")

            if st.button("Open phy"):
                st.text("")

                hashkey = (tables["SpikeSorting"] & spikesorting_dict).fetch1("phy")

                try:
                    open_phy(hashkey, username, password)

                except ImportError:
                    st.error("Phy not installed.")
                    st.warning(
                        "Please install phy by running: `pip install antelop[gui,phy]`"
                    )

                except Exception as e:
                    st.error("Error opening phy")
                    print(e)

                else:
                    st.warning(
                        """Please remember to save your manual curation results in phy when you're done!"""
                    )

            st.text("")

            st.info("This button will open phy in another window.")

            # upload data back to antelop

            st.divider()

            st.subheader("Upload manual curation results")

            # ask for user password for scheduling the job
            password = st.text_input(
                "Please enter your cluster password", type="password", key="2"
            )

            st.text("")

            if st.button("Upload results"):
                query = tables["SpikeSorting"] & spikesorting_dict
                in_compute = query.fetch1("spikesorting_in_compute")

                if in_compute == "True":
                    st.error(
                        """This entry is currently in a computation. You must wait until this job finishes to upload results."""
                    )

                else:
                    try:
                        # correction since datajoint returns np.int64 which isn't serialisable
                        if "labelledframes_in_compute" in spikesorting_dict.keys():
                            del spikesorting_dict["labelledframes_in_compute"]
                        del spikesorting_dict["spikesorting_in_compute"]
                        spikesorting_dict = {
                            key: (int(val) if isinstance(val, np.integer) else val)
                            for key, val in spikesorting_dict.items()
                        }
                        print(spikesorting_dict)

                        # send job
                        schedule_import_phy(
                            spikesorting_dict, username, password, numjobs=1
                        )

                        # success message
                        st.success("Upload job sent to cluster!")
                        st.info("You will receive an email once your job is completed")

                    except Exception as e:
                        print(e)

                        st.error("Error submitting job to cluster")

            st.text("")

            st.info(
                """This will schedule another job on the cluster that extracts the data from phy and reuploads it to the database.
            Note this will overwrite the existing electrophysiology results in the database.
            Please make sure you have saved your phy results before uploading!"""
            )

            st.text("")

            # if there are any downlaods this session
            if "import_phy_jobs" in st.session_state:
                # button which shows spikesort statuses
                if st.button("Check upload progress"):
                    import_phy_progress()

            # delete parameters section

            st.divider()

            st.subheader("Delete parameters")

            st.text("")

            if st.button("Check deletes"):
                # form delete query
                sort_dict = {
                    key: val
                    for key, val in spikesorting_dict.items()
                    if key
                    in [
                        "experimenter",
                        "experiment_id",
                        "animal_id",
                        "sortingparams_id",
                    ]
                }
                sort_dict["sortingparams_deleted"] = "False"
                query = tables["SortingParams"] & sort_dict
                # show cascaded deletes
                descendant_dict = show_deletes(tables, query)
                st.write("Entries that will get deleted:")
                st.dataframe(pd.DataFrame(data=descendant_dict).set_index("Table"))

            st.text("")

            st.info(
                "If your sorting parameters are not satisfactory, you can delete them here."
            )
            st.warning(
                "Note this will delete the sorting results for all sessions belonging to this parameter set."
            )

            st.text("")

            # input password and compare with hash on disk
            status = True  # change
            # status = bcrypt.checkpw(st.text_input(label='Please enter your antelop password to confirm deletion:',type='password').encode(),config['credentials']['usernames'][username]['password'].encode())

            st.text("")

            if st.button("Delete parameters"):
                # delete only if password correct
                if status:
                    # form delete query
                    sort_dict = {
                        key: int(val)
                        for key, val in spikesorting_dict.items()
                        if key in ["experiment_id", "animal_id", "sortingparams_id"]
                    }
                    sort_dict["experimenter"] = spikesorting_dict["experimenter"]
                    sort_dict["sortingparams_deleted"] = "False"
                    querystring = f"SortingParams & {json.dumps(sort_dict)}"
                    query = tables["SortingParams"] & sort_dict

                    # calculate number deletes
                    descendant_dict = show_deletes(tables, query)
                    num_delete = sum(descendant_dict["Number entries to be deleted"])

                    # if number deletes greater than 1000, use multithreading
                    if num_delete > 1000:
                        # retrieve thread pool
                        del_thread_pool = delete_thread_pool()

                        # submit job to thread pool
                        future_delete = del_thread_pool.submit(
                            safe_delete,
                            querystring,
                            username=st.session_state.username,
                            password=st.session_state.password,
                        )

                        # form query name
                        query_name = query_to_str(query)

                        # append future to session state
                        st.session_state.delete_futures.append(
                            (future_delete, query_name)
                        )

                        st.success("Deletion in progress.")

                    # otherwise delete in main thread
                    else:
                        safe_delete(querystring)

                        st.success("Deletion complete.")

                # incorrect password
                else:
                    st.error("Password incorrect.")
