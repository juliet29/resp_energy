from pathlib import Path
from resp.paths import DynamicPaths
from utils4plans.io import read_pickle


def get_plan_from_subset(file_name: Path = DynamicPaths.rp10, ix: int = 0):
    plans = read_pickle(file_name)
    return plans[ix]
