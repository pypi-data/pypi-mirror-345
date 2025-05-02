import streamlit as st
from antelop.utils.streamlit_utils import dropdown_insert_table
from datajoint.errors import DuplicateError


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Electrophysiology")
        st.subheader("Make Probe Insertion")

        st.divider()

        # get user to interactively insert table attributes
        tablename, insert_dict = dropdown_insert_table(
            tables,
            {"ProbeInsertion": tables["ProbeInsertion"]},
            username,
            headless=True,
        )

        # if upstream tables not populated, print error
        if tablename is None:
            st.text("")
            st.error(
                """You can't make a probe insertion yet as you haven't got entries in the necessary upstream tables."""
            )
            st.warning(
                "Please make sure you have inserted an animal and a probe before attempting to insert a probe insertion."
            )
            st.stop()

        st.text("")

        if st.button("Insert"):
            try:
                # check user only inserting their own data
                if insert_dict["experimenter"] == username:
                    tables[tablename].insert1(insert_dict)

                    # show success message
                    st.text("")
                    st.success("Data uploaded to database!")

                # otherwise print error
                else:
                    st.text("")
                    st.error("You can only insert your own data!")

            except DuplicateError:
                st.error("This animal already has a probe insertion!")
