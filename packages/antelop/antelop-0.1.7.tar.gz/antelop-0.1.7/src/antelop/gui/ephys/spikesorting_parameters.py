import streamlit as st
from antelop.utils.streamlit_utils import (
    dropdown_query_table,
    display_sorting_parameters,
    lfp_params_input,
    waveform_params_input,
    preprocessing_params_input,
    input_sorter_params,
    agreement_params_input,
)


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Electrophysiology")
        st.subheader("Insert Spikesorting Parameters")

        st.divider()
        st.subheader("Select the animal you want to add parameters to")

        # get input restriction
        _, primary_key = dropdown_query_table(
            tables, {"Animal": tables["Animal"]}, username, headless=True
        )

        # error if prerequisites not satisfied
        if primary_key == None:
            st.error(
                """You can't insert any sorting parameters yet as you haven't got entries in the necessary upstream tables."""
            )
            st.warning(
                "Please make sure you have at least one animal to add sorting parameters to."
            )

        # otherwise retrieve all the data
        elif "animal_id" in primary_key.keys():
            # calculate sortingparams id
            query = tables["SortingParams"]._admin() & primary_key
            next_key = max(query.fetch("sortingparams_id"), default=0) + 1
            primary_key["sortingparams_id"] = next_key

            st.divider()

            st.subheader("Insert parameters")

            # initialise paramdict
            paramdict = {}

            """
            LFP parameters
            """
            st.divider()

            # display message
            st.markdown("##### Select LFP extraction parameters:")
            paramdict["lfp"] = lfp_params_input()

            """
            waveform parameters
            """
            st.divider()

            # display message
            st.markdown("##### Select waveform extraction parameters:")
            paramdict["waveform"] = waveform_params_input()

            """
            Preprocessing parameters
            """
            st.divider()

            # display message
            st.markdown("##### Select preprocessing parameters:")

            # get user input preprocessing params
            paramdict["preprocessing"] = preprocessing_params_input()

            """
            Spikesorting parameters
            """
            st.divider()

            # display message
            st.markdown("##### Select spikesorting parameters:")
            st.write(
                "You can select one or more spikesorters which will run in parallel."
            )
            st.write(
                "Note some of the parameters for a given sorter may be irrelevant,\nparticularly those related to the allocation of computational resources."
            )

            # get user input sorter params
            paramdict["spikesorters"] = input_sorter_params()

            # only add agreement matching if more than one sorter
            if len(paramdict["spikesorters"]) > 1:
                """
                Agreement matching parameters
                """
                st.divider()

                # display message
                st.markdown("##### Select agreement matching parameters:")

                # get user input agreement matching params
                paramdict["matching"] = agreement_params_input(
                    len(paramdict["spikesorters"])
                )

            """
            Description
            """
            st.divider()

            st.subheader("Add a name")

            name = st.text_input(
                "Add an identifiable name for this set of sorting parameters"
            )

            st.subheader("Add a description")

            description = st.text_area(
                "Add a description of this set of sorting parameters"
            )

            """
            Upload section
            """
            st.divider()

            st.subheader("Add to database")

            # display confirmation showing parameters to be inserted
            st.text("Adding the following parameters to be run for this experiment:")
            display_sorting_parameters(paramdict)

            # upload on button click
            if st.button("Add to database"):
                # can't have parameters with no spikesorters
                if len(paramdict["spikesorters"]) == 0:
                    st.error("You must add at least one spikesorter!")

                # if user doesn't have permsission
                elif primary_key["experimenter"] != username:
                    st.error("You can only insert your own data!")

                # otherwise data can be inserted
                else:
                    tables["SortingParams"].insert1(
                        {
                            **primary_key,
                            "sortingparams_name": name,
                            "params": paramdict,
                            "sortingparams_notes": description,
                        }
                    )

                    # print success message
                    st.success("Parameters uploaded to database!")
