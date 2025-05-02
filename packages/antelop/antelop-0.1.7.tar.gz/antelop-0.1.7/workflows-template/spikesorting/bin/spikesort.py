import argparse
import json
from spikeinterface import load_extractor
from spikeinterface.sorters import run_sorter_local
import spikeinterface.sorters as ss  # remove
import spikeinterface as si
import os

# this __name__ protection help in some case with multiprocessing (for instance HS2)
if __name__ == "__main__":
    # extract arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sorter", type=str)
    args = parser.parse_args()
    sorter = args.sorter

    # use scratch space for sorting
    scratch = os.environ["SLURM_SCRATCH_DIR"]

    # load params
    with open("spikesorters.json") as f:
        params = json.load(f)[sorter]

    # set global job kwargs
    if sorter == "pykilosort":
        num_gpus = int(os.environ["SLURM_GPUS"])
        mem = str(int((int(os.environ["SLURM_MEM_PER_NODE"]) / 1024) * 0.9)) + "G"
        si.set_global_job_kwargs(n_jobs=num_gpus, chunk_memory=mem)

        params["n_jobs"] = num_gpus

    elif sorter == "mountainsort5":
        num_cpus = int(os.environ["SLURM_CPUS_PER_TASK"])
        mem = str(int((int(os.environ["SLURM_MEM_PER_NODE"]) / 1024) * 0.9)) + "G"
        si.set_global_job_kwargs(n_jobs=num_cpus, total_memory=mem)

        params["filter"] = False

    elif sorter == "spykingcircus2":
        num_cpus = int(os.environ["SLURM_CPUS_PER_TASK"])
        mem = str(int((int(os.environ["SLURM_MEM_PER_NODE"]) / 1024) * 0.75)) + "G"
        si.set_global_job_kwargs(n_jobs=num_cpus, total_memory=mem)

        params["job_kwargs"] = {"n_jobs": num_cpus}
        params["shared_memory"] = False
        params["apply_preprocessing"] = False

        if "registration" in params:
            del params["registration"]

    # load recording in container
    recording = load_extractor("preprocessed")

    # run spike sorter
    sorting = run_sorter_local(
        sorter, recording, output_folder=f"{scratch}/sorting", **params
    )

    # save
    sorting.save(folder=sorter)
