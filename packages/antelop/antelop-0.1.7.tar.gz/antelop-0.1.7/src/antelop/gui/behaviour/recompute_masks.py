import streamlit as st
from antelop.utils.streamlit_utils import dropdown_query_table
from antelop.utils.antelop_utils import (
    select_masks,
    recompute_masks,
    insert_masks,
    delete_masks,
)
from antelop.utils.analysis_utils import get_docstring
from antelop.utils.multithreading_utils import mask_thread_pool
import streamlit_antd_components as sac
import pandas as pd


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Behaviour")
        st.subheader("Compute Masks")

        st.divider()

        st.subheader("Select the sessions you want to recompute")

        tablename, world = dropdown_query_table(
            tables, {"Experimenter": tables["Experimenter"]}, username, headless=True
        )

        if "experimenter" in world.keys():
            # if no features in database raise warning
            if tablename == None:
                st.warning(
                    """You can't recompute any trials because you don't have the necessary upstream entries."""
                )
            elif len(tables["BehaviourRig"] & world) == 0:
                st.warning(
                    """You can't recompute any trials because you don't have the necessary upstream entries."""
                )
            elif username != world["experimenter"]:
                st.error("You can only edit your own data")
            else:
                st.text("")
                st.divider()

                sac.buttons(
                    [
                        sac.ButtonsItem(label="Change Mask Function"),
                        sac.ButtonsItem(label="Recompute Masks"),
                    ],
                    key="mask",
                    gap="md",
                    use_container_width=True,
                )

                if st.session_state["mask"] == "Change Mask Function":
                    # pull behaviour rig
                    rig_dicts = (
                        (tables["BehaviourRig"] & world)
                        .proj("behaviourrig_name")
                        .fetch(as_dict=True)
                    )
                    display_dict = {i["behaviourrig_name"]: i for i in rig_dicts}
                    rig = display_dict[
                        st.selectbox(
                            "Select the behaviour rig", list(display_dict.keys())
                        )
                    ]

                    # pull mask function
                    mask = (tables["MaskFunction"] & rig).fetch(format="frame")
                    mask = mask.reset_index()
                    del mask["experimenter"]
                    del mask["behaviourrig_id"]
                    if not mask.empty:
                        mask["mask_function"] = mask.apply(
                            lambda row: get_docstring(
                                row["mask_function"], row["maskfunction_name"]
                            ),
                            axis=1,
                        )
                    id = (
                        max((tables["MaskFunction"] & rig).fetch("mask_id"), default=0)
                        + 1
                    )

                    st.text("")
                    st.markdown("### Edit mask functions")
                    st.markdown("#### Current mask functions")
                    current_masks = st.data_editor(
                        mask,
                        hide_index=True,
                        use_container_width=True,
                        disabled=(
                            "mask_id",
                            "mask_name",
                            "mask_function",
                            "mask_description",
                        ),
                        column_config={
                            "mask_function": st.column_config.Column(width="small")
                        },
                    )

                    st.warning(
                        "Please note that the following performs a permanent delete on your masking functions"
                    )
                    st.text("")
                    if st.button("Delete selected masks"):
                        key = {
                            "experimenter": world["experimenter"],
                            "behaviourrig_id": rig["behaviourrig_id"],
                        }
                        if key["experimenter"] != username:
                            st.error("You can only delete your own masks")
                        else:
                            delete_masks(key, current_masks, tables)
                            st.success("Masks deleted")
                            st.rerun()

                    st.markdown("#### New mask functions")
                    edited_masks = select_masks(tables)
                    st.text("")
                    if st.button("Push new masks to database"):
                        if edited_masks:
                            masks = insert_masks(rig, edited_masks, id, tables)
                            tables["MaskFunction"].insert(masks)
                            st.success("Changes pushed to database")
                        else:
                            st.warning(
                                "No masks selected - nothing to push to database!"
                            )

                elif st.session_state["mask"] == "Recompute Masks":
                    st.text("")

                    # query sessions
                    table, world = dropdown_query_table(
                        tables,
                        {
                            "World": (tables["World"] - tables["Mask"])
                            & tables["MaskFunction"]
                        },
                        username,
                        headless=True,
                    )

                    if world:
                        # show how many sessions need recomputing
                        number_sessions = len(
                            (tables["World"] - tables["Mask"])
                            & tables["MaskFunction"]
                            & world
                        )
                        st.text("")
                        st.write(f"Computing masks for {number_sessions} sessions")
                        st.text("")

                        if st.button("Recompute masks"):
                            # retrieve thread pool
                            thread_pool = mask_thread_pool()

                            # submit job to thread pool
                            future = thread_pool.submit(
                                recompute_masks,
                                world,
                                username=st.session_state.username,
                                password=st.session_state.password,
                            )

                            # append future to session state
                            st.session_state.mask_futures.append((future, world))
                            st.text("")
                            st.success("Computation in progress!")

                        st.info(
                            "Note that computing many masks can take a while. This will occur in a separate thread so you can still use Antelop while the computation is occurring, and can use the button below to check your computation status."
                        )

                        st.text("")

                        if "mask_futures" in st.session_state:
                            if st.button("Check computation progress"):
                                st.write("Computation statuses:")

                                # initialise data
                                display_futures = []

                                # compute job statuses
                                for future, world in st.session_state.mask_futures:
                                    # compute statuses
                                    if future.done():
                                        if future.exception():
                                            status = "computation error"
                                        else:
                                            status = "computation success"
                                    else:
                                        status = "computation in progress"

                                    # primary keys for display
                                    keys = {
                                        key: val
                                        for key, val in world.items()
                                        if key in tables[tablename].primary_key
                                    }
                                    display = "-".join([str(i) for i in keys.values()])

                                    display_futures.append((display, status))

                                # make dataframe to display
                                df = pd.DataFrame(
                                    display_futures, columns=["Primary Key", "Status"]
                                )

                                # show dataframe
                                st.dataframe(df, hide_index=True)

                    else:
                        st.info("No masks to recompute")
