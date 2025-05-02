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
assert set(list(key.keys())) == set(
    [
        "experimenter",
        "experiment_id",
        "behaviourrig_id",
        "dlcmodel_id",
        "session_id",
        "video_id",
    ]
)

# make necessary folders
p = Path("dlc")
p.mkdir()
(p / "dlc-models").mkdir()
(p / "labeled-data").mkdir()
(p / "training-datasets").mkdir()
(p / "videos").mkdir()
(p / "inference").mkdir()

# download videos and model and config
with transaction_context(conn):
    conf, model = (DLCModel * LabelledFrames & key).fetch1(
        "dlcparams", "dlcmodel"
    )
    video = (Video & key).fetch1("video", download_path=p / "inference")

# write config to file
config = conf["config"]
config["project_path"] = str(p.resolve())
with open(p / "config.yaml", "w") as f:
    yaml.dump(config, f)

# unzip model
with zipfile.ZipFile(model, "r") as zip_ref:
    zip_ref.extractall(p / "dlc-models")
