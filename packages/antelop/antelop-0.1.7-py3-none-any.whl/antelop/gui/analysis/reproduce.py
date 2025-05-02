import streamlit as st
import streamlit_antd_components as sac
from antelop.utils import analysis_utils
from antelop.utils.streamlit_utils import display_analysis, server_directory_browser
from antelop.utils.external_utils import schedule_analysis, analysis_progress
from antelop.utils.analysis_utils import find_function
import json
from operator import itemgetter
from pathlib import Path, PurePosixPath


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    if not hasattr(st.session_state, "result"):
        st.session_state.result = None

    with col2:
        st.title("Analysis")
        st.subheader("Rerun an analysis")

        st.markdown(
            """###### Rerun an analysis from a saved reproducibility json file, checking the code and data haven't changed."""
        )

        st.divider()

        repr_json = server_directory_browser(
            "Select your reproducibility json", extension="json"
        )

        st.divider()

        if repr_json:
            with open(repr_json, "r") as f:
                repr_dict = json.load(f)

            # get the function from its name
            functions, _ = analysis_utils.import_analysis(
                tables["Experimenter"].connection, tables
            )
            function = find_function(functions, *itemgetter("name", "location", "folder")(repr_dict))
            restriction = repr_dict["restriction"]
            args = repr_dict["arguments"]

            if isinstance(function.query, str):
                table = tables[function.query].proj()
            elif isinstance(function.query, list):
                table = tables[function.query[0]]
                for q in function.query[1:]:
                    table = table * tables[q].proj()

        if st.button("Check hashes"):
            if repr_json:
                # check the hashes
                message = function.check_hash(repr_json)

                # print messages
                if message == "Reproducibility checks passed.":
                    st.text("")
                    st.success("Reproducibility checks passed.")
                else:
                    st.text("")
                    st.warning(message)

            else:
                st.text("")
                st.error("Please select a reproducibility json file.")

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
                if repr_json:

                    # get the restriction
                    restriction = repr_dict["restriction"]
                    # get the args
                    args = repr_dict["arguments"]

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

                    result = cache_fct(function.name, restriction, **args)
                    st.session_state.result = result

                    st.divider()
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

                else:
                    st.error("Please select a reproducibility json file.")

        if st.session_state.mode == "Cluster":
            st.text("")

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
