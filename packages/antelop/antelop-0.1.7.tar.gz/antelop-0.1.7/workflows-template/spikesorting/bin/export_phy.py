import argparse
import json
import os
from pathlib import Path
import numpy as np
import spikeinterface as si
from spikeinterface.postprocessing import (
    compute_spike_amplitudes,
    compute_principal_components,
)
from spikeinterface.exporters import export_to_phy
import spikeinterface.preprocessing as spre

# extract arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--probe_ids", type=str)
args = parser.parse_args()
probeids = sorted(json.loads(args.probe_ids))

# set global job kwargs
num_cpus = int(os.environ["SLURM_CPUS_PER_TASK"]) - 1
mem = str(int((int(os.environ["SLURM_MEM_PER_NODE"]) / 1024) * 0.9)) + "G"
si.set_global_job_kwargs(n_jobs=num_cpus, total_memory=mem)

# use scratch space for sorting
scratch = os.environ["SLURM_SCRATCH_DIR"]

# load recordings
recordings = []
for i in probeids:
    rec = si.load_extractor(f"preprocessed_{i}")
    recordings.append(rec)

# aggregate recordings
recording = si.aggregate_channels(recordings)
recording.annotate(is_filtered=True)

# load sortings
sortings = []
for i in probeids:
    sort = si.load_extractor(f"agreement_{i}")
    sortings.append(sort)

# aggregate sortings
unit_groups = []
for sorting, group in zip(sortings, probeids):
    num_units = sorting.get_unit_ids().size
    unit_groups.extend([group] * num_units)
unit_groups = np.array(unit_groups)

aggregate_sorting = si.aggregate_units(sortings)
aggregate_sorting.set_property(key="group", values=unit_groups)
aggregate_sorting.register_recording(recording)

# extract waveforms
# note this extracts a subset for manual curation
we = si.extract_waveforms(
    recording=recording,
    sorting=aggregate_sorting,
    folder=f"{scratch}/waveforms",
    return_scaled=True,
    sparse=True,
    sparsity_temp_folder=f"{scratch}/tmp_waveforms",
    method="by_property",
    by_property="group",
)

# compute metrics
_ = compute_spike_amplitudes(waveform_extractor=we)
_ = compute_principal_components(
    waveform_extractor=we, n_components=3, mode="by_channel_global"
)

# export to phy
export_to_phy(
    waveform_extractor=we, output_folder="phy", use_relative_path=True, peak_sign="both"
)
