import streamlit as st
from antelop.utils.streamlit_utils import (
    dropdown_insert_table,
    define_rig_json,
    get_rig_videos,
)
import json
import streamlit_antd_components as sac
from antelop.utils.antelop_utils import validate_behaviour_rig, insert_features
from antelop.connection.transaction import transaction_context


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Behaviour")
        st.subheader("Define Behaviour Rig Layout")

        st.divider()

        sac.buttons(
            [
                sac.ButtonsItem(label="Manually Specify", icon="pen"),
                sac.ButtonsItem(label="Import Json", icon="cloud-upload"),
            ],
            key="behaviour_import",
            gap="md",
            use_container_width=True,
        )

        # manually specify
        if st.session_state["behaviour_import"] == "Manually Specify":
            tablename, insert_dict = dropdown_insert_table(
                tables,
                {"BehaviourRig": tables["BehaviourRig"]},
                username,
                headless=True,
                primary_only=True,
            )

            insert_dict["behaviourrig_name"] = st.text_input("Enter behaviourrig_name")

            st.text("")

            if insert_dict:
                st.divider()

                st.subheader("Define Videos in Rig")

                videos = get_rig_videos()
                videos = list(videos.values())

                st.divider()

                st.subheader("Define Rig Layout")

                rig_json = define_rig_json(videos)

                st.text("")
                if st.button("Insert"):
                    # check user only inserting their own data
                    if insert_dict["experimenter"] == username:
                        value = validate_behaviour_rig(rig_json)

                        if value != True:
                            st.error(value)

                        else:
                            insert_dict["rig_json"] = rig_json

                            # get primary keys
                            primary_key = {
                                key: val
                                for key, val in insert_dict.items()
                                if key in ["experimenter", "behaviourrig_id"]
                            }

                            # make list of features to insert
                            feature_list = insert_features(primary_key, rig_json)

                            # in a single transaction, perform all inserts
                            with transaction_context(
                                tables["Experimenter"].connection
                            ):
                                # insert json into database
                                tables[tablename].insert1(insert_dict)

                                # insert features into database
                                tables["Feature"].insert(feature_list)

                            # show success message
                            st.text("")
                            st.success("Data uploaded to database!")

                    # otherwise print error
                    else:
                        st.text("")
                        st.error("You can only insert your own data!")

        # import predefined json
        elif st.session_state["behaviour_import"] == "Import Json":
            tablename, insert_dict = dropdown_insert_table(
                tables,
                {"BehaviourRig": tables["BehaviourRig"]},
                username,
                headless=True,
            )

            st.text("")

            if insert_dict:
                if st.button("Insert"):
                    # check user only inserting their own data
                    if insert_dict["experimenter"] == username:
                        try:
                            # first, validate the behaviour rig file
                            rigfile = insert_dict["rig_json"]

                            with open(rigfile, "r") as f:
                                read_rig = json.load(f)

                            # validate the rig file
                            assert validate_behaviour_rig(read_rig)

                        except AssertionError:
                            st.error("Rig file not valid!")
                            st.warning(
                                "Please read the documentation and ensure your file is in the correct format"
                            )

                        except Exception:
                            st.error("Error reading file!")

                        else:
                            insert_dict["rig_json"] = read_rig

                            # get primary keys
                            primary_key = {
                                key: val
                                for key, val in insert_dict.items()
                                if key in ["experimenter", "behaviourrig_id"]
                            }

                            # make list of features to insert
                            feature_list = insert_features(primary_key, read_rig)

                            with transaction_context(
                                tables["Experimenter"].connection
                            ):
                                # insert json into database
                                tables[tablename].insert1(insert_dict)
                                tables["Feature"].insert(feature_list)

                            # show success message
                            st.text("")
                            st.success("Data uploaded to database!")

                    # otherwise print error
                    else:
                        st.text("")
                        st.error("You can only insert your own data!")
