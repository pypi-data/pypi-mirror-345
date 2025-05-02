import streamlit as st
import streamlit_antd_components as sac
import os
from pathlib import Path


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        # query user's full name from database
        @st.cache_data
        def name(username):
            query = tables["Experimenter"] & {"experimenter": username}
            name = query.fetch1("full_name")
            return name

        name = name(username)

        # display welcome
        st.title("Antelop")
        st.write(f"Welcome back {name.split()[0]}!")
        st.write(
            """If you haven't done so already, please take a look at our documentation at:"""
        )
        st.write("https://antelop.readthedocs.io")

        st.divider()

        # display database structure
        st.header("Database structure")

        schema = ["session", "ephys", "behaviour"][
            sac.segmented(
                items=[
                    sac.SegmentedItem(label="Session", icon="table"),
                    sac.SegmentedItem(label="Electrophysiology", icon="lightning"),
                    sac.SegmentedItem(label="Behaviour", icon="joystick"),
                ],
                use_container_width=True,
                return_index=True,
            )
        ]

        resources = Path(os.path.abspath(__file__)).parent.parent / "resources"
        relative_resources = Path(
            os.path.relpath(resources, Path.cwd())
        )  # needed because of windows image bug
        image = relative_resources / f"{schema}.png"

        st.image(str(image), use_column_width=True)

        st.divider()

        # display general usage info
        st.header("Usage guide")
        st.write(
            "First of all, make sure you are familiar with the database structures shown above."
        )
        st.write(
            """Crucially, the tables in green are **Manual** tables, which require user input.
                The tables in red are **Computed** tables, which are populated automatically by submitting computations to the HPC.
                The tables in grey are **Lookup** tables, which are populated by the database administrators.
                The tables in blue are **Imported** tables, which are populated by importing data external data.
                """
        )
        st.write("Use the sidebar on the left to navigate between pages.")
        st.markdown(
            """
    * The **search** page allows you to search a database table, and download or delete the data.
    * The **schemas** tab guides you through uploading data to the various database schemas, perform computations, and visualise the results.
    * The **visualisation** tab allows you to interactively visualise the data in the database.
    * The **analysis** tab allows you to perform preliminary analysis on the data in the database.
    * The **admin** page (only available to database administrators) allows you to search deleted entries, and either restore them, or permanently delete them.
    """
        )
        st.write(
            "Please familiarise yourself with the documentation before using antelop."
        )
