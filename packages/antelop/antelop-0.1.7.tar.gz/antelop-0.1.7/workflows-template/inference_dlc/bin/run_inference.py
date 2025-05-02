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
videos = list((p / "inference").glob("*"))  # actually just one but needs to be list
videos = [str(v) for v in videos]
Path("result").mkdir()

# change project path
with open(config, "r") as f:
    c = yaml.load(f, Loader=yaml.FullLoader)
c["project_path"] = str(p)
with open(config, "w") as f:
    yaml.dump(c, f)

# run inference
deeplabcut.analyze_videos(config, videos, destfolder="result", gputouse=0)
deeplabcut.filterpredictions(config, videos, destfolder="result")
