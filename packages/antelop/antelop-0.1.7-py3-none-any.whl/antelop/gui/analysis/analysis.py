import streamlit as st
import streamlit_antd_components as sac
from antelop.utils import analysis_utils
from antelop.utils.streamlit_utils import (
    dropdown_query_table,
    enter_args,
    display_analysis,
    select_analysis,
    server_directory_browser,
)
from antelop.utils.external_utils import schedule_analysis, analysis_progress
from antelop.utils.analysis_utils import reload_analysis
from pathlib import Path, PurePosixPath


def reset_state():
    st.session_state.result = None


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Analysis")
        st.subheader("Run analysis on the database")

        def reset_state():
            st.session_state.result = None

        st.divider()
        if not hasattr(st.session_state, "result"):
            reset_state()

        # load analysis functions
        analysis_functions, import_errors = analysis_utils.import_analysis(
            tables["Experimenter"].connection, tables
        )
        analysis_dict = analysis_utils.functions_to_dict(analysis_functions)
        function = select_analysis(analysis_dict)

        # display docstring
        st.text("")
        if function:
            st.markdown(function.__doc__)
        if st.button("Reload functions"):
            analysis_functions = reload_analysis(
                tables["Experimenter"].connection, tables
            )
            st.rerun()
        st.divider()

        if function:
            # get user to select the restriction they want to apply
            st.markdown("#### Enter restriction")
            if hasattr(function, "key"):
                key = function.key
            else:
                key = {}
            if isinstance(function.query, str):
                table = tables[function.query].proj()
            elif isinstance(function.query, list):
                table = tables[function.query[0]]
                for q in function.query[1:]:
                    table = table * tables[q].proj()
            _, restriction = dropdown_query_table(
                tables, {"table": table & key}, username, headless=True
            )

            if _ == None:
                st.error("No data available to run analysis on.")

            else:
                # get the user to input the arguments
                if hasattr(function, "args") and function.args:
                    st.divider()
                    st.markdown("#### Enter arguments")
                    args = enter_args(function)
                else:
                    args = {}

                # run the function
                st.divider()
                st.markdown("#### Select mode")
                sac.buttons(
                    [sac.ButtonsItem(label="Local"), sac.ButtonsItem(label="Cluster")],
                    key="mode",
                    use_container_width=True,
                )

                if st.session_state.mode == "Local":
                    st.text("")
                    result = None
                    if st.button("Run"):

                        @st.cache_data(ttl=600)
                        def cache_fct(id, restriction, **args):
                            try:
                                return function(restriction, **args)
                            except Exception as e:
                                st.error(
                                    f"""
                                Your function has an error.\n
                                Error message:\n
                                {e}
                                """
                                )

                        result = cache_fct(id(function), restriction, **args)
                        st.session_state.result = result

                    st.divider()
                    if hasattr(st.session_state, "result"):
                        display_analysis(
                            st.session_state.result, function.returns, table.primary_key
                        )

                        if st.session_state.result is not None:

                            st.divider()
                            directory = server_directory_browser(message="Select save directory:")
                            if directory:
                                filename = st.text_input("Enter filename:")
                                extension = st.radio(label="Select file extension", options=["pkl", "csv"])
                                if filename:
                                    if st.button("Save results"):
                                        savepath = Path(directory) / filename
                                        function.save_result(
                                            savepath, extension, restriction, **args
                                        )
                                        st.success("Results saved!")

                if st.session_state.mode == "Cluster":
                    st.text("")
                    if function.location == "local":
                        st.warning("You cannot run local functions on the cluster.\nPlease push to your GitHub repository first.")
                    else:

                        savepath = st.text_input("Enter the path to save the results to:")
                        filename = st.text_input("Enter filename:")
                        extension = st.radio(label="Select file extension", options=["pkl", "csv"])
                        numcpus = st.number_input(
                            "Enter the number of cpus to use",
                            min_value=1,
                            max_value=64,
                            value=1,
                        )
                        time = st.number_input(
                            "Enter the time to run the job for (minutes)",
                            min_value=10,
                            max_value=24 * 60,
                            value=60,
                        )
                        password = st.text_input(
                            "Please enter your cluster password", type="password"
                        )

                        st.text("")
                        if st.button("Schedule analysis job"):
                            try:
                                if not PurePosixPath(savepath).is_absolute():
                                    st.error("Save path must be an absolute Unix path.")
                                    raise ValueError("Savepath must be an absolute path.")
                                savepath = PurePosixPath(savepath) / filename
                                savepath = savepath.with_suffix(f".{extension}")
                                schedule_analysis(
                                    function,
                                    restriction,
                                    str(savepath),
                                    numcpus,
                                    time,
                                    password,
                                    args,
                                )
                            except Exception as e:
                                st.error(
                                    "Job scheduling failed. Please check your inputs and try again."
                                )
                            else:
                                st.text("")
                                st.success("Job sent to cluster.")

                        # if there are any downlaods this session
                        if "analysis_jobs" in st.session_state:
                            # button which shows spikesort statuses
                            st.text("")
                            if st.button("Check analysis progress"):
                                analysis_progress()
