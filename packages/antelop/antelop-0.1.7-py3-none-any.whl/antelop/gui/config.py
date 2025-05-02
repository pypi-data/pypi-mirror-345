from antelop.utils.os_utils import (
    get_config,
    validate_config,
    get_config_path,
    github_repo_exists,
)
import toml
import streamlit as st
import os


def show(tables, username):
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

    with col2:
        # just a widget to load the config and allow modifications plus saving
        # get the config path
        config = get_config()

        if config is None:
            config = {
                "deployment": {"deployment": "local"},
                "mysql": {"host": ""},
                "s3": {"host": ""},
                "folders": {},
                "analysis": {"folders": []},
                "multithreading": {"max_workers": 1},
                "computation": {
                    "host": "",
                    "basedir": "",
                    "antelop_data": "",
                },
                "github": {},
            }
        if "analysis" not in config:
            config["analysis"] = {"folders": []}
        if "github" not in config:
            config["github"] = {}

        new_config = {"deployment": {"deployment": "local"}}

        new_config["mysql"] = {}
        new_config["mysql"]["host"] = st.text_input(
            "Enter MySQL host", config["mysql"]["host"]
        )
        new_config["s3"] = {}
        new_config["s3"]["host"] = st.text_input("Enter S3 host", config["s3"]["host"])

        st.markdown("###### Add searchable folders")
        if "config_folders" not in st.session_state:
            st.session_state["config_folders"] = config["folders"]
        new_folders = {}
        for i, (name, path) in enumerate(st.session_state["config_folders"].items()):
            namecol, pathcol = st.columns([0.3, 0.7])
            with namecol:
                new_name = st.text_input("Enter name", name, key=f"name_{i}")
            with pathcol:
                new_path = st.text_input("Enter path", path, key=f"path_{i}")
            new_folders[new_name] = new_path
        st.session_state["config_folders"] = new_folders
        plus, minus = st.columns([0.05, 0.95])
        with plus:
            if st.button("\+"):
                st.session_state["config_folders"][""] = ""
                st.rerun()
        with minus:
            if st.button("\-"):
                st.session_state["config_folders"].popitem()
                st.rerun()

        st.markdown("###### Add analysis folders")
        if "config_analysis" not in st.session_state:
            st.session_state["config_analysis"] = config["analysis"]["folders"]
        new_analysis = []
        for i, path in enumerate(st.session_state["config_analysis"]):
            new_path = st.text_input("Enter path", path, key=f"analysis_{i}")
            new_analysis.append(new_path)
        st.session_state["config_analysis"] = new_analysis
        plus, minus = st.columns([0.05, 0.95])
        with plus:
            if st.button("\+", key="add_analysis"):
                st.session_state["config_analysis"].append("")
                st.rerun()
        with minus:
            if st.button("\-", key="remove_analysis"):
                st.session_state["config_analysis"].pop()
                st.rerun()

        new_config["multithreading"] = {}
        new_config["multithreading"]["max_workers"] = st.number_input(
            "Enter max worker threads", config["multithreading"]["max_workers"]
        )

        new_config["computation"] = {}
        new_config["computation"]["host"] = st.text_input(
            "Enter cluster host", config["computation"]["host"]
        )
        new_config["computation"]["basedir"] = st.text_input(
            "Enter antelop cluster installation location",
            config["computation"]["basedir"],
        )
        new_config["computation"]["antelop_data"] = st.text_input(
            "Enter antelop cluster data location",
            config["computation"]["antelop_data"],
        )

        st.markdown("###### Add analysis GitHub repositories")
        if "config_repos" not in st.session_state:
            st.session_state["config_repos"] = config["github"]
        new_repos = {}
        for i, (name, path) in enumerate(st.session_state["config_repos"].items()):
            namecol, pathcol = st.columns([0.3, 0.7])
            with namecol:
                new_name = st.text_input("Enter name", name, key=f"repo_{i}_name")
            with pathcol:
                new_path = st.text_input("Enter path", path, key=f"repo_{i}_path")
            new_repos[new_name] = new_path
        st.session_state["config_repos"] = new_repos
        plus, minus = st.columns([0.05, 0.95])
        with plus:
            if st.button("\+", key="add_repo"):
                st.session_state["config_repos"][""] = ""
                st.rerun()
        with minus:
            if st.button("\-", key="remove_repo"):
                st.session_state["config_repos"].popitem()
                st.rerun()

        if st.button("Save"):
            new_config["folders"] = st.session_state["config_folders"]
            new_config["analysis"] = {}
            new_config["analysis"]["folders"] = st.session_state["config_analysis"]
            new_config["github"] = st.session_state["config_repos"]

            if validate_config(new_config):
                config_path = get_config_path()
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, "w") as f:
                    toml.dump(new_config, f)
                st.success("Config file saved")
            else:
                st.error("Invalid config file. Are all your paths correct?")
