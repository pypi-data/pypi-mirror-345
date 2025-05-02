import argparse
import json
import spikeinterface as si
import spikeinterface.comparison as sc
from pathlib import Path

# extract arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--probe", type=str)
parser.add_argument("-s", "--sortinglist", type=str)
args = parser.parse_args()
probekey = json.loads(args.probe)
sortlist = args.sortinglist.split(" ")

# load sorted data
sortdict = {sorter: si.load_extractor(sorter) for sorter in sortlist}

# if only one sorter
if len(sortdict) == 1:
    # just rename sorting folder
    p = Path(list(sortdict.keys())[0])
    p.rename(f"agreement_{probekey['probe_id']}")

# if multiple sorters
else:
    # if all sorters return more than one unit
    if all([len(val.get_unit_ids()) > 0 for val in sortdict.values()]):
        # load agreement matching parameters
        with open("params.json", "r") as f:
            agree_params = json.load(f)["matching"]

        # perform comparison
        mcmp = sc.compare_multiple_sorters(
            sorting_list=list(sortdict.values()),
            name_list=list(sortdict.keys()),
            delta_time=agree_params["delta_time"],
            match_score=agree_params["match_score"],
            spiketrain_mode=agree_params["spiketrain_mode"],
        )

        # extract agreement sorting
        agr = mcmp.get_agreement_sorting(
            minimum_agreement_count=agree_params["minimum_agreement_count"]
        )

        # dump to disk
        agr._is_json_serializable = (
            False  # fixes bug in spikeinterface - can be removed in > 0.99.0
        )
        agr = agr.save(folder=f"agreement_{probekey['probe_id']}")

    # if any are zero, return an empty directory
    else:
        p = Path(f"agreement_{probekey['probe_id']}")
        p.mkdir()

# write probe_id to disk
with open("probe_id.txt", "w") as f:
    f.write(str(probekey["probe_id"]))

# rename recording
preprocessed = Path("preprocessed")
preprocessed.rename(f"preprocessed_{probekey['probe_id']}")

# rename raw recording
p = Path("raw")
newname = f"raw_{probekey['probe_id']}"
p.rename(newname)

del probekey["probe_id"]

# write sortkey to disk
with open("sortkey.json", "w") as f:
    json.dump(probekey, f)
