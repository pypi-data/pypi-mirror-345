import json
import argparse
from spikeinterface import load_extractor
import spikeinterface.preprocessing as spre
import spikeinterface as si
import numpy as np
import os

# extract arguments
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--probe", type=str)
parser.add_argument("-t", "--key", type=str)
args = parser.parse_args()
probe = int(args.probe)
key = json.loads(args.key)

# read params
with open("params.json") as f:
    params = json.load(f)

# set global job kwargs
num_cpus = int(os.environ["SLURM_CPUS_PER_TASK"]) - 1
mem = str(int((int(os.environ["SLURM_MEM_PER_NODE"]) / 1024) * 0.9)) + "G"
si.set_global_job_kwargs(n_jobs=num_cpus, total_memory=mem)

# load recording
recording = load_extractor("probe")

# load preprocessing params
preprocessing = params["preprocessing"]

# apply preprocessing
# bandpass filter
if "bandpass_filter" in preprocessing.keys():
    filtered_recording = spre.bandpass_filter(
        recording,
        preprocessing["bandpass_filter"]["freq_min"],
        preprocessing["bandpass_filter"]["freq_max"],
    )

# save recording
filtered_recording.save(folder=f"preprocessed_{probe}")

# extract individual sorters
with open("spikesorters.json", "w") as f:
    json.dump(params["spikesorters"], f)

# extract rest of the params
with open("params.json", "w") as f:
    json.dump(params, f)
