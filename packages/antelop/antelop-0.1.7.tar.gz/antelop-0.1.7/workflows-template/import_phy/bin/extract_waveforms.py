import argparse
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
import spikeinterface as si
import decimal
from spikeinterface.postprocessing import (
    compute_spike_amplitudes,
    compute_principal_components,
    compute_unit_locations,
)
from spikeinterface.exporters import export_to_phy
import spikeinterface.preprocessing as spre
from scipy.spatial.transform import Rotation as R
import gc
from multiprocessing import Pool
import dask.dataframe as dd
import pyarrow as pa
import pickle  # Add this import for serialization


if __name__ == "__main__":

    # extract arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sortkey", type=str)
    parser.add_argument("-p", "--probeid", type=str)
    args = parser.parse_args()
    sortkey = json.loads(args.sortkey)
    probe = int(args.probeid)

    # load paramaeters
    with open("params.json") as f:
        params = json.load(f)

    # use scratch space for sorting
    scratch = Path(os.environ["SLURM_SCRATCH_DIR"])

    # set global job kwargs
    num_cpus = int(os.environ["SLURM_CPUS_PER_TASK"]) - 1
    mem = str(int((int(os.environ["SLURM_MEM_PER_NODE"]) / 1024) * 0.9)) + "G"
    si.set_global_job_kwargs(n_jobs=num_cpus, chunk_size=50000)

    channel_chunk_size = 1
    sample_chunk_size = 50000

    # first make subfolder
    p = Path(f"data_{probe}")
    p.mkdir(exist_ok=True)

    # load recording objects
    sorting = si.load_extractor(f"agreement_{probe}")
    recording = si.load_extractor(f"preprocessed_{probe}")
    raw = si.load_extractor(f"raw_{probe}")
    sorting.register_recording(recording)

    # annotations for later
    sampling_frequency = recording.get_sampling_frequency()
    ms_before = int(params["waveform"]["ms_before"])
    ms_after = int(params["waveform"]["ms_after"])
    lfp_sampling_frequency = int(params["lfp"]["sample_rate"])
    probecoords = params["probecoords"]

    # make rotation and translation arrays
    angles = [
        float(probecoords["yaw"]),
        float(probecoords["pitch"]),
        float(probecoords["roll"]),
    ]
    rotation = R.from_euler("zyx", angles, degrees=True)
    rot_matrix = rotation.as_matrix()  # makes rotation matrix from euler angles
    translation = np.array(
        [
            float(probecoords["ml_coord"]),
            float(probecoords["ap_coord"]),
            float(probecoords["total_dv"]),
        ]
    )

    print("Extracting waveforms...")
    # extract all waveforms
    we = si.extract_waveforms(
        recording=recording,
        sorting=sorting,
        folder=f"{scratch}/waveforms_{str(probe)}",
        ms_before=params["waveform"]["ms_before"],
        ms_after=params["waveform"]["ms_after"],
        return_scaled=True,
        max_spikes_per_unit=None,
        sparse=True,
        method="radius",
        radius_um=100,
        chunk_size=50000,
    )

    # make channel dataframe using Dask
    if recording.get_probe().ndim == 2:
        df = recording.get_probe().to_3d().to_dataframe()
    elif recording.get_probe().ndim == 3:
        df = recording.get_probe().to_dataframe()
    coords = df[["x", "y", "z"]].to_numpy()
    rot_coords = rot_matrix @ coords.T  # performs rotation about origin
    trans_coords = rot_coords + translation[:, np.newaxis]  # performs translation
    trans_coords = np.vectorize(decimal.Decimal.from_float, otypes="O")(trans_coords)
    trans_coords = np.vectorize(lambda x: x.quantize(decimal.Decimal("1")), otypes="O")(
        trans_coords
    )

    # now add data to dataframe
    channel_id = np.array(recording.get_channel_ids())
    channel_index = np.arange(len(channel_id))
    df = pd.DataFrame()
    length = len(channel_id)
    df["experimenter"] = np.full(length, fill_value=sortkey["experimenter"])
    df["experiment_id"] = np.full(length, fill_value=sortkey["experiment_id"])
    df["animal_id"] = np.full(length, fill_value=sortkey["animal_id"])
    df["session_id"] = np.full(length, fill_value=sortkey["session_id"])
    df["sortingparams_id"] = np.full(length, fill_value=sortkey["sortingparams_id"])
    df["probe_id"] = np.full(length, fill_value=int(probe))
    df["channel_id"] = channel_index
    df["ap_coord"] = trans_coords[1].astype(np.float32)
    df["ml_coord"] = trans_coords[0].astype(np.float32)
    df["dv_coord"] = trans_coords[2].astype(np.float32)

    # convert to Dask DataFrame and write to Parquet
    ddf = dd.from_pandas(df, npartitions=1)
    ddf.to_parquet(f"data_{probe}/channel.parquet", engine="pyarrow", write_index=False)
    del df, ddf

    # make unit dataframe using Dask
    coords = compute_unit_locations(we)
    rot_coords = rot_matrix @ coords.T  # performs rotation about origin
    trans_coords = rot_coords + translation[:, np.newaxis]  # performs translation
    trans_coords = np.vectorize(decimal.Decimal.from_float, otypes="O")(trans_coords)
    trans_coords = np.vectorize(lambda x: x.quantize(decimal.Decimal("1")), otypes="O")(
        trans_coords
    )

    # now add data to dataframe
    unit_id = np.array(sorting.get_unit_ids())
    df = pd.DataFrame()
    length = len(unit_id)
    df["experimenter"] = np.full(length, fill_value=sortkey["experimenter"])
    df["experiment_id"] = np.full(length, fill_value=sortkey["experiment_id"])
    df["animal_id"] = np.full(length, fill_value=sortkey["animal_id"])
    df["session_id"] = np.full(length, fill_value=sortkey["session_id"])
    df["sortingparams_id"] = np.full(length, fill_value=sortkey["sortingparams_id"])
    df["probe_id"] = np.full(length, fill_value=int(probe))
    df["unit_id"] = unit_id
    df["ap_coord"] = trans_coords[1].astype(np.float32)
    df["ml_coord"] = trans_coords[0].astype(np.float32)
    df["dv_coord"] = trans_coords[2].astype(np.float32)

    # convert to Dask DataFrame and write to Parquet
    ddf = dd.from_pandas(df, npartitions=1)
    ddf.to_parquet(f"data_{probe}/unit.parquet", engine="pyarrow", write_index=False)
    del df, ddf

    # extract LFPs
    print("Extracting LFPs...")
    lfp = spre.bandpass_filter(raw, params["lfp"]["min_freq"], params["lfp"]["max_freq"])
    lfp = spre.resample(lfp, lfp_sampling_frequency)

    num_channels = len(channel_id)
    lfp_path = f"data_{probe}/lfp.parquet"
    lfp_samples = lfp.get_total_samples()

    indices = list(range(0, lfp_samples, sample_chunk_size))

    schema = pa.schema([
        ('experimenter', pa.string()),
        ('experiment_id', pa.int32()),
        ('animal_id', pa.int32()),
        ('session_id', pa.int32()),
        ('sortingparams_id', pa.int32()),
        ('probe_id', pa.int32()),
        ('channel_id', pa.int32()),
        ('lfp', pa.binary()),  # Changed from pa.string() to pa.binary()
        ('lfp_sample_rate', pa.int32())
    ])

    def process_chunk(args):
        start, end, output_file = args
        print(f"Processing chunk {start} to {end}...")
        traces = np.empty((lfp_samples, end - start), dtype=np.float32)
        for idx0, idx1 in zip(indices[:-1], indices[1:]):
            traces[idx0:idx1] = lfp.get_traces(start_frame=idx0, end_frame=idx1, channel_ids=channel_id[start:end], return_scaled=True)

        lfp_series = pd.Series(np.hsplit(traces, traces.shape[1]), name="lfp")
        lfp_series = lfp_series.apply(np.squeeze)

        # Convert LFP traces to pickled strings before saving
        lfp_series = lfp_series.apply(lambda x: pickle.dumps(x))

        length = len(lfp_series)  # Should match the number of extracted channels

        df_chunk = pd.DataFrame({
            "experimenter": np.full(length, fill_value=sortkey["experimenter"]),
            "experiment_id": np.full(length, fill_value=sortkey["experiment_id"]),
            "animal_id": np.full(length, fill_value=sortkey["animal_id"]),
            "session_id": np.full(length, fill_value=sortkey["session_id"]),
            "sortingparams_id": np.full(length, fill_value=sortkey["sortingparams_id"]),
            "probe_id": np.full(length, fill_value=int(probe)),
            "channel_id": channel_index[start:end],
            "lfp": lfp_series,
            "lfp_sample_rate": np.full(length, fill_value=lfp_sampling_frequency),
        })

        df_chunk.to_parquet(output_file, engine="pyarrow", index=False, schema=schema)
        del df_chunk, traces, lfp_series
        gc.collect()

    # process in parallel using multiprocessing
    (scratch / 'lfp').mkdir(exist_ok=True)
    output_files = [os.path.join(scratch / 'lfp', f'part-{i}.parquet') for i in range(0, num_channels, channel_chunk_size)]
    args = [(i, min(i + channel_chunk_size, num_channels), output_files[i // channel_chunk_size]) for i in range(0, num_channels, channel_chunk_size)]

    with Pool(processes=num_cpus) as pool:
        pool.map(process_chunk, args)

    dask_combined = dd.read_parquet(scratch / 'lfp', engine="pyarrow")
    dask_combined.to_parquet(lfp_path, engine="pyarrow", write_index=False, schema=schema)

    # extract spiketrains
    sample_rate = recording.get_sampling_frequency()
    spiketrains = []
    for i in unit_id:
        spiketrains.append(sorting.get_unit_spike_train(unit_id=i) / sample_rate)
    spiketrain_series = pd.Series(spiketrains, name="spiketrain")

    # Convert spiketrains to pickled strings before saving
    spiketrain_series = spiketrain_series.apply(lambda x: pickle.dumps(x))

    schema = pa.schema([
        ('experimenter', pa.string()),
        ('experiment_id', pa.int32()),
        ('animal_id', pa.int32()),
        ('session_id', pa.int32()),
        ('sortingparams_id', pa.int32()),
        ('probe_id', pa.int32()),
        ('unit_id', pa.int32()),
        ('spiketrain', pa.binary()),  # Changed from pa.string() to pa.binary()
    ])

    # make spiketrain dataframe
    df = pd.DataFrame()
    length = len(unit_id)
    df["experimenter"] = np.full(length, fill_value=sortkey["experimenter"])
    df["experiment_id"] = np.full(length, fill_value=sortkey["experiment_id"])
    df["animal_id"] = np.full(length, fill_value=sortkey["animal_id"])
    df["session_id"] = np.full(length, fill_value=sortkey["session_id"])
    df["sortingparams_id"] = np.full(length, fill_value=sortkey["sortingparams_id"])
    df["probe_id"] = np.full(length, fill_value=int(probe))
    df["unit_id"] = unit_id
    df["spiketrain"] = spiketrain_series

    # convert to Dask DataFrame and write to Parquet
    ddf = dd.from_pandas(df, npartitions=1)
    ddf.to_parquet(f"data_{probe}/spiketrain.parquet", engine="pyarrow", write_index=False, schema=schema)
    del df, ddf

    # make subfolder
    p = Path(f"data_{probe}/waveforms")
    p.mkdir(exist_ok=True)

    waveform_path = f"data_{probe}/waveforms.parquet"
    scratch_waveform_path = scratch / 'waveforms'
    scratch_waveform_path.mkdir(exist_ok=True)

    schema = pa.schema([
        ('experimenter', pa.string()),
        ('experiment_id', pa.int32()),
        ('animal_id', pa.int32()),
        ('session_id', pa.int32()),
        ('sortingparams_id', pa.int32()),
        ('probe_id', pa.int32()),
        ('unit_id', pa.int32()),
        ('channel_id', pa.int32()),
        ('waveform', pa.binary()),  # Changed from pa.string() to pa.binary()
        ('waveform_sample_rate', pa.int32()),
        ('ms_before', pa.int32()),
        ('ms_after', pa.int32()),
        ('wave_shape', pa.list_(pa.int32()))
    ])

    def process_waveforms(args):
        unit, output_file = args
        """Extract waveforms for a unit and create a DataFrame."""
        waveforms = we.get_waveforms(unit)

        # sparse so need to get channel ids
        unit_channel_ids = we.sparsity.unit_id_to_channel_ids[unit]
        unit_channel_indexes = np.where(np.isin(channel_id, unit_channel_ids))[0]

        # split array down channel axis
        wave_series = pd.Series(
            np.split(waveforms, waveforms.shape[2], axis=2), name="waveform"
        )
        del waveforms
        wave_series = wave_series.apply(np.squeeze)
        wave_shape = wave_series.apply(lambda x: x.shape)
        wave_series = wave_series.apply(lambda x: x.flatten())

        # Convert waveforms to pickled strings before saving
        wave_series = wave_series.apply(lambda x: pickle.dumps(x))

        # make waveform dataframe
        df = pd.DataFrame()
        length = len(unit_channel_ids)
        df["experimenter"] = np.full(length, fill_value=sortkey["experimenter"])
        df["experiment_id"] = np.full(length, fill_value=sortkey["experiment_id"])
        df["animal_id"] = np.full(length, fill_value=sortkey["animal_id"])
        df["session_id"] = np.full(length, fill_value=sortkey["session_id"])
        df["sortingparams_id"] = np.full(length, fill_value=sortkey["sortingparams_id"])
        df["probe_id"] = np.full(length, fill_value=int(probe))
        df["unit_id"] = np.full(length, fill_value=int(unit))
        df["channel_id"] = unit_channel_indexes
        df["waveform"] = wave_series
        df["waveform_sample_rate"] = np.full(length, sampling_frequency)
        df["ms_before"] = np.full(length, fill_value=ms_before)
        df["ms_after"] = np.full(length, fill_value=ms_after)
        df["wave_shape"] = wave_shape

        df.to_parquet(output_file, engine="pyarrow", index=False, schema=schema)
        del df, wave_series
        gc.collect()

    # process in parallel using multiprocessing
    if len(unit_id) > 0:
        output_files = [os.path.join(scratch_waveform_path, f'part-{i}.parquet') for i in unit_id]
        args = [(unit, output_files[i]) for i, unit in enumerate(unit_id)]

        with Pool(processes=num_cpus) as pool:
            pool.map(process_waveforms, args)

        dask_combined = dd.read_parquet(scratch_waveform_path, engine="pyarrow")
        dask_combined.to_parquet(waveform_path, engine="pyarrow", write_index=False, schema=schema)