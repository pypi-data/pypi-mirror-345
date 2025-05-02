import streamlit as st
import pandas as pd
from antelop.utils.datajoint_utils import (
    form_query,
    query_without_external,
    show_true_deletes,
)
from antelop.utils.streamlit_utils import dropdown_query_table


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    tables = tables["Experimenter"]._admin().tables

    with col2:
        st.title("Database Administration")
        st.subheader("Permanently delete data")

        st.divider()

        # don't want to check experimenter table
        subtables = {key: val for key, val in tables.items() if key != "Experimenter"}

        # get input restriction
        tablename, restriction = dropdown_query_table(
            tables, subtables, username=None, delete_mode="True"
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
                        st.dataframe(df, hide_index=True)
                        st.text("Number of items: {}".format(number))
                else:
                    st.error("You must enter a query first!")

            st.text("")

            # warning message
            st.info(
                """
    Note that deletes cascade to avoid orphaned database entries.\n
    Please check your deletion before continuing."""
            )

            st.text("")

            if st.button("Check deletes"):
                # show cascaded deletes
                descendant_dict = show_true_deletes(tables, query)
                st.write("Entries that will get deleted:")
                st.dataframe(pd.DataFrame(data=descendant_dict).set_index("Table"))

            status = (
                st.text_input(
                    label="Please enter your password to confirm computation release:",
                    type="password",
                )
                == st.session_state.password
            )

            st.text("")

            # delete button
            if st.button("Delete", type="primary"):
                # delete only if password correct
                if status:
                    query.delete(safemode=False)

                    st.text("")

                    st.success("Data deleted!")

                # incorrect password
                else:
                    st.error("Password incorrect.")

            st.text("")

            # warning message
            st.error("Deletions are irreversible!")
