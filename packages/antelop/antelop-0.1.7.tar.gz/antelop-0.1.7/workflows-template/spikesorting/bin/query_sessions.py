"""
Script run on the hpc inside the datajoint singularity container
Input parameters: primary key for the session we want to spike sort
Function: queries which sessions are left to spike sort, outputs their primary keys
TODO: make it only pull the parameters which haven't already been sorted - will speed up workflow
"""

import argparse
import json
import os
from antelop.load_connection import *

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key")
args = parser.parse_args()

# convert key to dict
key = json.loads(args.key)

# perform all the following in a single transaction
with conn.transaction:
    # fetch session keys
    query = (
        Recording.proj()
        & (
            Recording * (SortingParams & {"manually_sorted": "False"}
            & ProbeInsertion) - SpikeSorting
        )
        & key
    )
    sessions = query.fetch(as_dict=True)
    new_sessions = []

    # get params which are uncomputed
    for session in sessions:
        # fetch params
        query = (
            Recording * (SortingParams & {"manually_sorted": "False"}) - SpikeSorting
            & session
        )
        params = query.proj().fetch(as_dict=True)
        paramslist = []
        for i in params:
            paramslist.append(i["sortingparams_id"])

        # now insert ephys to be in computation
        for param in paramslist:
            SpikeSorting.insert1(
                {
                    **session,
                    "sortingparams_id": param,
                    "phy": "None",
                    "manually_curated": "False",
                    "spikesorting_in_compute": "True",
                },
                allow_direct_insert=True,
            )

        session["paramslist"] = list(paramslist)
        new_sessions.append(session)

os.makedirs("sessions", exist_ok=True)

for i, session in enumerate(new_sessions):
    with open(f"sessions/session_{i}.json", "w") as f:
        json.dump(session, f)
