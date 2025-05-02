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

# perform all the following in a single transaction
with transaction_context(conn):
    # fetch trial keys
    query = World * DLCModel * Video.proj() - Kinematics.proj() & key
    worlds = query.proj().fetch(as_dict=True)

# write data to disk
with open("data.txt", "w") as f:
    for world in worlds:
        json.dump(world, f)
        f.write("\n")
