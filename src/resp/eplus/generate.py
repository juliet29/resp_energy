from replan2eplus.ezcase.ez import EZ
from replan2eplus.ops.subsurfaces.user_interfaces import EdgeGroup, SubsurfaceInputs
from replan2eplus.ops.zones.user_interface import Room
from pathlib import Path
from resp.config import WEATHER_FILE, ANALYSIS_PERIOD, INPUT_CAMPAIGN_NAME
from replan2eplus.campaigns.decorator2 import make_experimental_campaign
from resp.eplus.campaign import campaign_defn, campaign_data
from resp.paths import DynamicPaths
from resp.eplus.interfaces import make_details


@make_experimental_campaign(
    defn_dict=campaign_defn,
    data_dict=campaign_data,
    root_path=DynamicPaths.campaigns,
    campaign_name=INPUT_CAMPAIGN_NAME,
)
def generate_experiments(
    rooms: list[Room], edge_groups: list[EdgeGroup], out_path: Path
):
    case = EZ(
        epw_path=WEATHER_FILE, output_path=out_path, analysis_period=ANALYSIS_PERIOD
    )
    case.add_zones(rooms)

    subsurface_inputs = SubsurfaceInputs(
        edge_groups, make_details()  # pyright: ignore[reportArgumentType]
    )
    case.add_subsurfaces(subsurface_inputs)
    case.add_constructions()
    case.add_airflow_network()
    case.save_and_run(
        run=False, analysis_period=ANALYSIS_PERIOD
    )  # TODO: shouldlnt have to specify twice in different places.
