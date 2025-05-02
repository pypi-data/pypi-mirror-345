import streamlit as st
from antelop.utils.streamlit_utils import dropdown_insert_table


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Metadata")
        st.subheader("Insert data into the metadata schema")

        st.divider()

        # get dictionary of all session tables names and objects
        if (
            len(
                tables["Experiment"]
                & {"experimenter": username, "experiment_deleted": "False"}
            )
            > 0
        ):
            mantables = {
                key: tables[key] for key in ["Experiment", "Animal", "Session"]
            }
        else:
            mantables = {key: tables[key] for key in ["Experiment"]}

        # get user to interactively insert table attributes
        tablename, insert_dict = dropdown_insert_table(tables, mantables, username)

        st.text("")

        # add insert button
        if st.button("Insert"):
            # check user only inserting their own data
            if insert_dict["experimenter"] == username:
                # insert into database
                tables[tablename].insert1(insert_dict)

                # show success message
                st.text("")
                st.success("Data uploaded to database!")

            # otherwise print error
            else:
                st.text("")
                st.error("You can only insert your own data!")
