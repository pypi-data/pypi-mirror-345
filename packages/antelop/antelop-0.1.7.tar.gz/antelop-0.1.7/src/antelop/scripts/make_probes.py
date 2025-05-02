import probeinterface as pi
from probeinterface import ProbeGroup
from probeinterface.plotting import plot_probe_group
import git
from pathlib import Path
import matplotlib.pyplot as plt
import os

def validate_probe(probegroup):
    assert all([probe["ndim"] == 3 for probe in probegroup.to_dict()["probes"]]), "Not 3d"

# probeinterface library
def clone_repo(repo_url, target_dir):
    """Clone a Git repository into the target directory"""
    target_path = Path(target_dir)
    
    if target_path.exists():
        print(f"Directory {target_path} already exists. Pulling latest changes...")
        repo = git.Repo(target_path)
        repo.remotes.origin.pull()
    else:
        print(f"Cloning repository {repo_url} into {target_path}...")
        git.Repo.clone_from(repo_url, target_path)

repo_url = "https://github.com/SpikeInterface/probeinterface_library.git"
target_dir = "../resources/probes"
clone_repo(repo_url, target_dir)

# make probes 3d
probes = Path("../resources/probes")
for probefile in probes.rglob("*.json"):
    probegroup = pi.io.read_probeinterface(probefile)
    if probegroup.ndim == 2:
        newprobegroup = ProbeGroup()
        for probe in probegroup.probes:
            newprobegroup.add_probe(probe.to_3d(axes="xz"))
        validate_probe(newprobegroup)
        pi.io.write_probeinterface(probefile, newprobegroup)

tetrodes = Path("../resources/probes/tetrodes")
tetrodes.mkdir(exist_ok=True)
# tetrodes
n_tetrodes = [1, 2, 4, 8, 16]
for n in n_tetrodes:
    tetrode_path = tetrodes / f"tetrode_{n}"
    tetrode_path.mkdir(exist_ok=True)
    probegroup = ProbeGroup()
    for i in range(n):
        probe = pi.generate_tetrode()
        probe.move([i * 50, 0])
        device_channel_indices = list(range(i * 4, i * 4 + 4))
        probe.set_device_channel_indices(device_channel_indices)
        probegroup.add_probe(probe.to_3d(axes="xz"))
    pi.io.write_probeinterface(tetrode_path / f"tetrode_{n}.json", probegroup)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    plot_probe_group(probegroup, ax=ax)
    plt.savefig(tetrode_path / f"tetrode_{n}.png")