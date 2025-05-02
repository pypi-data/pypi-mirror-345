import streamlit as st
import concurrent.futures
from antelop.utils.os_utils import get_config


# function to initialize or get the existing thread pool from session state
def upload_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "upload_futures" not in st.session_state:
        st.session_state.upload_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def feature_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "feature_futures" not in st.session_state:
        st.session_state.feature_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def behaviour_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "behaviour_futures" not in st.session_state:
        st.session_state.behaviour_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def download_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "download_futures" not in st.session_state:
        st.session_state.download_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def delete_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "delete_futures" not in st.session_state:
        st.session_state.delete_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def restore_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "restore_futures" not in st.session_state:
        st.session_state.restore_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def release_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "release_futures" not in st.session_state:
        st.session_state.release_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def dlcup_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "upload_dlc_futures" not in st.session_state:
        st.session_state.upload_dlc_futures = []
    if "extract_frames_futures" not in st.session_state:
        st.session_state.extract_frames_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def dlc_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "download_dlc_futures" not in st.session_state:
        st.session_state.download_dlc_futures = []
    if "extract_frames_futures" not in st.session_state:
        st.session_state.extract_frames_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def phy_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def mask_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "mask_futures" not in st.session_state:
        st.session_state.mask_futures = []
    return st.session_state.process_pool


# function to initialize or get the existing thread pool from session state
def export_thread_pool():
    numworkers = get_config()["multithreading"]["max_workers"]
    if "process_pool" not in st.session_state:
        # create a ThreadPoolExecutor with 1 thread
        st.session_state.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=numworkers
        )
    if "export_futures" not in st.session_state:
        st.session_state.export_futures = []
    return st.session_state.process_pool
