import streamlit as st
from antelop.utils.streamlit_utils import dropdown_query_table
from antelop.utils.visualisation_utils import (
    plot_session,
    choose_animals,
    choose_objects,
)


def show(username, tables):
    st.title("Visualisation")
    st.subheader("Interactively visualise a session spiketrains and environment events")
    st.divider()

    # check if there is any data in the database
    data = (len(tables["Object"] & True) > 0) or (
        len(tables["SpikeSorting"] & True) > 0
    )

    if not data:
        st.error("""There's no data in the database to visualise""")
        st.warning(
            "Please make sure you have either some spikesorted data or some behavioural data to visualise"
        )

    else:
        col1, col2 = st.columns([0.4, 0.6], gap="large")

        with col1:
            st.markdown("**Select session**")

            # only select session
            session_tables = {"Session": tables["Session"]}

            # get user to interactively insert table attributes
            tablename, session_dict = dropdown_query_table(
                tables, session_tables, username, headless=True
            )

            if "session_id" in session_dict.keys():
                # get user to select the animals and sorting parameters they want to visualise
                selected_animals = choose_animals(tables, session_dict)

                # get user to select the behavioural objects they want to visualise
                selected_objects = choose_objects(tables, session_dict)

                # pull spike trains
                if session_dict and (
                    selected_animals
                    or selected_objects[0]
                    or selected_objects[1]
                    or selected_objects[2]
                    or selected_objects[3]
                    or selected_objects[4]
                ):
                    st.divider()
                    st.markdown("**Time range**")

                    # get the user to select the time window they want to visualise
                    @st.cache_data(ttl=3600)
                    def session_length(session_dict):
                        max_time = (tables['Session'] & session_dict).fetch1('session_duration')
                        return max_time
                    max_time = session_length(session_dict)
                    max_time = int(max_time + 0.5)
                    timerange = st.slider(
                        "Select the time range you want to visualise",
                        0,
                        max_time,
                        (0, max_time),
                    )

                    st.divider()
                    if st.button("Plot"):
                        # create the interactive plotly figure (uses webgl gpu rendering!)
                        fig = plot_session(
                            session_dict,
                            selected_animals,
                            selected_objects,
                            timerange,
                        )
                        st.session_state.rasters_fig = fig


                    with col2:
                        if st.session_state.get("rasters_fig", False):
                            config = {
                                "displayModeBar": True,
                                "displaylogo": False,
                                "modeBarButtonsToRemove": [
                                    "sendDataToCloud",
                                    "autoScale2d",
                                    "select2d",
                                    "lasso2d",
                                    "toImage",
                                ],
                            }
                            st.plotly_chart(
                                st.session_state.rasters_fig,
                                use_container_width=True,
                                config=config,
                            )

                else:
                    st.warning("No data to visualise")
