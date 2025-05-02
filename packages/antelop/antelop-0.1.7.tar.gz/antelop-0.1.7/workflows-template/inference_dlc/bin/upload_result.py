import argparse
import json
from pathlib import Path
import pandas as pd

from antelop.load_connection import *
from antelop.connection.transaction import transaction_context

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key")
parser.add_argument("-d", "--data")
args = parser.parse_args()

key = json.loads(args.key)
p = Path(args.data)

# load eval results
results = str(list(p.glob("*.h5"))[0])  # chnage to _filtered.h5
df = pd.read_hdf(results)
name = df.columns.get_level_values("scorer").unique()[0]
bodyparts = list(df[name].columns.get_level_values("bodyparts").unique())

# map feature keys to feature names
feature_keys = (Feature & key).proj("feature_name").fetch(as_dict=True)
name_mapping = {}
for f in feature_keys:
    if f["feature_name"] in bodyparts:
        name_mapping[f["feature_name"]] = f["feature_id"]

# map animal ids to feature ids
selfkey = (Self & key).proj().fetch1()
objects = (Object & selfkey).proj("animal_id").fetch()
animal_mapping = {}
for a in objects:
    animal_mapping[a["feature_id"]] = a["animal_id"]

# get timestamps
timestamps = (Video & key).fetch1("timestamps")

# insert each feature
with transaction_context(conn):
    for feature_name, feature_id in name_mapping.items():
        data = df[name][feature_name].values
        animal_id = animal_mapping[feature_id]
        prim = {
            **selfkey,
            "video_id": key["video_id"],
            "dlcmodel_id": key["dlcmodel_id"],
            "feature_id": feature_id,
            "animal_id": animal_id,
            "behaviourrig_id": key["behaviourrig_id"],
        }
        insert_dict = {
            **prim,
            "timestamps": timestamps,
            "data": data,
            "kinematics_name": feature_name,
        }
        Kinematics.insert1(insert_dict, allow_direct_insert=True)
