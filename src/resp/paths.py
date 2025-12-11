from typing import Literal
from utils4plans.paths import StaticPaths
import pyprojroot


BASE_PATH = pyprojroot.find_root(pyprojroot.has_dir(".git"))
static_paths = StaticPaths("", BASE_PATH)


# wonder if should separate file names..
ResPlanIds = Literal["16969", "14433", "14926", "3467", "14877", "17054"]
InputCampaignNames = Literal["zones_only"]
OutputCampaignNames = Literal["251211_zones_only"]


class Constants:
    processed_geom = "geom.json"
    idf_name = "out.idf"  # TODO: get from ep_paths.. same with sql..
    metadata = "metadata.toml"
    definition = "defn.toml"


class DynamicPaths:
    resplan_data = static_paths.inputs / "ResPlan.pkl"
    resplan_subsets = static_paths.temp / "resplan_subsets"
    rp10 = resplan_subsets / "rp10.pkl"
    processed_plan_geoms = static_paths.plans / "processed"
    weather_pa2024 = (
        static_paths.inputs / "weather" / "pa2024" / "CA_PALO-ALTO-AP_724937_24.EPW"
    )
    campaigns = static_paths.models / "campaigns"
    # TODO: can make this cleaner!
    #
    #


# ep_paths.idf_name
