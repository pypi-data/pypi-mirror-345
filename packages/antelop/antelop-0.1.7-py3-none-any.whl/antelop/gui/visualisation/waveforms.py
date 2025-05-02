import streamlit as st
from antelop.utils.streamlit_utils import dropdown_query_table
from antelop.utils.visualisation_utils import plot_units, plot_isi, unit_stats
import streamlit_antd_components as sac


def show(username, tables):
    st.title("Visualisation")
    st.subheader("Spikesorting unit waveforms and statistics")
    st.divider()

    col1, col2 = st.columns([0.4, 0.6], gap="large")

    with col1:
        st.markdown("**Select the spikesorting you want to visualise**")

        # get user to interactively insert table attributes
        tablename, spikesorting_dict = dropdown_query_table(
            tables, {"SpikeSorting": tables["SpikeSorting"]}, username, headless=True
        )

        if spikesorting_dict is None:
            st.warning("You currently have no spikesorted data to visualise")

        elif "sortingparams_id" in spikesorting_dict.keys():
            # first query the probes
            probes = (tables["Probe"] & spikesorting_dict).fetch(as_dict=True)

            # initialise selected units
            selected_units = []

            st.text("")
            st.text("Select the units you want to visualise")

            # loop through probes and get user to select units
            for probe in probes:
                # get units for this probe
                units = (tables["Unit"] & spikesorting_dict & probe).fetch(as_dict=True)

                # make a dict mapping unit names to unit dicts
                unit_dict = {}
                for unit in units:
                    unit_dict[str(unit["unit_id"])] = unit

                # get user to select the units they want to visualise
                selected_units += [
                    unit_dict[i]
                    for i in sac.checkbox(
                        items=list(unit_dict.keys()),
                        label=f"""Probe {probe["probe_id"]}""",
                        index=list(range(len(unit_dict))),
                        check_all="Select all",
                    )
                ]

            if st.button("Plot"):
                # generate plots
                st.session_state["waveforms_vis"] = plot_units(
                    spikesorting_dict, selected_units
                )
                st.session_state["isi_vis"] = plot_isi(
                    spikesorting_dict, selected_units
                )
                st.session_state["unit_stats"] = unit_stats(
                    spikesorting_dict, selected_units
                )

            with col2:
                if "waveforms_vis" in st.session_state.keys():
                    wav_figures = st.session_state["waveforms_vis"]
                    isi_figures = st.session_state["isi_vis"]
                    stats = st.session_state["unit_stats"]

                    st.markdown("**Select a probe**")

                    # button displays different probes
                    probe = sac.buttons(
                        [sac.ButtonsItem(label=probe) for probe in wav_figures.keys()],
                        format_func=lambda x: f"Probe {x}",
                        use_container_width=True,
                    )

                    mode = sac.buttons(
                        [
                            sac.ButtonsItem(label="Waveforms"),
                            sac.ButtonsItem(label="ISI histograms"),
                            sac.ButtonsItem(label="Statistics"),
                        ],
                        use_container_width=True,
                    )

                    # display the selected probe
                    if mode == "Waveforms":
                        group = sac.buttons(
                            [sac.ButtonsItem(label=group) for group in wav_figures[probe].keys()],
                            format_func=lambda x: f"{x}",
                            use_container_width=True,
                        )
                        st.plotly_chart(wav_figures[probe][group], use_container_width=True)
                    elif mode == "ISI histograms":
                        st.plotly_chart(isi_figures[probe], use_container_width=True)
                    elif mode == "Statistics":
                        st.dataframe(
                            stats[probe], hide_index=True, use_container_width=True
                        )
