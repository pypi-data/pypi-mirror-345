import json
import argparse
import spikeinterface as si
import spikeinterface.extractors as se
import numpy as np
import os
from pathlib import Path

# extract arguments
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--probe", type=str)
parser.add_argument("-p", "--phy", type=str)
args = parser.parse_args()
probeids = json.loads(args.probe)
phy = Path(args.phy) / "phy"

# load recordings
recordings = []
for i in probeids:
    rec = si.load_extractor(f"preprocessed_{i}")
    recordings.append(rec)

# aggregate recordings
recording = si.aggregate_channels(recordings)
recording.annotate(is_filtered=True)

# load phy sorting
sorting = se.read_phy(str(phy))

# split sortings by probe
for i in probeids:
    newunits = sorting.get_unit_ids()[sorting.get_property("channel_group") == i]
    tmpsort = sorting.select_units(newunits)
    tmpsort.save(folder=f"agreement_{i}")

# TODO: channel groups don't actually align with probeid all the time - need to check the extraction in the main pipeline to see why this is
