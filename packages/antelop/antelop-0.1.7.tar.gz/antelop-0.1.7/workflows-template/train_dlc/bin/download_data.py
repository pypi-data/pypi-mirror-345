import argparse
import yaml
import json
import zipfile
from pathlib import Path

from antelop.load_connection import *
from antelop.connection.transaction import transaction_context

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key")
args = parser.parse_args()

# convert key to dict
key = json.loads(args.key)

# check that the key is correct
if "behaviourrig_deleted" in key:
    key.pop("behaviourrig_deleted")
assert set(list(key.keys())) == set(
    ["experimenter", "experiment_id", "behaviourrig_id", "dlcmodel_id"]
)
p = Path("dlc")
p.mkdir()
(p / "dlc-models").mkdir()
(p / "labeled-data").mkdir()
(p / "training-datasets").mkdir()
(p / "videos").mkdir()

# download data
with transaction_context(conn):
    data = (LabelledFrames & key).fetch1()
    LabelledFrames.update1({**key, "labelledframes_in_compute": "True"})

# write config to file
config = data["dlcparams"]["config"]
config["project_path"] = str(p.resolve())
with open(p / "config.yaml", "w") as f:
    yaml.dump(config, f)

compute = data["dlcparams"]["compute"]
with open(p / "compute.json", "w") as f:
    json.dump(compute, f)

# unzip data
videos = data["labelled_frames"]
with zipfile.ZipFile(videos, "r") as zip_ref:
    zip_ref.extractall(p / "labeled-data")
