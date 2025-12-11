from utils4plans.paths import StaticPaths
import pyprojroot


BASE_PATH = pyprojroot.find_root(pyprojroot.has_dir(".git"))
static_paths = StaticPaths("", BASE_PATH)


# wonder if should separate file names..
class Constants:
    processed_geom = "geom.json"


class DynamicPaths:
    resplan_data = static_paths.inputs / "ResPlan.pkl"
    resplan_subsets = static_paths.temp / "resplan_subsets"
    rp10 = resplan_subsets / "rp10.pkl"
    processed_plan_geoms = static_paths.plans / "processed"
