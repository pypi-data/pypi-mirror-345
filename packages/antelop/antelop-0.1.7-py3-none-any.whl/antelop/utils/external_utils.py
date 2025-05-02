"""
Utility functions involving applications outside the main antelop container.

Author: Rory Bedford
Date: 02/11/23
"""

import json
import paramiko
import os
import socket
from pathlib import Path, PurePosixPath
import math
import streamlit as st
from datetime import datetime, timedelta
from antelop.utils.os_utils import get_config
import numpy as np


def slurm_time(numjobs, scale=1):
    """
    Function calculates how long to schedule master job for
    """
    # function is a sigmoid starting at around two hours, and saturating at a day at around 100 params
    t = scale * 3600 * (24 / (1 + math.exp((-numjobs + 50) / 20)))

    # convert to slurm format
    t_delta = timedelta(seconds=t)
    timestring = str(t_delta).split(".")[0]
    if len(timestring) == 7:
        timestring = "0" + timestring

    return timestring


def compute_log():
    """
    Computes directory in which to store log files for this job
    """
    # current time
    d = datetime.now()

    # logdir
    logdir = PurePosixPath(str(d.year)) / str(d.month) / str(d.day)

    return str(logdir)


def schedule_spikesorting(session_dict, username, password, numjobs):
    """
    Function calls the nextflow spikesorting pipeline
    """

    config = get_config()

    # get hostname
    if config["deployment"]["deployment"] == "apptainer":
        node = socket.gethostname()
    elif config["deployment"]["deployment"] == "local":
        node = config["computation"]["host"]

    # path for bash submission
    compute_dict = config["computation"]
    basedir = PurePosixPath(compute_dict["basedir"])
    script = str(basedir / "workflows" / "submit.sh")

    # load credentials for nextflow environment
    credentials = dict(
        DB_HOST=config["mysql"]["host"],
        DB_USER=st.session_state.username,
        DB_PASS=st.session_state.password,
        S3_HOST=config["s3"]["host"],
        S3_USER=st.session_state.username,
        S3_PASS=st.session_state.password,
    )

    # make slurm env var string
    env_string = ",".join([f"{key}='{val}'" for key, val in credentials.items()])

    # make nextflow submission command
    param = json.dumps(session_dict, separators=(",", ":"))

    logdir = compute_log()
    logdirmnt = Path(config["computation"]["antelop_data"]) / "logs" / logdir

    slurmtime = slurm_time(numjobs, scale=4)

    # command to be run
    command = (
        f"""bash {script} '{param}' {logdir} spikesorting {env_string} {slurmtime}"""
    )

    # initialise paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # connect to node
    ssh.connect(
        node,
        username=username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
    )

    # execute command
    stdin, stdout, stderr = ssh.exec_command(command)
    bash_id = stdout.read().decode().strip()

    # initialise session state
    if "spikesort_jobs" not in st.session_state:
        st.session_state.spikesort_jobs = []

    # append job id and logdir to session state
    st.session_state.spikesort_jobs.append((bash_id, logdirmnt))


def spikesorting_progress():
    """
    Function checks progress of currently running spikesorting jobs
    """
    for i, val in enumerate(st.session_state.spikesort_jobs):
        st.divider()
        st.text("")

        st.write(f"Job {i + 1} progress:")

        # read log file
        slurmfile = Path(os.path.expandvars(val[1])) / f"slurm-{val[0]}.out"
        try:
            with open(slurmfile, "r") as f:
                log = f.read()

            # split log at double newline
            if len(log.split("\n\nexecutor")) > 1:
                log = log.split("\n\nexecutor")[-1]
                st.text(log)
            else:
                st.text("\nJob awaiting cluster submission\n")

        except FileNotFoundError:
            st.text("\nJob awaiting cluster submission\n")


def schedule_import_phy(ephys_dict, username, password, numjobs):
    """
    Function calls the nextflow spikesorting pipeline
    """

    config = get_config()

    # get hostname
    if config["deployment"]["deployment"] == "apptainer":
        node = socket.gethostname()
    elif config["deployment"]["deployment"] == "local":
        node = config["computation"]["host"]

    # path for bash submission
    compute_dict = config["computation"]
    basedir = PurePosixPath(compute_dict["basedir"])
    script = str(basedir / "workflows" / "submit.sh")

    # load credentials for nextflow environment
    credentials = dict(
        DB_HOST=config["mysql"]["host"],
        DB_USER=st.session_state.username,
        DB_PASS=st.session_state.password,
        S3_HOST=config["s3"]["host"],
        S3_USER=st.session_state.username,
        S3_PASS=st.session_state.password,
    )

    # make slurm env var string
    env_string = ",".join([f"{key}='{val}'" for key, val in credentials.items()])

    # make nextflow submission command
    param = json.dumps(ephys_dict, separators=(",", ":"))

    logdir = compute_log()
    logdirmnt = Path(config["computation"]["antelop_data"]) / "logs" / logdir

    slurmtime = slurm_time(numjobs)

    # command to be run
    command = (
        f"""bash {script} '{param}' {logdir} import_phy {env_string} {slurmtime}"""
    )

    # initialise paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # execute command
    ssh.connect(
        node,
        username=username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
    )
    stdin, stdout, stderr = ssh.exec_command(command)
    bash_id = stdout.read().decode().strip()

    # initialise session state
    if "import_phy_jobs" not in st.session_state:
        st.session_state.import_phy_jobs = []

    # append job id and logdir to session state
    st.session_state.import_phy_jobs.append((bash_id, logdirmnt))


def import_phy_progress():
    """
    Function checks progress of currently running spikesorting jobs
    """
    for i, val in enumerate(st.session_state.import_phy_jobs):
        st.divider()
        st.text("")

        st.write(f"Job {i + 1} progress:")

        # read log file
        slurmfile = Path(os.path.expandvars(val[1])) / f"slurm-{val[0]}.out"
        try:
            with open(slurmfile, "r") as f:
                log = f.read()

            # split log at double newline
            if len(log.split("\n\nexecutor")) > 1:
                log = log.split("\n\nexecutor")[-1]
                st.text(log)
            else:
                st.text("\nJob awaiting cluster submission\n")

        except FileNotFoundError:
            st.text("\nJob awaiting cluster submission\n")


def open_phy(hashkey, username, password):
    """
    Function opens phy on the given ephys entry
    """

    config_dict = get_config()

    if config_dict["deployment"]["deployment"] == "apptainer":
        # need to change this since we don't configure cluster data location anymore

        # get hostname
        node = socket.gethostname()

        # calculate phy container
        basedir = Path(config_dict["computation"]["basedir"])
        phycontainer = str(basedir / "containers" / "phy.sif")

        # where phy data get stored
        phybase = Path(config_dict["computation"]["antelop_data"]) / "phy"
        phypath = str(phybase / hashkey / "phy")

        # command to be run
        command = f"""DISPLAY={os.environ["DISPLAY"]} apptainer run -B {phypath}:/mnt {phycontainer}"""

        # initialise paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # execute command
        ssh.connect(
            node,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
        )
        stdin, stdout, stderr = ssh.exec_command(command)

    elif config_dict["deployment"]["deployment"] == "local":
        from phy.apps.template import template_gui
        from antelop.utils.multithreading_utils import phy_thread_pool

        phybase = Path(config_dict["computation"]["antelop_data"]) / "phy"
        phypath = str(phybase / hashkey / "phy" / "params.py")

        phy_thread = phy_thread_pool()
        phy_thread.submit(template_gui, phypath)


def schedule_train_dlc(key, num_videos, password):
    """
    Function calls the nextflow spikesorting pipeline
    """

    config = get_config()

    # get hostname
    if config["deployment"]["deployment"] == "apptainer":
        node = socket.gethostname()
    elif config["deployment"]["deployment"] == "local":
        node = config["computation"]["host"]

    # path for bash submission
    compute_dict = config["computation"]
    basedir = PurePosixPath(compute_dict["basedir"])
    script = str(basedir / "workflows" / "submit.sh")

    # load credentials for nextflow environment
    credentials = dict(
        DB_HOST=config["mysql"]["host"],
        DB_USER=st.session_state.username,
        DB_PASS=st.session_state.password,
        S3_HOST=config["s3"]["host"],
        S3_USER=st.session_state.username,
        S3_PASS=st.session_state.password,
    )

    # make slurm env var string
    env_string = ",".join([f"{key}='{val}'" for key, val in credentials.items()])

    # make key json serialisable
    key = {
        k: (int(v) if k in ["experiment_id", "behaviourrig_id", "dlcmodel_id"] else v)
        for k, v in key.items()
    }

    # make nextflow submission command
    param = json.dumps(key, separators=(",", ":"))

    logdir = compute_log()
    logdirmnt = Path(config["computation"]["antelop_data"]) / "logs" / logdir

    # convert to slurm format
    slurmtime = slurm_time(num_videos * 0.2, 5)

    # command to be run
    command = f"""bash {script} '{param}' {logdir} train_dlc {env_string} {slurmtime}"""

    # initialise paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # execute command
    ssh.connect(
        node,
        username=st.session_state.username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
    )
    stdin, stdout, stderr = ssh.exec_command(command)
    bash_id = stdout.read().decode().strip()

    # initialise session state
    if "train_dlc_jobs" not in st.session_state:
        st.session_state.train_dlc_jobs = []

    # append job id and logdir to session state
    st.session_state.train_dlc_jobs.append((bash_id, logdirmnt))


def train_dlc_progress():
    """
    Function checks progress of currently running dlc training jobs
    """
    for i, val in enumerate(st.session_state.train_dlc_jobs):
        st.divider()
        st.text("")

        st.write(f"Job {i + 1} progress:")

        # read log file
        slurmfile = Path(os.path.expandvars(val[1])) / f"slurm-{val[0]}.out"
        try:
            with open(slurmfile, "r") as f:
                log = f.read()

            # split log at double newline
            if len(log.split("\n\nexecutor")) > 1:
                log = log.split("\n\nexecutor")[-1]
                st.text(log)
            else:
                st.text("\nJob awaiting cluster submission\n")

        except FileNotFoundError:
            st.text("\nJob awaiting cluster submission\n")


def schedule_analysis(function, restriction, savepath, numcpus, time, password, args):
    """
    Function sends analysis job to cluster.
    """

    for key, val in restriction.items():
        if isinstance(val, np.int64):
            restriction[key] = int(val)

    # get function name and script
    func_name = function.name
    func_folder = function.folder
    func_location = function.location

    # get other arguments
    restriction_str = json.dumps(restriction, separators=(",", ":"))
    args_str = json.dumps(args, separators=(",", ":"))

    # submission path
    config = get_config()
    node = config["computation"]["host"]
    compute_dict = config["computation"]
    basedir = PurePosixPath(compute_dict["basedir"])
    script = str(basedir / "workflows" / "analysis" / "submit.sh")

    # convert time to slurm format
    t_delta = timedelta(seconds=time * 60)
    timestring = str(t_delta).split(".")[0]
    if len(timestring) == 7:
        timestring = "0" + timestring

    # make slurm env var string
    credentials = dict(
        DB_HOST=config["mysql"]["host"],
        DB_USER=st.session_state.username,
        DB_PASS=st.session_state.password,
        S3_HOST=config["s3"]["host"],
        S3_USER=st.session_state.username,
        S3_PASS=st.session_state.password,
    )
    env_string = ",".join([f"{key}='{val}'" for key, val in credentials.items()])

    logdir = compute_log()
    logdirmnt = Path(config["computation"]["antelop_data"]) / "logs" / logdir

    # command to be run
    command = f"""bash {script} {logdir} {env_string} {timestring} {numcpus} {savepath} '{func_location}' '{func_folder}' '{func_name}' '{restriction_str}' '{args_str}'"""

    # initialise paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # connect to cluster
    ssh.connect(
        node,
        username=st.session_state.username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
    )

    # execute command
    stdin, stdout, stderr = ssh.exec_command(command)
    bash_id = stdout.read().decode().strip()

    # initialise session state
    if "analysis_jobs" not in st.session_state:
        st.session_state.analysis_jobs = []

    # append job id and logdir to session state
    st.session_state.analysis_jobs.append((bash_id, logdirmnt))


def analysis_progress():
    """
    Function checks progress of currently running analysis jobs
    """
    for i, val in enumerate(st.session_state.analysis_jobs):
        st.divider()
        st.text("")

        st.write(f"Job {i + 1} progress:")

        # read log file
        slurmfile = Path(os.path.expandvars(val[1])) / f"slurm-{val[0]}.out"
        try:
            with open(slurmfile, "r") as f:
                log = f.read()

            st.text(log)

        except FileNotFoundError:
            st.text("\nJob awaiting cluster submission\n")


def schedule_inference_dlc(key, num_videos, password):
    """
    Function calls the nextflow spikesorting pipeline
    """

    config = get_config()

    # get hostname
    if config["deployment"]["deployment"] == "apptainer":
        node = socket.gethostname()
    elif config["deployment"]["deployment"] == "local":
        node = config["computation"]["host"]

    # path for bash submission
    compute_dict = config["computation"]
    basedir = PurePosixPath(compute_dict["basedir"])
    script = str(basedir / "workflows" / "submit.sh")

    # load credentials for nextflow environment
    credentials = dict(
        DB_HOST=config["mysql"]["host"],
        DB_USER=st.session_state.username,
        DB_PASS=st.session_state.password,
        S3_HOST=config["s3"]["host"],
        S3_USER=st.session_state.username,
        S3_PASS=st.session_state.password,
    )

    # make slurm env var string
    env_string = ",".join([f"{key}='{val}'" for key, val in credentials.items()])

    # make key json serialisable
    key = {
        k: (
            int(v)
            if k in ["experiment_id", "behaviourrig_id", "dlcmodel_id", "session_id"]
            else v
        )
        for k, v in key.items()
    }

    # make nextflow submission command
    param = json.dumps(key, separators=(",", ":"))

    logdir = compute_log()
    logdirmnt = Path(config["computation"]["antelop_data"]) / "logs" / logdir

    # convert to slurm format
    slurmtime = slurm_time(num_videos * 0.2, 5)

    # command to be run
    command = (
        f"""bash {script} '{param}' {logdir} inference_dlc {env_string} {slurmtime}"""
    )

    # initialise paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # execute command
    ssh.connect(
        node,
        username=st.session_state.username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
    )
    stdin, stdout, stderr = ssh.exec_command(command)
    bash_id = stdout.read().decode().strip()

    # initialise session state
    if "inference_dlc_jobs" not in st.session_state:
        st.session_state.inference_dlc_jobs = []

    # append job id and logdir to session state
    st.session_state.inference_dlc_jobs.append((bash_id, logdirmnt))


def inference_dlc_progress():
    """
    Function checks progress of currently running dlc inferenceing jobs
    """
    for i, val in enumerate(st.session_state.inference_dlc_jobs):
        st.divider()
        st.text("")

        st.write(f"Job {i + 1} progress:")

        # read log file
        slurmfile = Path(os.path.expandvars(val[1])) / f"slurm-{val[0]}.out"
        try:
            with open(slurmfile, "r") as f:
                log = f.read()

            # split log at double newline
            if len(log.split("\n\nexecutor")) > 1:
                log = log.split("\n\nexecutor")[-1]
                st.text(log)
            else:
                st.text("\nJob awaiting cluster submission\n")

        except FileNotFoundError:
            st.text("\nJob awaiting cluster submission\n")
