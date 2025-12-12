from typing import get_args
from replan2eplus.campaigns.decorator2 import DataDict, DefinitionDict
from replan2eplus.ezcase.ez import Room
from replan2eplus.ops.subsurfaces.user_interfaces import EdgeGroup
from resp.eplus.interfaces import read_edges, read_geoms_to_ezcase_rooms
from resp.paths import ResPlanIds


def process_resplan_ids():
    ids = get_args(ResPlanIds)
    return [str(i) for i in ids]


def generate_rooms() -> dict[str, list[Room]]:
    return {v: read_geoms_to_ezcase_rooms(v) for v in get_args(ResPlanIds)}


def generate_edge_groups() -> dict[str, list[EdgeGroup]]:
    return {v: read_edges(v) for v in get_args(ResPlanIds)}


campaign_defn = DefinitionDict(
    case_names=process_resplan_ids(),
    case_variables=["rooms", "edge_groups"],
    modifications=[
        # Variable(
        #     name="window_dimension",
        #     options=[
        #         Option("-30%"),
        #         Option("Default", IS_DEFAULT=True),
        #         Option("+30%"),
        #     ],
        # ),
        # Variable(
        #     name="door_vent_schedule",
        #     options=[
        #         Option("Always Closed"),
        #         Option("Dynamic"),
        #         Option("Always Open", IS_DEFAULT=True),
        #     ],
        # ),
        # Variable(
        #     name="construction_set",
        #     options=[
        #         Option("Light"),
        #         Option("Medium", IS_DEFAULT=True),
        #         Option("Heavy"),
        #     ],
        # ),
    ],
)


campaign_data = DataDict(
    case={
        "rooms": generate_rooms(),
        "edge_groups": generate_edge_groups(),
        # "edge_groups": generate_edge_groups(),
        # "airboundary_edges": generate_airboundary_edges(),
    },
    mods={
        # "window_dimension": generate_window_dimensions(),
        # "door_vent_schedule": generate_door_venting_schedules(),
        # "construction_set": generate_construction_sets(),
    },
)
