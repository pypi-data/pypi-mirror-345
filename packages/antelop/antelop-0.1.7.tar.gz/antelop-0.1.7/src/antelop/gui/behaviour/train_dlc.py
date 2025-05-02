import streamlit as st
from antelop.utils.external_utils import schedule_train_dlc, train_dlc_progress
from antelop.utils.streamlit_utils import dropdown_query_table
from antelop.utils.antelop_utils import display_dlc_images
import streamlit_antd_components as sac


def show(username, tables):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        st.title("Behaviour")
        st.subheader("Train your DeepLabCut model")

        st.divider()
        sac.buttons(
            [
                sac.ButtonsItem(label="Schedule Model Training"),
                sac.ButtonsItem(label="Evaluate Model"),
            ],
            key="dlcmode",
            gap="md",
            use_container_width=True,
        )

        if st.session_state.dlcmode == "Schedule Model Training":
            st.subheader("Select the model you want to train")

            # Select the feature to add
            tablename, key = dropdown_query_table(
                tables,
                {
                    "LabelledFrames": tables["LabelledFrames"] - tables["DLCModel"]
                    & {"labelledframes_in_compute": "False"}
                },
                username,
                headless=True,
            )
            if key:
                key["behaviourrig_deleted"] = "False"

            if key is None:
                st.error(
                    """You can't train a DeepLabCut model yet as you haven't labelled any frames or all possible models are already trained."""
                )
                st.warning("Please go to the insert tab and label some frames.")

            else:
                st.divider()

                # schedule computation section
                st.subheader("Schedule computation")

                # ask for user password for scheduling the job
                password = st.text_input(
                    "Please enter your cluster password", type="password"
                )

                st.text("")
                if st.button("Schedule model training"):
                    if key["experimenter"] != username:
                        st.error("You can only train models on your own data")

                    else:
                        try:
                            num_videos = len(
                                tables["World"] * tables["Video"]
                                & key
                                & {
                                    "dlc_training": "True",
                                    "world_deleted": "False",
                                    "video_deleted": "False",
                                }
                            )

                            # send job
                            schedule_train_dlc(key, num_videos, password)

                            # success message
                            st.success("Job sent to cluster!")
                            st.info(
                                "You will receive an email once your job is completed"
                            )

                        except Exception as e:
                            print(e)
                            st.error("Error submitting job to cluster")

                st.text("")

                # if there are any downlaods this session
                if "train_dlc_jobs" in st.session_state:
                    # button which shows spikesort statuses
                    if st.button("Check model training progress"):
                        train_dlc_progress()

        if st.session_state.dlcmode == "Evaluate Model":
            st.subheader("Select the model you want to evaluate")

            # Select the feature to add
            tablename, key = dropdown_query_table(
                tables, {"DLCModel": tables["DLCModel"]}, username, headless=True
            )

            if key is None:
                st.error(
                    """You can't evaluate a DeepLabCut model yet as you haven't trained any models."""
                )
                return

            # fetch results and display
            st.divider()
            st.markdown("### Evaluation metrics")
            metrics = (tables["DLCModel"] & key).fetch1("evaluation_metrics")
            st.dataframe(metrics, use_container_width=True)

            # fetch images and display
            st.divider()
            if st.button("Show evaluated images"):
                st.session_state["dlc_inference_folder"] = display_dlc_images(
                    tables["DLCModel"], key
                )

            # display images
            if "dlc_inference_folder" in st.session_state:
                folder = st.session_state["dlc_inference_folder"]

                images = list(folder.glob("*.png"))

                test_images = [i for i in images if "Test" in i.name]
                train_images = [i for i in images if "Train" in i.name]

                image_dict = {
                    f"Test {i + 1}": str(test_images[i].resolve())
                    for i in range(len(test_images))
                }
                image_dict.update(
                    {
                        f"Train {i + 1}": str(train_images[i].resolve())
                        for i in range(len(train_images))
                    }
                )

                image = image_dict[
                    st.selectbox("Select image to display", list(image_dict.keys()))
                ]

                st.image(image)
