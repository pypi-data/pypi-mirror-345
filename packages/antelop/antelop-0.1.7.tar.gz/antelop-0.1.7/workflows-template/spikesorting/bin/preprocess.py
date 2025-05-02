import json
import argparse
from spikeinterface import load_extractor
import spikeinterface.preprocessing as spre
import spikeinterface as si
import numpy as np
import os

# extract arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--param", type=str)
parser.add_argument("-o", "--probe", type=str)
parser.add_argument("-t", "--trial", type=str)
args = parser.parse_args()
params = json.loads(args.param)
probe = int(args.probe)
trial = json.loads(args.trial)

# set global job kwargs
num_cpus = int(os.environ["SLURM_CPUS_PER_TASK"]) - 1
mem = str(int((int(os.environ["SLURM_MEM_PER_NODE"]) / 1024) * 0.9)) + "G"
si.set_global_job_kwargs(n_jobs=num_cpus, total_memory=mem)

# load recording
recording = load_extractor("probe")

# load preprocessing params
preprocessing = params["params"]["preprocessing"]

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
    json.dump(params["params"]["spikesorters"], f)

# extract rest of the params
with open("params.json", "w") as f:
    json.dump(params["params"], f)

# rewrite key
probekey = {**trial, "sortingparams_id": params["sortingparams_id"], "probe_id": probe}
with open("probekey.json", "w") as f:
    json.dump(probekey, f)
