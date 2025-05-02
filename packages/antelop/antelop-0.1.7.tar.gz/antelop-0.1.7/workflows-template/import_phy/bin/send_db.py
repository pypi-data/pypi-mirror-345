import argparse
import json
import pandas as pd
from pathlib import Path
from antelop.load_connection import *
from antelop.connection.transaction import transaction_context

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--sortkey")
parser.add_argument("-p", "--probe_ids")
parser.add_argument("-s", "--hashkey")
args = parser.parse_args()
sortkey = json.loads(args.sortkey)
probe_ids = sorted(json.loads(args.probe_ids))
hashkey = str(args.hashkey)

# perform all the following in a single transaction
with transaction_context(conn):
    # first, update spikesorting table
    spikesorting = {
        **sortkey,
        "manually_curated": "True",
        "spikesorting_deleted": "False",
        "spikesorting_in_compute": "False",
    }
    SpikeSorting.update1(spikesorting)

    # now loop through probe_ids
    for probe in probe_ids:
        # load and insert units
        df = pd.read_pickle(f"data_{str(probe)}/unit.pkl")
        Unit.insert(df, allow_direct_insert=True)

        # load and insert spiketrains
        df = pd.read_pickle(f"data_{str(probe)}/spiketrain.pkl")
        SpikeTrain.insert(df, allow_direct_insert=True)

        # loop through waveforms, load and insert
        wavedir = Path(f"data_{str(probe)}/waveforms")

        for waveform in wavedir.iterdir():
            df = pd.read_pickle(str(waveform))
            Waveform.insert(df, allow_direct_insert=True)
