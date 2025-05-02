import argparse
import json
import sys
import datajoint as dj
import pandas as pd
import toml
from pathlib import Path
from antelop.load_connection import *
from decimal import Decimal
import numpy as np
import pickle

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--sortkey")
parser.add_argument("-p", "--probe_ids")
parser.add_argument("-s", "--hashkey")
args = parser.parse_args()
sortkey = json.loads(args.sortkey)
probe_ids = sorted(json.loads(args.probe_ids))
hashkey = str(args.hashkey)

def quantize_column(df, column):
    """Quantize a column to integers."""
    df[column] = df[column].apply(lambda x: Decimal(x).quantize(Decimal("1")))
    return df

def process_parquet_files(folder_path, process_function):
    """Process each Parquet file in a folder."""
    folder = Path(folder_path)
    for part_file in folder.glob("*.parquet"):
        df = pd.read_parquet(part_file)
        process_function(df)

# perform all the following in a single transaction
with conn.transaction:
    # first, update spikesorting table
    print("Updating SpikeSorting table...")
    spikesorting = {
        **sortkey,
        "phy": hashkey,
        "manually_curated": "False",
        "spikesorting_in_compute": "False",
    }
    SpikeSorting.update1(spikesorting)
    print("SpikeSorting table updated.")

    # now loop through probe_ids
    for probe in probe_ids:
        # Insert probe
        print(f"Inserting probe {probe}...")
        Probe.insert1(
            {**sortkey, "probe_id": int(probe)},
            allow_direct_insert=True,
            skip_duplicates=True
        )
        print(f"Probe {probe} inserted.")

        # Insert channels
        print(f"Loading and inserting channels for probe {probe}...")
        channel_path = f"data_{probe}/channel.parquet"

        def process_channel(df):
            df = quantize_column(df, 'ap_coord')
            df = quantize_column(df, 'ml_coord')
            df = quantize_column(df, 'dv_coord')
            Channel.insert(df.to_dict(orient="records"), allow_direct_insert=True, skip_duplicates=True)

        process_parquet_files(channel_path, process_channel)
        print(f"Channels for probe {probe} inserted.")

        # Insert units
        print(f"Loading and inserting units for probe {probe}...")
        unit_path = f"data_{probe}/unit.parquet"

        def process_unit(df):
            df = quantize_column(df, 'ap_coord')
            df = quantize_column(df, 'ml_coord')
            df = quantize_column(df, 'dv_coord')
            Unit.insert(df.to_dict(orient="records"), allow_direct_insert=True, skip_duplicates=True)

        process_parquet_files(unit_path, process_unit)
        print(f"Units for probe {probe} inserted.")

        # Insert LFPs
        print(f"Loading and inserting LFPs for probe {probe}...")
        lfp_path = f"data_{probe}/lfp.parquet"

        def process_lfp(df):
            df['lfp'] = df['lfp'].apply(lambda x: pickle.loads(x) if isinstance(x, bytes) else x)
            LFP.insert(df.to_dict(orient="records"), allow_direct_insert=True, skip_duplicates=True)

        process_parquet_files(lfp_path, process_lfp)
        print(f"LFPs for probe {probe} inserted.")

        # Insert spiketrains
        print(f"Loading and inserting SpikeTrains for probe {probe}...")
        spiketrain_path = f"data_{probe}/spiketrain.parquet"

        def process_spiketrain(df):
            df['spiketrain'] = df['spiketrain'].apply(lambda x: pickle.loads(x) if isinstance(x, bytes) else x)
            SpikeTrain.insert(df.to_dict(orient="records"), allow_direct_insert=True, skip_duplicates=True)

        process_parquet_files(spiketrain_path, process_spiketrain)
        print(f"SpikeTrains for probe {probe} inserted.")

        # Insert waveforms
        print(f"Loading and inserting Waveforms for probe {probe}...")
        waveform_path = f"data_{probe}/waveforms.parquet"

        def process_waveform(df):
            df['waveform'] = df.apply(
                lambda row: pickle.loads(row['waveform']).reshape(row['wave_shape']),
                axis=1
            )
            del df['wave_shape']
            Waveform.insert(df.to_dict(orient="records"), allow_direct_insert=True, skip_duplicates=True)

        if Path(waveform_path).exists():
            process_parquet_files(waveform_path, process_waveform)
            print(f"Waveforms for probe {probe} inserted.")
        else:
            print(f"Waveform file for probe {probe} does not exist. Skipping insertion.")

        # Update session duration
        print(f"Finding maximum timestamp from LFP data for probe {probe}...")
        lfp_path = f"data_{probe}/lfp.parquet"

        def find_max_lfp_timestamp(part_file):
            """Find the maximum timestamp in a single LFP Parquet file."""
            df = pd.read_parquet(part_file)
            # Assuming LFP timestamps are derived from the length of the LFP array
            df['max_timestamp'] = df.apply(
                lambda row: len(pickle.loads(row['lfp'])) / row['lfp_sample_rate']
                if isinstance(row['lfp'], bytes) else len(row['lfp']) / row['lfp_sample_rate'],
                axis=1
            )
            return df['max_timestamp'].max()

        # Aggregate maximum timestamps across all part files
        max_timestamps = []
        for part_file in Path(lfp_path).glob("*.parquet"):
            max_timestamps.append(find_max_lfp_timestamp(part_file))

        max_timestamp = max(max_timestamps)

        # Update session duration in the database
        session_key = {k: v for k, v in sortkey.items() if k in ['experimenter', 'experiment_id', 'session_id']}
        current_max = (Session & sortkey).fetch1('session_duration')
        if current_max is None or max_timestamp > current_max:
            Session.update1({**session_key, 'session_duration': max_timestamp})