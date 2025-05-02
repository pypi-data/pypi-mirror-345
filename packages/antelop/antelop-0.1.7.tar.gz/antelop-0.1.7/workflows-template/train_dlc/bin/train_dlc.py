import argparse
import deeplabcut
import yaml
import json
from pathlib import Path

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data")
args = parser.parse_args()

p = Path(args.data)
config = p / "config.yaml"

# change project path
with open(config, "r") as f:
    c = yaml.load(f, Loader=yaml.FullLoader)
c["project_path"] = str(p)
with open(config, "w") as f:
    yaml.dump(c, f)

# load compute parameters
compute = p / "compute.json"
with open(compute, "r") as f:
    compute = json.load(f)

# train and evaluate
deeplabcut.create_training_dataset(
    config.resolve(),
    net_type=c["default_net_type"],
    augmenter_type=compute["augmenter"],
)
del compute["augmenter"]
deeplabcut.train_network(config.resolve(), gputouse=0, **compute)
deeplabcut.evaluate_network(config.resolve(), Shuffles=[1], plotting=True)
