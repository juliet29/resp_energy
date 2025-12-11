from pathlib import Path
from resp.paths import DynamicPaths
from utils4plans.io import read_pickle, write_pickle


def save_subset(file_name: Path, n: int = 10):
    plans = read_pickle(
        DynamicPaths.resplan_data
    )  # this becomes its own function in access
    examples = plans[0:n]
    write_pickle(examples, file_name, OVERWRITE=True)
