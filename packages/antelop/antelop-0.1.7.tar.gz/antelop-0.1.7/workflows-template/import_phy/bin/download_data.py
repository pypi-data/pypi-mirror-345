import argparse
import json
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
    ["experimenter", "experiment_id", "animal_id", "session_id", "sortingparams_id"]
)

# make sure only pull non-deleted and not in computation keys
key["spikesorting_deleted"] = "False"

# do the following in a transaction
with transaction_context(conn):
    # pull spikesorting metadata
    query = SpikeSorting & key
    spikesorting = query.fetch1()

    # check it's not currently in computation or deleted
    assert spikesorting["spikesorting_in_compute"] == "False"

    # delete all sorting data
    query = Unit & key
    query.delete(safemode=False, force=True)

    # update spikesorting to be in compute
    del spikesorting["spikesorting_in_compute"]
    del spikesorting["manually_curated"]
    SpikeSorting.update1(
        {**key, "spikesorting_in_compute": "True", "manually_curated": "True"}
    )

# write hash
hashkey = spikesorting["phy"]
with open("hashkey.txt", "w") as f:
    f.write(hashkey)

# download raw data
query = Recording & key
query.fetch1(download_path="recording")

# fetch equip_type
query = Recording & key
equip_type = query.fetch1("ephys_acquisition")
with open("equip.txt", "w") as f:
    f.write(equip_type)

# fetch probe
query = ProbeGeometry * ProbeInsertion * Recording.proj() & key
probefile = query.fetch1("probe")
with open("probe.json", "w") as f:
    json.dump(probefile, f)

# add device_channel_mapping
probe = pi.read_probeinterface("probe.json")
device_channel_mapping = (Recording & session).fetch1('device_channel_mapping')
if device_channel_mapping is not None:
    device_channel_mapping = np.array(json.loads(device_channel_mapping))
else:
    device_channel_mapping = np.arange(probe.get_contact_count())
probe.set_global_device_channel_indices(device_channel_mapping)
pi.write_probeinterface("probe.json", probe)

# animal key
animal = {
    akey: val
    for akey, val in key.items()
    if akey in ["experimenter", "experiment_id", "animal_id"]
}

# fetch probe transformation
query = ProbeInsertion * Recording.proj() & animal
probecoords = query.fetch(as_dict=True)[0]  # needs fixing
probecoords = {
    pkey: float(val)
    for pkey, val in probecoords.items()
    if pkey in ["yaw", "pitch", "roll", "ap_coord", "ml_coord", "dv_coord"]
}

# need to also sum over DV increment for all trials
trial_timestamp = (Session & key).fetch1("session_timestamp")
query = (
    Session * Recording & animal & f'session_timestamp <= "{str(trial_timestamp)}"'
).proj("session_timestamp", "probe_dv_increment")  # all increments less than timestamp
total_dv = float(query.fetch("probe_dv_increment").sum()) + probecoords["dv_coord"]
probecoords["total_dv"] = float(total_dv)

# fetch params
query = SortingParams & key
param = query.fetch1("params")
param["probecoords"] = probecoords
with open("params.json", "w") as f:
    json.dump(param, f)
